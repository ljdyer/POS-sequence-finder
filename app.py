
# app.py

# Main module for POS sequence finder app.

import PySimpleGUI as sg
from backend import *


# === UI SETTINGS ===

# Prompt to display on startup
INPUT_PROMPT = "Enter a sequence of two or more POS tags from the" \
"Brown universal tagset, separated by spaces (e.g. 'ADJ NOUN NOUN')"

# POS tag table strings
POS_TABLE_HEADINGS = ["Tag", "Description"]
ALL_POS = [[tag, desc] for tag, desc in POS_LOOKUP.items()]

# Button labels
FIND_TEXT = 'Find phrases'
RESET_TEXT = 'Reset all'
SAVE_TEXT = 'Save to .txt file'

# Sizes
MAIN_COL_WIDTH = 50
PHRASE_DISPLAY_ROWS = 10
POS_TABLE_COL_WIDTHS = [7,18]

# === INITIAL WINDOW LAYOUT ===

# Each sublist in column list is a row in the window

main_column = [
    [sg.In(key="-SEQUENCE-", size=(MAIN_COL_WIDTH, 1),
           enable_events=True)],
    [
        sg.Button(key="-FIND-", button_text=FIND_TEXT, disabled=True),
        sg.Button(key="-RESET-", button_text=RESET_TEXT,
                  button_color='red', disabled=True)],
    [sg.Text(key="-INFO-", text=INPUT_PROMPT,
             size=(MAIN_COL_WIDTH, 2), justification='center')],
    [sg.Multiline(key="-PHRASES-",
                  size=(MAIN_COL_WIDTH, PHRASE_DISPLAY_ROWS))],
    [sg.Button(key="-SAVE-", button_text=SAVE_TEXT, 
               button_color="green", disabled=True)]
]

pos_column = [
    [sg.Table(
        key="-TAG_TABLE-",values=ALL_POS,
        headings=POS_TABLE_HEADINGS, num_rows=len(ALL_POS),
        hide_vertical_scroll=True, justification='left',
        auto_size_columns=False, col_widths=POS_TABLE_COL_WIDTHS,          
            # Because default cuts off some tags
        enable_events=True,                       
            # Listens for click event
        select_mode=sg.TABLE_SELECT_MODE_BROWSE   
            # Disables multiple row selection
    )]
]

layout = [
    [
        sg.Column(main_column, element_justification='center'),
        sg.VSeperator(),
        sg.Column(pos_column, element_justification='center'),
    ]
]


# === WINDOW INITIALIZATION ===

window = sg.Window("POS sequence finder", layout, finalize='True')

# snake_case variable names for UI elements
findButton = window['-FIND-']
sequenceInput = window['-SEQUENCE-']
infoText = window['-INFO-']
phraseBox = window['-PHRASES-']
resetButton = window['-RESET-']
saveButton = window['-SAVE-']

# Global variable to track sequence currently being displayed
currently_displayed = None
# Global variable to track number of matches currently displayed
current_matches = 0

# Listen for Enter key press in sequenceInput
sequenceInput.bind("<Return>", "_Enter")


# === WINDOW CONTROL FUNCTIONS ===

# snake_case function names

# Enable/disable buttons
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
    """Set text to display in info box"""

    infoText.update(msg)
    window.refresh()

def writeMatches(matches: list):
    """Write list of matches to text box"""

    phraseBox.update('\n'.join(matches))
    # Set scroll position to top of text box
    phraseBox.set_vscroll_position(0)

def enableFindIfValidSequence():
    """"""
    disableFind()
    # Enable find button if sequence is valid and is not already being
    # displayed
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
    if event == "-FIND-" or event == "-SEQUENCE-" + "_Enter":
        disableFind()
        disableReset()
        if pos:
            # Display loading message
            setInfo(f"Getting phrases for POS sequence " + \
                    f"{' '.join(pos)}...")
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
            current_matches = len(matches)
            
    # Handle input box value change
    elif event == "-SEQUENCE-":
        enableFindIfValidSequence()
        # Disable reset if box is empty and no search results are being
        # displayed
        if not input_ and not currently_displayed:
            disableReset()

    # Handle reset button click
    elif event == "-RESET-":
        # Reset info and clear sequence input and phrase box
        setInfo(INPUT_PROMPT)
        sequenceInput.update('')
        phraseBox.update('')
        # Disable reset and save
        disableReset()
        disableSave()
        # Reset currently_displayed
        currently_displayed = None
        current_matches = 0

    # Handle save button click
    elif event == "-SAVE-":
        file_name_default = ' '.join(currently_displayed) + \
                            f" ({current_matches} phrases)"
        # Prompt user for save location
        file_path = sg.popup_get_file(message="", 
                                      save_as=True,
                                      default_path=file_name_default,
                                      default_extension=".txt",
                                      file_types=[
                                          ('Text files', '*.txt')],
                                      no_window=True)
        if file_path == '':
            # User pressed Cancel
            pass
        else:
            # Attempt to write phrases to file and inform user if successful
            # or not
            try:
                with open(file_path, 'w') as f:
                    f.write(values['-PHRASES-'])
            except:
                sg.Popup(f'Unable to save file! (Unknown error.)',
                         keep_on_top=True)
            else:
                sg.Popup('File saved.', keep_on_top=True)

    # Handle click in POS tag table
    elif event == "-TAG_TABLE-":
        # Add the POS tag from the clicked row to the sequence input
        clicked_row = next(iter(values['-TAG_TABLE-']), None)
        if clicked_row is not None:
            input_ = (input_.strip() + ' ' + \
                      ALL_POS[clicked_row][0]).strip()
        sequenceInput.update(input_)
        enableFindIfValidSequence()


# === APP TERMINATION ===

window.close()