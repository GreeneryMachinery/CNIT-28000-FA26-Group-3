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


#Function to launch a file.
def activateMacro(filePath):
    #print(filePath)
    os.startfile(filePath)


#Function to initialize the macros found in the CSV config file. This function will be called on startup always.
def initializeMacros():
    #Open the config.csv file.
    with open("config.csv", newline="") as file:
        #reader iterates through the CSV file row by row.
        reader = csv.reader(file)
        for row in reader:
                #For loop to handle each row. macroKeys is the hotkeys expected, filePath is the file to open when the hotkeys in the adjacent cell are pressed.
                macroKeys = row[0].strip().lower()
                filePath = row[1].strip()
                #Initializes the macro within the keyboard library using the filePath as an argument for the activateMacro function.
                keyboard.add_hotkey(macroKeys, activateMacro, args=[filePath])



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
    csvTestData()
    initializeMacros()
    keyboard.wait()
    # Additional code for recording actions and generating scripts will be added here.


def main():
    #Call the initial tests function.
    initialTests()

#Call main.
main()