"""
Authors: Andrew Connolly and Trey Greene
Program Name: MacroMakerV1.py
Date Initialized: Nov 10, 2026
Current Version: 0.3
Version Purpose: Converting from CSV file format to an SQLite database to reduce performance overhead/ease of CRUD operations.
"""


#Import required libraries.
import keyboard
import sqlite3
import os
import time


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
        

"""
AI Disclosure
ChatGPT V6.0 Sol
How would I modify the existing macro check to normalize key order (e.g. prevent users from inputting shift+z and z+shift)
Goal of code is to cover every scenario of duplicate macro creation. Initial check was hand-written but didn't account for the same keys in different orders.
AI was used to create a more elegant solution (AI normalizing function is only one line)
"""
def normalizeHotkeys(hotkeys):
    return "+".join(sorted(key.strip().lower() for key in hotkeys.split("+")))
#END OF AI GENERATED CODE SEGMENT


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
            macroID = connection.execute("SELECT macroID FROM macroStorage WHERE hotkeys = ?", (hotkeysNormalized))
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


"""
#Function to display all macros (WILL NOT BE NEEDED/WILL NEED MAJOR CHANGES WHEN GUI IS FINISHED)
def readMacros():
    print("\nNum. ==Hotkeys== \t| ==FilePaths==")
    with sqlite3.connect("config.db") as connection:
        connection.execute()
""" 


#Function to edit an existing macro.
def updateMacro(macroID, hotkeys, filePath):
    #Normalize hotkeys prior to use.
    hotkeysNormalized = normalizeHotkeys(hotkeys)
    #Try-except to handle duplicate hotkeys.
    try:
        #Open connection to DB.
        with sqlite3.connect("macroStorage.db") as connection:
            #Creates a variable that contains the isEnabled status.
            macroStatus = connection.execute("SELECT isEnabled FROM macroStorage WHERE macroID = ?", [macroID]).fetchone()
            #If macro is enabled, do...
            if macroStatus[0] == 1:
                #De-initialize the macro by removing the keyboard hotkey.
                deinitializeMacro(macroID)
            #Update macro with new hotkeys and filePath once it has been deactivated above.
            connection.execute("UPDATE macroStorage SET hotkeys = ?, filePath = ? WHERE macroID = ?", (hotkeysNormalized, filePath, macroID))
        #If check to see if macro is enabled, if so run the initializeMacro function to make sure it is re-enabled.
        if macroStatus[0] == 1:
            initializeMacro(macroID, hotkeysNormalized, filePath)
        print("Macro updated successfully.")
        return True
    #Except handles if a hotkey combination already exists.
    except sqlite3.IntegrityError:
        print("Error: A macro with those hotkeys already exists. Please try again.")
        return False


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
        #Prints the request to press hotkeys,
        print("Please press your desired hotkeys...")
        #Pause for 1 second so user can release any keys used in the menu.
        time.sleep(1)
        #User entered hotkeys are converted to a string using the read_hotkey function.
        userEnteredKeys = keyboard.read_hotkey(suppress=True)
        normalizedEnteredKeys = normalizeHotkeys(userEnteredKeys)
        #Print shows the hotkeys that were read.
        print(f"The hotkeys entered are {normalizedEnteredKeys}")
        #CODE BELOW SOMETIMES DOES NOT RECOGNIZE THE SHIFT KEY WHEN CREATING A MACRO, MAY NEED ADVANCED TESTING TO DETERMINE ROOT CAUSE
        isCorrect = input("Are these the keys you wish to use? y/n: ")
        if isCorrect == "y" or isCorrect == "Y":
            repeatEntry = False
        elif isCorrect == "n" or isCorrect == "N":
            repeatEntry = True
        else:
            print("Error: Please select a valid option!")
    return normalizedEnteredKeys


def tempTerminalMenu():
    #Temporary command line menu for testing purposes, will be replaced with a GUI.
        userSelection = "0"
        while userSelection == "0":
            print("\nPlease select an option from the menu below.")
            print("1 - Create new macro.")
            print("2 - Toggle Macro.")
            print("3 - Modify existing macro.")
            print("4 - Delete existing macro.")
            print("5 - Activate MacroMaker.")
            userSelection = input("Please enter your selection: ")
            if userSelection == "1":
                print("\n===Create new macro===")
                hotkeysCreate = autoEnterHotkeys()
                print("FilePath expected format (without quotes) \"C:\\Windows\\System32\\\"")
                time.sleep(0.5)
                filePathCreate = input("Please enter your desired filepath: ")
                successfulCreation = createMacro(hotkeysCreate, filePathCreate)
                if successfulCreation == True:
                    userSelection = "0"
                elif successfulCreation == False:
                    userSelection = "1"
            elif userSelection == "2":
                macroID = int(input("Please enter the ID of the macro you wish to toggle: "))
                toggleMacro(macroID)
                userSelection = "0"
            elif userSelection == "3":
                print("\n===Modify a macro===")
                macroIDModify = int(input("Please enter the macroID if the macro you wish to modify: "))
                hotkeysModify = autoEnterHotkeys()
                print("FilePath expected format (without quotes) \"C:\\Windows\\System32\\\"")
                filePathModify = input("Please enter your desired filepath: ")
                successfulModification = updateMacro(macroIDModify, hotkeysModify, filePathModify)
                if successfulModification == True:
                    userSelection = "0"
                elif successfulModification == False:
                    userSelection = "3"
            elif userSelection == "4":
                print("\n===Delete a macro===")
                macroIDDelete = int(input("Please enter the macroID if the macro you wish to Delete: "))
                confirmDelete = input(f"Are you sure you want to delete macro {macroIDDelete}? If so type \"delete\" (without quotations): ")
                if confirmDelete == "delete":
                    deleteMacro(macroIDDelete)
                else:
                    print("Confirmation unsuccessful, please try again.")
                userSelection = "0"
            elif userSelection == "5":
                print("Listening for macros...")
                #keyboard.wait()
                reinvokeMenu = input("To invoke the menu, type (without quotes) \"menu\" and press the Enter key.\n")
                if reinvokeMenu == "menu":
                    userSelection = "0"
                else:
                    print("Error: Unknown Request\nPlease type \"menu\" to return to menu.")
                    userSelection = "5"
            else:
                print("Error: Unknown Request")
                userSelection = "0"
    

#Main function.
def main():

    initializeDB()
    initializeMacrosOnStartup()
    tempTerminalMenu()

#Call main.
main()