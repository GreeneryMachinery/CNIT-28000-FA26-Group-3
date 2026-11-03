"""
Authors: Andrew Connolly and Trey Green
Program Name: MacroMakerV1.py
Date Initialized: 2024-06-10
Current Version: 1.0
Version Purpose: This program is designed to create macros for automating repetitive tasks in various applications. It allows users to record their actions and generate a script that can be executed later to replicate those actions.
"""

import keyboard


#Test code to see if keyboard library will work.
def testHotkey():
    print("Test Macro Activated")

def testHotkey2():
    print("2nd Test Macro Activated")

#keyboard.add_hotkey("shift+p", testHotkey)

#print("Listening for Shift + P.")
#keyboard.wait()



# Attempt to make a function that works with user inputs.
def testFunction(desiredHotkeys):
    keyboard.add_hotkey(desiredHotkeys, testHotkey)


def testMacroMaking():
    desiredHotkeys = input("Please enter the keys you would like for your macro with a + between each one (e.g. shift+x): ")
    testFunction(desiredHotkeys)

def testSecondMacro():
    keyboard.add_hotkey("shift+z", testHotkey2)

def main():
    # Placeholder for the main functionality of the MacroMaker program
    #testHotkey()
    testMacroMaking()
    testSecondMacro()
    keyboard.wait()
    # Additional code for recording actions and generating scripts will be added here.


main()