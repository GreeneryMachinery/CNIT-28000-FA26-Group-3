"""
Authors: Andrew Connolly and Trey Greene
Program Name: MacroMakerV1.py
Date Initialized: Nov 10, 2026
Current Version: 0.3
Version Purpose: Converting from CSV file format to an SQLite database to reduce performance overhead/ease of CRUD operations.
"""


import keyboard
import sqlite3
import os
import time


#Function to initialize the database if one hasn't been created. Does nothing if DB exists already.
def initializeDB():
    with sqlite3.connect("macroStorage.db") as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS macroStorage (
            macroID INTEGER PRIMARY KEY AUTOINCREMENT,
            hotkeys TEXT NOT NULL UNIQUE,
            filePath TEXT NOT NULL,
            isEnabled INTEGER NOT NULL DEFAULT 1)""")


#Function to initialize macros. Loads all macros with isEnabled = 1 into MacroMaker by registering their hotkeys.
def initializeMacros():
    with sqlite3.connect("macroStorage.db") as connection:
        macrosToInitialize = connection.execute("SELECT hotkeys, filePath FROM macroStorage WHERE isEnabled = 1").fetchall()
        for hotkeys, filePath in macrosToInitialize:
            keyboard.add_hotkey(hotkeys, executeMacro, args=[filePath])


#Function to launch a file.
def executeMacro(filePath):
    #print(filePath)
    os.startfile(filePath)


#Function to toggle a macro between active and inactive.
def toggleMacro(macroID):
    with sqlite3.connect("macroStorage.db") as connection:
        macroStatus = connection.execute("SELECT isEnabled FROM macroStorage WHERE macroID = ?", [macroID]).fetchone()
        macroHotkeys = connection.execute("SELECT hotkeys FROM macroStorage WHERE macroID = ?", [macroID]).fetchone()
        if macroStatus[0] == 0:
            macroFilePath = connection.execute("SELECT filePath FROM macroStorage WHERE macroID = ?", [macroID]).fetchone()
            keyboard.add_hotkey(macroHotkeys[0], executeMacro, args=[macroFilePath[0]])
            toggleEnableStatus = 1
            print("Macro successfully activated.")
        else:
            keyboard.remove_hotkey(macroHotkeys[0])
            toggleEnableStatus = 0
            print("Macro successfully deactivated.")
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


#Function to display all macros (WILL NOT BE NEEDED/WILL NEED MAJOR CHANGES WHEN GUI IS FINISHED)
def readMacros():
    print("\nNum. ==Hotkeys== \t| ==FilePaths==")
    with sqlite3.connect("config.db") as connection:
        connection.execute()
 

#Function that creates a new macro in the database.
def createMacro(hotkeys, filePath):
    #Ensure hotkeys are normalized before inserting into database.
    hotkeysNormalized = normalizeHotkeys(hotkeys)
    #Try-except to handle duplicate hotkeys.
    try:
        with sqlite3.connect("macroStorage.db") as connection:
            connection.execute("INSERT INTO macroStorage (hotkeys, filePath) VALUES (?, ?)", (hotkeysNormalized, filePath))
        print("Macro created successfully.")
        return True
    
    except sqlite3.IntegrityError:
        print("Error: A macro with those hotkeys already exists. Please try again.")
        return False


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


#Main function.
def main():

    initializeDB()
    initializeMacros()

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
            print("Hotkey expected format (without quotes) \"shift+z\"")
            print("FilePath expected format (without quotes) \"C:\\Windows\\System32\\\"")
            hotkeys = autoEnterHotkeys()
            time.sleep(0.5)
            filePath = input("Please enter your desired filepath: ")
            successfulCreation = createMacro(hotkeys, filePath)
            if successfulCreation == True:
                userSelection = "0"
            elif successfulCreation == False:
                userSelection = "1"
        elif userSelection == "2":
            macroID = int(input("Please enter the ID of the macro you wish to toggle: "))
            toggleMacro(macroID)
            userSelection = "0"
        elif userSelection == "5":
            initializeMacros()
            print("Listening for macros...")
            #keyboard.wait()
            reinvokeMenu = input("To invoke the menu, type (without quotes) \"menu\" and press the Enter key.\n")
            if reinvokeMenu == "menu":
                userSelection = "0"
            else:
                print("Error: Unknown Request\nPlease type \"menu\" to return to menu.")
                userSelection = "3"
        else:
            print("Error: Unknown Request")
            userSelection = "0"


#Call main.
main()