"""
SMRT -- The Shinri Music Replacement Tool
I know this code is terrible, I don't expect anyone but me to work on it -ermez
"""
# Imports
import sys
from pathlib import Path
import config
import utils
import gmod
import state
import soundpacks
import overridelib

def option_nuke_smrt(gmod_path:Path):
    if utils.nuke_smrt(gmod_path):
        config.save_config(config.template_config)
        sys.exit(0)
if __name__ == "__main__":

    # Basic boilerplate
    utils.clear_terminal()
    state.platform = utils.get_platform()
    state.scr_root = utils.get_scr_root()
    state.config_path = state.scr_root / "config.json"
    assert state.platform is not None and state.scr_root is not None and state.config_path is not None
    state.config_dict = config.process_config()
    utils.clear_terminal()
    assert state.config_dict is not None
    # If GMOD path is unset
    if state.config_dict["path_to_gmod"] is None or (not (Path(state.config_dict["path_to_gmod"]) / "garrysmod").exists()): 
        gmod_path, steam_root = gmod.setup_gmod_path()
    else:
        steam_root = None
        gmod_path = Path(state.config_dict["path_to_gmod"])
    state.config_dict["path_to_gmod"] = str(gmod_path)
    config.save_config(state.config_dict)
    state.audio_path = state.scr_root / "st_sound"
    assert state.audio_path is not None
    # Check if audio extraction has already been done
    if not state.audio_path.is_dir() or not state.config_dict.get("extraction",False):
        # If the workshop path is not set
        if state.config_dict["path_to_workshop"] is None or (not Path(state.config_dict["path_to_workshop"]).exists()):
            workshop_path = gmod.setup_workshop_path(gmod_path)
        else:
            workshop_path = Path(state.config_dict["path_to_workshop"])
        state.config_dict["path_to_workshop"] = str(workshop_path)
        config.save_config(state.config_dict)
        # 4000 is gmod's id, workshop_gmod_content_path is where the addons are stored
        gmod.extract_addons(workshop_path,gmod_path)
        utils.clear_terminal()
        print("File extraction complete.")
    # The actual music replacement part
    workshop_path = state.config_dict["path_to_workshop"]
    config_dict = config.process_config(gmod_path)
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
            case "1": overridelib.option_add_override(gmod_path)
            case "2": overridelib.option_manage_overrides(gmod_path)
            case "3": option_nuke_smrt(gmod_path)
            case "4": soundpacks.option_export_soundpack()
            case "5": soundpacks.option_import_soundpack(gmod_path)
            case _: continue
        config_dict = config.process_config(gmod_path)
    

