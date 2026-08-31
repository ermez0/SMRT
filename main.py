"""
SMRT -- The Shinri Music Replacement Tool
I know this code is terrible, I don't expect anyone but me to work on it -ermez
"""
# Imports
import static_ffmpeg
static_ffmpeg.add_paths(weak=True)
import vdf # pyright: ignore[reportMissingTypeStubs]
import sys
import shutil
import json
import subprocess
from pathlib import Path
from typing import Any,cast
import config
import utils
import audiolib
import gmod
import state

def option_import_soundpack(config_dict: dict, config_path: Path, scr_root: Path, audio_path: Path):       
    warnFlag = False
    utils.clear_terminal()
    print("The current config will be ERASED and replaced with a soundpack. Are you sure you want to proceed?(y/N)")
    proceed = input("Choice: ")
    if proceed.lower().strip() != "y":
        return
    soundpack_path = utils.file_picker("Select your soundpack",[("SMRT Soundpack file","*.smrt"),("All Files","*.*")],(scr_root / "soundpacks"))
    if soundpack_path is None:
        print("No soundpack selected! Enter to continue...")
        input()
        return
    with open(soundpack_path,"r",encoding="utf-8") as soundpack_file:
        soundpack = json.load(soundpack_file)
        new_overrides = {}
        for replacing,properties in soundpack.items():
            if properties["relative"]:
                override_path = audio_path / properties["path"]
            else:
                warnFlag = True
                override_path = properties["path"]
            new_overrides[Path(replacing).as_posix()] = Path(override_path).as_posix()
        list_overrides_dict(new_overrides)
        if warnFlag:
            print("This pack has non-relative paths so it may not work if you got it from someone else or moved your SMRT directory. Proceed with caution!")
        print("Are you sure you want to override your config with this soundpack?(y/N)")
        proceed = input("Choice: ")
        if proceed.lower().strip() != "y":
            return
        config_dict["active_overrides"] = new_overrides
        config.save_config(config_dict,config_path)

def option_export_soundpack(config_dict: dict, audio_path: Path, scr_root: Path):
    utils.clear_terminal()
    warnFlag = False
    soundpack_dict: dict = {}
    print("The currently loaded config will be exported as a soundpack file.\n" \
    "Would you like to list the config? (Y/n)")
    choice = input("Choice: ")
    if choice.lower().strip() != "n":
        list_overrides_dict(config_dict["active_overrides"])
    for replacing_str,override_str in config_dict["active_overrides"].items():
        replacing = Path(replacing_str)
        override = Path(override_str).resolve()
        is_relative = override.is_relative_to(audio_path.resolve())
        soundpack_dict[replacing.as_posix()] = {}
        soundpack_dict[replacing.as_posix()]["relative"] = is_relative
        if is_relative:
            soundpack_dict[replacing.as_posix()]["path"] = (override.relative_to(audio_path)).as_posix()
        else:
            warnFlag = True
            soundpack_dict[replacing.as_posix()]["path"] = override.as_posix()
    if warnFlag:
        print("This soundpack has overrides outside of st_sound and as such will *not* be compatible on another system.")
    soundpacks_dir = scr_root / "soundpacks"
    soundpacks_dir.mkdir(exist_ok=True)
    count = 0
    already_exists = set()
    # The set idea came from AI, i would have never thought of it.
    for file in sorted(soundpacks_dir.iterdir()):
        if file.is_file() and file.name.startswith("soundpack"):
            if (file.stem.removeprefix("soundpack")).isdigit():
                already_exists.add(int(file.stem.removeprefix("soundpack")))
    while count in already_exists:
        count += 1
    path_to_save = soundpacks_dir / ("soundpack" + str(count) + ".smrt")
    with open(path_to_save,"w",encoding="utf-8") as f:
        json.dump(soundpack_dict,f,indent=4)
    print("Exported to: "+str(path_to_save))
    input("Enter to continue...")

def option_add_override(gmod_path: Path,audio_path: Path, config_dict: dict, scr_root: Path, config_path: Path):
    utils.clear_terminal()
    print("You will now be prompted to pick an mp3 file to be overridden. Please pick the file you wish to be replaced")
    replacing = utils.file_picker("Select the file to be overridden",[("mp3 files","*.mp3"),("All Files","*.*")],audio_path/"sound"/"dro"/"bgm")
    if not replacing:
        return # if no file, just go back to menu
    try:
        replacing_relative = replacing.resolve().relative_to(audio_path.resolve()) #i dont think the .resolve() is needed but no harm in having it. gets the relative path (starting with .../sound)
    except ValueError:
        print("File must be inside the st_sound directory!")
        input("Enter to continue...") #if the file isnt in st_sound, it cant be replaced
        return
    if str(replacing_relative.as_posix()) in config_dict["active_overrides"]: #if file is already overridden you cant do it
        utils.clear_terminal()
        print("That file is already overridden. Remove it first. Press Enter to proceed.")
        input()
        return 
    utils.clear_terminal()
    print("File to be replaced: "+ str(replacing_relative))
    print("You will now be prompted to pick an mp3 file to override. Please pick the file you wish to be replace the previous one")
    override = utils.file_picker("Select the file to override",[("mp3 files","*.mp3"),("All Files","*.*")],audio_path/"sound"/"dro"/"bgm")
    if not override:
        return
    # the copy operation now
    if audiolib.get_audio_len_secs(replacing) > audiolib.get_audio_len_secs(override):
        print("SMRT detected that the new audio is shorter than the original one. Would you like an automatic looped extension instead? (y/N)")
        extend = input("Choice: ")
        if extend.lower().strip() == "y":
            override = audiolib.extend_audio(replacing,override,(scr_root) / "audio_cache")
    add_override(replacing,override,gmod_path,config_dict,config_path,audio_path)

def option_manage_overrides(gmod_path: Path,config_dict: dict, config_path: Path):
    utils.clear_terminal()
    overrides_list = list_overrides_dict(config_dict["active_overrides"])
    choicer = input("ID to remove, q to go back: ")
    if choicer.strip().lower() == "q":
        return              
    if not choicer.strip().isnumeric():
        return
    if int(choicer) < 0 or int(choicer) >= len(overrides_list):
        return
    replacing_to_remove = overrides_list[int(choicer)]
    (gmod_path / "garrysmod" / "addons" / "smrt" / Path(replacing_to_remove)).unlink(missing_ok=True)
    del config_dict["active_overrides"][replacing_to_remove]
    config.save_config(config_dict,config_path)

def option_nuke_smrt(gmod_path:Path, audio_path: Path, config_path: Path):
    utils.clear_terminal()
    smrt_addon_folder = gmod_path / "garrysmod" / "addons" / "smrt"
    print("NOTE: THIS WILL WIPE \"" + str(smrt_addon_folder) + "\" and \"" + str(audio_path) +"\".\n"
    "If any of those directories should not be wiped, do NOT proceed with the deletion! ")
    print("Are you sure you want to proceed and nuke SMRT? If so, type \"YES\".")
    confirm = input("Choice: ")
    if confirm == "YES":
        if smrt_addon_folder.is_dir():
            shutil.rmtree(smrt_addon_folder)
        if audio_path.is_dir():
            shutil.rmtree(audio_path)
        config.save_config(config.template_config,config_path)
        sys.exit(0)

def add_override(replacing:Path,override:Path, gmod_path:Path,config_dict:dict[Any,Any],config_path:Path,audio_path:Path):
    relative_path = replacing.resolve().relative_to(audio_path.resolve())
    dest = gmod_path / "garrysmod" / "addons" / "smrt" / relative_path.parent
    dest_file = gmod_path / "garrysmod" / "addons" / "smrt" / relative_path
    dest.mkdir(parents=True,exist_ok=True)
    shutil.copy2(override,dest_file)
    config_dict["active_overrides"][relative_path.as_posix()] = override.as_posix()
    config.save_config(config_dict,config_path)

def list_overrides_dict(active_overrides:dict[Any,Any], noPrint:bool = False) -> list[str]:
    overrides_list: list[str] = []
    for i,replacing in enumerate(active_overrides):
        if not noPrint:
            print("ID: " + str(i) + " | " + str(replacing) + " is being overridden by "+ active_overrides[str(replacing)])
        overrides_list.append(str(replacing))
    return overrides_list



if __name__ == "__main__":
    utils.clear_terminal() # you will see me write this a lot, to clear the terminal
    state.platform = utils.get_platform()
    scr_root = utils.get_scr_root()
    config_path = scr_root / "config.json"
    config_dict = config.process_config(config_path)
    utils.clear_terminal()
    # If GMOD path is unset
    if config_dict["path_to_gmod"] is None or (not (Path(config_dict["path_to_gmod"]) / "garrysmod").exists()): 
        gmod_path, steam_root = gmod.setup_gmod_path()
    else:
        steam_root = None
        gmod_path = Path(config_dict["path_to_gmod"])
    config_dict["path_to_gmod"] = str(gmod_path)
    config.save_config(config_dict,config_path)
    audio_path = scr_root / "st_sound"
    # Check if audio extraction has already been done
    workshop_fail = False
    choice = ""
    if not audio_path.is_dir() or not config_dict.get("extraction",False):
        # If the workshop path is not set
        if config_dict["path_to_workshop"] is None or (not Path(config_dict["path_to_workshop"]).exists()):
            workshop_path = gmod.setup_workshop_path(gmod_path)
        else:
            workshop_path = Path(config_dict["path_to_workshop"])
        config_dict["path_to_workshop"] = str(workshop_path)
        config.save_config(config_dict,config_path)
        # 4000 is gmod's id, workshop_gmod_content_path is where the addons are stored
        gmod.extract_addons(workshop_path,gmod_path,config_dict,audio_path,config_path)
        utils.clear_terminal()
        print("File extraction complete.")
    # The actual music replacement part
    workshop_path = config_dict["path_to_workshop"]
    while True:
        utils.clear_terminal()
        print("Below, GMod root should be set. Steam Root and Workshop Root may not be set depending on if they were needed during launch.\n"
              "Please ensure GMod root is correct before proceeding.")
        print("Steam Root: "+ str(steam_root)+ "\n"+
              "GMod Root: "+ str(gmod_path)+ "\n"+
              "Workshop Root: " + str(workshop_path)) 
        print("Pick an option:\n" \
        "1) Add override\n" \
        "2) Manage existing overrides\n" \
        "3) Nuke SMRT\n" \
        "4) Export soundpack\n" \
        "5) Import soundpack\n" \
        "Q) Exit Program")
        option = input("Choice: ").lower().strip()
        match option:
            case "q": break
            case "1": option_add_override(gmod_path,audio_path,config_dict,scr_root,config_path)
            case "2": option_manage_overrides(gmod_path,config_dict,config_path)
            case "3": option_nuke_smrt(gmod_path,audio_path,config_path)
            case "4": option_export_soundpack(config_dict,audio_path,scr_root)
            case "5": option_import_soundpack(config_dict,config_path,scr_root,audio_path)
            case _: continue
    

