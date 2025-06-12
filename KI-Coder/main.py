# -*- coding: utf-8 -*-
# Hauptanwendung

import tkinter as tk
from gui import CodeUpdaterApp
import sys
import io

if sys.stdout.encoding != 'UTF-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeUpdaterApp(root)
    root.mainloop()
