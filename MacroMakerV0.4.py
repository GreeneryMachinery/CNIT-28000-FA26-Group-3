"""
Authors: Andrew Connolly and Trey Greene
Program Name: MacroMakerV1.py
Date Initialized: Nov 10, 2026
Current Version: 0.4
Version Purpose: To begin integrating a TKInter GUI.
"""


#Import required libraries.
#Used to manage macro execution / process keyboard input.
import keyboard

#Used to store macros in a database.
import sqlite3

#Used to open a filepath when a macro is executed.
import os

#Used to avoid detecting unwanted inputs.
import time

#Used to create GUI.
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

#Used for launching on startup.
import winreg
import sys
import subprocess


STARTUP_KEY = r"Software\\Microsoft\Windows\\CurrentVersion\\Run"
APP_NAME = "MacroMaker"


#Dictionary of currently initialized macros.
initializedMacroDictionary = {}


#Function to initialize the database if one hasn't been created. Does nothing if DB exists already.
def initializeDB():
    #Open a connection to the database.
    with sqlite3.connect("macroStorage.db") as connection:
        #Create the database with macroID, hotkeys, filePath, isEnabled as fields.
        connection.execute("""CREATE TABLE IF NOT EXISTS macroStorage (
            macroID INTEGER PRIMARY KEY AUTOINCREMENT,
            hotkeys TEXT NOT NULL UNIQUE,
            filePath TEXT NOT NULL,
            isEnabled INTEGER NOT NULL DEFAULT 1)""")

        
#Function to initialize macros on startup of program. ***WARNING*** DO NOT USE TO INITIALIZE A MACRO OUTSIDE OF STARTUP, IT WILL CAUSE ISSUES
def initializeMacrosOnStartup():
    #Open a connection to the database.
    with sqlite3.connect("macroStorage.db") as connection:
        #Create a tuple of tuples that contains a hotkey and filepath per enabled macro.
        macrosToInitialize = connection.execute("SELECT macroID, hotkeys, filePath FROM macroStorage WHERE isEnabled = 1").fetchall()
        #For loop iterates through the tuple of tuples and initialized a macro with hotkeys being the required keystrokes and filepath being the args for the executeMacro function.
        for macroID, hotkeys, filePath in macrosToInitialize:
            initializeMacro(macroID, hotkeys, filePath)


#Function that initializes macros and adds them to the dictionary to prevent dual-initialization (will cause multiple windows to open per hotkey otherwise)
def initializeMacro(macroID, hotkeys, filePath):
    #If macro is already initialized, return (False for future use if needed, doesn't do anything currently)
    if macroID in initializedMacroDictionary:
        return False
    #Else initialize the hotkey and add it to the macro dictionary to prevent duplicate initialization.
    else:
        macroDictionaryEntry = keyboard.add_hotkey(hotkeys, executeMacro, args=[filePath])
        #Add handler object for the keyboard hotkey to the dictionary.
        initializedMacroDictionary[macroID] = macroDictionaryEntry
        return True


#Function that deinitializes macros and removes them from the dictionary so they can be initialized later.
def deinitializeMacro(macroID):
    #Assigns the dictionary entry to a variable, then removes it from the dictionary.
    macroDict = initializedMacroDictionary.pop(macroID, None)
    #If the dictionary entry didn't exist, return False.
    if macroDict == None:
        return False
    #Else remove the hotkey using the handler object as reference and return True.
    else:
        keyboard.remove_hotkey(macroDict)
        return True


#Function to launch a file.
def executeMacro(filePath):
    #Uses OS library to launch a file at a given address, which in this case is the variable filePath.
    os.startfile(filePath)


#Function to toggle a macro between active and inactive.
def toggleMacro(macroID):
    #Open a connection to the database.
    with sqlite3.connect("macroStorage.db") as connection:
        #Create variables that contain the isEnabled status and the hotkeys of a macro.
        macroStatus = connection.execute("SELECT isEnabled FROM macroStorage WHERE macroID = ?", [macroID]).fetchone()
        #Check if macro exists.
        if macroStatus == None:
            print("Error: Macro ID does not exist.")
            return False
        macroHotkeys = connection.execute("SELECT hotkeys FROM macroStorage WHERE macroID = ?", [macroID]).fetchone()
        #If macro is disabled, do...
        if macroStatus[0] == 0:
            #Create varaible that contains the filePath of the macro.
            macroFilePath = connection.execute("SELECT filePath FROM macroStorage WHERE macroID = ?", [macroID]).fetchone()
            #Initialize a hotkey in the keyboard library using the hotkeys and the filePath.
            initializeMacro(macroID, macroHotkeys[0], macroFilePath[0])
            #Set the value of toggleEnableStatus to 1 to indicate the macro now being enabled.
            toggleEnableStatus = 1
            print("Macro successfully activated.")
        #Else macro is enabled, do...
        else:
            #De-initialize the hotkey with the coresponding hotkey combination so the macro is no longer active.
            deinitializeMacro(macroID)
            #Set the value of toggleEnableStatus to 0 to indicate the macro now being disabled.
            toggleEnableStatus = 0
            print("Macro successfully deactivated.")
        #Update the macro isEnabled value to either 0 or 1 depending on the outcome of the above select statement.    
        connection.execute("UPDATE macroStorage SET isEnabled = ? WHERE macroID = ?", (int(toggleEnableStatus), macroID))


#Function that creates a new macro in the database.
def createMacro(hotkeys, filePath):
    #Ensure hotkeys are normalized before inserting into database.
    hotkeysNormalized = normalizeHotkeys(hotkeys)
    #Try-except to handle duplicate hotkeys.
    try:
        #Create connection to DB.
        with sqlite3.connect("macroStorage.db") as connection:
            #Creates a new macro with hotkeys and filePath being variables.
            connection.execute("INSERT INTO macroStorage (hotkeys, filePath) VALUES (?, ?)", (hotkeysNormalized, filePath))
            #Get macroID from the new macro.
            macroID = connection.execute("SELECT macroID FROM macroStorage WHERE hotkeys = ?", (hotkeysNormalized,)).fetchone()[0]
        #InitializeMacro is called to make sure the new macro is enabled by default.
        initializeMacro(macroID, hotkeysNormalized, filePath)
        print("Macro created successfully.")
        #Return true to know if creation was successful.
        return True
    #Except to catch error of identical hotkeys.
    except sqlite3.IntegrityError:
        print("Error: A macro with those hotkeys already exists. Please try again.")
        #Returns false to know that macro creation failed.
        return False


#Function to edit an existing macro.
def updateMacro(macroID, hotkeys, filePath):
    #Normalize hotkeys prior to use.
    hotkeysNormalized = normalizeHotkeys(hotkeys)
    #Try-except to handle duplicate hotkeys.
    try:
        #Open connection to DB.
        with sqlite3.connect("macroStorage.db") as connection:
            #Check to see if a macro with the same hotkeys already exists, excluding the current macroID being modified.
            duplicateMacro = connection.execute("SELECT macroID FROM macroStorage WHERE hotkeys = ? AND macroID != ?", (hotkeysNormalized, macroID)).fetchone()
            if duplicateMacro != None:
                print("Error: A macro with those hotkeys already exists. Please try again.")
                return False
            #Creates a variable that contains the isEnabled status.
            macroStatus = connection.execute("SELECT isEnabled FROM macroStorage WHERE macroID = ?", [macroID]).fetchone()
            if macroStatus == None:
                print("Error: Macro ID does not exist.")
                return False
            #If macro is enabled, do...
            if macroStatus[0] == 1:
                #De-initialize the macro by removing the keyboard hotkey.
                deinitializeMacro(macroID)
            #Update macro with new hotkeys and filePath once it has been deactivated above.
            connection.execute("UPDATE macroStorage SET hotkeys = ?, filePath = ? WHERE macroID = ?", (hotkeysNormalized, filePath, macroID))
            #If check to see if macro is enabled, if so run the initializeMacro function to make sure it is re-enabled.
            if macroStatus[0] == 1:
                if macroStatus == None: # Check to see if macroID exists, if not return false and print error message.
                    print("Error: Macro ID does not exist.")
                    return False
                initializeMacro(macroID, hotkeysNormalized, filePath)
            print("Macro updated successfully.")
            return True
    #Except handles if a hotkey combination already exists.
    except sqlite3.IntegrityError:
        print("Error: A macro with those hotkeys already exists. Please try again.")
        return False


#Function to delete an existing macro.
def deleteMacro(macroID):
    #Deinitialize macro to remove from memory.
    deinitializeMacro(macroID)
    #Open connection to the DB.
    with sqlite3.connect("macroStorage.db") as connection:
        #Delete the macro with the given macroID.
        connection.execute("DELETE FROM macroStorage WHERE macroID = ?", [macroID])
    #Print a success message when complete.
    print("Macro successfully deleted!")


#Function to record keystrokes for hotkey entry rather than requiring the user to type in the keys they want to use.   
def autoEnterHotkeys():
    repeatEntry = True
    while repeatEntry == True:
        #Prompts user for their desired hotkeys
        continueEntry = messagebox.askokcancel("Enter Hotkeys:", "Click OK, then press your desired hotkeys...")
        #Check if the user closed the window - cancel the operation if so.
        if continueEntry == False:
            return None
        #Pause so the system doesnt catch the click of OK as a hotkey
        time.sleep(1)
        #user entered hotkeys are converted into a string and sent over to the normalizehotkey function to be put into the desired order
        userEnteredKeys = keyboard.read_hotkey(suppress=True)
        normalizedEnteredKeys = normalizeHotkeys(userEnteredKeys)
        #Ask user if the hotkeys displayed are correct, otherwiser the the loop will run again
        isCorrect = messagebox.askyesnocancel("Confirm Hotkeys", "The hotkeys entered are " + normalizedEnteredKeys + "\n\nUse these keys?")
        #Check if the user closed the window.
        if isCorrect == None:
            return None
        if isCorrect == True:
            repeatEntry = False
    return normalizedEnteredKeys


#Function to normalize hotkeys so that they are in a consistent order for storage and comparison.
def normalizeHotkeys(hotkeys):
    # List of keys that should be up front in the list.
    modifierKeys = ["shift", "ctrl", "alt", "windows"]
    # Lists to separate modifier keys and other keys.
    modifiers = []
    otherKeys = []
    #Sort each key into the correct list, and return ordered string 
    for key in hotkeys.split("+"):
        key = key.strip().lower()
        if key in modifierKeys:
            modifiers.append(key)
        else:
            otherKeys.append(key)
    # sort each list, then put them back together in the right order
    return "+".join(sorted(modifiers) + sorted(otherKeys))


def cleanFilePath(filePath):
    #Remove any quotation marks and whitespace from the beginning and end of the file path.
    return filePath.strip().strip('"')

"""
AI Disclosure
ChatGPT V6.0 Sol
"Help me develop a solution that allows the program to launch on startup without requiring the user to manually add files to the startup directory"
AI was used to aid in the development of a more elegant solution to allowing for Macro Maker to run on startup.
"""
def toggleLaunchOnStartup(isStartupEnabled):
    if isStartupEnabled == True:
        #Code that checks for both a standard .py file or an .exe file (final release plan to package into an .exe)
        if getattr(sys, "frozen", False):
            command = subprocess.list2cmdline([sys.executable])
        else:
            scriptPath = os.path.abspath(sys.argv[0])
            pythonPath = sys.executable

            #Use pythonw.exe to avoid a console window.
            if os.path.basename(pythonPath).lower() == "python.exe":pythonPath = os.path.join(os.path.dirname(pythonPath),"pythonw.exe")

            command = subprocess.list2cmdline([pythonPath, scriptPath])

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,STARTUP_KEY,0,winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, command)

    else:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,STARTUP_KEY,0,winreg.KEY_SET_VALUE) as key:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass


def programStartupStatus():
    #Try-except to catch an error if the file isn't found.
    try:
        #Opens the windows registry to search and see if MacroMaker is currently set as a startup program.
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY) as key:
            #Search registry for an entry for MacroMaker.
            winreg.QueryValueEx(key, APP_NAME)
            #Returns true if the file referencing the APP_NAME MacroMaker is found indicating it is enabled at startup.
            return True
    #If the registry entry isn't found, the function returns False indicating that the program is not enabled at startup.
    except FileNotFoundError:
        return False
"""
End AI Assist Segment
"""


"""
AI Disclosure
ChatGPT V6.0
Assistance was used to develop a simple Tkinter GUI to replace the
temporary terminal menu (tempTerminalMenu).

The GUI follows the project's wireframe and connects the existing
macro creation, editing, deletion, and toggle functions to graphical
buttons and a macro display table.

AI was used to assist with the Tkinter layout and basic GUI functionality.
"""
def runGUI():
    #Create the main window.
    window = tk.Tk()
    window.title("Macro Maker")
    window.geometry("850x450")
    window.minsize(750, 350)

    #Create the title.
    title = tk.Label(window,text="Macro Maker",font=("Arial", 20, "bold"))
    title.pack(fill="x")

    #Create the top buttons.
    buttonFrame = tk.Frame(window)
    buttonFrame.pack(fill="x")

    #Create the macro table.
    columns = ("icon", "name", "hotkeys", "filePath", "status")
    macroTable = ttk.Treeview(window,columns=columns,show="headings")

    #Set the table headings.
    macroTable.heading("icon", text="Program Icon")
    macroTable.heading("name", text="Name")
    macroTable.heading("hotkeys", text="Keyboard Shortcut")
    macroTable.heading("filePath", text="Program / File / URL")
    macroTable.heading("status", text="Status")

    #Set the table column sizes.
    macroTable.column("icon", width=55, anchor="center")
    macroTable.column("name", width=110)
    macroTable.column("hotkeys", width=145)
    macroTable.column("filePath", width=350)
    macroTable.column("status", width=65, anchor="center")

    macroTable.pack(fill="both", expand=True)

    #Function to load macros from the database.
    def refreshMacros():
        #Clear the table.
        for item in macroTable.get_children():
            macroTable.delete(item)
        #Retrieve macros from the database.
        with sqlite3.connect("macroStorage.db") as connection:
            macros = connection.execute("SELECT macroID, hotkeys, filePath, isEnabled FROM macroStorage").fetchall()
        #Insert each macro into the table.
        for macroID, hotkeys, filePath, isEnabled in macros:
            #Get the name from the file path.
            macroName = os.path.basename(filePath.rstrip("\\/"))
            if macroName == "":
                macroName = filePath
            #Display a checked or unchecked status.
            if isEnabled == 1:
                status = "☑"
            else:
                status = "☐"
            macroTable.insert("", "end", iid=macroID, values=("▶", macroName, hotkeys, filePath, status))

    #Function to add a macro.
    def addMacroGUI():
        hotkeys = autoEnterHotkeys()
        #Check if the user canceled the hotkey entry.
        if hotkeys == None:
            return
        filePath = simpledialog.askstring("Add Macro", "Enter the program, file, folder, or URL:")
        if filePath == None:
            return
        #Remove quotation marks from the file path.
        filePath = cleanFilePath(filePath)
        #Check that the target exists or is a URL.
        if not (os.path.exists(filePath) or filePath.startswith(("http://", "https://"))):
            messagebox.showerror("Error", "Invalid file path or URL.")
            return
        #Create the macro using the existing function.
        successful = createMacro(hotkeys, filePath)
        if successful == True:
            refreshMacros()

    #Function to edit a macro.
    def editMacroGUI():
        selected = macroTable.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a macro first.")
            return
        macroID = int(selected[0])
        #Get the current macro information.
        with sqlite3.connect("macroStorage.db") as connection:
            macro = connection.execute("SELECT hotkeys, filePath FROM macroStorage WHERE macroID = ?", (macroID,)).fetchone()
        if macro == None:
            messagebox.showerror("Error", "Macro could not be found.")
            refreshMacros()
            return
        #Ask for the updated information.
        hotkeys = autoEnterHotkeys()
        #Check if the user canceled the hotkey entry.
        if hotkeys == None:
            return
        filePath = simpledialog.askstring("Edit Macro", "Enter the new program, file, folder, or URL:", initialvalue=macro[1])
        if filePath == None:
            return
        #Remove quotation marks from the file path.
        filePath = cleanFilePath(filePath)
        #Check that the target exists or is a URL.
        if not (os.path.exists(filePath) or filePath.startswith(("http://", "https://"))):
            messagebox.showerror("Error", "Invalid file path or URL.")
            return
        #Update the macro using the existing function.
        successful = updateMacro(macroID, hotkeys, filePath)
        if successful == True:
            refreshMacros()

    #Function to delete a macro.
    def deleteMacroGUI():
        selected = macroTable.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a macro first.")
            return
        macroID = int(selected[0])
        confirm = messagebox.askyesno("Delete Macro", "Are you sure you want to delete this macro?")
        if confirm:
            deleteMacro(macroID)
            refreshMacros()

    #Function to toggle a macro's status.
    def toggleMacroGUI(event):
        selected = macroTable.identify_row(event.y)
        column = macroTable.identify_column(event.x)
        #Only toggle when the status column is clicked.
        if selected and column == "#5":
            macroID = int(selected)
            toggleMacro(macroID)
            refreshMacros()

    #Function to minimize window when clicking the X button.
    def minimizeOnX():
        #Iconify is the tkinter function to minimize a program to the taskbar.
        window.iconify()

    
    #Function for the Settings button.
    def settings():
        #messagebox.showinfo("Settings", "Macro Maker must remain running for global hotkeys to work.\n\nDatabase: " + os.path.abspath("macroStorage.db"))
        #Create settings window.
        settingsWindow = tk.Toplevel()
        settingsWindow.title("Settings")
        settingsWindow.geometry("275x100")
        settingsWindow.minsize(200, 100)

        #Create the settings window title.
        settingsTitle = tk.Label(settingsWindow,text="Settings",font=("Arial", 20, "bold"))
        settingsTitle.pack(fill="x")
       
        #Create the settings button frame.
        settingsButtonFrame = tk.Frame(settingsWindow)
        settingsButtonFrame.pack(fill="x")

        #Create text of the name of the first setting, launch on startup.
        toggleStartupText = tk.Label(settingsWindow,text="Launch on System Startup: ")
        toggleStartupText.pack(side="left",padx=(25,0),expand=False,fill="x")

        #Create a checkbox for the first setting, launch on startup.
        isStartupEnabled = tk.BooleanVar(value=programStartupStatus())
        toggleStartupCheckbox = tk.Checkbutton(settingsWindow,variable=isStartupEnabled,command=lambda: toggleLaunchOnStartup(isStartupEnabled.get()))
        toggleStartupCheckbox.pack(side="left",padx=(25,25),expand=False,fill="x")



    #Connect the status column to the toggle function.
    macroTable.bind("<ButtonRelease-1>", toggleMacroGUI)

    #Create the top buttons.
    tk.Button(buttonFrame,text="Add Macro",command=addMacroGUI).pack(side="left", expand=True, fill="x")
    tk.Button(buttonFrame,text="Edit Macro",command=editMacroGUI).pack(side="left", expand=True, fill="x")
    tk.Button(buttonFrame,text="Delete Macro",command=deleteMacroGUI).pack(side="left", expand=True, fill="x")

    #Create the bottom Settings button.
    bottomFrame = tk.Frame(window)
    bottomFrame.pack(fill="x")
    tk.Button(bottomFrame,text="Settings",command=settings).pack(side="right")

    #Instead of closing upon clicking X, minimize to taskbar instead (requires users to right-click icon and close if they wish to exit program).
    window.protocol("WM_DELETE_WINDOW", minimizeOnX)

    #Load existing macros.
    refreshMacros()
    #Keep the window open.
    window.mainloop()
"""
END OF AI ASSISTED CODE SECTION
"""


#Main function.
def main():

    initializeDB()
    initializeMacrosOnStartup()
    runGUI()


#Call main.
main()