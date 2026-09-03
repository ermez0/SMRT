import utils
from pathlib import Path
import json
import config
import overridelib
import zipfile
import shutil
import state



def import_soundpack(gmod_path: Path,smrtx: bool = False):       
    assert state.audio_path is not None
    assert state.platform is not None and state.scr_root is not None and state.config_path is not None
    assert state.config_dict is not None
    warnFlag = False
    utils.clear_terminal()
    if not smrtx:
        soundpack_path = utils.file_picker("Select your soundpack",[("SMRT Soundpack file","*.smrt"),("All Files","*.*")],(state.scr_root / "soundpacks"))
        if soundpack_path is None:
            print("No soundpack selected! Enter to continue...")
            input()
            return
    else:
        soundpack_path = state.scr_root / "smrtx_info.smrt"
    with open(soundpack_path,"r",encoding="utf-8") as soundpack_file:
        soundpack = json.load(soundpack_file)
        new_overrides = {}
        for replacing,properties in soundpack.items():
            if properties["relative"]:
                override_path = state.audio_path / properties["path"]
            else:
                warnFlag = True
                override_path = properties["path"]
            new_overrides[Path(replacing).as_posix()] = Path(override_path).as_posix()
        utils.list_overrides_dict(new_overrides)
        if warnFlag and not smrtx:
            print("This pack has non-relative paths so it may not work if you got it from someone else or moved your SMRT directory. Proceed with caution!")
        if not smrtx:
            print("Are you sure you want to override your config with this soundpack?(y/N)")
            proceed = input("Choice: ")
            if proceed.lower().strip() != "y":
                return
        state.config_dict["active_overrides"] = new_overrides
        config.save_config(state.config_dict)
        if not smrtx:
            overridelib.load_overrides_from_config(gmod_path)

def get_path_to_save(extension: str,info: bool = False) -> Path:
    assert state.scr_root is not None
    prefix: str = "smrtx_info" if info else "soundpack"
    soundpacks_dir = state.scr_root / "soundpacks"
    soundpacks_dir.mkdir(exist_ok=True)
    count = 0
    already_exists = set()
    # The set idea came from AI, i would have never thought of it.
    if info:
        return soundpacks_dir / (prefix + extension)
    for file in sorted(soundpacks_dir.iterdir()):
        if file.is_file() and file.name.startswith(prefix):
            if (file.stem.removeprefix(prefix)).isdigit():
                already_exists.add(int(file.stem.removeprefix(prefix)))
    while count in already_exists:
        count += 1
    path_to_save = soundpacks_dir / (prefix + str(count) + extension)
    return path_to_save

def export_soundpack(smrtx: bool = False) -> Path:
    assert state.audio_path is not None
    assert state.platform is not None and state.scr_root is not None and state.config_path is not None
    assert state.config_dict is not None
    utils.clear_terminal()
    warnFlag = False
    soundpack_dict: dict = {}
    if not smrtx:
        print("The currently loaded config will be exported as a soundpack file.\n" \
        "Would you like to list the config? (Y/n)")
        choice = input("Choice: ")
        if choice.lower().strip() != "n":
            utils.list_overrides_dict(state.config_dict["active_overrides"])
    for replacing_str,override_str in state.config_dict["active_overrides"].items():
        replacing = Path(replacing_str)
        override = Path(override_str).resolve()
        is_relative = override.is_relative_to(state.audio_path.resolve())
        soundpack_dict[replacing.as_posix()] = {}
        soundpack_dict[replacing.as_posix()]["relative"] = is_relative
        if is_relative:
            soundpack_dict[replacing.as_posix()]["path"] = (override.relative_to(state.audio_path)).as_posix()
        else:
            warnFlag = True
            soundpack_dict[replacing.as_posix()]["path"] = override.as_posix()
    if warnFlag and not smrtx:
        print("This soundpack has overrides outside of st_sound and as such will *not* be compatible on another system.")
    path_to_save = get_path_to_save(".smrt",smrtx)
    with open(path_to_save,"w",encoding="utf-8") as f:
        json.dump(soundpack_dict,f,indent=4)
    if not smrtx:
        print("Exported to: "+str(path_to_save))
        input("Enter to continue...")
    return path_to_save



def option_export_soundpack(gmod_path: Path):
    utils.clear_terminal()
    print("This is a very experimental feature so please read the README.md file's section on soundpacks before proceeding!")
    print("1) SMRT Soundpack File\n" \
    "2) SMRTX Soundpack Archive")
    choice = input("Choice: ")
    match choice:
        case "1":
            export_soundpack()
        case "2":
            export_soundpackx(gmod_path)

def option_import_soundpack(gmod_path: Path):
    utils.clear_terminal()
    print("This is a very experimental feature so please read the README.md file's section on soundpacks before proceeding!")
    print("1) SMRT Soundpack File\n" \
    "2) SMRTX Soundpack Archive")
    choice = input("Choice: ")
    match choice:
        case "1":
            import_soundpack(gmod_path)
        case "2":
            import_soundpackx(gmod_path)



def export_soundpackx(gmod_path: Path) -> Path | None:
    utils.clear_terminal()
    assert state.config_dict is not None
    if not utils.config_sanity_check(state.config_dict,gmod_path):
        print("Soundpack export failed because of config sanity check!")
        input("Enter to proceed...")
        return
    if not state.config_dict["active_overrides"]:
        print("No overrides to export!")
        input("Enter to proceed...")
        return
    path_to_save = get_path_to_save(".smrtx")
    actual_path = Path(shutil.make_archive(str(path_to_save),"zip",str(gmod_path / "garrysmod" / "addons" / "smrt")))
    actual_path.rename(path_to_save)
    actual_path = path_to_save
    soundpack_info = export_soundpack(True)
    with zipfile.ZipFile(actual_path,"a") as soundpack:
        soundpack.write(soundpack_info,soundpack_info.name)
    if soundpack_info.is_file():
        print(f"Soundpack created! Delete the leftover info file at path {soundpack_info}? (y/N)?")
        choice = input("Choice: ").lower().strip()
        if choice == "y":
            soundpack_info.unlink()
    return actual_path


def import_soundpackx(gmod_path: Path) -> bool:
    assert state.audio_path is not None
    assert state.platform is not None and state.scr_root is not None and state.config_path is not None
    assert state.config_dict is not None
    soundpack_path = utils.file_picker("Select your soundpack",[("SMRT Soundpack archive","*.smrtx"),("All Files","*.*")],(utils.get_scr_root() / "soundpacks"))
    if soundpack_path is None:
        print("No soundpack selected! Enter to continue...")
        input()
        return False
    with zipfile.ZipFile(soundpack_path,"r") as soundpack:
        if "smrtx_info.smrt" not in soundpack.namelist():
            print("Soundpack info not found! Invalid soundpack. Enter to continue...")
            input()
            return False
        sound_files = []
        for file in soundpack.namelist():
            if file == "sound/" or file.startswith("sound/"):
                sound_files.append(file)
        soundpack.extractall((gmod_path / "garrysmod" / "addons" / "smrt"),sound_files)
        soundpack.extract("smrtx_info.smrt",utils.get_scr_root())
        import_soundpack(gmod_path,True)
        (utils.get_scr_root() / "smrtx_info.smrt").unlink(missing_ok=True)

    return True
        
    