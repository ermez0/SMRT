import utils
from pathlib import Path
import json
import config
import overridelib

def option_import_soundpack(config_dict: dict, config_path: Path, scr_root: Path, audio_path: Path,gmod_path: Path):       
    warnFlag = False
    utils.clear_terminal()
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
        utils.list_overrides_dict(new_overrides)
        if warnFlag:
            print("This pack has non-relative paths so it may not work if you got it from someone else or moved your SMRT directory. Proceed with caution!")
        print("Are you sure you want to override your config with this soundpack?(y/N)")
        proceed = input("Choice: ")
        if proceed.lower().strip() != "y":
            return
        config_dict["active_overrides"] = new_overrides
        config.save_config(config_dict,config_path)
        overridelib.load_overrides_from_config(config_dict,gmod_path,config_path,audio_path)

def option_export_soundpack(config_dict: dict, audio_path: Path, scr_root: Path):
    utils.clear_terminal()
    warnFlag = False
    soundpack_dict: dict = {}
    print("The currently loaded config will be exported as a soundpack file.\n" \
    "Would you like to list the config? (Y/n)")
    choice = input("Choice: ")
    if choice.lower().strip() != "n":
        utils.list_overrides_dict(config_dict["active_overrides"])
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
