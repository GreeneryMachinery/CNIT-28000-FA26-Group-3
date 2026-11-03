"""
Authors: Andrew Connolly and Trey Green
Program Name: MacroMakerV1.py
Date Initialized: 2024-06-10
Current Version: 1.0
Version Purpose: This program is designed to create macros for automating repetitive tasks in various applications. It allows users to record their actions and generate a script that can be executed later to replicate those actions.
"""

import keyboard
import json


#Test function 1.
def testHotkey():
    print("Test Macro Activated")

#Test function 2.
def testHotkey2():
    print("2nd Test Macro Activated")

#Test to make a macro using the user-supplied hotkeys pointed at Test Function 1.
def testFunction(desiredHotkeys):
    keyboard.add_hotkey(desiredHotkeys, testHotkey)

#Test to see if a user can input hotkeys and send that input to the macro creation function.
def testMacroMaking():
    desiredHotkeys = input("Please enter the keys you would like for your macro with a + between each one (e.g. shift+x): ")
    testFunction(desiredHotkeys)

#Test to make sure program can listen to two macros at once.
def testSecondMacro():
    keyboard.add_hotkey("shift+z", testHotkey2)




#JSON Test code. WIP (Don't have windows laptop on me)
def jsonTest():
    jsonTestStr = '{"hotkeys": "shift+g+h", "filePath": "C:\\Windows\\System32"}'
    testData = json.loads(jsonTestStr)

    print(testData["hotkeys"])
    print(testData["filePath"])




def main():
    # Placeholder for the main functionality of the MacroMaker program
    #testHotkey()
    testMacroMaking()
    testSecondMacro()
    keyboard.wait()
    # Additional code for recording actions and generating scripts will be added here.


main()