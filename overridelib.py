from pathlib import Path
import utils
import config
import audiolib
from typing import Any
import shutil
import state

def add_override(replacing:Path,override:Path, gmod_path:Path):
    assert state.audio_path is not None
    assert state.platform is not None and state.scr_root is not None and state.config_path is not None
    assert state.config_dict is not None
    if not override.is_file() or not replacing.resolve().is_file():
        print(f"Invalid override attempt on replacing {replacing} with {override}. Skipping...")
        input("Enter to proceed...")
        return
    relative_path = replacing.resolve().relative_to(state.audio_path.resolve())
    dest = gmod_path / "garrysmod" / "addons" / "smrt" / relative_path.parent
    dest_file = gmod_path / "garrysmod" / "addons" / "smrt" / relative_path
    dest.mkdir(parents=True,exist_ok=True)
    shutil.copy2(override,dest_file)
    state.config_dict["active_overrides"][relative_path.as_posix()] = override.as_posix()
    config.save_config(state.config_dict)


def option_add_override(gmod_path: Path):
    assert state.audio_path is not None
    assert state.platform is not None and state.scr_root is not None and state.config_path is not None
    assert state.config_dict is not None
    utils.clear_terminal()
    print("You will now be prompted to pick an mp3 file to be overridden. Please pick the file you wish to be replaced")
    replacing = utils.file_picker("Select the file to be overridden",[("mp3 files","*.mp3"),("All Files","*.*")],state.audio_path/"sound"/"dro"/"bgm")
    if not replacing:
        return # if no file, just go back to menu
    try:
        replacing_relative = replacing.resolve().relative_to(state.audio_path.resolve()) #i dont think the .resolve() is needed but no harm in having it. gets the relative path (starting with .../sound)
    except ValueError:
        print("File must be inside the st_sound directory!")
        input("Enter to continue...") #if the file isnt in st_sound, it cant be replaced
        return
    if str(replacing_relative.as_posix()) in state.config_dict["active_overrides"]: #if file is already overridden you cant do it
        utils.clear_terminal()
        print("That file is already overridden. Remove it first. Press Enter to proceed.")
        input()
        return 
    utils.clear_terminal()
    print("File to be replaced: "+ str(replacing_relative))
    print("You will now be prompted to pick an mp3 file to override. Please pick the file you wish to be replace the previous one")
    override = utils.file_picker("Select the file to override",[("mp3 files","*.mp3"),("All Files","*.*")],state.audio_path/"sound"/"dro"/"bgm")
    if not override:
        return
    # the copy operation now
    if audiolib.get_audio_len_secs(replacing) > audiolib.get_audio_len_secs(override):
        print("SMRT detected that the new audio is shorter than the original one. Would you like an automatic looped extension instead? (y/N)")
        extend = input("Choice: ")
        if extend.lower().strip() == "y":
            override = audiolib.extend_audio(replacing,override,(state.scr_root) / "audio_cache")
    add_override(replacing,override,gmod_path)

def option_manage_overrides(gmod_path: Path):
    assert state.audio_path is not None
    assert state.platform is not None and state.scr_root is not None and state.config_path is not None
    assert state.config_dict is not None
    utils.clear_terminal()
    overrides_list = utils.list_overrides_dict(state.config_dict["active_overrides"])
    choicer = input("ID to remove, q to go back: ")
    if choicer.strip().lower() == "q":
        return              
    if not choicer.strip().isnumeric():
        return
    if int(choicer) < 0 or int(choicer) >= len(overrides_list):
        return
    replacing_to_remove = overrides_list[int(choicer)]
    (gmod_path / "garrysmod" / "addons" / "smrt" / Path(replacing_to_remove)).unlink(missing_ok=True)
    del state.config_dict["active_overrides"][replacing_to_remove]
    config.save_config(state.config_dict)

def load_overrides_from_config(gmod_path: Path):
    assert state.audio_path is not None
    assert state.platform is not None and state.scr_root is not None and state.config_path is not None
    assert state.config_dict is not None
    smrt_addon_folder = gmod_path / "garrysmod" / "addons" / "smrt"
    print("NOTE: THIS WILL WIPE \"" + str(smrt_addon_folder) + "\".\n"
    "If this directory should not be wiped, do NOT proceed with the deletion! ")
    print("Are you sure you want to proceed and delete your music overrides? If so, type \"YES\".")
    confirm = input("Choice: ")
    if confirm == "YES":
        if smrt_addon_folder.is_dir():
            shutil.rmtree(smrt_addon_folder)
    for replacing_str, override_str in state.config_dict["active_overrides"].items():
        replacing = state.scr_root / "st_sound" / Path(replacing_str)
        override = Path(override_str)
        add_override(replacing,override,gmod_path)
    