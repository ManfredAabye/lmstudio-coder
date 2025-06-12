# -*- coding: utf-8 -*-
# Verarbeitung der Code-Dateien

import os
import requests
import time
import logging
from datetime import datetime
from config import file_extensions

class FileProcessor:
    def __init__(self):
        self.status_callback = None
        self.progress_callback = None

    def run_update(self, directory, language, prompt_template, status_callback, progress_callback):
        """Hauptmethode zur Aktualisierung der Dateien"""
        self.status_callback = status_callback
        self.progress_callback = progress_callback
        
        extension = file_extensions.get(language, ".py")
        target_files = self.find_target_files(directory, extension)
        
        if not target_files:
            if self.status_callback:
                self.status_callback(f"Keine {extension}-Dateien gefunden!")
            return False

        if self.progress_callback:
            self.progress_callback["maximum"] = len(target_files)

        success = 0
        for index, filepath in enumerate(target_files, 1):
            if self.update_file(filepath, prompt_template, language, index, len(target_files)):
                success += 1
            if self.progress_callback:
                self.progress_callback["value"] = index

        if self.status_callback:
            self.status_callback(f"Fertig - {success}/{len(target_files)} Dateien aktualisiert")
        return success

    def find_target_files(self, directory, extension):
        """Sucht nach Dateien mit der gegebenen Endung"""
        target_files = []
        for root_dir, _, files in os.walk(directory):
            for f in files:
                if f.endswith(extension) and not root_dir.endswith("backups"):
                    filepath = os.path.join(root_dir, f)
                    if os.path.getsize(filepath) <= 2 * 1024 * 1024:  # Max 2MB
                        target_files.append(filepath)
        return target_files

    def update_file(self, filepath, prompt_template, language, index, total_files):
        try:
            if self.status_callback:
                self.status_callback(f"Verarbeite {os.path.basename(filepath)} ({index}/{total_files})")

            # 1. Backup erstellen
            if not self.create_backup(filepath):
                return False

            # 2. Datei lesen
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()

            # 3. Code in Chunks teilen
            chunks = self.split_code_into_chunks(code, max_chunk_size=6000)
            updated_chunks = []

            # 4. Jeden Chunk verarbeiten
            for i, chunk in enumerate(chunks):
                processed_chunk = self.process_code_chunk(
                    chunk, 
                    prompt_template, 
                    language,
                    os.path.basename(filepath),
                    f"{i+1}/{len(chunks)}"
                )
                if processed_chunk is None:
                    return False  # Verarbeitung fehlgeschlagen
                updated_chunks.append(processed_chunk)

            # 5. Aktualisierte Datei speichern
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("".join(updated_chunks))

            logging.info(f"Erfolgreich aktualisiert: {filepath}")
            return True

        except Exception as e:
            logging.error(f"Fehler in {filepath}: {str(e)}")
            if self.status_callback:
                self.status_callback(f"Fehler bei {os.path.basename(filepath)}")
            return False

    def ask_lm_studio(self, prompt, language):
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "http://localhost:1234/v1/chat/completions",
                    json={
                        "messages": [
                            {"role": "system", "content": f"Du bist ein {language}-Experte. Antworte NUR mit Code."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 4000
                    },
                    timeout=180
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                logging.error(f"API-Fehler nach {max_retries} Versuchen: {str(e)}")
                if self.status_callback:
                    self.status_callback(f"API-Fehler: {str(e)}")
                return None
            except Exception as e:
                logging.error(f"Unerwarteter Fehler: {str(e)}")
                if self.status_callback:
                    self.status_callback(f"Fehler: {str(e)}")
                return None

    def create_backup(self, filepath):
        backup_dir = os.path.join(os.path.dirname(filepath), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"{os.path.basename(filepath)}.bak_{timestamp}")
        try:
            with open(filepath, "rb") as src, open(backup_path, "wb") as dst:
                dst.write(src.read())
            return True
        except Exception as e:
            logging.error(f"Backup fehlgeschlagen für {filepath}: {str(e)}")
            return False

    def process_code_chunk(self, chunk, prompt_template, language, filename, chunk_info):
        prompt = prompt_template.format(language=language, code=chunk)
        if self.status_callback:
            self.status_callback(f"Verarbeite {filename} (Chunk {chunk_info})")
        
        response = self.ask_lm_studio(prompt, language)
        if response:
            return self.clean_code_response(response)
        return None  # Bei Fehler None zurückgeben

    def split_code_into_chunks(self, code, max_chunk_size):
        """Teilt Code in sinnvolle Abschnitte, ohne mitten in Funktionen/Classes zu trennen"""
        chunks = []
        current_chunk = ""
        
        # Einfache Implementierung - kann für spezifische Sprachen verbessert werden
        lines = code.split('\n')
        for line in lines:
            if len(current_chunk) + len(line) > max_chunk_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = line + '\n'
            else:
                current_chunk += line + '\n'
        
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    def clean_code_response(self, code):
        if "```" in code:
            parts = code.split("```")
            if len(parts) > 1:
                # Entferne Markdown-Codeblöcke
                code = parts[1].strip()
                if code.lower().startswith("python\n"):
                    code = code[7:]
        return code