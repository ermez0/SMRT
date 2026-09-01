import sys
import subprocess
import state
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from typing import Any
import shutil
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

def list_overrides_dict(active_overrides:dict[Any,Any], noPrint:bool = False) -> list[str]:
    overrides_list: list[str] = []
    for i,replacing in enumerate(active_overrides):
        if not noPrint:
            print("ID: " + str(i) + " | " + str(replacing) + " is being overridden by "+ active_overrides[str(replacing)])
        overrides_list.append(str(replacing))
    return overrides_list

def nuke_smrt(gmod_path:Path) -> bool:
    assert state.audio_path is not None
    assert state.platform is not None and state.scr_root is not None and state.config_path is not None
    assert state.config_dict is not None
    clear_terminal()
    smrt_addon_folder = gmod_path / "garrysmod" / "addons" / "smrt"
    audio_cache_folder = state.scr_root / "audio_cache"
    print("NOTE: THIS WILL WIPE \"" + str(smrt_addon_folder) + "\", \"" + str(state.audio_path) +"\" and \""+ str(audio_cache_folder) + "\".\n"
    "If any of those directories should not be wiped, do NOT proceed with the deletion! ")
    print("Are you sure you want to proceed and nuke SMRT? If so, type \"YES\".")
    confirm = input("Choice: ")
    if confirm == "YES":
        if smrt_addon_folder.is_dir():
            shutil.rmtree(smrt_addon_folder)
        if state.audio_path.is_dir():
            shutil.rmtree(state.audio_path)
        if audio_cache_folder.is_dir():
            shutil.rmtree(audio_cache_folder)
        return True
    return False

def config_sanity_chceck(config_dict: dict, gmod_path: Path) -> bool:
    real_count = 0
    for file in (gmod_path / "garrysmod" / "addons" / "smrt").rglob("*.mp3"):
        if file.is_file():
            real_count += 1
    config_count = len(config_dict["active_overrides"])
    if real_count != config_count:
        return False
    return True
