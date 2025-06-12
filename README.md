# LM Studio KI Coder

Dieses Tool aktualisiert automatisch Quellcode-Dateien in einem Verzeichnis mithilfe einer lokalen KI (z. B. LM Studio + LLM). Unterstützt werden viele Programmiersprachen wie Python, C++, JavaScript, Rust u. v. m.

## ✨ Funktionen

- Lokale Verarbeitung über LM Studio (kein Cloud-Zwang)
- Unterstützung für zahlreiche Programmiersprachen
- Backups aller bearbeiteten Dateien
- Individuell anpassbarer Prompt

---

## 🧠 Voraussetzungen

- [LM Studio](https://lmstudio.ai) installiert und gestartet
- Ein passendes LLM-Modell ist geladen und als **lokaler Chat-Endpunkt** erreichbar:

[http://localhost:1234/v1/chat/completions](http://localhost:1234/v1/chat/completions)

> Tipp: In LM Studio unter „API“ den lokalen Server aktivieren und Port 1234 verwenden.

---

## 🛠 Installation

1. **Python 3.8+** installieren (falls noch nicht vorhanden)
2. Erforderliche Pakete (nur Standard-Libraries werden genutzt)
3. Repository klonen oder Dateien lokal speichern
4. Programm starten:

 ```bash
 python KI-Code-Updater.py
````

---

## 🚀 Verwendung

1. **Arbeitsverzeichnis** wählen (z. B. ein Projektordner mit `.py`, `.js` usw.)
2. **Programmiersprache** auswählen
3. **Prompt anpassen** (optional)

   * Platzhalter `{language}` und `{code}` werden automatisch ersetzt
4. Auf **„Code aktualisieren“** klicken
5. Ergebnis abwarten – Fortschrittsbalken zeigt den Status an

> ✅ Alle bearbeiteten Dateien werden vorher gesichert (Ordner `backups/` im jeweiligen Quellverzeichnis).

---

## 🔧 Beispiel-Prompt

```text
Aktualisiere diesen {language}-Code:
- Ersetze veraltete oder unsichere Syntax
- Behalte die Funktionalität bei

Code:
{code}
```

---

## 📁 Unterstützte Sprachen & Dateiendungen

| Sprache    | Endung  |
| ---------- | ------- |
| Assembly  | .asm    |
| Bash      | .sh     |
| Batch     | .bat    |
| C#        | .cs     |
| C++       | .cpp    |
| CSS       | .css    |
| F#        | .fs     |
| Go        | .go     |
| HTML      | .html   |
| JSON      | .json   |
| Java      | .java   |
| JavaScript| .js     |
| Lua       | .lua    |
| Markdown  | .md     |
| PHP       | .php    |
| PowerShell| .ps1    |
| Python    | .py     |
| Ruby      | .rb     |
| Rust      | .rs     |
| SQL       | .sql    |
| Shell     | .sh     |
| TypeScript| .ts     |
| VBScript  | .vbs    |
| Visual Basic| .vb   |
| XML       | .xml    |

> Die vollständige Liste wird dynamisch aus dem internen Mapping erzeugt.

---

## ❓ Fehlersuche

* **„API-Fehler: Verbindung abgelehnt“** → Ist LM Studio aktiv und auf Port 1234?
* **Keine Dateien gefunden** → Verzeichnis korrekt gewählt? Sprache und Dateiendung stimmen überein?

---

Hier ist die optimale Konfiguration für **Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf** in LM Studio, um die besten Ergebnisse mit Ihrem Code-Updater zu erzielen:

## 1. **Modell in LM Studio laden**
- Herunterladen der Modelldatei ([z.B. von HuggingFace](https://huggingface.co/TheBloke/Meta-Llama-3-8B-Instruct-GGUF))
- In LM Studio: 
  - Zu **"Models"** navigieren
  - Modelldatei (`Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf`) auswählen

## 2. **Empfohlene Modelleinstellungen**
| Einstellung          | Optimaler Wert       | Erklärung |
|----------------------|----------------------|-----------|
| **Context Length**   | 4096                 | Maximale Kontextlänge für Codeanalyse |
| **Temperature**      | 0.3 - 0.5            | Für präzise Code-Updates (nicht zu kreativ) |
| **Top-K**           | 40                   | Balance zwischen Qualität und Vielfalt |
| **Top-P**           | 0.9                  | Filtert unwahrscheinliche Optionen |
| **Repeat Penalty**  | 1.1                  | Vermeidet Wiederholungen im Code |

## 3. **API-Server starten**
1. In LM Studio zu **"Local Server"** wechseln
2. Folgende API-Einstellungen wählen:
   ```json
   {
     "port": 1234,
     "enable_api": true,
     "model": "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
     "context_length": 4096
   }
   ```
3. **"Start Server"** klicken

## 4. **Code-Updater anpassen (optional)**
In `file_processor.py` die API-Parameter optimieren:
```python
response = requests.post(
    "http://localhost:1234/v1/chat/completions",
    json={
        "messages": [
            {"role": "system", "content": f"Du bist ein {language}-Experte. Antworte NUR mit Code."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,  # Für konservative Code-Änderungen
        "top_k": 40,
        "top_p": 0.9,
        "max_tokens": 4000
    },
    timeout=180
)
```

## 5. **Prompt-Engineering für bessere Ergebnisse**
```text
Aktualisiere diesen {language}-Code:
- Behalte die Funktionalität bei
- Ersetze veraltete/deprecated Funktionen
- Verbessere die Lesbarkeit
- Füge kurze Kommentare hinzu wo nötig

Code:
{code}
```

## 💡 Tipps für beste Performance:
1. **GPU-Beschleunigung aktivieren** (falls verfügbar)
2. **Nicht zu viele Dateien parallel** verarbeiten (LM Studio arbeitet besser sequenziell)
3. **Chunk-Größe** in `file_processor.py` auf ~6000 Zeichen begrenzen

Mit diesen Einstellungen erhalten Sie:
- Präzisere Code-Updates
- Bessere Beibehaltung der Originalfunktionalität
- Schnellere Verarbeitung durch optimierte Parameter
