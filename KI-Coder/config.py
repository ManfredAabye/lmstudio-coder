# -*- coding: utf-8 -*-
# Konfiguration und Konstanten

file_extensions = {
    "Assembly": ".asm", "Bash": ".sh", "Batch": ".bat", "C#": ".cs",
    "C++": ".cpp", "CSS": ".css", "F#": ".fs", "Go": ".go", "html": ".html",
    "JSON": ".json", "Java": ".java", "JavaScript": ".js", "Lua": ".lua",
    "Markdown": ".md", "PHP": ".php", "PowerShell": ".ps1", "Python": ".py",
    "Ruby": ".rb", "Rust": ".rs", "SQL": ".sql", "Shell": ".sh",
    "TypeScript": ".ts", "VBScript": ".vbs", "Visual Basic": ".vb",
    "XML": ".xml"
}

DEFAULT_PROMPT = """Aktualisiere diesen {language}-Code:
- Ersetze veraltete oder unsichere API-Aufrufe
- Behalte die bestehende Funktionalität bei

Hier ist der Code:
{code}"""