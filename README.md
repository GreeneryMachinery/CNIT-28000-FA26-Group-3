# CNIT-28000-FA26-Group-3
Welcome to the MacroMaker repository! This project is designed by Andrew Connolly & Trey Greene for our CNIT 28000 class at Purdue University.
This program is currently only supported for Windows 10/11. There are not plans to port the program to macOS or Linux.
To install and run the program, please see the instructions below.

NOTE: As of version 0.5, the program is intended to be run as an executeable file, not as a Python script. Modifications to the program may be
required to retain functionality as a Python script.

## Installation:
1. Download the MacroMaker.exe file from the latest release on the Github repository.
2. Select a location for the install folder (NOTE: MacroMaker does not have an installer, simply move the .exe file to a folder where you want the program to be kept).
3. Open the MacroMaker executable file. The .exe file will generate a .db file within the same directory.
4. You're done!
Optional Installation Steps:
5. Create a shortcut for MacroMaker by right clicking the exe file, and clicking on 'Create Shortcut' (may need to enter the right click sub-menu on Win11)
6. Configure MacroMaker to launch when your PC starts up by clicking 'Settings' and making sure that 'Launch on System Startup' is checked

## User Tutorial / FAQ
**Q:** How do I create a macro?
**A:**
1. Open the MacroMaker exe file
2. Click on Add Macro
3. Use the textbox to enter a name for the macro and click 'Ok' when done, or 'Cancel' to exit
4. Click 'Ok', and then press the desired combination of keys.
5. Verify that the program read your desired keys correctly, click 'Yes' if correct, click 'No' to retry entry, and click 'Cancel' to exit
6. Enter the file path to the program or file, or the URL of the webpage you want to open with the macro
7. Click 'Ok', your macro is now active and ready for use!

**Q:** How to I enable or disable a macro?
**A:** On the main GUI page, find the macro you want to enable/disable on the list. Under the 'Status' column, there is a checkbox. Click the checkbox to toggle the status (checked = enabled, unchecked = disabled)

**Q:** How do I delete a macro?
**A:**
1. Select the macro you wish to delete by clicking on it in the main GUI window
2. Once the desired macro is highlighted, click on 'Delete Macro'
3. A confirmation will appear confirming you wish to delete the macro, click 'Yes' to delete, click 'No' to cancel

**Q:** I want to delete all of my macros, is there an easy way to do that?
**A:** Yes! If you want to start fresh, simply delete or rename the .db file and MacroMaker will automatically generate a new empty database with no entries.

**Q:** How do I enable MacroMaker to launch on startup?
**A:** Click on the 'Settings' button in the bottom right of the GUI, and click the 'Launch on System Startup' checkbox. Uncheck it to disable launch on startup.

**Q:** I want to update MacroMaker, will I be able to keep my macros?
**A:** Yes* V1.0 and beyond will use the same database structure, so all you need to do is replace the exe file and you will be able to use your old macros.

**Q:** I want multiple different profiles, does MacroMaker support this?
**A:** At this time, MacroMaker only supports one profile. However, a workaround exists if you have two db files and name the active one macroStorage.db and name the inactive one something else (this is not officially supported, and MacroMaker should be closed during the renaming process to avoid any issues)

**Q:** My macros are clearing every time I restart my PC.
**A:** This behavior has been observed if multiple versions of Macro Maker are installed at the same time. Please disable 'Launch on Startup' and delete the .exe file for each version, then re-install the latest release following the installation instructions. If behavior persists, please open an issue with steps to replicate.
