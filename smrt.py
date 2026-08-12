"""
SMRT -- The Shinri Music Replacement Tool
I know this code is terrible, I don't expect anyone but me to work on it -ermez
"""
# Imports
import vdf # pyright: ignore[reportMissingTypeStubs]
import sys
import shutil
import json
import subprocess
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import Any,cast
# Default config
template_config: dict[Any,Any] = {
    "version":0.3,
    "path_to_gmod": None,
    "path_to_workshop":None,
    "extraction":False,
    "active_overrides" : {} # format will be "active_overrides" : {"something(replacing)":"another thing(the replacement)"}
}

# Saves the JSON provided as config to config_path
def saveConfig(config:dict[Any,Any],config_path:Path) -> None:
    with open(config_path,"w",encoding="utf-8") as fconfig:
        json.dump(config,fconfig,indent=4)

# Extracts the .gma file at gma_path using gmad.exe found at gmad_path and saves the output at out_path
def extractGMA(gmad_path:Path,gma_path:Path,out_path:Path) -> bool:
    #if gmad/gma doesnt exist, quit
    if not gmad_path.is_file() or not gma_path.is_file():
        return False
    # the command
    command = [
        str(gmad_path), 
        "extract", 
        "-file", str(gma_path), 
        "-out", str(out_path)
    ]
    #runs the command
    result = subprocess.run(command,capture_output=True,text=True)
    #if gmad didnt return 0, it failed
    if result.returncode != 0:
        print("GMAD extraction failed!")
        print(result.stderr)
        return False
    #if gmad's output has "Problem" in it
    if "Problem" in result.stdout or "Problem" in result.stderr:
        print("GMAD experienced a problem.")
        print(result.stdout)
        print(result.stderr)
        return False
    #if the output directory is empty or doesnt exist than it failed
    if not out_path.exists() or not out_path.is_dir() or not any(out_path.iterdir()):
        print("It appears output directory is empty.")
        return False
    #if none of the above are true, the extract succeeded
    return True

def clearTerminal() -> None:
    if sys.platform == "win32":
        clear = "cls"
    else:
        clear = "clear"
    subprocess.run(clear,shell=True) # shell = True because cls is not a program
    print("SMRT -- The Shinri Music Replacement Tool\n" + "-"*41)

def folderPicker(windowTitle: str) -> Path | None:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True) # type: ignore
    folder = filedialog.askdirectory(title=windowTitle)
    root.destroy()
    return Path(folder) if folder else None

def filePicker(windowTitle: str, fileTypes: list, initialDir: Path | None = None) -> Path | None: # type: ignore
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True) # type: ignore
    file = filedialog.askopenfilename(
                        title=windowTitle,
                        filetypes=fileTypes, # type: ignore
                        initialdir=initialDir)
    root.destroy()
    return Path(file) if file else None

def getScriptRoot() -> Path:
    if getattr(sys, "frozen", False):
        scr_root = Path(sys.executable).parent
    else:
        scr_root = Path(__file__).resolve().parent
    return scr_root

def processConfig(config_path: Path) -> dict[Any,Any]:
    if not config_path.is_file():
        with open(config_path,"w",encoding="utf-8") as fconfig:
            json.dump(template_config, fconfig, indent=4)
    # Load the config
    with open(config_path,"r",encoding="utf-8") as fconfig:
        config = json.load(fconfig)
    # if config version is wrong, warn and fill in empty values
    if config.get("version",0) != template_config["version"]:
        clearTerminal()
        print("Config file out of date! Config may be unfunctional. It is recommended you nuke SMRT and set-up your overrides from scratch. Proceeding with your existing config is unsupported.\n" \
        "SMRT will try to merge your config with a default config however this may not be reliable. Use at your own risk!")
        for k,v in template_config.items():
            config.setdefault(k,v)
        input("Enter to proceed...")
    return config

def detectGMod(steam_root: Path) -> Path | None:
    gmod_path = steam_root / "steamapps" / "common" / "GarrysMod"
    if not gmod_path.is_dir():
        # i need to parse a vdf here i have no clue how you do that, update: i figured it out
        libraryfolders = steam_root / "steamapps" / "libraryfolders.vdf"
        if not libraryfolders.is_file():
            print("Failure to locate libraryfolders.vdf! Reverting to manual folder select.")
            return None
        with open(libraryfolders, "r",encoding="utf-8") as f:
            libraryfolders_data: dict[Any,Any] = cast(dict[Any,Any],vdf.parse(f))  # pyright: ignore[reportUnknownMemberType]
            for value in libraryfolders_data["libraryfolders"].values():
                if isinstance(value,dict) and "path" in value:
                    assert isinstance(value["path"],str)
                    gmod_path = Path(value["path"]) / "steamapps" / "common" / "GarrysMod"
                    if gmod_path.is_dir():
                        break
    return gmod_path if gmod_path.is_dir() else None
    
def detectSteamRoot(platform: str) -> Path | None:
    if platform == "win32":
        import winreg
        try:    
            steam_install_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            steam_root_s, _ = winreg.QueryValueEx(steam_install_key, "SteamPath")
            steam_root = Path(steam_root_s)
            if (steam_root / "steamapps").is_dir():
                return steam_root
        except Exception:
            pass
        try:
            steam_install_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432NODE\Valve\Steam")
            steam_root_s, _ = winreg.QueryValueEx(steam_install_key, "InstallPath")
            steam_root = Path(steam_root_s)
            if (steam_root / "steamapps").is_dir():
                return steam_root
        except Exception:
            pass
        steam_root = Path(r"C:\Program Files (x86)\Steam")
        return steam_root if (steam_root / "steamapps").is_dir() else None
    elif platform == "macos":
        steam_root = Path.home() / "Library" /"Application Support" /"Steam"
        return steam_root if (steam_root/"steamapps").is_dir() else None
    elif platform == "linux":
        # i dont use linux so i will pull a bunch of random directories from the internet and hope one sticks
        possible_steams = [Path.home() / ".local" / "share" / "Steam",
                            Path.home() /".var"/"app"/"com.valvesoftware.Steam"/".local"/"share"/"Steam",
                            Path.home() /".var"/"app"/"com.valvesoftware.Steam"/"data"/"Steam",
                            Path.home() / "snap/steam/common/.local/share/Steam",
                            Path.home() / ".steam" / "steam",
                            Path.home() / ".steam" / "root"]
        for possible_steam in possible_steams:
            if possible_steam.is_dir() and (possible_steam / "steamapps").is_dir():
                steam_root = possible_steam
                return steam_root
        return None
    else:
        return None

def detectWorkshop(gmod_path: Path) -> Path | None:
    print("SMRT will attempt to auto-configure the Workshop path. If this is incorrect, you will be allowed to choose a custom path.")
    workshop_path = gmod_path.parent.parent / "workshop"
    if not (workshop_path / "content" /"4000").is_dir():
        print("Auto detect failure, reverting to manual pick.")
        return None
    return workshop_path

def extractAddons(workshop_path:Path,gmod_path:Path,config:dict[Any,Any],audio_path:Path,config_path:Path) -> None:
    workshop_gmod_content_path = workshop_path / "content" / "4000"
    addons_to_extract = ["3600114514","2560009684","2560012664","3600116031"] # These are the IDs of BGM Base, 1, 2 and 3 by Mikvoin on the steam workshop
    # get gmad
    gmad_path = findGmad(gmod_path)
    if not gmad_path:
        print("GMad not found! Exiting...")
        input("Enter to exit...")
        sys.exit(1)
        
    # For every addon in the addons to extract
    for addon_id in addons_to_extract:
        addon_folder_path = workshop_gmod_content_path / addon_id
        # Get the gma files for the addon
        gma_files = list(addon_folder_path.glob("*.gma"))
        if not gma_files:
            print(f"No gma files to extract in addon {addon_id}! Might be a problem.")
            input("Enter to continue...")
            continue
        # Extract
        for addon_file_path in gma_files:
            result = extractGMA(gmad_path,addon_file_path,audio_path)
            if not result: # If the extraction fails, st_sound probably makes no sense at that point so I recomment just wiping it. I am being paranoid and asking for the user's consent before rm -r ing a directory
                print("Because extraction failed, it is *heavily* recommeneded you remove the st_sound directory.")
                print(str(audio_path) + " will be removed PERMANENTLY. If this path is valid, input \"YES\". If the path is invalid, type \"NO\" or close out of the program.\n"
                "If you do not authorize the deletion, please delete the directory yourself.\n"
                "Leaving a faulty st_sound directory MIGHT prevent SMRT from properly functioning.")
                confirm = input("Confirm>> ")
                if confirm == "YES":
                    shutil.rmtree(audio_path,ignore_errors=True)
                sys.exit("GMAD Failure")
    config["extraction"] = True # mark the extraction as complete
    saveConfig(config,config_path)

def findGmad(gmod_path: Path) -> Path | None:
    gmad_paths = [gmod_path / "bin" / "gmad",
        gmod_path / "bin" / "linux64" / "gmad",
        gmod_path / "bin" / "gmad_osx",
        gmod_path / "bin" / "gmad_linux",
        gmod_path / "bin" / "gmad.exe",
        gmod_path / "bin" / "win64" / "gmad.exe",
        gmod_path / "bin" / "osx64" / "gmad"]
    for maybe_gmad in gmad_paths:
        if maybe_gmad.is_file():
            gmad_path = maybe_gmad
            return gmad_path
    return None

def addOverride(replacing:Path,override:Path, gmod_path:Path,config:dict[Any,Any],config_path:Path,audio_path:Path):
    relative_path = replacing.resolve().relative_to(audio_path.resolve())
    dest = gmod_path / "garrysmod" / "addons" / "smrt" / relative_path.parent
    dest_file = gmod_path / "garrysmod" / "addons" / "smrt" / relative_path
    dest.mkdir(parents=True,exist_ok=True)
    shutil.copy2(override,dest_file)
    config["active_overrides"][str(relative_path)] = str(override)
    saveConfig(config,config_path)

def listOverrides(config:dict[Any,Any]) -> list[str]:
    overrides_list: list[str] = []
    for i,replacing in enumerate(config["active_overrides"]):
        print("ID: " + str(i) + " | " + str(replacing) + " is being overridden by "+ config["active_overrides"][str(replacing)])
        overrides_list.append(str(replacing))
    return overrides_list
if __name__ == "__main__":
    clearTerminal() # you will see me write this a lot, to clear the terminal
    if sys.platform.startswith("win32"):
        platform = "win32"
    elif sys.platform.startswith("darwin"):
        platform = "macos"
    elif sys.platform.startswith("linux"):
        platform = "linux" 
    else:
        platform = "undefined"
        print("Could not identify operating system! Input \"BYPASS\" to bypass this check. Proceeding from here on out is unsupported.(Much like everything in this program)")
        choice = input("Input>>")
        if choice.strip().upper() != "BYPASS":
            sys.exit("OS not recognized.")
    scr_root = getScriptRoot()
    config_path = scr_root / "config.json"
    config = processConfig(config_path)
    clearTerminal()
    # If GMOD path is unset
    if config["path_to_gmod"] is None or (not (Path(config["path_to_gmod"]) / "garrysmod").exists()): 
        print("SMRT will attempt to auto-configure the GMOD path. If this is incorrect, you will be allowed to choose a custom path.")
        gmod_path = None
        steam_root = detectSteamRoot(platform)
        choice = ""
        if not steam_root:
            print("Failure to locate Steam! Reverting to manual folder select.")
        else:
            gmod_path = detectGMod(steam_root)
            if gmod_path:
                print("GMod located at " + str(gmod_path) + ". if this is incorrect, type MANUAL, otherwise hit Enter.")
                choice = input("Input>>")
        if choice.strip().upper() == "MANUAL" or not gmod_path:
            print("GMod path has not been configured or is invalid!\nPlease input your GMod path.\nThis is the path you get placed into when you click \"Browse local files\" on Steam.")
            gmod_path = folderPicker("Select GMod Path")
            if not gmod_path:
                sys.exit("File picker failed.")
    else:
        steam_root = None
        gmod_path = Path(config["path_to_gmod"])
    config["path_to_gmod"] = str(gmod_path)
    saveConfig(config,config_path)
    audio_path = scr_root / "st_sound"
    # Check if audio extraction has already been done
    workshop_fail = False
    choice = ""
    if not audio_path.is_dir() or not config.get("extraction",False):
        # If the workshop path is not set
        if config["path_to_workshop"] is None or (not Path(config["path_to_workshop"]).exists()):
            clearTerminal()
            workshop_path = detectWorkshop(gmod_path)
            if workshop_path:
                print("Workshop located at " + str(workshop_path) + ". if this is incorrect, type MANUAL, otherwise hit Enter.")
                choice = input("Input>>")
            if choice.strip().upper() == "MANUAL" or not workshop_path:          
                print("Workshop path has not been configured!\nPlease input your workshop path.\nThis is located at STEAMPATH/steamapps/workshop\nC:\\Program Files (x86)\\Steam\\steamapps\\workshop is the default.(On Windows)")
                workshop_path = folderPicker("Select Workshop Path")
                if not workshop_path:
                    sys.exit("File picker failed.")
                if workshop_path.name == "4000" and workshop_path.parent.name == "content": #they chose wrong
                    workshop_path = workshop_path.parent.parent
                elif workshop_path.name == "content":
                    workshop_path = workshop_path.parent
        else:
            workshop_path = Path(config["path_to_workshop"])
        config["path_to_workshop"] = str(workshop_path)
        saveConfig(config,config_path)
        # 4000 is gmod's id, workshop_gmod_content_path is where the addons are stored
        extractAddons(workshop_path,gmod_path,config,audio_path,config_path)
        clearTerminal()
        print("File extraction complete.")

    # The actual music replacement part
    workshop_path = config["path_to_workshop"]
    while True:
        clearTerminal()
        print("Below, GMod root should be set. Steam Root and Workshop Root may not be set depending on if they were needed during launch.\n"
              "Please ensure GMod root is correct before proceeding.")
        print("Steam Root: "+ str(steam_root)+ "\n"+
              "GMod Root: "+ str(gmod_path)+ "\n"+
              "Workshop Root: " + str(workshop_path)) 
        print("Pick an option:\n" \
        "1) Add override\n" \
        "2) Manage existing overrides\n" \
        "3) Nuke SMRT\n" \
        "Q) Exit Program")
        option = input("Choice>> ")
        match option:
            case "Q": # exit
                break
            case "q": #exit
                break
            case "1":
                clearTerminal()
                print("You will now be prompted to pick an mp3 file to be overridden. Please pick the file you wish to be replaced")
                replacing = filePicker("Select the file to be overridden",[("mp3 files","*.mp3"),("All Files","*.*")],audio_path/"sound"/"dro"/"bgm")
                if not replacing:
                    continue # if no file, just go back to menu
                try:
                    replacing_relative = replacing.resolve().relative_to(audio_path.resolve()) #i dont think the .resolve() is needed but no harm in having it. gets the relative path (starting with .../sound)
                except ValueError:
                    print("File must be inside the st_sound directory!")
                    input("Enter to continue...") #if the file isnt in st_sound, it cant be replaced
                    continue
                if str(replacing_relative) in config["active_overrides"]: #if file is already overridden you cant do it
                    clearTerminal()
                    print("That file is already overridden. Remove it first. Press Enter to proceed.")
                    input()
                    continue 
                clearTerminal()
                print("File to be replaced: "+ str(replacing_relative))
                print("You will now be prompted to pick an mp3 file to override. Please pick the file you wish to be replace the previous one")
                override = filePicker("Select the file to override",[("mp3 files","*.mp3"),("All Files","*.*")],audio_path/"sound"/"dro"/"bgm")
                if not override:
                    continue
                # the copy operation now
                addOverride(replacing,override,gmod_path,config,config_path,audio_path)
            case "2":
                clearTerminal()
                overrides_list = listOverrides(config)


                
                choicer = input("ID to remove, q to go back>>")
                if choicer.strip().lower() == "q":
                    continue                
                if not choicer.strip().isnumeric():
                    continue
                if int(choicer) < 0 or int(choicer) >= len(overrides_list):
                    continue
                replacing_to_remove = overrides_list[int(choicer)]
                (gmod_path / "garrysmod" / "addons" / "smrt" / Path(replacing_to_remove)).unlink(missing_ok=True)
                del config["active_overrides"][replacing_to_remove]
                saveConfig(config,config_path)
            case "3":
                clearTerminal()
                smrt_addon_folder = gmod_path / "garrysmod" / "addons" / "smrt"
                print("NOTE: THIS WILL WIPE \"" + str(smrt_addon_folder) + "\" and \"" + str(audio_path) +"\".\n"
                "If any of those directories should not be wiped, do NOT authorize the deletion! ")
                print("Are you sure you want to proceed and nuke SMRT? If so, type \"YES\".")
                confirm = input("Input>>")
                if confirm == "YES":
                    if smrt_addon_folder.is_dir():
                        shutil.rmtree(smrt_addon_folder)
                    if audio_path.is_dir():
                        shutil.rmtree(audio_path)
                    
                    saveConfig(template_config,config_path)
                    break
            case _:
                continue
    

