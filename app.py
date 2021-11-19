
# app.py

# Main module for POS sequence finder app.

import PySimpleGUI as sg
from backend import *


# === UI TEXT ===

INPUT_PROMPT = "Enter a sequence of two or more POS tags from the Brown \
universal tagset, separated by spaces (e.g. 'ADJ NOUN NOUN')"


# === INITIAL WINDOW LAYOUT ===

main_column = [
    [sg.In(size=(50, 1), enable_events=True, key="-SEQUENCE-")],
    [
        sg.Button('Find phrases', key="-BUTTON-", disabled=True),
        sg.Button('Reset all', key="-RESET-", button_color='red', disabled=True)],
    [sg.Text(text=INPUT_PROMPT, size=(50, 2), key="-INFO-", justification='center')],
    [sg.Multiline(size=(50, 10), key="-PHRASES-")],
    [sg.Button('Save to .txt file', key="-SAVE-", button_color="green", disabled=True)]
]

pos_column = [
    [sg.Table(ALL_POS, headings=["Tag", "Description"], num_rows=len(ALL_POS), hide_vertical_scroll=True,
              enable_events=True, key="-TAG_TABLE-", select_mode=sg.TABLE_SELECT_MODE_BROWSE)]
    # [sg.Multiline(default_text=ALL_POS, size=(25,20), key="-POS-", no_scrollbar=True)]
]

layout = [
    [
        sg.Column(main_column, element_justification='center'),
        sg.VSeperator(),
        sg.Column(pos_column),
    ]
]


# === WINDOW INITIALIZATION ===

window = sg.Window("POS sequence finder", layout, finalize='True')

# snake_case variable names for UI elements
findButton = window['-BUTTON-']
sequenceInput = window['-SEQUENCE-']
infoText = window['-INFO-']
phraseBox = window['-PHRASES-']
resetButton = window['-RESET-']
saveButton = window['-SAVE-']

# Global variable to track sequence currently being displayed
currently_displayed = None

# Listen for Enter key press in sequenceInput
sequenceInput.bind("<Return>", "_Enter")


# === WINDOW CONTROL FUNCTIONS ===

def disableFind():
    findButton.update(disabled=True)
def enableFind():
    findButton.update(disabled=False)
def disableReset():
    resetButton.update(disabled=True)
def enableReset():
    resetButton.update(disabled=False)
def disableSave():
    saveButton.update(disabled=True)
def enableSave():
    saveButton.update(disabled=False)

def setInfo(msg: str):
    infoText.update(msg)
    window.refresh()

def writeMatches(matches: list):
    # Write list of matches to text box
    phraseBox.update('\n'.join(matches))
    # Set scroll position to top of text box
    phraseBox.set_vscroll_position(0)

def enableFindIfValidSequence():
    disableFind()
    # Enable find button if sequence is valid and is not already being displayed
    if pos_list(input_):
        enableFind()
    enableReset()
    

# === EVENT LOOP ===

while True:
    # Get events
    event, values = window.read()
    if values:
        input_ = values['-SEQUENCE-']
        pos = pos_list(input_)

    # Handle exit
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    # Handle button click or Enter
    if event == "-BUTTON-" or event == "-SEQUENCE-" + "_Enter":
        disableFind()
        disableReset()
        if pos:
            # Display loading message
            setInfo(f"Getting phrases for POS sequence {' '.join(pos)}...")
            # Get matches
            matches = get_matches(pos)
            # Display info and write matches to text box
            setInfo(get_match_info_string(pos, matches))
            writeMatches(matches)
            # Enable reset
            enableReset()
            # Enable save if there is at least one match
            if matches:
                enableSave()
            currently_displayed = pos
            
    # Handle input box change
    elif event == "-SEQUENCE-":
        enableFindIfValidSequence()
        # Disable reset if box is empty and no search results are being displayed
        if not input_ and not currently_displayed:
            disableReset()

    # Handle reset button
    elif event == "-RESET-":
        # Reset info
        setInfo(INPUT_PROMPT)
        # Clear sequence input and phrase box
        sequenceInput.update('')
        phraseBox.update('')
        # Disable reset and save
        disableReset()
        disableSave()
        currently_displayed = None

    elif event == "-SAVE-":
        # Prompt user for save location
        file_path = sg.popup_get_file(message="", 
                                      save_as=True,
                                      default_path=' '.join(currently_displayed),
                                      default_extension=".txt",
                                      file_types=[('Text files', '*.txt')],
                                      no_window=True)
        if file_path == '':
            # User pressed Cancel
            pass
        else:
            # Attempt to write phrases to file and inform user if successful or not
            try:
                with open(file_path, 'w') as f:
                    f.write(values['-PHRASES-'])
            except:
                sg.Popup(f'Unable to save file! (Unknown error.)', keep_on_top=True)
            else:
                sg.Popup('File saved.', keep_on_top=True)

    elif event == "-TAG_TABLE-":
        clicked_row = values['-TAG_TABLE-'][0]
        input_ = input_.strip() + ' ' + ALL_POS[clicked_row][0]
        sequenceInput.update(input_)
        enableFindIfValidSequence()


# === APP TERMINATION ===

window.close()