# SMRT - The Shinri Music Replacement Tool
### WARNING - This project was originally intended for personal use only and may contain bugs! Use at your own risk.
### Project *will* use around 3GB of space as it will extract all the audio files from Shinri Trial for use.

## How it works
SMRT extracts the music files already shipped with Shinri Trial by using a tool built into Garry's Mod called gmad.exe. After the extraction, SMRT will allow the user to pick a file to be replaced and a file to replace with. It also allows the user to list and remove the overrides as they see fit.

## How to Use
When starting up SMRT for the first time, it will generate a config file. Then it will ask you for your GMod path. This is the path that you get when clicking "Browse Local Files" on GMod in Steam. By default it is ```C:\Program Files (x86)\Steam\steamapps\common\GarrysMod```.

After that, SMRT will prompt you for your "workshop path". This folder is specifically located in the "steamapps" folder 2 directories above the GMod folder in most cases. Note that it does **not** want the GMod workshop folder, just the general workshop folder. By default it is ```C:\Program Files (x86)\Steam\steamapps\workshop```.

After getting the folder directories, you may see a bunch of text coming out of the command output. That is gmad.exe unpacking the music files bundled into the game. You will know that process is done when it shows you the SMRT menu.

Option 1 will allow you to pick 2 ```.mp3``` files. The first file you pick will be the one that plays in game that you want to get rid of and the second file will be the one that replaces it. While you can *technically* choose a file outside of the ones that come with Shinri Trial, doing so is **unsupported** as there has been no testing on if GMod plays nice with them. You can certainly try *at your own risk*.

Option 2 will allow you to see all overrides that are currently listed in the ```config.json``` file. Note that this does **not** check what overrides are actually active, just which overrides are listed in the config. If your config becomes out of sync with the actual overrides, you may try option 3. When listing all these overrides, they will all get an ID. By inputting an ID number into SMRT, you can remove that override.

Option 3 will reset the config to a basic one and also remove the SMRT addon from GMod, essentially doing a soft-uninstall of the program. You may want to do this when you are trying to remove SMRT from your device or your config file is invalid or otherwise bad and you want a fresh start.

## Known Problems
### If you have any issues not listed here, please open an issue on the GitHub page.
- It is known that the program will mess up if the user chooses a wrong directory for their Garry's Mod or Workshop directory. I am planning to introduce a way to check if the directory is correct before allowing the program to proceed
- There might be some places without input validation which may cause the program to crash.

## Credits
- The Shinri Trial developers for making this possible
- I have used the assistance of Gemini 3.6 Flash in the development of SMRT. Please know that I did not "vibe code" this, I am just inexperienced with Python and programming in general and I needed help on file manipulation.
