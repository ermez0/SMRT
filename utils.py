import sys
import subprocess
import state
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
def clear_terminal() -> None:
    if sys.platform == "win32":
        clear = "cls"
    else:
        clear = "clear"
    subprocess.run(clear,shell=True) # shell = True because cls is not a program
    print("SMRT -- The Shinri Music Replacement Tool v" + str(state.VERSION) + "\n" + "-"*46)

def folder_picker(windowTitle: str) -> Path | None:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True) # type: ignore
    folder = filedialog.askdirectory(title=windowTitle)
    root.destroy()
    return Path(folder) if folder else None

def file_picker(windowTitle: str, fileTypes: list, initialDir: Path | None = None) -> Path | None: # type: ignore
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True) # type: ignore
    file = filedialog.askopenfilename(
                        title=windowTitle,
                        filetypes=fileTypes, # type: ignore
                        initialdir=initialDir)
    root.destroy()
    return Path(file) if file else None

def get_scr_root() -> Path:
    if getattr(sys, "frozen", False):
        scr_root = Path(sys.executable).parent
    else:
        scr_root = Path(__file__).resolve().parent
    return scr_root

def get_platform():
    if sys.platform.startswith("win32"):
        platform = "win32"
    elif sys.platform.startswith("darwin"):
        platform = "macos"
    elif sys.platform.startswith("linux"):
        platform = "linux" 
    else:
        platform = "undefined"
        print("Could not identify operating system! Input \"BYPASS\" to bypass this check. Proceeding from here on out is unsupported.(Much like everything in this program)")
        choice = input("Choice: ")
        if choice.strip().upper() != "BYPASS":
            sys.exit("OS not recognized.")
    return platform

