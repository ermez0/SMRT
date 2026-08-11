"""
SMRT -- The Shinri Music Replacement Tool
I know this code is terrible, I don't expect anyone but me to work on it -ermez
"""
# Imports
steam_root = None
import vdf
import sys
import shutil
import json
import subprocess
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
# Default config
template_config = {
    "version":0.3,
    "path_to_gmod": None,
    "path_to_workshop":None,
    "extraction":False,
    "active_overrides" : {} # format will be "active_overrides" : {"something(replacing)":"another thing(the replacement)"}
}
# Removes the root window
root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)

# Saves the JSON provided as config to config_path
def saveConfig(config:dict,config_path:Path) -> None:
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
    if not out_path.exists() or not any(out_path.iterdir()):
        print("It appears output directory is empty.")
        return False
    #if none of the above are true, the extract succeeded
    return True

def clearTerminal() -> None:
    print("\033[H\033[2JSMRT -- The Shinri Music Replacement Tool")

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
    # Figure out the root of the script based on if its running as a script/as an executable
    if getattr(sys, "frozen", False):
        scr_root = Path(sys.executable).parent
    else:
        scr_root = Path(__file__).resolve().parent
    config_path = scr_root / "config.json"
    # Make the config if it doesnt exist
    if not config_path.is_file():
        with open(config_path,"w",encoding="utf-8") as fconfig:
            json.dump(template_config, fconfig, indent=4)
    # Load the config
    with open(config_path,"r",encoding="utf-8") as fconfig:
        config = json.load(fconfig)
    # if config version is wrong, warn and fill in empty values
    if config.get("version",0) != template_config["version"]:
        clearTerminal()
        print("Config file out of date! Config may be unfunctional. It is recommended you nuke your config and set-up your overrides from scratch. Proceeding with your existing config is unsupported.\n" \
        "SMRT will try to merge your config with a default config however this may not be reliable. Use at your own risk!")
        for k,v in template_config.items():
            config.setdefault(k,v)
        input("Enter to proceed...")
        clearTerminal()
    # If GMOD path is unset
    if config["path_to_gmod"] is None or (not Path(config["path_to_gmod"]).exists()) or (not (Path(config["path_to_gmod"]) / "garrysmod").exists()): 
        gmod_detect = False
        print("SMRT will attempt to auto-configure the GMOD path. If this is incorrect, you will be allowed to choose a custom path.")
        exit_flag = False
        steam_root = None
        gmod_path = None
        if platform == "win32":
            import winreg
            try:
                steam_install_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432NODE\Valve\Steam")
                steam_root_s, _ = winreg.QueryValueEx(steam_install_key, "InstallPath")
                steam_root = Path(steam_root_s)
            except:
                steam_root = Path(r"C:\Program Files (x86)\Steam")
        elif platform == "macos":
            steam_root = Path.home() / "Library" /"Application Support" /"Steam"
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
                    break
            
        if not steam_root or not steam_root.is_dir():
            print("Failure to locate Steam! Reverting to manual folder select.")
            exit_flag = True
        if not exit_flag:
            assert steam_root is not None
            gmod_path = steam_root / "steamapps" / "common" / "GarrysMod"
            if not gmod_path.is_dir():
                # i need to parse a vdf here i have no clue how you do that, update: i figured it out
                libraryfolders = steam_root / "steamapps" / "libraryfolders.vdf"
                if not libraryfolders.is_file():
                    print("Failure to locate libraryfolders.vdf! Reverting to manual folder select.")
                    exit_flag = True
                if not exit_flag:
                    with open(libraryfolders, "r",encoding="utf-8") as f:
                        libraryfolders_data = vdf.parse(f)
                        for key, value in libraryfolders_data["libraryfolders"].items():
                            if isinstance(value,dict) and "path" in value:
                                gmod_path = Path(value["path"]) / "steamapps" / "common" / "GarrysMod"
                                if gmod_path.is_dir():
                                    gmod_detect = True
                                    library_path = Path(value["path"])
                                    break
            else:
                gmod_detect = True
                library_path = steam_root
            if gmod_detect:
                print("GMod located at " + str(gmod_path) + ". if this is incorrect, type MANUAL, otherwise hit Enter.")
                choice = input("Input>>")
                if choice.strip().upper() == "MANUAL":
                    gmod_detect = False
        if not gmod_detect:
            print("GMod path has not been configured or is invalid!\nPlease input your GMod path.\nThis is the path you get placed into when you click \"Browse local files\" on Steam.")
            root.update()
            sgmod_path = filedialog.askdirectory(title="Select GMod Path")
            if not sgmod_path:
                sys.exit("File picker failed.")
            gmod_path = Path(sgmod_path)
    else:
        steam_root = None
        gmod_path = Path(config["path_to_gmod"])
    config["path_to_gmod"] = str(gmod_path)
    saveConfig(config,config_path)
    assert gmod_path is not None
    audio_path = scr_root / "st_sound"
    # Check if audio extraction has already been done
    workshop_path = None
    workshop_fail = False
    if not audio_path.is_dir() or not config.get("extraction",False):
        # If the workshop path is not set
        if config["path_to_workshop"] is None or (not Path(config["path_to_workshop"]).exists()):
            clearTerminal()
            print("SMRT will attempt to auto-configure the Workshop path. If this is incorrect, you will be allowed to choose a custom path.")
            workshop_path = gmod_path.parent.parent / "workshop"
            if not (workshop_path / "content" /"4000").is_dir():
                print("Auto detect failure, reverting to manual pick.")
                workshop_fail = True
            if not workshop_fail:
                print("Workshop located at " + str(workshop_path) + ". if this is incorrect, type MANUAL, otherwise hit Enter.")
                choice = input("Input>>")
                if choice.strip().upper() == "MANUAL":
                    workshop_fail = True
            if workshop_fail:
                print("Workshop path has not been configured!\nPlease input your workshop path.\nThis is located at STEAMPATH/steamapps/workshop\nC:\\Program Files (x86)\\Steam\\steamapps\\workshop is the default.(On Windows)")
                root.update()
                sworkshop_path = filedialog.askdirectory(title="Select Workshop Path")
                if not sworkshop_path:
                    sys.exit("File picker failed.")
                workshop_path = Path(sworkshop_path)
                if workshop_path.name == "4000" and workshop_path.parent.name == "content": #they chose wrong
                    workshop_path = workshop_path.parent.parent
                elif workshop_path.name == "content":
                    workshop_path = workshop_path.parent
        else:
            workshop_path = Path(config["path_to_workshop"])
        config["path_to_workshop"] = str(workshop_path)
        saveConfig(config,config_path)
        # 4000 is gmod's id, workshop_gmod_content_path is where the addons are stored
        workshop_gmod_content_path = workshop_path / "content" / "4000"
        addons_to_extract = ["3600114514","2560009684","2560012664","3600116031"] # These are the IDs of BGM Base, 1, 2 and 3 by Mikvoin on the steam workshop
        # get gmad
        gmad_path = None
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
                break
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
        clearTerminal()
        print("File extraction complete.")



    # The actual music replacement part
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
                root.update()
                sreplacing = filedialog.askopenfilename(
                    title="Select the file to be overridden",
                    filetypes=[("mp3 files","*.mp3"),("All Files","*.*")],
                    initialdir=audio_path/"sound"/"dro"/"bgm"
                ) # Bring up a file select dialogue for the first mp3
                if not sreplacing:
                    continue # if no file, just go back to menu
                replacing = Path(sreplacing)
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
                print("File to be replaced: "+ str(replacing))
                print("You will now be prompted to pick an mp3 file to override. Please pick the file you wish to be replace the previous one")
                root.update()
                soverride = filedialog.askopenfilename( #same as last time
                    title="Select the file to override",
                    filetypes=[("mp3 files","*.mp3"),("All Files","*.*")],
                    initialdir=audio_path/"sound"/"dro"/"bgm"
                )
                if not soverride:
                    continue
                override = Path(soverride)
                # the copy operation now
                # now, relative_path is the relative path to the original file, showing it into the smrt folder makes it into the destination.
                # it ensures that the destination exists before copying the new file(override) to the correct place(the aforementioned dest_file)
                # then saves into config the override
                # the config is saved as relative + absoulute path because file getting replaced has to be in st_sound but not the file replacing 
                relative_path = replacing.resolve().relative_to(audio_path.resolve())
                dest = gmod_path / "garrysmod" / "addons" / "smrt" / relative_path.parent
                dest_file = gmod_path / "garrysmod" / "addons" / "smrt" / relative_path
                dest.mkdir(parents=True,exist_ok=True)
                shutil.copy2(override,dest_file)
                config["active_overrides"][str(replacing_relative)] = str(override)
                saveConfig(config,config_path)
            case "2":
                clearTerminal()
                overrides_list = []
                for i,replacing in enumerate(config["active_overrides"]):
                    print("ID: " + str(i) + " | " + str(replacing) + " is being overridden by "+ config["active_overrides"][str(replacing)])
                    overrides_list.append(str(replacing))
                choicer = input("ID to remove, q to go back>>")
                if choicer.strip().lower() == "q":
                    continue                
                if not choicer.strip().isnumeric():
                    continue
                if int(choicer) < 0 or int(choicer) >= len(overrides_list):
                    continue
                replacing_to_remove = overrides_list[int(choicer)]
                override_to_remove = config["active_overrides"][replacing_to_remove]
                (gmod_path / "garrysmod" / "addons" / "smrt" / Path(replacing_to_remove)).unlink(missing_ok=True)
                del config["active_overrides"][replacing_to_remove]
                saveConfig(config,config_path)
            case "3":
                clearTerminal()
                smrt_addon_folder = gmod_path / "garrysmod" / "addons" / "smrt"
                print("NOTE: THIS WILL WIPE + \"" + str(smrt_addon_folder) + "\" and \"" + str(audio_path) +"\".\n"
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
    

