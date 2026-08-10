"""
SMRT -- The Shinri Music Replacement Tool
I know this code is terrible, I don't expect anyone but me to work on it -ermez
"""
import sys
import shutil
import json
import subprocess
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
template_config = {
    "version":0.3,
    "path_to_gmod": None,
    "path_to_workshop":None,
    "extraction":False,
    "active_overrides" : {} # format will be "active_overrides" : {"something(replacing)":"another thing(the replacement)"}
}
# removes the root window since i dont need it, i just need tkinter for the file select 
root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)
def saveConfig(config:dict,config_path:Path) -> None:
    with open(config_path,"w") as fconfig:
        json.dump(config,fconfig,indent=4)

def extractGMA(gmad_path:Path,gma_path:Path,out_path:Path) -> bool:
    if not gmad_path.is_file() or not gma_path.is_file():
        return False
    command = [
        str(gmad_path), 
        "extract", 
        "-file", str(gma_path), 
        "-out", str(out_path)
    ]
    result = subprocess.run(command,capture_output=True,text=True)
    if result.returncode != 0:
        print("GMAD extraction failed!")
        print(result.stderr)
        return False
    if "Problem" in result.stdout or "Problem" in result.stderr:
        print("GMAD experienced a problem.")
        print(result.stdout)
        print(result.stderr)
        return False
    if not out_path.exists() or not any(out_path.iterdir()):
        print("It appears output directory is empty.")
        return False
    return True


if __name__ == "__main__":
    print("\033[H\033[2JSMRT -- The Shinri Music Replacement Tool")
    # Figure out the root of the script based on if its running as a script/as an executable
    if getattr(sys, "frozen", False):
        scr_root = Path(sys.executable).parent
    else:
        scr_root = Path(__file__).resolve().parent
    config_path = scr_root / "config.json"
    # Make the config if it doesnt exist
    if not config_path.is_file():
        with open(config_path,"w") as fconfig:
            json.dump(template_config, fconfig, indent=4)
    # Load the config
    with open(config_path,"r") as fconfig:
        config = json.load(fconfig)
    if config.get("version",0) != template_config["version"]:
        print("\033[H\033[2JSMRT -- The Shinri Music Replacement Tool")
        print("Config file out of date! Config may be unfunctional. It is recommended you nuke your config and set-up your overrides from scratch. Proceeding with your existing config is unsupported.\n" \
        "SMRT will try to merge your config with a default config however this may not be reliable. Use at your own risk!")
        for k,v in template_config.items():
            config.setdefault(k,v)
        input("Enter to proceed...")
        print("\033[H\033[2JSMRT -- The Shinri Music Replacement Tool")
    # If GMOD path is unset
    if config["path_to_gmod"] is None or (not Path(config["path_to_gmod"]).exists()):
        print("GMod path has not been configured or is invalid!\nPlease input your GMod path.\nThis is the path you get placed into when you click \"Browse local files\" on Steam.")
        root.update()
        sgmod_path = filedialog.askdirectory(title="Select GMod Path")
        if not sgmod_path:
            sys.exit("File picker failed.")
        gmod_path = Path(sgmod_path)
    else:
        gmod_path = Path(config["path_to_gmod"])
    config["path_to_gmod"] = str(gmod_path)
    saveConfig(config,config_path)
    audio_path = scr_root / "st_sound"
    # Check if audio extraction has already been done
    if not audio_path.is_dir() or not config.get("extraction",False):
        # Do the workshop path thing
        if config["path_to_workshop"] is None or (not Path(config["path_to_workshop"]).exists()):
            print("\033[H\033[2JSMRT -- The Shinri Music Replacement Tool")
            print("Workshop path has not been configured!\nPlease input your workshop path.\nThis is located at STEAMPATH/steamapps/workshop\nC:\\Program Files (x86)\\Steam\\steamapps\\workshop is the default.(On Windows)")
            root.update()
            sworkshop_path = filedialog.askdirectory(title="Select Workshop Path")
            if not sworkshop_path:
                sys.exit("File picker failed.")
            workshop_path = Path(sworkshop_path)
        else:
            workshop_path = Path(config["path_to_workshop"])
        config["path_to_workshop"] = str(workshop_path)
        saveConfig(config,config_path)
        workshop_gmod_content_path = workshop_path / "content" / "4000"
        addons_to_extract = ["3600114514","2560009684","2560012664","3600116031"]
        if sys.platform == "win32":
            gmad_path = gmod_path / "bin" / "gmad.exe"
        else:
            gmad_path = gmod_path / "bin" / "gmad"
        for addon_id in addons_to_extract:
            addon_folder_path = workshop_gmod_content_path / addon_id
            gma_files = list(addon_folder_path.glob("*.gma"))
            if not gma_files:
                print(f"No gma files to extract in addon {addon_id}! Might be a problem.")
                input("Enter to continue...")
                continue
            for addon_file_path in gma_files:
               result = extractGMA(gmad_path,addon_file_path,audio_path)
               if not result:
                   print("Because extraction failed, it is *heavily* recommeneded you remove the st_sound directory.")
                   print(str(audio_path) + " will be removed PERMANENTLY. If this path is valid, input \"YES\". If the path is invalid, type \"NO\" or close out of the program.\n"
                   "If you do not authorize the deletion, please delete the directory yourself.\n"
                   "Leaving a faulty st_sound directory WILL prevent SMRT from properly functioning.")
                   confirm = input("Confirm>> ")
                   if confirm == "YES":
                       shutil.rmtree(audio_path,ignore_errors=True)
                   sys.exit("GMAD Failure")
        config["extraction"] = True
        saveConfig(config,config_path)
        
        print("\033[H\033[2JSMRT -- The Shinri Music Replacement Tool")
        print("File extraction complete.")

    # The actual music replacement part
    while True:
        print("\033[H\033[2JSMRT -- The Shinri Music Replacement Tool")
        print("Pick an option:\n" \
        "1) Add override\n" \
        "2) Manage existing overrides\n" \
        "3) Nuke config\n" \
        "Q) Exit Program")
        option = input("Choice>> ")
        match option:
            case "Q":
                break
            case "q":
                break
            case "1":
                print("\033[H\033[2JSMRT -- The Shinri Music Replacement Tool")
                print("You will now be prompted to pick an mp3 file to be overridden. Please pick the file you wish to be replaced")
                root.update()
                sreplacing = filedialog.askopenfilename(
                    title="Select the file to be overridden",
                    filetypes=[("mp3 files","*.mp3"),("All Files","*.*")],
                    initialdir=audio_path/"sound"/"dro"/"bgm"
                )
                if not sreplacing:
                    continue
                replacing = Path(sreplacing)
                try:
                    replacing_relative = replacing.resolve().relative_to(audio_path.resolve())
                except ValueError:
                    print("File must be inside the st_sound directory!")
                    input("Enter to continue...")
                    continue
                if str(replacing_relative) in config["active_overrides"]:
                    print("\033[H\033[2JSMRT -- The Shinri Music Replacement Tool")
                    print("That file is already overridden. Remove it first. Press Enter to proceed.")
                    input()
                    continue
                print("\033[H\033[2JSMRT -- The Shinri Music Replacement Tool")
                print("File to be replaced: "+ str(replacing))
                print("You will now be prompted to pick an mp3 file to override. Please pick the file you wish to be replace the previous one")
                root.update()
                soverride = filedialog.askopenfilename(
                    title="Select the file to override",
                    filetypes=[("mp3 files","*.mp3"),("All Files","*.*")],
                    initialdir=audio_path/"sound"/"dro"/"bgm"
                )
                if not soverride:
                    continue
                override = Path(soverride)
                # the copy operation now
                # the path beginning with /sound...
                relative_path = replacing.resolve().relative_to(audio_path.resolve())
                dest = gmod_path / "garrysmod" / "addons" / "smrt" / relative_path.parent
                dest_file = gmod_path / "garrysmod" / "addons" / "smrt" / relative_path
                dest.mkdir(parents=True,exist_ok=True)
                shutil.copy2(override,dest_file)
                config["active_overrides"][str(replacing_relative)] = str(override)
                saveConfig(config,config_path)
            case "2":
                print("\033[H\033[2JSMRT -- The Shinri Music Replacement Tool")
                overrides_list = []
                for i,replacing in enumerate(config["active_overrides"]):
                    print("ID: " + str(i) + " | " + str(replacing) + " is being overridden by "+ config["active_overrides"][str(replacing)])
                    overrides_list.append(str(replacing))
                choicer = input("ID to remove, q to go back>>")
                if choicer.lower() == "q":
                    continue                
                if not choicer.isnumeric():
                    continue
                if int(choicer) < 0 or int(choicer) >= len(overrides_list):
                    continue
                replacing_to_remove = overrides_list[int(choicer)]
                override_to_remove = config["active_overrides"][replacing_to_remove]
                (gmod_path / "garrysmod" / "addons" / "smrt" / Path(replacing_to_remove)).unlink(missing_ok=True)
                del config["active_overrides"][replacing_to_remove]
                saveConfig(config,config_path)
            case "3":
                print("\033[H\033[2JSMRT -- The Shinri Music Replacement Tool")
                print("Are you sure? This will remove all existing overrides and wipe your config. If so, type \"YES\".")
                confirm = input("Input>>")
                if confirm == "YES":
                    smrt_addon_folder = gmod_path / "garrysmod" / "addons" / "smrt"
                    if smrt_addon_folder.is_dir():
                        shutil.rmtree(smrt_addon_folder)
                    saveConfig(template_config,config_path)
                    break
            case _:
                continue
    

