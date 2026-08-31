# SMRT - The Shinri Music Replacement Tool
### WARNING - This project was originally intended for personal use only and may contain bugs! Use at your own risk.
### Project *will* use around 3GB of space as it will extract all the audio files from Shinri Trial for use.

## How it works
SMRT extracts the music files already shipped with Shinri Trial by using a tool built into Garry's Mod called gmad.exe. After the extraction, SMRT will allow the user to pick a file to be replaced and a file to replace with. It also allows the user to list and remove the overrides as they see fit. The replacement works by making a folder in ```.../garrysmod/addons``` named "smrt", and putting the files in there. From my experimentation, the music there overrides the music that Shinri Trial comes with.

## How to Use
When starting up SMRT for the first time, it will generate a config file. Then it will attempt to auto-detect your GMod folder. If it fails, it ask you for your GMod path. This is the path that you get when clicking "Browse Local Files" on GMod in Steam. By default it is ```C:\Program Files (x86)\Steam\steamapps\common\GarrysMod```.

After that, SMRT will attempt to auto-detect the workshop folder. If it fails, it will prompt you for your "workshop path". This folder is specifically located in the "steamapps" folder 2 directories above the GMod folder in most cases. Note that it does **not** want the GMod workshop folder, just the general workshop folder. By default it is ```C:\Program Files (x86)\Steam\steamapps\workshop```.

After the initial setup is complete, you will be presented with 5 options.

1. **Add Override:** This option will allow you to pick a track to be replaced and a track to override the first track. It will then allow you to extend the track if it is too short.
2. **Manage Existing Overrides:** This option will allow you to remove any overrides that currently exist.
3. **Nuke SMRT:** This option will delete the ```st_sound```,```audio_cache``` and ```.../garrysmod/addons/smrt``` directories in addition to the config.json file being reset. Will essentially do a factory reset.
4. **Export soundpack:** Will export the current config as a ```.smrt``` file, containing information on overrides.
5. **Import soundpack:** Will import a ```.smrt``` file into the config, putting the override information in it into effect.

## Known Problems
### If you have any issues not listed here, please open an issue on the GitHub page.
- **\*.smrt soundpack files have problems when using any non-relative paths**

  This will be adressed with a new *.smrtx soundpack bundling the audio with it.

## FAQ(Not really I'm just answering questions I thought *might* get asked)
- **Why is this not a workshop addon?**

  Because this tool allows customizability that you just can't get from one addon. Also I don't know how steam works well enough to make an addon
- **Why does the looping feature exist?**

  Without it, the music will end but instead of starting the new track, the game will wait in silence until the length of the original track has passed. This feature will fill the gap.

## Credits
- The Shinri Trial developers for making this possible
- I have used the assistance of Gemini 3.6 Flash in the development of SMRT. Please know that I did not "vibe code" this, I am just inexperienced with Python and programming in general and I needed help on file manipulation.
