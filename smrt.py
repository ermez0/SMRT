"""
What needs to happen
1: Check for config file
2: Locate GMOD
3: Use GMAD to extract all audio .gma files
4: the actual replacement stuff
"""
import sys
import shutil
import json
import os
import subprocess
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
template_config = {
    "path_to_gmod": None,
    "path_to_workshop":None,
    "active_overrides" : {} # format will be "active_overrides" : {"something(replacing)":"another thing(the replacement)"}
}
# removes the root window since i dont need it, i just need tkinter for the file select 
root = tk.Tk()
root.withdraw()
def saveConfig(config:dict,config_path:Path) -> None:
    with open(config_path,"w") as fconfig:
        json.dump(config,fconfig,indent=4)

def extractGMA(gmad_path:Path,gma_path:Path,out_path:Path) -> None:
    command = [
        str(gmad_path), 
        "extract", 
        "-file", str(gma_path), 
        "-out", str(out_path)
    ]
    subprocess.run(command)


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
    # If GMOD path is unset
    if config["path_to_gmod"] is None:
        print("GMod path has not been configured!\nPlease input your GMod path.\nThis is the path you get placed into when you click \"Browse local files\" on Steam.")
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
    if not audio_path.is_dir():
        # Do the workshop path thing
        if config["path_to_workshop"] is None:
            print("\033[H\033[2JSMRT -- The Shinri Music Replacement Tool")
            print("Workshop path has not been configured!\nPlease input your workshop path.\nThis is located at STEAMPATH/steamapps/workshop\nC:\\Program Files (x86)\\Steam\\steamapps\\workshop is the default.(On Windows)")
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
        gmad_path = gmod_path / "bin" / "gmad.exe"
        for addon_id in addons_to_extract:
            addon_file_path = workshop_gmod_content_path / addon_id / "gmpublisher.gma"
            extractGMA(gmad_path,addon_file_path,audio_path)
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
                sreplacing = filedialog.askopenfilename(
                    title="Select the file to be overridden",
                    filetypes=[("mp3 files","*.mp3"),("All Files","*.*")],
                    initialdir=audio_path/"sound"/"dro"/"bgm"
                )
                if not sreplacing:
                    continue
                replacing = Path(sreplacing)
                replacing_relative = replacing.relative_to(audio_path)
                if str(replacing_relative) in config["active_overrides"]:
                    print("\033[H\033[2JSMRT -- The Shinri Music Replacement Tool")
                    print("That file is already overridden. Remove it first. Press Enter to proceed.")
                    input()
                    continue
                print("\033[H\033[2JSMRT -- The Shinri Music Replacement Tool")
                print("File to be replaced: "+ str(replacing))
                print("You will now be prompted to pick an mp3 file to override. Please pick the file you wish to be replace the previous one")
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
                relative_path = replacing.relative_to(audio_path)
                dest = gmod_path / "garrysmod" / "addons" / "smrt" / relative_path.parent
                dest_file = gmod_path / "garrysmod" / "addons" / "smrt" / relative_path
                dest.mkdir(parents=True,exist_ok=True)
                shutil.copy2(override,dest_file)
                override_relative = override.relative_to(audio_path)
                config["active_overrides"][str(replacing_relative)] = str(override_relative)
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
    

