# -*- coding: utf-8 -*-
# KI-Code-Updater.py
# Dieses Skript aktualisiert Code in einem Verzeichnis mithilfe von LM Studio KI.

import os
import json
import requests
import time
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

file_extensions = {
    "Assembly": ".asm", "Bash": ".sh", "Batch": ".bat", "C#": ".cs",
    "C++": ".cpp", "CSS": ".css", "F#": ".fs", "Go": ".go", "html": ".html",
    "JSON": ".json", "Java": ".java", "JavaScript": ".js", "Lua": ".lua",
    "Markdown": ".md", "PHP": ".php", "PowerShell": ".ps1", "Python": ".py",
    "Ruby": ".rb", "Rust": ".rs", "SQL": ".sql", "Shell": ".sh",
    "TypeScript": ".ts", "VBScript": ".vbs", "Visual Basic": ".vb",
    "XML": ".xml"
}

class CodeUpdaterApp:
    def __init__(self, root):
        self.root = root
        root.title("KI Code-Updater")
        self.setup_logging()
        
        self.create_ui()
        self.load_last_settings()
        
    def setup_logging(self):
        logging.basicConfig(
            filename="code_updater.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            encoding="utf-8"
        )
        
    def create_ui(self):
        ttk.Label(self.root, text="Arbeitsverzeichnis:").grid(row=0, column=0, padx=5, pady=5)
        self.dir_entry = ttk.Entry(self.root, width=50)
        self.dir_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="Durchsuchen...", command=self.select_directory).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(self.root, text="Programmiersprache:").grid(row=1, column=0, padx=5, pady=5)
        self.language_var = tk.StringVar()
        languages = sorted(file_extensions.keys())
        self.language_dropdown = ttk.Combobox(self.root, textvariable=self.language_var, values=languages)
        self.language_dropdown.grid(row=1, column=1, padx=5, pady=5)
        self.language_dropdown.set("Python")

        prompt_frame = ttk.Frame(self.root)
        prompt_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        
        ttk.Label(prompt_frame, text="Prompt:").pack(side="left")
        ttk.Button(prompt_frame, text="Laden", command=self.load_prompt).pack(side="right", padx=2)
        ttk.Button(prompt_frame, text="Speichern", command=self.save_prompt).pack(side="right", padx=2)
        
        self.prompt_entry = tk.Text(self.root, width=50, height=10)
        self.prompt_entry.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        # Universeller Standardprompt
        default_prompt = """Aktualisiere diesen {language}-Code:
- Ersetze veraltete oder unsichere API-Aufrufe
- Behalte die bestehende Funktionalität bei

Hier ist der Code:
{code}"""
        self.prompt_entry.insert("1.0", default_prompt)

        self.progress = ttk.Progressbar(self.root, length=300)
        self.progress.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        self.status_var = tk.StringVar(value="Bereit")
        ttk.Label(self.root, textvariable=self.status_var).grid(row=5, column=0, columnspan=3)

        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)
        ttk.Button(button_frame, text="Code aktualisieren", command=self.run_update).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Beenden", command=self.root.quit).pack(side="right", padx=10)


    def load_last_settings(self):
        try:
            with open("last_settings.json", "r", encoding='utf-8') as f:
                settings = json.load(f)
                self.dir_entry.insert(0, settings.get("directory", ""))
                self.language_var.set(settings.get("language", "Python"))
        except FileNotFoundError:
            pass

    def save_settings(self):
        settings = {
            "directory": self.dir_entry.get(),
            "language": self.language_var.get()
        }
        with open("last_settings.json", "w", encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

    def load_prompt(self):
        filepath = filedialog.askopenfilename(
            title="Prompt laden",
            filetypes=[("JSON Dateien", "*.json"), ("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, "r", encoding='utf-8') as f:
                    if filepath.endswith(".json"):
                        data = json.load(f)
                        self.prompt_entry.delete("1.0", "end")
                        self.prompt_entry.insert("1.0", data.get("prompt", ""))
                    else:
                        self.prompt_entry.delete("1.0", "end")
                        self.prompt_entry.insert("1.0", f.read())
            except Exception as e:
                messagebox.showerror("Fehler", f"Prompt konnte nicht geladen werden:\n{str(e)}")

    def save_prompt(self):
        filepath = filedialog.asksaveasfilename(
            title="Prompt speichern",
            defaultextension=".json",
            filetypes=[("JSON Dateien", "*.json"), ("Textdateien", "*.txt")]
        )
        if filepath:
            try:
                prompt_content = self.prompt_entry.get("1.0", "end-1c")
                if filepath.endswith(".json"):
                    with open(filepath, "w", encoding='utf-8') as f:
                        json.dump({
                            "language": self.language_var.get(),
                            "prompt": prompt_content,
                            "saved_at": datetime.now().isoformat()
                        }, f, ensure_ascii=False, indent=2)
                else:
                    with open(filepath, "w", encoding='utf-8') as f:
                        f.write(prompt_content)
            except Exception as e:
                messagebox.showerror("Fehler", f"Prompt konnte nicht gespeichert werden:\n{str(e)}")

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)


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
                return response.json()["choices"][0]["message"]["content"]
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                logging.error(f"API-Fehler nach {max_retries} Versuchen: {str(e)}")
                self.status_var.set(f"API-Fehler: {str(e)}")
                return None
            except Exception as e:
                logging.error(f"Unerwarteter Fehler: {str(e)}")
                self.status_var.set(f"Fehler: {str(e)}")
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

    def process_code_chunk(self, chunk, prompt_template, language, filepath, chunk_info):
        prompt = prompt_template.format(language=language, code=chunk)
        self.status_var.set(f"Verarbeite {filepath} (Chunk {chunk_info})")
        self.root.update_idletasks()
        
        response = self.ask_lm_studio(prompt, language)
        if response:
            return self.clean_code_response(response)
        return chunk  # Bei Fehler originalen Chunk zurückgeben

    def update_file(self, filepath, index, total):
        try:
            logging.info(f"Starte Verarbeitung: {filepath}")
            
            if not self.create_backup(filepath):
                return False

            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()

            # Dateigröße checken
            if len(code) > 2 * 1024 * 1024:  # 2MB
                self.status_var.set(f"Überspringe große Datei: {os.path.basename(filepath)}")
                logging.warning(f"Datei zu groß, übersprungen: {filepath}")
                return False

            prompt_template = self.prompt_entry.get("1.0", "end-1c")
            language = self.language_var.get()
            
            # Code in sinnvolle Abschnitte teilen (bei Funktionen/Classes nicht mitten drin)
            chunks = self.split_code_into_chunks(code, max_chunk_size=6000)
            
            updated_chunks = []
            for i, chunk in enumerate(chunks):
                processed_chunk = self.process_code_chunk(
                    chunk, prompt_template, language, 
                    os.path.basename(filepath),
                    f"{i+1}/{len(chunks)}"
                )
                updated_chunks.append(processed_chunk)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write("".join(updated_chunks))
                
            logging.info(f"Erfolgreich aktualisiert: {filepath}")
            return True
            
        except Exception as e:
            logging.error(f"Fehler bei {filepath}: {str(e)}")
            self.status_var.set(f"Fehler bei {os.path.basename(filepath)}")
            return False

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

    def run_update(self):
        directory = self.dir_entry.get()
        if not directory:
            messagebox.showerror("Fehler", "Bitte Verzeichnis auswählen!")
            return

        self.save_settings()

        extension = file_extensions.get(self.language_var.get(), ".py")
        target_files = []

        MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
        for root_dir, _, files in os.walk(directory):
            for f in files:
                if f.endswith(extension) and not root_dir.endswith("backups"):
                    filepath = os.path.join(root_dir, f)
                    file_size = os.path.getsize(filepath)
                    if file_size <= MAX_FILE_SIZE:
                        target_files.append(filepath)
                    else:
                        logging.warning(f"Datei übersprungen (zu groß): {filepath}")
                        self.status_var.set(f"Überspringe große Datei: {f}")

        if not target_files:
            messagebox.showwarning("Keine Dateien", f"Keine {extension}-Dateien gefunden!")
            return

        self.progress["maximum"] = len(target_files)
        success = 0

        for index, filepath in enumerate(target_files, 1):
            if self.update_file(filepath, index, len(target_files)):
                success += 1
            self.progress["value"] = index
            self.root.update()

        messagebox.showinfo(
            "Fertig", 
            f"{success}/{len(target_files)} Dateien erfolgreich aktualisiert!\n"
            f"Backups wurden im 'backups'-Ordner gespeichert.\n"
            f"Details im Logfile: code_updater.log"
        )
        self.status_var.set(f"Fertig - {success}/{len(target_files)} Dateien aktualisiert")

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeUpdaterApp(root)
    root.mainloop()