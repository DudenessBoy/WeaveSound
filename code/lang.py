#   WeaveSound is a music player designed with a simple and small interface in mind
#     Copyright (C) 2024  Luke Moyer
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

# this module contains code to keep the lang file updated by adding new keys and checking for syntax errors
import os
import re
import json
from pathlib import Path
from platform import system
from tkinter import messagebox

lang = {
    "button": {
        "random": "random",
        "refresh": "refresh",
        "play_track": "Play Track",
        "play_queue": "Play Queue",
        "play_all": "Play All",
        "browse": "Browse",
        "find": "Find",
        "queue_add": "Add to queue",
        "queue_manage": "Manage queue",
        "queue_save": "Save queue",
        "queue_save_as": "Save queue as",
        "queue_load": "Load queue",
        "settings": "Settings…",
        "filters": "Filters…",
        "license": "License…",
        "credits": "Credits…",
        "remove": "Remove",
        "move_up": "Move Up",
        "move_down": "Move Down",
        "add": "Add",
        "duplicate": "Duplicate",
        "shuffle": "Shuffle",
        "clear_queue": "Clear queue",
        "new_queue": "New queue",
        "done": "Done",
        "change": "Change…",
        "cancel": "cancel",
        "apply_filters": "Apply Filters",
        "clear_filters": "Clear Filters",
        "volume_up": "vol ↑",
        "volume_down": "vol ↓",
        "mute": "mute",
        "unmute": "unmute",
        "pause": "⏯",
        "rewind": "⏪",
        "stop": "⏹",
        "prev_track": "⏮",
        "next_track": "⏭",
        "open": "Open",
        "playlist": "Playlist",
        "play": "Play",
        "make_queue": "Extract & make queue",
        "export_playlist": "Export Playlist",
        "about": "About…"
    },
    "tooltip": {
        "random": "pick a random track",
        "refresh": "refresh the list of tracks",
        "play_track": "play the selected track",
        "play_queue": "play your queue (alt+p)",
        "play_all": "play all of your tracks",
        "browse": "select a file from somwhere else",
        "find": "find tracks more easily",
        "queue_add": "add the selected track to the current queue ({}+a)",
        "queue_manage": "manage the current queue",
        "queue_save": "save the current queue",
        "queue_load": "load a previously saved queue",
        "settings": "customize WeaveSound",
        "filters": "apply filters to single out tracks",
        "license": "view WeaveSound's license",
        "credits": "view WeaveSound's credits",
        "remove": "remove the selected track",
        "move_up": "move the selected track up",
        "move_down": "move the selected track down",
        "add": "add new tracks to the queue",
        "duplicate": "duplicate the selected track",
        "shuffle": "shuffle your queue",
        "clear_queue": "clear your queue",
        "new_queue": "create a new queue",
        "done_queue": "save changes and exit queue manager",
        "done_settings": "save changes and exit settings",
        "done_filters": "exit filters",
        "apply_filters": "apply all used filters",
        "clear_filters": "clear all filters",
        "volume_up": "volume up",
        "volume_down": "vol down",
        "mute": "mute/unmute",
        "pause": "pause/play",
        "rewind": "rewind",
        "stop": "stop the music and return to the selection window",
        "prev_track": "previous track",
        "next_track": "next track",
        "find_next": "find next (down, enter)",
        "find_prev": "find previous (up)",
        "close": "close",
        "queue_save_as": "choose a location to save this queue",
        "done_dirs": "exit directory manager",
        "export_playlist": "export queue to a playlist",
        "playlist": "play a playlist",
        "about": "show helpful information about the program"
    },
    "checkbox": {
        "midi": "Musical Instrument Digital Interface (*.midi;*.mid)",
        "wav": "Waveform Audio Format (*.wav)",
        "mp3": "MPEG Audio Layer III (*.mp3)",
        "ogg": "OGG Vorbis Compressed Audio (*.ogg)",
        "flac": "Free Lossless Audio Codec (*.flac)",
        "opus": "Opus Lossy Compression Audio Format (*.opus)",
        "aiff": "Audio Interchange File Format (*.aiff;*.aif)",
        "mod": "Music Module File (*.mod)",
        "xm": "Extended Module (*.xm)",
        "save_queue": "Save current queue",
        "loop_queue": "Loop queue",
        "loop_play_all": "Loop after play all",
        "in_queue": "In queue",
        "track_length": "Get track length",
        "wrap": "Wrap around"
    },
    "radiobutton": {
        "loop_infinite": "∞",
        "loop_zero": "0",
        "loop_custom": "Custom…",
        "dark": "Dark",
        "light": "Light",
        "ask": "Ask every time",
        "loop": "Loop current",
        "next": "Play next"
    },
    "context_menu": {
        "random": "Random",
        "refresh": "Refresh",
        "play_track": "Play Track",
        "play_queue": "Play Queue",
        "play_all": "Play All",
        "browse": "Browse",
        "find": "Find",
        "queue_add": "Add to queue",
        "queue_manage": "Manage queue",
        "queue_save": "Save queue",
        "queue_load": "Load queue",
        "settings": "Settings",
        "filters": "Filters",
        "license": "Veiw License",
        "credits": "Veiw Credits",
        "remove": "Remove",
        "move_up": "Move Selected Track Up",
        "move_down": "Move Selected Track Down",
        "add": "Add New Tracks",
        "duplicate": "Duplicate Selected Track",
        "shuffle": "Shuffle",
        "clear_queue": "Clear queue",
        "new_queue": "New queue",
        "apply_filters": "Apply Filters",
        "clear_filters": "Clear Filters",
        "volume_up": "Volume Up",
        "volume_down": "Volume Down",
        "mute": "Mute/Unmute",
        "pause": "Play/Pause",
        "rewind": "Rewind",
        "stop": "Stop",
        "prev_track": "Previous Track",
        "next_track": "Next Track"
    },
    "tab": {
        "dir": "Directory",
        "key_bindings": "Key Bindings",
        "queue": "Queue",
        "play_all": "Play All",
        "file_type": "File Type",
        "contains": "Contains…",
        "no_contains": "Does Not Contain…",
        "begins_with": "Begins With…",
        "no_begins_with": "Does Not Begin With…",
        "ends_with": "Ends With…",
        "no_ends_with": "Does Not End With…",
        "language": "Language",
        "theme": "Theme",
        "in_queue": "In queue",
        "playlist": "Playlist",
        "track_length": "Track Length",
        "track_end": "Track End Event"
    },
    "title": {
        "main": "WeaveSound",
        "selection": "Selection",
        "manager": "Queue Manager",
        "filters": "Filters",
        "settings": "Settings",
        "control": "Control",
        "eula": "License",
        "credits": "Credits",
        "save_as": "Save As",
        "open_queue": "Open Queue File",
        "open": "Open File",
        "bad_ext": "Invalid File Extension",
        "save_error": "Save Error",
        "dir_manager": "Directory Manager",
        "add_dir": "Add a Search Directory",
        "pickle_error": "Pickle Error",
        "permission_error": "Permission Error",
        "file_missing": "File Not Found",
        "error": "Error",
        "bad_format": "Incorrect Format",
        "replace_file": "Replace File",
        "about": "About WeaveSound"
    },
    "label": {
        "search_dirs": "Search directories",
        "loop": "Number of times to loop music after initial playthrough",
        "pause": "Pause/play",
        "mute": "Mute/unmute",
        "volume_up": "Volume Up",
        "volume_down": "Volume Down",
        "contains": "Contains…",
        "no_contains": "Does Not Contain…",
        "begins_with": "Begins With…",
        "no_begins_with": "Does Not Begin With…",
        "ends_with": "Ends With…",
        "no_ends_with": "Does Not End With…",
        "choose": "Choose an audio file to play",
        "compatable": "WeaveSound Compatable Files",
        "queue_file": "Queue Files",
        "audio_file": "Audio Files",
        "pickle": "Pickle Files",
        "any_file": "All Files",
        "current_key": "Current Key: {}\nPress your new key",
        "untitled": "Untitled",
        "language": "Choose your language",
        "theme": "Choose your theme",
        "playlist_file": "Playlist Files",
        "playlist_query": "What do you wish to do with {}?",
        "track_length": "Get track length. Enabling this may cause some tracks to load slower.",
        "playlist": "What to do when opening playlist",
        "data_folder": "Data Folder"
    },
    "message": {
        "bad_queue": "Invalid queue file",
        "done_queue": "Queue finished",
        "done_all": "Tracks finished",
        "track_done": "Track finished",
        "bad_file": "Invalid file name/type",
        "empty": "try adding music to one of your search directories",
        "dupe_key": "That key is already used!",
        "empty_queue": "Queue is empty!",
        "play_none": "There are no tracks to play",
        "no_search_dir": "try adding a search directory"
    },
    "popup": {
        "bad_ext": "WeaveSound does not recognize the file extension you are trying to load. Please make sure it is from a trusted source before trying to load it.\nTry to load the file anyway?",
        "save_error_0": "An Error occurred while trying to save data to \"{}\". This could be due to an error in your system, or WeaveSound may not have permission to modify the file.",
        "save_error_1": "An Error occurred while trying to save data to \"{}\". This could be due to an error in your system, or WeaveSound may not have permission to modify the file. this error is NOT due to nonexistant file, as WeaveSound will create it if it does not exist.",
        "pickle_error": "There was an error while attempting to unpickle the file \"{}\"",
        "permission_error": "Permission to read the file \"{}\" could not be obtained.",
        "eof": "The file \"{}\" seems to be corrupted",
        "file_missing": "The file \"{}\" could not be found",
        "error": "An error occurred while loading the file \"{}\"",
        "bad_playlist": "The file you tried to load is not a valid playlist file",
        "error_write": "An error occurred while attempting to write to the file \"{}\".",
        "permission_error_write": "Permission to write to the file \"{}\" could not be obtained.",
        "replace_file": "A file with the name \"{}\" already exists at the path \"{}\".\nWould you like to replace it?"
    },
}

match system():
    case 'Windows':
        dataFolder = os.getenv('LOCALAPPDATA')
    case 'Darwin':# macOS
        dataFolder = Path.home() / 'Library/caches'
    case 'Linux':
        dataFolder = Path.home() / '.config'

# Define regex to find curly braces with numbers inside
pattern = re.compile(r'{\d+}')

# Re-create lang.json
def make() -> bool:
    valid = False
    while not valid:
        try:
            with open(os.path.join(str(dataFolder), 'WeaveSound', 'lang.json'), 'w', encoding='utf-8') as f:
                json.dump(lang, f, indent=4)
        except (PermissionError, IOError):
            ans = messagebox.showerror('Error Writing to JSON File', 
                f'There was an error writing to the file "{os.path.join(str(dataFolder), "WeaveSound", "lang.json")}".\n'
                'Please make sure that the program has permission to modify the file and that the drive has enough space.',
                type='retrycancel'
            )
            if ans == 'cancel':
                return False
        else:
            valid = True
            return True

# Function to check for curly braces with numbers inside them
def check_for_invalid_placeholders(loaded: dict) -> bool:
    """Scans the loaded language data for placeholders like '{0}', '{1}', etc."""
    invalid_found = False

    # Recursive function to scan nested dictionaries
    def check_values(d: dict, path: str = ''):
        nonlocal invalid_found
        for key, value in d.items():
            current_path = f'{path}.{key}' if path else key
            if isinstance(value, dict):
                check_values(value, current_path)
            elif isinstance(value, str):
                # Look for patterns like "{0}", "{1}" in the string
                if pattern.search(value):
                    print(f'Invalid placeholder found at {current_path}: {value}')
                    invalid_found = True

    check_values(loaded)
    return invalid_found

# Check lang.json for validity
def check() -> dict:
    try:
        with open(os.path.join(str(dataFolder), 'WeaveSound', 'lang.json'), 'r', encoding='utf-8') as f:
            loaded = json.load(f)
    except (PermissionError, EOFError, json.JSONDecodeError, FileNotFoundError):
        make()
        loaded = lang

    # Validate that there are no curly braces with numbers
    if check_for_invalid_placeholders(loaded):
        make()
    
    # Proceed with the existing language verification and syncing logic
    for lang_key, lang_value in lang.items():
        if lang_key not in loaded:
            loaded[lang_key] = {}

        for i in lang_value:
            if i not in loaded[lang_key]:
                if lang_key not in lang:
                    loaded[lang_key][i] = lang.get(i, '')
                else:
                    loaded[lang_key][i] = lang_value[i]
            elif isinstance(lang_value[i], dict):
                for j in lang_value[i]:
                    if j not in loaded[lang_key][i]:
                        if lang_key not in lang:
                            loaded[lang_key][i][j] = lang[i].get(j, '')
                        else:
                            loaded[lang_key][i][j] = lang_value[i][j]

    # Save the updated JSON back to the file
    try:
        with open(os.path.join(str(dataFolder), 'WeaveSound', 'lang.json'), 'w', encoding='utf-8') as f:
            json.dump(loaded, f, ensure_ascii=False, indent=4)
    except (PermissionError, IOError):
        messagebox.showerror(
            'Error Writing to JSON File',
            f'There was an error writing to the file "{os.path.join(str(dataFolder), "WeaveSound", "lang.json")}".\n'
            'Please make sure that the program has permission to modify the file and that the drive has enough space.',
            type='retrycancel'
        )
        return {}

    return loaded
