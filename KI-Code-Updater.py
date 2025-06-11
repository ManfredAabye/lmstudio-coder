# KI-Code-Updater.py
# Dieses Skript aktualisiert Python-Code in einem Verzeichnis mithilfe von LM Studio KI.

# Prompt Beispiel für Blender 4.4-Update
# """Aktualisiere diesen Blender-Python-Code für Version 4.4:
#     - Ersetze veraltete API-Aufrufe (z. B. `bpy.context` → `bpy.context.scene`).
#     - Suche 2.8.0 und ersetze diese durch 4.4.0
#     - Behalte die Funktionalität bei.
#     Hier der Code:\n\n{code}"""

import os
import json
import requests
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
        
        self.create_ui()
        self.load_last_settings()
        
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
            with open("last_settings.json", "r") as f:
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
        with open("last_settings.json", "w") as f:
            json.dump(settings, f)

    def load_prompt(self):
        filepath = filedialog.askopenfilename(
            title="Prompt laden",
            filetypes=[("JSON Dateien", "*.json"), ("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, "r") as f:
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
                    with open(filepath, "w") as f:
                        json.dump({
                            "language": self.language_var.get(),
                            "prompt": prompt_content,
                            "saved_at": datetime.now().isoformat()
                        }, f, indent=2)
                else:
                    with open(filepath, "w") as f:
                        f.write(prompt_content)
            except Exception as e:
                messagebox.showerror("Fehler", f"Prompt konnte nicht gespeichert werden:\n{str(e)}")

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)

    def ask_lm_studio(self, prompt, language):
        try:
            response = requests.post(
                "http://localhost:1234/v1/chat/completions",
                json={
                    "messages": [
                        {
                            "role": "system",
                            "content": f"Du bist ein {language}-Experte. Antworte NUR mit Code."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2048
                },
                timeout=90
            )
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            self.status_var.set(f"API-Fehler: {str(e)}")
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
        except Exception:
            return False

    def update_file(self, filepath, index, total):
        try:
            if not self.create_backup(filepath):
                return False

            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()

            prompt_template = self.prompt_entry.get("1.0", "end-1c")
            language = self.language_var.get()
            prompt = prompt_template.format(language=language, code=code[:8000])

            self.status_var.set(f"Verarbeite {index}/{total}: {os.path.basename(filepath)}")
            self.root.update_idletasks()

            updated_code = self.ask_lm_studio(prompt, language)
            if updated_code:
                cleaned_code = self.clean_code_response(updated_code)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(cleaned_code)
                return True
        except Exception as e:
            self.status_var.set(f"Fehler bei {filepath}: {str(e)}")
        return False

    def clean_code_response(self, code):
        if "```" in code:
            parts = code.split("```")
            if len(parts) > 1:
                return parts[1].strip().lstrip("python\n")
        return code

    def run_update(self):
        directory = self.dir_entry.get()
        if not directory:
            messagebox.showerror("Fehler", "Bitte Verzeichnis auswählen!")
            return

        self.save_settings()

        extension = file_extensions.get(self.language_var.get(), ".py")
        target_files = []

        for root_dir, _, files in os.walk(directory):
            target_files.extend(
                os.path.join(root_dir, f) for f in files 
                if f.endswith(extension) and not root_dir.endswith("backups")
            )

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
            f"Backups wurden im 'backups'-Ordner gespeichert."
        )
        self.status_var.set(f"Fertig - {success}/{len(target_files)} Dateien aktualisiert")

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeUpdaterApp(root)
    root.mainloop()
