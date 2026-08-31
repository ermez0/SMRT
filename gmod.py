from pathlib import Path
import subprocess
from typing import cast,Any
import vdf
import sys
import shutil
import config
import utils
import state
# Extracts the .gma file at gma_path using gmad.exe found at gmad_path and saves the output at out_path
def extract_gma(gmad_path:Path,gma_path:Path,out_path:Path) -> bool:
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





def detect_gmod(steam_root: Path) -> Path | None:
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
    
def detect_steam_root(platform: str) -> Path | None:
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

def detect_workshop(gmod_path: Path) -> Path | None:
    print("SMRT will attempt to auto-configure the Workshop path. If this is incorrect, you will be allowed to choose a custom path.")
    workshop_path = gmod_path.parent.parent / "workshop"
    if not (workshop_path / "content" /"4000").is_dir():
        print("Auto detect failure, reverting to manual pick.")
        return None
    return workshop_path

def extract_addons(workshop_path:Path,gmod_path:Path,config_dict:dict[Any,Any],audio_path:Path,config_path:Path) -> None:
    workshop_gmod_content_path = workshop_path / "content" / "4000"
    addons_to_extract = ["3600114514","2560009684","2560012664","3600116031"] # These are the IDs of BGM Base, 1, 2 and 3 by Mikvoin on the steam workshop
    # get gmad
    gmad_path = find_gmad(gmod_path)
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
            result = extract_gma(gmad_path,addon_file_path,audio_path)
            if not result: # If the extraction fails, st_sound probably makes no sense at that point so I recomment just wiping it. I am being paranoid and asking for the user's consent before rm -r ing a directory
                print("Because extraction failed, it is *heavily* recommeneded you remove the st_sound directory.")
                print(str(audio_path) + " will be removed PERMANENTLY. If this path is valid, input \"YES\". If the path is invalid, type \"NO\" or close out of the program.\n"
                "If you do not authorize the deletion, please delete the directory yourself.\n"
                "Leaving a faulty st_sound directory MIGHT prevent SMRT from properly functioning.")
                confirm = input("Confirm>> ")
                if confirm == "YES":
                    shutil.rmtree(audio_path,ignore_errors=True)
                sys.exit("GMAD Failure")
    config_dict["extraction"] = True # mark the extraction as complete
    config.save_config(config_dict,config_path)

def find_gmad(gmod_path: Path) -> Path | None:
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

def setup_gmod_path() -> tuple[Path,Path | None]:
    assert state.platform is not None
    print("SMRT will attempt to auto-configure the GMOD path. If this is incorrect, you will be allowed to choose a custom path.")
    gmod_path = None
    steam_root = detect_steam_root(state.platform)
    choice = ""
    if not steam_root:
        print("Failure to locate Steam! Reverting to manual folder select.")
    else:
        gmod_path = detect_gmod(steam_root)
        if gmod_path:
            print("GMod located at " + str(gmod_path) + ". if this is incorrect, type MANUAL, otherwise hit Enter.")
            choice = input("Choice: ")
    if choice.strip().upper() == "MANUAL" or not gmod_path: 
        print("GMod path has not been configured or is invalid!\nPlease input your GMod path.\nThis is the path you get placed into when you click \"Browse local files\" on Steam.")
        gmod_path = utils.folder_picker("Select GMod Path")
        if not gmod_path:
            sys.exit("File picker failed.")
    return gmod_path,steam_root

def setup_workshop_path(gmod_path: Path) -> Path:
    utils.clear_terminal()
    workshop_path = detect_workshop(gmod_path)
    choice = ""
    if workshop_path:
        print("Workshop located at " + str(workshop_path) + ". if this is incorrect, type MANUAL, otherwise hit Enter.")
        choice = input("Choice: ")
    if not workshop_path or choice.strip().upper() == "MANUAL":          
        print("Workshop path has not been configured!\nPlease input your workshop path.\nThis is located at STEAMPATH/steamapps/workshop\nC:\\Program Files (x86)\\Steam\\steamapps\\workshop is the default.(On Windows)")
        workshop_path = utils.folder_picker("Select Workshop Path")
        if not workshop_path:
            sys.exit("File picker failed.")
        if workshop_path.name == "4000" and workshop_path.parent.name == "content": #they chose wrong
            workshop_path = workshop_path.parent.parent
        elif workshop_path.name == "content":
            workshop_path = workshop_path.parent
    return workshop_path