from typing import Any,cast
from pathlib import Path
import json
import utils
import sys
import state
template_config: dict[Any,Any] = {
    "version":0.5,
    "path_to_gmod": None,
    "path_to_workshop":None,
    "extraction":False,
    "active_overrides" : {} # format will be "active_overrides" : {"something(replacing)":"another thing(the replacement)"}
}

def save_config(config_dict:dict[Any,Any]) -> None:
    assert state.config_path is not None
    with open(state.config_path,"w",encoding="utf-8") as fconfig:
        json.dump(config_dict,fconfig,indent=4)

def process_config(gmod_path: Path | None = None) -> dict[Any,Any]:
    # We know this for a fact
    assert state.platform is not None and state.scr_root is not None and state.config_path is not None
    # Make the config if it doesnt exist
    if not state.config_path.is_file():
        with open(state.config_path,"w",encoding="utf-8") as fconfig:
            json.dump(template_config, fconfig, indent=4)
    
    # Load the config
    with open(state.config_path,"r",encoding="utf-8") as fconfig:
        config_dict = json.load(fconfig)

    
    # if config version is wrong, warn and fill in empty values
    if config_dict.get("version",0) != template_config["version"]:
        utils.clear_terminal()
        print("Config file out of date! Config may be unfunctional. It is recommended you nuke SMRT and set-up your overrides from scratch. Proceeding with your existing config is unsupported.\n" \
        "SMRT will try to merge your config with a default config however this may not be reliable. Use at your own risk!")
        for k,v in template_config.items():
            config_dict.setdefault(k,v)
        input("Enter to proceed...")

    
    if gmod_path is not None:
        if not utils.config_sanity_check(config_dict,gmod_path):
            print("Config sanity check failed! Config file unreliable! Type BYPASS if you want to bypass this check. Otherwise, SMRT will be reset and all your overrides will be lost!")
            choice = input("Choice: ").lower().strip()
            if choice != "bypass":
                if utils.nuke_smrt(gmod_path):
                    save_config(template_config)
                    sys.exit(0)
            
    return config_dict
