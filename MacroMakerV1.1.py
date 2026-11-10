"""
Authors: Andrew Connolly and Trey Green
Program Name: MacroMakerV1.py
Date Initialized: 2024-06-10
Current Version: 1.1
Version Purpose: Testing .csv as an alternative to .JSON as the data format may work better for our situation.
"""

import keyboard
import csv
import os
import time

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

#Function to launch a file.
def activateMacro(filePath):
    #print(filePath)
    os.startfile(filePath)


#Function to initialize the macros found in the CSV config file. This function will be called on startup always.
def initializeMacros():
    #Open the config.csv file.
    with open("config.csv", "r", newline="") as file:
        #reader iterates through the CSV file row by row.
        reader = csv.reader(file)
        for row in reader:
                #For loop to handle each row. hotkeys is the hotkeys expected, filePath is the file to open when the hotkeys in the adjacent cell are pressed.
                hotkeys = row[0].strip().lower()
                filePath = row[1].strip()
                #Initializes the macro within the keyboard library using the filePath as an argument for the activateMacro function.
                keyboard.add_hotkey(hotkeys, activateMacro, args=[filePath])


#Function to add a macro to the config.csv file.
def addMacro(hotkeys, filePath):

    #Call normalization function.
    hotkeysNormalized = normalizeHotkeys(hotkeys)
    print(hotkeysNormalized)

    #Code to check for duplicate macro hotkeys, and return a value of False if a match is found.
    with open("config.csv", "r", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if hotkeysNormalized == normalizeHotkeys(row[0]):
                print("Error: Macro with specified hotkeys already exists!\n\nPlease select a new set of hotkeys.")
                return False

    #Code to write the macro to the config.csv file if no duplicate is found. Returns True if macro is successfully created.
    with open("config.csv", "a", newline="") as file:
        writer = csv.writer(file)
        macroToAdd = [hotkeysNormalized, filePath]
        writer.writerow(macroToAdd)
        print("Macro added successfully!")
        return True
# CODE NEEDS WORK< NOT WORKING ATM
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
        isCorrect = input("Are these the keys you wish to use? y/n: ")
        if isCorrect == "y" or isCorrect == "Y":
            repeatEntry = False
        elif isCorrect == "n" or isCorrect == "N":
            repeatEntry = True
        else:
            print("Error: Please select a valid option!")
    return normalizedEnteredKeys


"""
#NEEDS REMOVED FROM PRODUCTION BUILDS, WILL OVERWRITE CONFIG FILES
def csvTestData():
    #Adds test data to the CSV file for testing purposes.
    testData = [["shift+z", "C:\\Windows\\System32\\Notepad.exe"]]

    #Writes test data to 
    with open("config.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(testData)

    print("Try the test macro (Shift + Z) to launch the Notepad program!")


def initialTests():
    # Placeholder for the main functionality of the MacroMaker program
    #csvTestData()
    # Additional code for recording actions and generating scripts will be added here.
"""

def main():

    #Temporary python-based menu.
    userSelection = "0"
    while userSelection == "0":
        print("\nPlease select an option from the menu below.")
        print("1 - Create new macro.")
        print("2 - Activate program.")
        userSelection = input("Please enter your selection: ")
        if userSelection == "1":
            print("\n===Create new macro===")
            print("Hotkey expected format (without quotes) \"shift+z\"")
            print("FilePath expected format (without quotes) \"C:\\Windows\\System32\\\"")
            hotkeys = autoEnterHotkeys()
            time.sleep(0.5)
            filePath = input("Please enter your desired filepath: ")
            successfulCreation = addMacro(hotkeys, filePath)
            if successfulCreation == True:
                userSelection = "0"
            elif successfulCreation == False:
                userSelection = "1"
        elif userSelection == "2":
            initializeMacros()
            print("Listening for macros...")
            #keyboard.wait()
            reinvokeMenu = input("To invoke the menu, type (without quotes) \"menu\" and press the Enter key.\n")
            if reinvokeMenu == "menu":
                userSelection = "0"
            else:
                print("Error: Unknown Request\nPlease type \"menu\" to return to menu.")
                userSelection = "2"
        else:
            print("Error: Unknown Request")
            userSelection = "0"



#Call main.
main()