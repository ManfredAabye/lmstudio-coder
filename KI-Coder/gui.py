# -*- coding: utf-8 -*-
# Grafische Benutzeroberfläche

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from datetime import datetime
import logging
from file_processor import FileProcessor
from config import file_extensions

class CodeUpdaterApp:
    def __init__(self, root):
        self.root = root
        root.title("KI Code-Updater v1.0")
        self.setup_logging()
        self.create_ui()
        self.load_last_settings()
        
        # Initialize FileProcessor with callbacks
        self.file_processor = FileProcessor()
        
        # Set window icon if available
        try:
            root.iconbitmap('icon.ico')  # Provide your icon file
        except:
            pass
        
        # Make window resizable
        root.minsize(600, 500)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(3, weight=1)

    def setup_logging(self):
        logging.basicConfig(
            filename="code_updater.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            encoding="utf-8"
        )
        self.logger = logging.getLogger(__name__)
        
    def create_ui(self):
        # Configure style
        style = ttk.Style()
        style.configure('TButton', padding=5)
        style.configure('TLabel', padding=5)
        
        # Directory selection
        dir_frame = ttk.Frame(self.root)
        dir_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        dir_frame.columnconfigure(1, weight=1)
        
        ttk.Label(dir_frame, text="Arbeitsverzeichnis:").grid(row=0, column=0, sticky="w")
        self.dir_entry = ttk.Entry(dir_frame)
        self.dir_entry.grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(dir_frame, text="Durchsuchen...", command=self.select_directory).grid(row=0, column=2)

        # Language selection
        lang_frame = ttk.Frame(self.root)
        lang_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        
        ttk.Label(lang_frame, text="Programmiersprache:").grid(row=0, column=0, sticky="w")
        self.language_var = tk.StringVar()
        languages = sorted(file_extensions.keys())
        self.language_dropdown = ttk.Combobox(lang_frame, textvariable=self.language_var, values=languages, state="readonly")
        self.language_dropdown.grid(row=0, column=1, sticky="ew", padx=5)
        self.language_dropdown.set("Python")

        # Prompt section
        prompt_frame = ttk.LabelFrame(self.root, text="Prompt", padding=10)
        prompt_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        prompt_frame.columnconfigure(0, weight=1)
        
        # Prompt buttons
        btn_frame = ttk.Frame(prompt_frame)
        btn_frame.grid(row=0, column=0, sticky="ew", pady=(0,5))
        
        ttk.Button(btn_frame, text="Standard", command=self.load_default_prompt).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Laden", command=self.load_prompt).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Speichern", command=self.save_prompt).pack(side="left", padx=2)
        
        # Prompt text area with scrollbar
        prompt_container = ttk.Frame(prompt_frame)
        prompt_container.grid(row=1, column=0, sticky="nsew")
        prompt_container.columnconfigure(0, weight=1)
        prompt_container.rowconfigure(0, weight=1)
        
        self.prompt_entry = tk.Text(prompt_container, wrap="word")
        self.prompt_entry.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(prompt_container, command=self.prompt_entry.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.prompt_entry.config(yscrollcommand=scrollbar.set)
        
        # Load default prompt
        self.load_default_prompt()

        # Progress bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Status label
        self.status_var = tk.StringVar(value="Bereit")
        status_label = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", padding=5)
        status_label.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        # Action buttons
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Code aktualisieren", command=self.run_update, style="Accent.TButton").pack(side="left", padx=10)
        ttk.Button(button_frame, text="Beenden", command=self.on_exit).pack(side="right", padx=10)

    def load_default_prompt(self):
        """Load the default prompt template"""
        default_prompt = """Aktualisiere diesen {language}-Code:
- Ersetze veraltete oder unsichere API-Aufrufe
- Behalte die bestehende Funktionalität bei
- Verbessere die Codequalität wo möglich
- Füge Kommentare hinzu wo nötig

Hier ist der Code:
{code}"""
        self.prompt_entry.delete("1.0", "end")
        self.prompt_entry.insert("1.0", default_prompt)

    def load_last_settings(self):
        """Load last used settings from file"""
        try:
            with open("last_settings.json", "r", encoding='utf-8') as f:
                settings = json.load(f)
                self.dir_entry.insert(0, settings.get("directory", ""))
                self.language_var.set(settings.get("language", "Python"))
                self.logger.info("Einstellungen geladen")
        except FileNotFoundError:
            self.logger.info("Keine gespeicherten Einstellungen gefunden")
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Einstellungen: {str(e)}")
            messagebox.showwarning("Warnung", "Einstellungen konnten nicht geladen werden")

    def save_settings(self):
        """Save current settings to file"""
        settings = {
            "directory": self.dir_entry.get(),
            "language": self.language_var.get(),
            "last_updated": datetime.now().isoformat()
        }
        try:
            with open("last_settings.json", "w", encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.logger.info("Einstellungen gespeichert")
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Einstellungen: {str(e)}")

    def load_prompt(self):
        """Load prompt from file"""
        filepath = filedialog.askopenfilename(
            title="Prompt laden",
            filetypes=[("JSON Dateien", "*.json"), ("Textdateien", "*.txt"), ("Alle Dateien", "*.*")],
            initialdir="."
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
                self.logger.info(f"Prompt geladen aus {filepath}")
            except Exception as e:
                self.logger.error(f"Fehler beim Laden des Prompts: {str(e)}")
                messagebox.showerror("Fehler", f"Prompt konnte nicht geladen werden:\n{str(e)}")

    def save_prompt(self):
        """Save prompt to file"""
        filepath = filedialog.asksaveasfilename(
            title="Prompt speichern",
            defaultextension=".json",
            filetypes=[("JSON Dateien", "*.json"), ("Textdateien", "*.txt")],
            initialdir="."
        )
        if filepath:
            try:
                prompt_content = self.prompt_entry.get("1.0", "end-1c")
                if filepath.endswith(".json"):
                    data = {
                        "language": self.language_var.get(),
                        "prompt": prompt_content,
                        "saved_at": datetime.now().isoformat()
                    }
                    with open(filepath, "w", encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                else:
                    with open(filepath, "w", encoding='utf-8') as f:
                        f.write(prompt_content)
                self.logger.info(f"Prompt gespeichert in {filepath}")
            except Exception as e:
                self.logger.error(f"Fehler beim Speichern des Prompts: {str(e)}")
                messagebox.showerror("Fehler", f"Prompt konnte nicht gespeichert werden:\n{str(e)}")

    def select_directory(self):
        """Select working directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
            self.logger.info(f"Verzeichnis ausgewählt: {directory}")

    def update_progress(self, value):
        """Update progress bar"""
        self.progress["value"] = value
        self.root.update_idletasks()

    def run_update(self):
        """Run the code update process"""
        directory = self.dir_entry.get()
        if not directory or not os.path.isdir(directory):
            messagebox.showerror("Fehler", "Bitte gültiges Verzeichnis auswählen!")
            return

        self.save_settings()
        
        # Prepare progress bar
        self.progress["value"] = 0
        self.status_var.set("Vorbereitung...")
        self.root.update_idletasks()
        
        # Get parameters
        prompt_template = self.prompt_entry.get("1.0", "end-1c")
        language = self.language_var.get()
        
        # Configure callbacks
        def status_callback(message):
            self.status_var.set(message)
            self.root.update_idletasks()
            
        def progress_callback(value):
            self.progress["value"] = value
            self.root.update_idletasks()
        
        # Run the update
        try:
            success = self.file_processor.run_update(
                directory=directory,
                language=language,
                prompt_template=prompt_template,
                status_callback=status_callback,
                progress_callback={"maximum": self.progress["maximum"], "step": lambda x: self.update_progress(x)}
            )
            
            if success is not False:
                messagebox.showinfo("Erfolg", f"Code-Update abgeschlossen!\n{success} Dateien wurden aktualisiert.")
                self.logger.info(f"Update erfolgreich abgeschlossen. {success} Dateien aktualisiert.")
            else:
                messagebox.showwarning("Warnung", "Update wurde nicht durchgeführt.")
                self.logger.warning("Update nicht durchgeführt")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Ein schwerwiegender Fehler ist aufgetreten:\n{str(e)}")
            self.logger.error(f"Update fehlgeschlagen: {str(e)}", exc_info=True)
        finally:
            self.status_var.set("Bereit")
            self.progress["value"] = 0

    def on_exit(self):
        """Handle application exit"""
        self.save_settings()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeUpdaterApp(root)
    root.mainloop()