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

import os
import sys
import zlib
import time
import json
import random
import pickle
import webbrowser
import lang as lang_
import tkinter as tk
from glob import glob
from io import BytesIO
from pygame import error
from pathlib import Path
from platform import system
from base64 import b64decode
from threading import Thread
from tooltip import Hovertip
from pydub import AudioSegment
from LicenseText import LICENSE
from pygame.mixer import init, music
from tkinter import ttk, filedialog, messagebox

init()# initiate mixer

# platform dependant stuff
print('Getting OS...')
OS = system()
match OS:
    case 'Windows':
        lightTheme = 'xpnative'
        dataFolder = os.getenv('LOCALAPPDATA')
        musicDir = Path.home() / 'Music'
        x = 215
        length = 26
        Control = 'Control'
        ctrl = 'ctrl'
        size = 160
        shift = 10
        spacing = 0
        width = 10
    case 'Darwin':# macOS
        lightTheme = 'alt'
        dataFolder = Path.home() / 'Library/caches'
        musicDir = Path.home() / 'Music/Music/Media'
        x = 215
        length = 26
        Control = 'Command'
        ctrl = 'cmd'
        size = 160
        shift = 0
        spacing = 0
        width = 6
    case 'Linux':
        lightTheme = 'alt'
        dataFolder = Path.home() / '.config'
        musicDir = Path.home() / 'Music'
        x = 293
        length  = 15
        Control = 'Control'
        ctrl = 'ctrl'
        size = 170
        shift = 10
        spacing = 10
        width = 5
    case _:
        messagebox.showerror('WeaveSound', 'This program does not yet support your operating system')
        exit()
print('Done')

FORMATS = ['mp3', 'wav', 'ogg', 'flac', 'opus', 'midi', 'mid', 'aiff', 'aif', 'mod', 'xm']# a list of supported file formats
muted = False # a flag for whether or not the music is muted
# the image code for the window icon
ICON = 'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsEAAA7BAbiRa+0AAAJRSURBVHhe7ZrpjoMgEIDV2tO2pkfSvv9D9k8P1nHBAFprFYZhZ79kgpqWOZgBJCahKYpCVI0uqGSyZct/AGTLluAByDL2Y2BMgGI+n6NOhKlsQ9LlMJpdJPMvTVO0LCAZACFEslwuUUshJHXtd8lisYDWK1TnABtvdsYSAIVze6NahGezmfOSiC0DdJzYHvM2zEk2xL4PFVOXy5hLoIuv/aGYAeCEkq9elsbsIClmQJ9NoloJkufzKW97oeDbICAAugxF7Pd7+7+NYL5PTMU2fgwiz3O7H11I49JYsdvt7P5UppDFNtgFopo8jX597CJdYRgKDxxi9C2DYhD7RugTxkrwer0S7CO3IRijBA88YOg4n8++9IzCMA4e+GC9XqPoGQOmYY0euWxGtxOcSkvXX58EbVrB5RYAg+PxKLiVgKLWCW+arDNgs9nIq7DAaOjiHbktrnWxzAA4U6CEPvr1qPgGzgrUlpjzJFjrYVkC1D7KUKmvxCv2KzG7DCiKQl79wm0OAF1G/2wy4HK5tJwH2ATgdrvJK3rAyOjinK6zQEp4DUC13+/tk9sk2ILlRkiHfQB8pFtfzXXpi7cE4Eipamzpo/mdnJnFdruF58EYE+1PTk4FNQOGKvPttA6NEpDrpxI+HA4H3XFUWa1W0KJipxu6ARao6Q/oJRDU+ev1Kq/C0KRhCKmWQmiD0jIKS8qyhDYYKRwP3+93eYsOes3bZJXz6EacTidogjvfgLj0kafL6ElC/Ru9d2k42ug8z5PH40EnvT8w1NB3AYnG0W6S5AerblWkxL02nAAAAABJRU5ErkJggg=='
special = []# list to be used with filters
playingQueue = (False, None)# flag for whether a queue or a regular track is playing, and whether queue or play all is playing
num = 0 # which index of the queue should play
findWord = ''
managerFindWord = ''
isClosing = False
plylst = {}
trackLength = '00:00:00'
loops = 0
showingAll = True

# open a file location
def openLocation(directory: str) -> None:
    match OS:
        case 'Windows':
            os.startfile(directory)
        case 'Darwin':# macOS
            os.system('open "%s"' % directory)
        case 'Linux':
            os.system('xdg-open "%s"' % directory)
    print('Opened file location')

# create a list containing all the compatable music files from the search directories
def getFiles() -> tuple[list[str], list[str], list[str]]:
    print('Getting files from search directories...')
    files = []
    shortened = []
    beginning = []
    
    for i in data.directories:
        dirFiles = []
        for format in FORMATS:
            dirFiles += glob(str(i) + os.sep + '*.' + format)
        for file in dirFiles:
            path = os.path.split(file)
            files.append(file)
            beginning.append(path[0])
            shortened.append(path[1])
    print('Done')
    return files, shortened, beginning

# volume up
def up(event = None) -> None:
    global vol
    if music.get_volume() < 10:
        vol.set(vol.get() + 1)
    music.set_volume(vol.get() / 10)
    slider.set(vol.get())
    print(f'Volume set to {vol.get()}')

# volume down
def down(event = None) -> None:
    global vol
    if music.get_volume() > 0:
        vol.set(vol.get() - 1)
    music.set_volume(vol.get() / 10)
    slider.set(vol.get())
    print(f'Volume set to {vol.get()}')

# volume change
def volume(event = None) -> None:
    if not muted:
        music.set_volume(vol.get() / 10)
        print(f'Volume set to {vol.get()}')

# mutes or unmutes, depending on the state of the 'muted' var
def mute(event = None) -> None:
    global muted
    if muted:
        music.set_volume(vol.get() / 10)
        muted = False
        mutebtn.config(text = lang['button']['mute'])
        print(f'Volume set to {vol.get()}')
    else:
        music.set_volume(0)
        muted = True
        mutebtn.config(text = lang['button']['unmute'])
        print('Volume set to 0')

# pauses or plays, depending on music state
def pauseplay(event = None) -> None:
    try:
        if music.get_busy():
            music.pause()
            print('Music paused')
        else:
            music.unpause()
            print('Music resumed')
    except Exception as error:
        print(f'Non-fatal error: {error}')
        with open(os.path.join(str(dataFolder), 'WeaveSound', 'errorOutputLog.txt'), 'a') as file:
            file.write(error) 

# time update, also handles music end event
def update() -> None:
    global num, playingQueue
    while True:
        try:
            if music.get_busy():
                label.config(text = time.strftime('%H:%M:%S', time.gmtime(round(music.get_pos() / 1000))) + '/' + trackLength)
                time.sleep(.1)
                if music.get_pos() == -1:
                    if playingQueue[0]:
                        if playingQueue[1] == 'queue':
                            num += 1
                            if not num >= len(data.queue.queue):
                                loaded = tryLoad(data.queue.queue[num])
                                if not loaded:
                                    music.unload()
                                    control.withdraw()
                                    root.deiconify()
                            else:
                                num = 0
                                if data.loopQueue:
                                    startQueue(False)
                                else:
                                    mess.config(text = lang['message']['queue_done'])
                                    minimized = control.state() == 'iconic'
                                    playingQueue = (False, None)
                                    music.unload()
                                    control.withdraw()
                                    if minimized:
                                        root.iconify()
                                    else:
                                        root.deiconify()
                                    if minimized:
                                        root.iconify()
                                    else:
                                        root.deiconify()
                        elif playingQueue[1] == 'playlist':
                            num += 1
                            if not num >= len(plylst['values'].keys()):
                                name = list(plylst['values'].keys())[num]
                                loaded = tryLoad(BytesIO(zlib.decompress(plylst['values'][name])), name)
                                if not loaded:
                                    music.unload()
                                    control.withdraw()
                                    root.deiconify()
                            else:
                                num = 0
                                if data.loopPlaylist:
                                    startPlaylist()
                        else:
                            num += 1
                            if not num >= len(box['values']):
                                loaded = tryLoad(os.path.join(beginning[shortened.index(box['values'][num])], box['values'][num]))
                                if not loaded:
                                    music.unload()
                                    control.withdraw()
                                    root.deiconify()
                            else:
                                if data.loopAll:
                                    playAll()
                                else:
                                    mess.config(text = lang['message']['tracks_done'])
                                    minimized = control.state() == 'iconic'
                                    playingQueue = (False, None)
                                    music.unload()
                                    control.withdraw()
                                    if minimized:
                                        root.iconify()
                                    else:
                                        root.deiconify()
                    else:
                        trackEndEvent()
        except Exception as ex:
            if not isClosing:
                with open(os.path.join(str(dataFolder), 'WeaveSound', 'errorOutputLog.txt'), 'a') as file:
                    file.write(str(ex) + '\n')

# rewind the music and reset position
def rewind() -> None:
    music.stop()
    music.play()
    print('Music set to postition 0')

# try to load the music
def tryLoad(file: os.PathLike | BytesIO, n: str | None = None) -> bool:
    global played, trackLength
    if not isinstance(file, BytesIO):
        try:
            ext = os.path.splitext(file)[1].removeprefix('.')
        except IndexError:
            ext = ''
        if (ext not in FORMATS) and os.path.exists(file):
            ans = messagebox.askyesnocancel(lang['title']['bad_ext'], lang['popup']['bad_ext'], default = 'no', type = 'yesnocancel' if box.get() != file else 'yesno')
            if ans is False:
                return
            elif ans is None:
                root.destroy()
                return
    try:
        music.load(file)
    except (error, FileNotFoundError):
        mess.config(text = lang['message']['bad_file'])
        return False
    else:
        played = file
        trackLength = getTrackLength(file)
        if n is None:
            name.config(text = os.path.splitext(os.path.split(played)[1])[0] if len(os.path.splitext(os.path.split(played)[1])[0]) <= 26 else os.path.splitext(os.path.split(played)[1])[0][0:25] + '…')
        else: name.config(text = os.path.splitext(n)[0] if len(os.path.splitext(n)[0]) <= 26 else os.path.splitext(n)[0][0:25] + '…')
        if not playingQueue[0]:
            addRecent(str(file))
            music.play(0)
            if root.state() != 'withdrawn':
                root.withdraw()
                control.deiconify()
            mess.config(text = '')
        else:
            if playingQueue[1] == 'queue':
                try:
                    music.play(0)
                except error:
                    mess.config(text = lang['message']['bad_file'])
                else:
                    mess.config(text = '')
            elif playingQueue[1] == 'playlist':
                try:
                    music.play(0)
                except error:
                    mess.config(text = lang['message']['bad_file'])
                else:
                    mess.config(text = '')
                    if root.state() != 'withdrawn':
                        root.withdraw()
                        control.deiconify()
            else:
                try:
                    music.load(file)
                except error:
                    mess.config(text = lang['message']['bad_file'])
                else:
                    music.play()
                    if root.state() != 'withdrawn':
                        root.withdraw()
                        control.deiconify()
        return True

# refresh the music list
def refreshDir() -> None:
    global files, shortened, beginning
    files, shortened, beginning = getFiles()
    box['values'] = sorted(tuple(shortened)) if len(files) > 0 else tuple(' ')
    mess.config(text = '' if len(files) > 0 else lang['message']['empty'])
    if box.get() not in shortened:
        box.current(0)

# open a file
def openFile() -> str:
    string = ''
    for i in range(len(FORMATS)):
        string += '*.' + FORMATS[i] + ';'
    print('Waiting for user input...')
    file = filedialog.askopenfilename(title = lang['title']['open'], filetypes = [(lang['label']['compatable'], string + '*.queue'), (lang['label']['audio_file'], string.removesuffix(';')), (lang['label']['queue_file'], '*.queue')], initialdir = data.lastDir)
    if file:
        if not file.endswith('queue'):
            data.lastDir = os.path.split(file)[0]
            if os.path.split(file)[0] in data.directories:
                box.current(box['values'].index(os.path.split(file)[1]))
            tryLoad(file)
        else:
            try:
                with open(file, 'rb') as f:
                    dat = pickle.load(f)
            except (FileNotFoundError, pickle.PickleError):
                mess.config(text = lang['message']['bad_queue'])
                return
            else:
                data.queue = dat
                data.save()
                startQueue()
        print(f'File "{file}" opened')
    else:
        print('File open canceled')

# set the number of times for music to loop
def loopSet(num: int):
    data.loops = num
    data.save()
    refreshDir()
    print(f'Set property "loops" to integer value of "{num}" in data')

# save settings for queue
def queueSet(save: int, loop: int, type: str) -> None:
    if type == 'queue':
        data.saveQueue = save
        print(f'Set property "saveQueue" to integer value of "{save}" in data')
        data.loopQueue = loop
        print(f'Set property "loopQueue" to integer value of "{loop}" in data')
    else:
        data.loopPlaylist = loop
        print(f'Set property "loopPlaylist" to integer value of "{loop}" in data')
    data.save()

# set the theme
def setTheme(theme: int, resetWin: bool = True) -> None:
    data.theme = theme
    print(f'Set property "theme" to integer value of "{theme}" in data')
    if theme:
        style.theme_use(lightTheme)
        if resetWin:
            root.config(bg = 'white')
            control.config(bg = 'white')
        style.configure('TButton', background = 'white', foreground = 'black')
        style.configure("TEntry", foreground = 'black', fieldbackground = 'white''#1e1e2e')
        style.configure("TCombobox", foreground = 'black', fieldbackground = 'white', background = 'white', arrowcolor = 'black')
        style.configure("TSpinbox", foreground = 'black', fieldbackground = 'white', background = 'white', arrowcolor = 'black')
        style.configure('TScale', background = 'white')
        style.configure('TFrame', background = 'white')
        style.configure('TLabel', background = 'white', foreground = 'black')
        style.configure('TRadiobutton', background = 'white', foreground = 'black', indicatorcolor = 'white')
        style.configure('TCheckbutton', background = 'white', foreground = 'black', indicatorcolor = 'white')
        root.option_add('*TCombobox*Listbox.background', 'white')
        root.option_add('*TCombobox*Listbox.foreground', 'black')
        style.configure('Vertical.TScrollbar', background = 'white', troughcolor = 'white', arrowcolor = 'black')
        style.map('TButton', background = [('active', '#f2f2f2')])
        style.map('TCombobox', background = [('active', '!focus', '#f2f2f2')], fieldbackground = [('readonly', '#f2f2f2')])
        style.map('TSpinbox', background = [('active', '!focus', '#f2f2f2')], fieldbackground = [('readonly', '#f2f2f2')])
        style.map('Vertical.TScrollbar', background = [('active', '!focus', '#f2f2f2')])
        style.configure('TNotebook', background = 'white')
        style.configure('TNotebook.Tab', background = 'white', foreground = 'black')
        style.map('TNotebook.Tab', background = [('active', '!focus', '#f2f2f2')])
        style.map('TScale', background = [('active', '!focus', '#f2f2f2')])
        style.map('TRadiobutton', background = [('active', '!focus', 'white')], indicatorcolor = [('active', '#f2f2f2')])
        style.map('TCheckbutton', background = [('active', '!focus', 'white')], indicatorcolor = [('active', '#f2f2f2')])
    else:
        style.theme_use('alt')
        if resetWin:
            root.config(bg = '#1e1e2e')
            control.config(bg = '#1e1e2e')
        style.configure('TButton', background = '#1e1e2e', foreground = 'white', focuscolor = 'gray')
        style.map('TButton', background = [('active', '#2a2a3a')])
        style.map('TCombobox', background = [('active', '!focus', '#2a2a3a')], fieldbackground = [('readonly', '#2a2a3a')])
        style.map('TSpinbox', background = [('active', '!focus', '#2a2a3a')], fieldbackground = [('readonly', '#2a2a3a')])
        style.map('Vertical.TScrollbar', background = [('active', '!focus', '#2a2a3a')])
        style.configure('TEntry', foreground = 'white', fieldbackground = '#1e1e2e', insertcolor = 'white')
        style.configure('TCombobox', foreground = 'white', fieldbackground = '#1e1e2e', background = '#1e1e2e', arrowcolor = 'white', insertcolor = 'white')
        style.configure('TSpinbox', foreground = 'white', fieldbackground = '#1e1e2e', background = '#1e1e2e', arrowcolor = 'white', insertcolor = 'white')
        style.configure('TScale', background = '#1e1e2e')
        style.map('TScale', background = [('active', '!focus', '#2a2a3a')])
        style.configure('TFrame', background = '#1e1e2e')
        style.configure('TLabel', background = '#1e1e2e', foreground = 'white')
        style.configure('TRadiobutton', background = '#1e1e2e', foreground = 'white', indicatorcolor = '#1e1e2e', focuscolor = 'gray')
        style.configure('TCheckbutton', background = '#1e1e2e', foreground = 'white', indicatorcolor = '#1e1e2e', focuscolor = 'gray')
        root.option_add('*TCombobox*Listbox.background', '#1e1e2e')
        root.option_add('*TCombobox*Listbox.foreground', 'white')
        style.configure('Vertical.TScrollbar', background = '#1e1e2e', troughcolor = '#1e1e2e', arrowcolor = 'white')
        style.configure('TNotebook', background = '#1e1e2e')
        style.configure('TNotebook.Tab', background = '#1e1e2e', foreground = 'white')
        style.map('TNotebook.Tab', background = [('active', '!focus', '#2a2a3a')])
        style.map('TRadiobutton', background = [('active', '!focus', '#1e1e2e')], indicatorcolor = [('active', '#2a2a3a')])
        style.map('TCheckbutton', background = [('active', '!focus', '#1e1e2e')], indicatorcolor = [('active', '#2a2a3a')])
    data.save()

# functions to save settings
def after(value: int) -> None:
    data.startNext = value
    print(f'Set property "startNext" to integer value of "{value}" in data')

def wrapSet(value: int) -> None:
    data.wrap = value
    print(f'Set property "wrap" to integer value of "{value}" in data')

def lenSet(value: int) -> None:
    data.getLen = value
    print(f'Set property "getLen" to integer value of "{value}" in data')

def playlistSet(num: int) -> None:
    data.playlist = num
    print(f'Set property "getLen" to integer value of "{num}" in data')

# change the settings
def settings() -> None:
    global data
    # set key binding
    pauseKey = data.pause
    muteKey = data.mute
    dwnKey = data.voldown
    upKey = data.volup
    def getKey(current: str, binding: str) -> str | None:
        nonlocal pauseKey, muteKey, dwnKey, upKey
        # get a keysym
        def getSym(event: tk.Event) -> None:
            if (binding != 'pause' and event.keysym == data.pause) or (binding != 'mute' and event.keysym == data.mute) or (binding != 'volup' and event.keysym == data.volup) or (binding != 'voldown' and event.keysym == data.voldown) or event.keysym == 'Pause' or event.keycode == 179 or event.keysym == 'equal' or event.keysym == 'minus':
                mess.config(text = lang['message']['dupe_key'])
                return
            else:
                mess.config(text = '')
                match binding:
                    case 'pause':
                        data.pause = event.keysym
                        pauseLbl.config(text = f'Pause: {data.pause}')
                    case 'mute':
                        data.mute = event.keysym
                        muteLbl.config(text = f'Mute: {data.mute}')
                    case 'volup':
                        data.volup = event.keysym
                        upLbl.config(text = f'Volume Up: {data.volup}')
                    case 'voldown':
                        data.voldown = event.keysym
                        downLbl.config(text = f'Volume Down: {data.voldown}')
                data.save()
                prompt.destroy()

        prompt = tk.Toplevel(setWin, takefocus = True)
        prompt.config(bg = 'white' if data.theme else '#1e1e2e')
        prompt.focus()
        prompt.resizable(False, False)
        prompt.grab_set()
        prompt.overrideredirect(True)
        prompt.geometry(f'200x200+{setWin.winfo_x()}+{setWin.winfo_y()}')
        prompt.bind('<Key>', lambda event: [getSym(event)])
        ttk.Label(prompt, text = lang['label']['current_key'].format(current)).pack()
        mess = ttk.Label(prompt)
        mess.pack()
        cancel = ttk.Button(prompt, text = 'cancel', cursor = 'hand2', command = prompt.destroy)
        cancel.pack()

    # choose a new default directory
    def chooseDir() -> None:
        folder = filedialog.askdirectory(title = lang['title']['add_dir'], initialdir = data.lastDir)
        if folder:
            data.lastDir = os.path.split(folder)[0]
            data.directories.append(folder)
            data.save()
            refreshDir()

    def manageDirs(event = None):
        manager = tk.Toplevel(setWin, takefocus = True)
        manager.config(bg = 'white' if data.theme else '#1e1e2e')
        manager.focus()
        # manager.grab_set()

        # update the list box with the new values
        def updateListbox():
            listbox.delete(0, tk.END)
            for item in data.directories:
                listbox.insert(tk.END, item)

        manager.resizable(False, False)
        manager.title(f'{lang["title"]["dir_manager"]} - {lang["title"]["main"]}')
        manager.geometry(f'+{setWin.winfo_x()}+{setWin.winfo_y()}')
        listbox = tk.Listbox(manager, height = 4, width = 50, bg = 'white' if data.theme else '#1e1e2e', fg = 'black' if data.theme else 'white')
        listbox.pack()
        updateListbox()
        
        removeButton = ttk.Button(manager, text=lang['button']['remove'],
                           command=lambda: [data.directories.remove(data.directories[listbox.curselection()[0]]) if listbox.curselection() else None, updateListbox(), dirLabel.config(text = '{0}:\n{1}'.format(lang["label"]["search_dirs"], "\n".join(data.directories))), data.save(), refreshDir()], cursor='hand2')
        removeButton.pack()
        openButton = ttk.Button(manager, text=lang['button']['open'],
                           command=lambda: openLocation(data.directories[listbox.curselection()[0]]) if listbox.curselection() else None, cursor='hand2')
        openButton.pack()
        done = ttk.Button(manager, text = lang['button']['done'], command = manager.destroy, cursor = 'hand2')
        done.pack()
        Hovertip(done, lang['tooltip']['done_dirs'])

    def switchFrame() -> None:
        if var9.get():
            loopFrame.pack_forget()
            nextFrame.pack()
        else:
            nextFrame.pack_forget()
            loopFrame.pack()

    setWin = tk.Toplevel(root)
    setWin.config(bg = 'white' if data.theme else '#1e1e2e')
    setWin.resizable(False, False)
    setWin.grab_set()
    setWin.title(f'{lang["title"]["settings"]} - {lang["title"]["main"]}')
    setWin.focus()
    setWin.geometry(f'+{root.winfo_x()}+{root.winfo_y()}')
    # create a notebook
    notebook = ttk.Notebook(setWin)
    notebook.pack(pady = 10, expand = True)

    # create frames
    frame1 = ttk.Frame(notebook, width = 400, height = 280)
    frame2 = ttk.Frame(notebook, width = 400, height = 280)
    frame4 = ttk.Frame(notebook, width = 400, height = 280)
    frame5 = ttk.Frame(notebook, width = 400, height = 280)
    frame9 = ttk.Frame(notebook, width = 400, height = 280)
    frame6 = ttk.Frame(notebook, width = 400, height = 280)
    frame8 = ttk.Frame(notebook, width = 400, height = 280)
    frame10 = ttk.Frame(notebook, width = 400, height = 280)

    frame1.pack(fill = 'both', expand = True)
    frame2.pack(fill = 'both', expand = True)
    frame4.pack(fill = 'both', expand = True)
    frame5.pack(fill = 'both', expand = True)
    frame9.pack(fill = 'both', expand = True)
    frame6.pack(fill = 'both', expand = True)
    frame8.pack(fill = 'both', expand = True)
    frame10.pack(fill = 'both', expand = True)

    # add frames to notebook
    notebook.add(frame1, text = lang['tab']['dir'])
    notebook.add(frame2, text = lang['tab']['track_end'])
    notebook.add(frame4, text = lang['tab']['key_bindings'])
    notebook.add(frame5, text = lang['tab']['queue'])
    notebook.add(frame9, text = lang['tab']['playlist'])
    notebook.add(frame6, text = lang['tab']['play_all'])
    notebook.add(frame8, text = lang['tab']['theme'])
    notebook.add(frame10, text = lang['tab']['track_length'])

    # directory
    dirLabel = ttk.Label(frame1, text = '{0}:\n{1}'.format(lang["label"]["search_dirs"], '\n'.join(data.directories)), cursor = 'hand2')
    dirLabel.pack()
    dirLabel.bind('<Button-1>', manageDirs)
    changeDir = ttk.Button(frame1, text = lang['button']['add'], command = lambda: [chooseDir(), dirLabel.config(text = '{0}:\n{1}'.format(lang["label"]["search_dirs"], '\n'.join(data.directories)))], cursor = 'hand2')
    changeDir.pack()
    dataLabel = ttk.Label(frame1, text = f'{lang["label"]["data_folder"]}:\n{os.path.join(str(dataFolder), "WeaveSound")}', cursor = 'hand2')
    dataLabel.pack()
    dataLabel.bind('<Button-1>', lambda event: openLocation(os.path.join(str(dataFolder), 'WeaveSound')))

    # after track ending
    var9 = tk.IntVar(value = data.startNext)
    loop = ttk.Radiobutton(frame2, text = lang['radiobutton']['loop'], variable = var9, value = 0, command = switchFrame)
    loop.pack()
    next = ttk.Radiobutton(frame2, text = lang['radiobutton']['next'], variable = var9, value = 1, command = switchFrame)
    next.pack()
    loopFrame = ttk.Frame(frame2)
    nextFrame = ttk.Frame(frame2)
    switchFrame()
    var1 = tk.IntVar()
    ttk.Label(loopFrame, text = lang['label']['loop']).pack()
    infinite = ttk.Radiobutton(loopFrame, text = lang['radiobutton']['loop_infinite'], variable = var1, value = 0, command = lambda: [loopSet(-1), number.config(state = 'disabled')])
    infinite.pack()
    zero = ttk.Radiobutton(loopFrame, text = lang['radiobutton']['loop_zero'], variable = var1, value = 1, command = lambda: [loopSet(0), number.config(state = 'disabled')])
    zero.pack()
    custom = ttk.Radiobutton(loopFrame, text = lang['radiobutton']['loop_custom'], variable = var1, value = 2, command = lambda: [loopSet(number.get()), number.config(state = 'readonly')])
    number = ttk.Spinbox(loopFrame, from_ = 0, to = 15, state = 'readonly' if var1.get() == 2 else 'disabled')
    number.set(0)
    if data.loops == 0:
        var1.set(1)
    elif data.loops > 0:
        var1.set(2)
        number.config(state = 'readonly')
        number.set(data.loops - 1)
    custom.pack()
    number.pack()
    var10 = tk.IntVar(value = data.wrap)
    wrap = ttk.Checkbutton(nextFrame, text = lang['checkbox']['wrap'], variable = var10)
    wrap.pack()

    # key bindings
    pauseLbl = ttk.Label(frame4, text = f'{lang["label"]["pause"]}: {data.pause}')
    pauseLbl.pack()
    pauseBtn = ttk.Button(frame4, text = lang['button']['change'], command = lambda: getKey(data.pause, 'pause'), cursor = 'hand2')
    pauseBtn.pack()
    muteLbl = ttk.Label(frame4, text = f'{lang["label"]["mute"]}: {data.mute}')
    muteLbl.pack()
    muteBtn = ttk.Button(frame4, text = lang["button"]["change"], command = lambda: getKey(data.mute, 'mute'), cursor = 'hand2')
    muteBtn.pack()
    upLbl = ttk.Label(frame4, text = f'{lang["label"]["volume_up"]}: {data.volup}')
    upLbl.pack()
    upBtn = ttk.Button(frame4, text = lang["button"]["change"], command = lambda: getKey(data.volup, 'volup'), cursor = 'hand2')
    upBtn.pack()
    downLbl = ttk.Label(frame4, text = f'{lang["label"]["volume_down"]}: {data.voldown}')
    downLbl.pack()
    downBtn = ttk.Button(frame4, text = lang['button']['change'], command = lambda: getKey(data.voldown, 'voldown'), cursor = 'hand2')
    downBtn.pack()

    # queue
    var3 = tk.IntVar(value = data.saveQueue)
    save = ttk.Checkbutton(frame5, text = lang['checkbox']['save_queue'], variable = var3)
    save.pack()
    var4 = tk.IntVar(value = data.loopQueue)
    loop = ttk.Checkbutton(frame5, text = lang['checkbox']['loop_queue'], variable = var4)
    loop.pack()

    # playlist
    var8 = tk.IntVar(value = data.loopPlaylist)
    loop = ttk.Checkbutton(frame9, text = 'Loop playlist', variable = var8)
    loop.pack()
    ttk.Label(frame9, text = lang['label']['playlist']).pack()
    var12 = tk.IntVar(value = data.playlist)
    ask = ttk.Radiobutton(frame9, text = lang['radiobutton']['ask'], value = 0, variable = var12)
    ask.pack()
    play = ttk.Radiobutton(frame9, text = lang['button']['play'], value = 1, variable = var12)
    play.pack()
    extract = ttk.Radiobutton(frame9, text = lang['button']['make_queue'], value = 2, variable = var12)
    extract.pack()

    # play all
    var6 = tk.IntVar(value = data.loopAll)
    loop1 = ttk.Checkbutton(frame6, text = lang['checkbox']['loop_play_all'], variable = var6)
    loop1.pack()

    # theme
    ttk.Label(frame8, text = lang['label']['theme']).pack()
    var7 = tk.IntVar(value = data.theme)
    dark = ttk.Radiobutton(frame8, text = lang['radiobutton']['dark'], value = 0, variable = var7)
    dark.pack()
    light = ttk.Radiobutton(frame8, text = lang['radiobutton']['light'], value = 1, variable = var7)
    light.pack()

    # get track length
    ttk.Label(frame10, text = lang['label']['track_length']).pack()
    var11 = tk.IntVar(value = data.getLen)
    length = ttk.Checkbutton(frame10, text = lang['checkbox']['track_length'], variable = var11)
    length.pack()

    done = ttk.Button(setWin, text = lang['button']['done'], command = lambda: [lenSet(var11.get()), loopSet(int(number.get())) if var1.get() == 2 else ..., queueSet(var3.get(), var4.get(), 'queue'), queueSet(var8.get(), None, 'queue'), pausetip.change(f'pause/play ({data.pause.lower()})'), mutetip.change(f'mute/unmute ({data.mute.lower()})'), uptip.change(f'volume up ({data.volup.lower()})'), dwntip.change(f'volume down ({data.voldown.lower()})'), setTheme(var7.get()), playlistSet(var12.get()), setWin.destroy(), after(var9.get()), wrapSet(var10.get())], cursor = 'hand2')
    done.pack()
    Hovertip(done, lang['tooltip']['done_settings'])
    setWin.mainloop()

# filters
def filterWin() -> None:
    def applyFilters(event = None) -> None:
        global special, filterDict
        special = shortened.copy()
        filterDict = {'types': {'midi': midi.get(), 'wav': wav.get(), 'ogg': ogg.get(), 'flac': flac.get(), 'opus': opus.get(), 'aiff': aiff.get(), 'mp3': mp3.get(), 'mid': midi.get(), 'aif': aiff.get(), 'mod': mod.get(), 'xm': xm.get()}, 'contains': contains.get(), 'nocontains': nocontains.get(), 'begins': begins.get(), 'nobegins': nobegins.get(), 'ends': ends.get(), 'noends': noends.get(), 'inqueue': queueVar.get(), 'folder': {'include': include.get(0, tk.END), 'exclude': exclude.get(0, tk.END)}}
        
        # Filter by file type
        special = [item for item in special if any(item.lower().endswith(extension) for extension, value in filterDict['types'].items() if value)]
        
        # Filter by contains
        if len(filterDict['contains']) > 0:
            contains_filter = filterDict['contains'].lower()
            special = [item for item in special if contains_filter in os.path.splitext(item)[0].lower()]
        
        # Filter by does not contain
        if len(filterDict['nocontains']) > 0:
            nocontains_filter = filterDict['nocontains'].lower()
            special = [item for item in special if nocontains_filter not in os.path.splitext(item)[0].lower()]
        
        # Filter by begins with
        if len(filterDict['begins']) > 0:
            begins_filter = filterDict['begins'].lower()
            special = [item for item in special if os.path.splitext(item)[0].lower().startswith(begins_filter)]
        
        # Filter by does not begin with
        if len(filterDict['nobegins']) > 0:
            nobegins_filter = filterDict['nobegins'].lower()
            special = [item for item in special if not os.path.splitext(item)[0].lower().startswith(nobegins_filter)]
        
        # Filter by ends with
        if len(filterDict['ends']) > 0:
            ends_filter = filterDict['ends'].lower()
            special = [item for item in special if os.path.splitext(item.lower())[0].endswith(ends_filter)]
        
        # Filter by does not end with
        if len(filterDict['noends']) > 0:
            noends_filter = filterDict['noends'].lower()
            special = [item for item in special if not os.path.splitext(item.lower())[0].endswith(noends_filter)]

        if filterDict['inqueue']:
            queue = []
            for i in data.queue.queue:
                queue.append(os.path.split(i)[1])
            special = [item for item in special if item in queue]

        including = []
        for i in special:
            for j in filterDict['folder']['include']:
                if i in os.listdir(j):
                    including.append(i)
        special = including

        # set the selection combobox to special
        box['values'] = sorted(tuple(special)) if len(special) > 0 else tuple(' ')
        if box.get() not in special:
            box.current(0)

    # clear filters
    def clearFilters() -> None:
        global filterDict
        special.clear()
        refreshDir()
        box['values'] = sorted(tuple(shortened)) if len(files) > 0 else tuple(' ')
        if box.get() not in shortened:
            box.current(0)
        filterDict = {'types': {'midi': 1, 'wav': 1, 'ogg': 1, 'flac': 1, 'opus': 1, 'aiff': 1, 'mp3': 1, 'mid': 1, 'aif': 1, 'mod': 1, 'xm': 1}, 'contains': '', 'nocontains': '', 'begins': '', 'nobegins': '', 'ends': '', 'noends': '', 'inqueue': 0, 'folder': {'include': data.directories, 'exclude': []}}
        midi.set(1)
        wav.set(1)
        mp3.set(1)
        ogg.set(1)
        flac.set(1)
        opus.set(1)
        aiff.set(1)
        mod.set(1)
        xm.set(1)
        contains.delete(0, 'end')
        nocontains.delete(0, 'end')
        begins.delete(0, 'end')
        nobegins.delete(0, 'end')
        ends.delete(0, 'end')
        noends.delete(0, 'end')
        queueVar.set(0)
        exclude.delete(0, tk.END)
        include.delete(0, tk.END)
        for i in data.directories:
            include.insert(0, i)

    def moveItem(excluding: bool = False) -> None:
        if excluding:
            if include.curselection():
                index = include.curselection()[0]
                exclude.insert(tk.END, include.get(index))
                include.delete(index)
        else:
            if exclude.curselection():
                index = exclude.curselection()[0]
                include.insert(tk.END, exclude.get(index))
                exclude.delete(index)

    # file type
    filter = tk.Toplevel(root)
    filter.config(bg = 'white' if data.theme else '#1e1e2e')
    filter.title('Filters - WeaveSound')
    filter.grab_set()
    filter.resizable(False, False)
    filter.geometry(f'+{root.winfo_x()}+{root.winfo_y()}')
    filters = ttk.Notebook(filter)
    filters.pack(pady = 10, expand = True)
    extension = ttk.Frame(filters)
    extension.pack(fill = 'both', expand = True)
    filters.add(extension, text = 'File Type')
    midi = tk.IntVar(value = filterDict['types']['midi'])
    wav = tk.IntVar(value = filterDict['types']['wav'])
    mp3 = tk.IntVar(value = filterDict['types']['mp3'])
    ogg = tk.IntVar(value = filterDict['types']['ogg'])
    flac = tk.IntVar(value = filterDict['types']['flac'])
    opus = tk.IntVar(value = filterDict['types']['opus'])
    aiff = tk.IntVar(value = filterDict['types']['aiff'])
    mod = tk.IntVar(value = filterDict['types']['mod'])
    xm = tk.IntVar(value = filterDict['types']['xm'])
    c1 = ttk.Checkbutton(extension, text = lang['checkbox']['midi'], variable = midi, onvalue = 1, offvalue = 0)
    c1.pack(anchor = tk.W)
    c2 = ttk.Checkbutton(extension, text = lang['checkbox']['wav'], variable = wav, onvalue = 1, offvalue = 0)
    c2.pack(anchor = tk.W)
    c3 = ttk.Checkbutton(extension, text = lang['checkbox']['mp3'], variable = mp3, onvalue = 1, offvalue = 0)
    c3.pack(anchor = tk.W)
    c4 = ttk.Checkbutton(extension, text = lang['checkbox']['ogg'], variable = ogg, onvalue = 1, offvalue = 0)
    c4.pack(anchor = tk.W)
    c5 = ttk.Checkbutton(extension, text = lang['checkbox']['flac'], variable = flac, onvalue = 1, offvalue = 0)
    c5.pack(anchor = tk.W)
    c6 = ttk.Checkbutton(extension, text = lang['checkbox']['opus'], variable = opus, onvalue = 1, offvalue = 0)
    c6.pack(anchor = tk.W)
    c7 = ttk.Checkbutton(extension, text = lang['checkbox']['aiff'], variable = aiff, onvalue = 1, offvalue = 0)
    c7.pack(anchor = tk.W)
    c8 = ttk.Checkbutton(extension, text = lang['checkbox']['mod'], variable = mod, onvalue = 1, offvalue = 0)
    c8.pack(anchor = tk.W)
    c9 = ttk.Checkbutton(extension, text = lang['checkbox']['xm'], variable = xm, onvalue = 1, offvalue = 0)
    c9.pack(anchor = tk.W)

    # contains
    has = ttk.Frame(filters)
    ttk.Label(has, text = lang['label']['contains']).pack()
    has.pack()
    contains = ttk.Entry(has)
    contains.insert(0, filterDict['contains'])
    contains.pack(fill = 'both')
    filters.add(has, text = lang['tab']['contains'])
    contains.bind('<Return>', applyFilters)

    # does not contain
    nohas = ttk.Frame(filters)
    ttk.Label(nohas, text = lang['label']['no_contains']).pack()
    nohas.pack()
    nocontains = ttk.Entry(nohas)
    nocontains.insert(0, filterDict['nocontains'])
    nocontains.pack(fill = 'both')
    filters.add(nohas, text = lang['tab']['no_contains'])
    nocontains.bind('<Return>', applyFilters)

    # begins with
    start = ttk.Frame(filters)
    ttk.Label(start, text = lang['label']['begins_with']).pack()
    start.pack()
    begins = ttk.Entry(start)
    begins.insert(0, filterDict['begins'])
    begins.pack(fill = 'both')
    filters.add(start, text = lang['tab']['begins_with'])
    begins.bind('<Return>', applyFilters)
    
    # does not begin with
    nostart = ttk.Frame(filters)
    ttk.Label(nostart, text = lang['label']['no_begins_with']).pack()
    nostart.pack()
    nobegins = ttk.Entry(nostart)
    nobegins.insert(0, filterDict['nobegins'])
    nobegins.pack(fill = 'both')
    filters.add(nostart, text = lang['tab']['no_begins_with'])
    nobegins.bind('<Return>', applyFilters)

    # ends with
    end = ttk.Frame(filters)
    ttk.Label(end, text = lang['label']['ends_with']).pack()
    end.pack()
    ends = ttk.Entry(end)
    ends.insert(0, filterDict['ends'])
    ends.pack(fill = 'both')
    filters.add(end, text = lang['tab']['ends_with'])
    ends.bind('<Return>', applyFilters)

    # does not end with
    noend = ttk.Frame(filters)
    ttk.Label(noend, text = lang['label']['no_ends_with']).pack()
    noend.pack()
    noends = ttk.Entry(noend)
    noends.insert(0, filterDict['noends'])
    filters.add(noend, text = lang['tab']['no_ends_with'])
    noends.pack(fill = 'both')
    noends.bind('<Return>', applyFilters)

    # in queue
    inqueue = ttk.Frame(filters)
    queueVar = tk.IntVar(value = filterDict['inqueue'])
    inqueue_ = ttk.Checkbutton(inqueue, text = lang['checkbox']['in_queue'], variable = queueVar, onvalue = 1, offvalue = 0)
    inqueue_.pack()
    inqueue.pack()
    filters.add(inqueue, text = lang['tab']['in_queue'])

    # by folder
    folders = ttk.Frame(filters)
    folders.pack()
    foldersIn = ttk.Frame(folders)
    foldersIn.pack(side = tk.LEFT)
    ttk.Label(foldersIn, text = 'Included').pack()
    include = tk.Listbox(foldersIn, bg = 'white' if data.theme else '#1e1e2e', fg = 'black' if data.theme else 'white', width = 50)
    include.pack()
    for i in filterDict['folder']['include']:
        include.insert(tk.END, i)
    moveout = ttk.Button(foldersIn, text = 'Exclude selected folder', command = lambda: moveItem(True), cursor = 'hand2')
    moveout.pack()
    foldersEx = ttk.Frame(folders)
    foldersEx.pack(side = tk.RIGHT)
    ttk.Label(foldersEx, text = 'Excluded').pack()
    exclude = tk.Listbox(foldersEx, bg = 'white' if data.theme else '#1e1e2e', fg = 'black' if data.theme else 'white', width = 50)
    exclude.pack()
    movein = ttk.Button(foldersEx, text = 'Include selected folder', command = moveItem, cursor = 'hand2')
    movein.pack()

    for i in filterDict['folder']['exclude']:
        exclude.insert(tk.END, i)
    filters.add(folders, text = 'Folders')

    apply = ttk.Button(filter, text = lang['button']['apply_filters'], cursor = 'hand2', command = applyFilters)
    apply.pack()
    Hovertip(apply, lang['tooltip']['apply_filters'])

    clear = ttk.Button(filter, text = lang['button']['clear_filters'], cursor = 'hand2', command = clearFilters)
    clear.pack()
    Hovertip(clear, lang['tooltip']['clear_filters'])

    done = ttk.Button(filter, text = lang['button']['done'], command = filter.destroy, cursor = 'hand2')
    done.pack()
    Hovertip(done, lang['tooltip']['done_filters'])
    
    filter.mainloop()

# handle key presses
def onPress(event: tk.Event) -> None:
    print('Getting keypress...')
    if event.keycode == 179 or event.keysym == data.pause:
        print(f'Pause key pressed: {event.keysym}')
        pauseplay()
    elif event.keysym == data.volup:
        print(f'Volume up key pressed: {event.keysym}')
        up()
    elif event.keysym == data.voldown:
        print(f'Volume down key pressed: {event.keysym}')
        down()
    elif event.keysym == data.mute:
        print(f'Mute key pressed: {event.keysym}')
        mute()
    else:
        print(f"Keypress doesn't match mappings: {event.keysym}")

# set playingQueue var to false
def setPlaying() -> None:
    global playingQueue
    playingQueue = (False, 'none')

# start playing the queue
def startQueue(first: bool = True) -> None:
    global playingQueue, num
    num = 0
    if len(data.queue.queue) < 1:
        mess.config(text = lang['message']['empty_queue'])
    else:
        playingQueue = (True, 'queue')
        loaded = tryLoad(data.queue.queue[num])
        if loaded and first:
            control.deiconify()
            root.withdraw()
    print('Started queue')

# show the license in a window
def license() -> None:
    print('Displaying license window...')
    
    # Create a new window for the license
    licenseWin = tk.Toplevel(root, takefocus=True)
    licenseWin.config(bg='white' if data.theme else '#1e1e2e')
    licenseWin.title(f'{lang["title"]["eula"]} - {lang["title"]["main"]}')
    licenseWin.focus()
    licenseWin.geometry(f'805x550+{root.winfo_x()}+{root.winfo_y()}')

    # Frame to hold the text widget and scrollbar
    textFrame = ttk.Frame(licenseWin)
    textFrame.pack(fill='both', expand=True, padx=10, pady=10)

    # Text widget to display the license
    licenseText = tk.Text(
        textFrame, wrap='word', bg='white' if data.theme else '#1e1e2e',
        fg='black' if data.theme else 'white', font='Helvetica 12', state='normal'
    )
    licenseText.insert('1.0', LICENSE)  # Insert license text
    licenseText.config(state='disabled')  # Make it read-only
    licenseText.pack(side='left', fill='both', expand=True)

    # Scrollbar for the text widget
    textScrollbar = ttk.Scrollbar(textFrame, orient='vertical', command=licenseText.yview)
    licenseText.config(yscrollcommand=textScrollbar.set)
    textScrollbar.pack(side='right', fill='y')

    # Additional information section
    ttk.Label(
        licenseWin, text='Websites for more info on this topic:',
        font='Helvetica 15', background='white' if data.theme else '#1e1e2e'
    ).pack(pady=(10, 5))

    # Frame to hold hyperlinks
    linkFrame = ttk.Frame(licenseWin)
    linkFrame.pack()

    # Hyperlinks
    Hyperlink(
        linkFrame, text='GNU GPL License V3 (Main program)',
        url='https://www.gnu.org/licenses/gpl-3.0.en.html', cursor='hand2',
        bg='white' if data.theme else '#1e1e2e'
    ).pack()

    Hyperlink(
        linkFrame, text='GNU LGPL License V2.1 (PyGame library)',
        url='https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html', cursor='hand2',
        bg='white' if data.theme else '#1e1e2e'
    ).pack()

# show the credits in a window
def credits() -> None:
    print('Displaying credits window...')
    creditWin = tk.Toplevel(root, takefocus=True)
    creditWin.config(bg='white' if data.theme else '#1e1e2e')
    creditWin.title(f'{lang["title"]["credits"]} - {lang["title"]["main"]}')
    creditWin.focus()
    creditWin.geometry(f'400x400+{root.winfo_x()}+{root.winfo_y()}')

    # Center container frame
    frame = ttk.Frame(creditWin)
    frame.grid(row=0, column=0, padx=20, pady=20)
    
    bg_color = 'white' if data.theme else '#1e1e2e'

    # Author section
    author = ttk.Label(frame, text='Authored by:', justify='center', background=bg_color)
    author.grid(row=0, column=0, sticky='w', pady=5)
    Hyperlink(frame, text='• Luke Moyer', url='https://github.com/DudenessBoy', bg=bg_color,
              justify='left', cursor='hand2').grid(row=1, column=0, sticky='w', padx=20)

    # Thanks section
    thanks = ttk.Label(frame, text='Special thanks to:', justify='center', background=bg_color)
    thanks.grid(row=2, column=0, sticky='w', pady=15)
    contributors = [
        ('• Jordan Russel Software', 'https://jrsoftware.org'),
        ('• PyGame', 'https://www.pygame.org'),
        ('• PyInstaller', 'https://pyinstaller.org'),
        ('• Python Software Foundation', 'https://www.python.org'),
        ('• Free Software Foundation', 'https://www.fsf.org')
    ]

    for idx, (name, url) in enumerate(contributors):
        Hyperlink(frame, text=name, url=url, bg=bg_color, justify='left', cursor='hand2').grid(row=3 + idx, column=0, sticky='w', padx=20)

# show info about the program
def about() -> None:
    print('Displaying about window...')
    aboutWin = tk.Toplevel(root, takefocus = True)
    aboutWin.config(bg = 'white' if data.theme else '#1e1e2e')
    aboutWin.title(f'{lang["title"]["about"]} - {lang["title"]["main"]}')
    aboutWin.focus()
    aboutWin.geometry(f'800x550+{root.winfo_x()}+{root.winfo_y()}')
    about = ttk.Label(aboutWin, text = 'WeaveSound is a lightweight music player designed with simplicity and efficiency at its core. It features a compact and\nuser-friendly interface, making it ideal for users who want quick access to their music without unnecessary distractions.\nFocused on delivering a streamlined listening experience, WeaveSound prioritizes essential features, ensuring smooth\nperformance even on systems with limited resources.',
    justify = 'left')
    about.pack()
    Hyperlink(aboutWin, text = 'Github repository', url = 'https://github.com/DudenessBoy/WeaveSound', bg = 'white' if data.theme else '#1e1e2e', cursor = 'hand2').pack()
    Hyperlink(aboutWin, text = 'Report bugs/suggest features', url = 'https://github.com/DudenessBoy/WeaveSound/issues', bg = 'white' if data.theme else '#1e1e2e', cursor = 'hand2').pack()

# load a queue
def loadQueue() -> None:
    print('Waiting for user input...')
    raw = filedialog.askopenfilename(title = lang['title']['open_queue'], filetypes = [(lang['label']['queue_file'], '*.queue')], initialdir = os.path.join(str(dataFolder), 'WeaveSound', 'queues'))
    if len(raw) > 0:
        print(f'Done. File: {raw}')
        try:
            with open(raw, 'rb') as f:
                file = pickle.load(f)
        except (TypeError, pickle.PickleError):
            mess.config(text = lang['message']['bad_queue'])
            return
        if not isinstance(file, Queue):
            mess.config(text = lang['message']['bad_queue'])
        else:
            data.queue = file
            data.save()
    else:
        print('Done. User cancelled')

# play all tracks in the default dir
def playAll() -> None:
    global num, playingQueue
    num = 0
    if len(box['values']) > 0:
        playingQueue = [True, 'all']
        tryLoad(os.path.join(beginning[shortened.index(box['values'][0])], box['values'][0]))
    else:
        mess.config(lang['message']['play_none'])
    print('Play all event started')

# find feature
def findWindow(event = None) -> None:
    def close() -> None:
        print('Closing find window...')
        global findWord
        findWord = findEntry.get()
        findWin.destroy()
    print('Opening find window...')
    findWin = tk.Toplevel(root)
    findWin.config(bg = 'white' if data.theme else '#1e1e2e')
    findWin.focus()
    findWin.grab_set()
    findWin.overrideredirect(True)
    # Calculate the center coordinates of the main window
    root.update_idletasks()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    x_center = root.winfo_rootx() + root_width // 2
    y_center = root.winfo_rooty() + root_height // 2
    
    # Calculate the offset to position the Toplevel window in the center of the main window
    findWin_width = findWin.winfo_width()
    findWin_height = findWin.winfo_height()
    x_offset = (x_center - findWin_width // 2 ) - 100
    y_offset = (y_center - findWin_height // 2) + 20
    
    findWin.geometry(f"+{x_offset}+{y_offset}")
    findEntry = ttk.Entry(findWin, width = 50)
    findEntry.pack(side = 'left')
    findEntry.focus()
    findEntry.insert(0, findWord)
    findEntry.select_range(0, tk.END)
    nextBtn = ttk.Button(findWin, text = '↓', command = lambda: findNext(findEntry.get()), width = 5, takefocus = False)
    nextBtn.pack(side = 'left')
    Hovertip(nextBtn, lang['tooltip']['find_next'])
    prevBtn = ttk.Button(findWin, text = '↑', command = lambda: findPrev(findEntry.get()), width = 5, takefocus = False)
    prevBtn.pack(side = 'left')
    Hovertip(prevBtn, lang['tooltip']['find_prev'])
    closeBtn = ttk.Button(findWin, text = '×', command = close, width = 5, takefocus = False)
    closeBtn.pack(side = 'left')
    Hovertip(closeBtn, 'close')
    findWin.bind('<Return>', lambda event: findNext(findEntry.get()))
    findWin.bind('<Down>', lambda event: findNext(findEntry.get()))
    findWin.bind('<Up>', lambda event: findPrev(findEntry.get()))

# find next
def findNext(searchKey: str):
    print(f'Searching for next instance of {searchKey}')
    if searchKey:
        items = box["values"]
        current_index = box.current()
        if current_index is None:
            current_index = -1
        found = False
        for i in range(current_index + 1, len(items)):
            if searchKey.lower() in items[i].lower():
                box.current(i)
                found = True
                print('Search succesful')
                break
            else:
                print(f'No instance of {searchKey} found. Searching again from top')
        if not found:
            for i in range(len(items)):
                if searchKey.lower() in items[i].lower():
                    box.current(i)
                    print('Search succesful')
                    break
                else:
                    print(f'No instance of {searchKey} found')

# find previous
def findPrev(searchKey: str):
    print(f'Searching for previous instance of {searchKey}')
    if searchKey:
        items = box["values"]
        current_index = box.current()
        if current_index is None:
            current_index = len(items)
        found = False
        for i in range(current_index - 1, -1, -1):
            if searchKey.lower() in items[i].lower():
                box.current(i)
                found = True
                print('Search succesful')
                break
        else:
            print(f'No instance of {searchKey} found. Searching again from bottom')
        if not found:
            for i in range(len(items) - 1, -1, -1):
                if searchKey.lower() in items[i].lower():
                    box.current(i)
                    print('Search succesful')
                    break
            else:
                print(f'No instance of {searchKey} found')

# calculate where to place root
def calculateWindowPosition(offsetX: int, offsetY: int):
    screenWidth = root.winfo_screenwidth()
    screenHeight = root.winfo_screenheight()
    
    # Calculate the position near the top-left corner of the screen
    x = offsetX
    y = offsetY
    
    return f"+{x}+{y}"

# previous track
def prevTrack() -> None:
    global num, played
    print('Skipping to previous tracks')
    if not playingQueue[0]:
        split = os.path.split(played)[1]
        if split in box['values']:
            if box['values'].index(split) > 0:
                box.current(box.current() - 1)
                ok.invoke()
    else:
        if playingQueue[1] == 'queue':
            if num > 0:
                num -= 1
                tryLoad(data.queue.queue[num])
        else:
            if num > 0:
                num -= 1
                tryLoad(os.path.join(beginning[shortened.index(box['values'][num])], box['values'][num]))

# next track
def nextTrack() -> None:
    global num, played
    print('Skipping to next track')
    if not playingQueue[0]:
        split = os.path.split(played)[1]
        if split in box['values']:
            if box['values'].index(split) < len(box['values']) - 1:
                box.current(box.current() + 1)
                ok.invoke()
    else:
        if playingQueue[1] == 'queue':
            if num < len(data.queue.queue) - 1:
                num += 1
                tryLoad(data.queue.queue[num])
        else:
            if num < len(box['values']) - 1:
                num += 1
                tryLoad(os.path.join(beginning[shortened.index(box['values'][num])], box['values'][num]))

# right-click function for control
def controlContextMenu(event: tk.Event):
    print('Showing context menu')
    contextMenu = tk.Menu(root, tearoff=0)
    contextMenu.add_command(label=lang['context_menu']['pause'], command=pauseplay)
    contextMenu.add_command(label=lang['context_menu']['rewind'], command=rewind)
    contextMenu.add_separator()
    contextMenu.add_command(label=lang['context_menu']['next_track'], command=nextTrack)
    contextMenu.add_command(label=lang['context_menu']['prev_track'], command=prevTrack)
    contextMenu.add_separator()
    contextMenu.add_command(label=lang['context_menu']['mute'], command=mute)
    contextMenu.add_command(label=lang['context_menu']['volume_up'], command=up)
    contextMenu.add_command(label=lang['context_menu']['volume_down'], command=down)
    contextMenu.tk_popup(event.x_root, event.y_root)

# right-click function for root
def rootContextMenu(event: tk.Event):
    print('Showing context menu')
    contextMenu = tk.Menu(root, tearoff=0)
    contextMenu.add_command(label=lang['context_menu']['play_track'], command=lambda: ok.invoke())
    contextMenu.add_command(label=lang['context_menu']['play_queue'], command=lambda: playQueue.invoke())
    contextMenu.add_command(label=lang['context_menu']['play_all'], command=lambda: playAllBtn.invoke())
    contextMenu.add_separator()
    contextMenu.add_command(label=lang['context_menu']['find'], command=findWindow)
    contextMenu.add_command(label=lang['context_menu']['browse'], command=openFile)
    contextMenu.add_command(label=lang['context_menu']['random'], command=lambda: rand.invoke())
    contextMenu.add_separator()
    contextMenu.add_command(label=lang['context_menu']['queue_add'], command=lambda: addQueue.invoke())
    contextMenu.add_command(label=lang['context_menu']['queue_manage'], command=lambda: manage.invoke())
    contextMenu.add_command(label=lang['context_menu']['queue_save'], command=lambda: saveQueue.invoke())
    contextMenu.add_command(label=lang['context_menu']['queue_load'], command=lambda: load.invoke())
    contextMenu.add_separator()
    contextMenu.add_command(label=lang['context_menu']['settings'], command=settings)
    contextMenu.add_command(label=lang['context_menu']['filters'], command=filterWin)
    contextMenu.add_separator()
    contextMenu.add_command(label=lang['context_menu']['license'], command=license)
    contextMenu.add_command(label=lang['context_menu']['credits'], command=credits)
    contextMenu.tk_popup(event.x_root, event.y_root)

# start a playlist
def startPlaylist() -> None:
    global playingQueue, num
    print('Starting playlist')
    byte = zlib.decompress(plylst['values'][list(plylst['values'].keys())[num]])
    playable = BytesIO(byte)
    num = 0
    playingQueue = [True, 'playlist']
    tryLoad(playable, list(plylst['values'].keys())[num])

# open a playlist
def playlist() -> None:
    global plylst
    print('Waiting for user input...')
    def makeQueue():
        filename = os.path.split(file)
        path = os.path.join(filename[0], os.path.splitext(filename[1])[0])
        print('Making directories...')
        os.makedirs(path, exist_ok = True)
        print('Done')
        queueList = []
        print('Extracting music files...')
        for i in plylst['values']:
            byte = zlib.decompress(plylst['values'][i])
            queueList.append(os.path.join(path, i))
            if os.path.exists(os.path.join(path, i)):
                ok = messagebox.askyesno(lang['title']['replace_file'], lang['popup']['replace_file'].format(i, path))
            else:
                ok = True
            if ok:
                try:
                    with open(os.path.join(path, i), 'wb') as f:
                        f.write(byte)
                except PermissionError:
                    messagebox.showerror(lang['title']['permission_error'], lang['popup']['permission_error_write'].format(os.path.join(path, f)))
                except IOError:
                    messagebox.showerror(lang['title']['error'], lang['popup']['error_write'].format(os.path.join(path, f)))

        print('Done. Building queue...')
        queue = Queue(queueList)
        queue.filename = str(dataFolder/'WeaveSound'/'queues'/(os.path.splitext(filename[1])[0] + '.queue'))
        queue.name = plylst['title']
        queue.save()
        win.destroy()

    file = filedialog.askopenfilename(initialdir = data.lastDir, filetypes = [(lang['label']['playlist_file'], '*.plylst'), (lang['label']['pickle'], '*.pickle;*.pkl'), (lang['label']['any_file'], '*.*')])
    if file:
        print(f'Done. File: {file}')
        data.lastDir = os.path.split(file)[0]
        print('Reading file contents...')
        try:
            with open(file, 'rb') as f:
                plylst = pickle.load(f)
        except pickle.PickleError:
            messagebox.showerror(lang['title']['pickle_error'], lang['popup']['pickle_error'].format(file))
            print('Failed. Invalid pickle file')
        except PermissionError:
            messagebox.showerror(lang['title']['permission_error'], lang['popup']['permission_error'].format(file))
            print('Failed. No permission')
        except EOFError:
            messagebox.showerror('EOF', lang['popup']['eof'].format(file))
            print('Failed. Corrupt file')
        except FileNotFoundError:
            messagebox.showerror(lang['title']['file_missing'], lang['popup']['file_missing'].format(file))
            print('Failed. File does not exist')
        except IOError:
            messagebox.showerror(lang['title']['error'], lang['popup']['error'].format(file))
            print('Failed. I/O error')
        else:
            if not isinstance(plylst, dict):
                print('Done. Incorrect file format')
                messagebox.showerror(lang['title']['bad_format'], lang['popup']['bad_playlist'])
                return
            print('Done. Playlist valid')
            for i in plylst['values']:
                if not isinstance(i, str) or not isinstance(plylst['values'][i], bytes):
                    messagebox.showerror(lang['title']['bad_format'], lang['popup']['bad_playlist'])
                    return
            if data.playlist == 0:
                win = tk.Toplevel(root, bg = 'white' if data.theme else '#1e1e2e')
                win.title('Playlist Manager - WeaveSound')
                win.resizable(False, False)
                win.geometry(f'+{root.winfo_x()}+{root.winfo_y()}')
                ttk.Label(win, text = lang['label']['playlist_query'].format(plylst['title'])).pack()
                play = ttk.Button(win, text = lang['button']['play'], cursor = 'hand2', command = lambda: [startPlaylist(), win.destroy()], width = 20)
                play.pack()
                queue = ttk.Button(win, text = lang['button']['make_queue'], cursor = 'hand2', command = makeQueue, width = 20)
                queue.pack()
                formatted_tracks = '\n'.join(['    ' + item for item in plylst['values']])
                ttk.Label(win, text = 'Title: {0}\nTracks:\n{1}'.format(plylst['title'], formatted_tracks)).pack()
            elif data.playlist == 1:
                startPlaylist()
            else:
                makeQueue()
    else:
        print(f'Done. User cancelled')

# get the length of a music track
def getTrackLength(filePath: str | BytesIO):
    if data.getLen:
        print('Getting track length...')
        try:
            audio = AudioSegment.from_file(filePath)
            length = round(len(audio) / 1000)
            print('Done')
            return time.strftime('%H:%M:%S', time.gmtime(length))
        except:
            print('Invalid file for track length. Possibly MIDI sequence')
            return '\b'
    else:
        return '\b'

# the end event for a music track
def trackEndEvent() -> None:
    global loops
    if data.startNext:
        print('Starting next track...')
        music.unload()
        index = box['values'].index(box.get()) + 1
        if index >= len(box['values']):
            if data.wrap:
                box.current(0)
            else:
                minimized = control.state() == 'iconic'
                control.withdraw()
                if minimized:
                    root.iconify()
                else:
                    root.deiconify()
                mess.config(text = lang['message']['track_done'])
                return
        else:
            box.current(index)
        tryLoad(os.path.join(beginning[shortened.index(box.get())] if box.get() in shortened else '', box.get()))
    else:
        print('Looping current track...')
        if data.loops < 0:
            rewind()
        elif loops < data.loops:
            rewind()
            loops += 1
        else:
            minimized = control.state() == 'iconic'
            control.withdraw()
            if minimized:
                root.iconify()
            else:
                root.deiconify()
            loops = 0
            mess.config(text = lang['message']['track_done'])

# part of experimental seek functionality, not fully implemented
def seek(position: int) -> None:
    music.set_pos(position)

# close the window
def onClose() -> None:
    if box.current() >= 0:
        data.index = box.current()
    else:
        data.index = 0
    root.destroy()

# add the file to recent
def addRecent(path: str) -> None:
    if path in recent:
        recent.remove(path)
    recent.append(path)
    if len(recent) > 10:
        recent.remove(recent[0])
    with open(os.path.join(str(dataFolder), 'WeaveSound', 'recent.txt'), 'w') as file:
        file.write('\n'.join(recent))

# a function to switch the selection combobox between showing recent and showing all files
def switchBox() -> None:
    global showingAll
    if showingAll:
        box['values'] = list(reversed(recent)) if len(recent) > 0 else tuple(' ')
        showingAll = False
        toggle.config(text = 'Show all')
        box.current(0)
    else:
        box['values'] = sorted(tuple(shortened)) if len(files) > 0 else tuple(' ')
        showingAll = True
        toggle.config(text = 'Show recent')
        box.current(data.index)

# an object representing the queue
class Queue:
    def __init__(self, queue: list):
        self.queue = queue
        self.saved = False
        self.name = lang['label']['untitled']
        self.filename = None

    # save the queue
    def save(self, saveas: bool = False) -> None:
        if not hasattr(self, 'filename'):
            self.filename = None
        if self.filename is None or saveas or not self.saved:
            if not hasattr(self, 'name'):
                self.name = lang['label']['untitled']
            print('Waiting for user input...')
            file = filedialog.asksaveasfilename(confirmoverwrite = True, defaultextension = '.queue', filetypes = [(lang['label']['queue_file'], '*.queue'), (lang['label']['pickle'], '*.pickle;*.pkl'), (lang['label']['any_file'], '*.*')], initialfile = f'{self.name}.queue', initialdir = os.path.join(str(dataFolder), 'WeaveSound', 'queues'))
        else:
            file = self.filename
        if file:
            print(f'File: {file}')
            while True:
                print('Writing file data...')
                try:
                    with open(file, 'wb') as f:
                        pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
                except (pickle.PickleError, PermissionError, IOError):
                    print('Failed. Error while writing.')
                    ans = messagebox.showerror(lang['title']['save_error'], lang['popup']['save_error_0'].format(file), type = 'retrycancel')
                    if ans == 'cancel':
                        return
                else:
                    print('Done')
                    self.saved = True
                    self.filename = file
                    return

    # add an object to the queue
    def add(self, item):
        print('Adding item to queue...')
        self.queue.append(item)
        self.saved = False
    
    # remove an object from the queue
    def take(self, item):
        print('Removing item from queue...')
        self.queue.remove(item)
        self.saved = False

    def clear(self) -> None:
        print('Clearing queue...')
        self.saved = False
        self.filename = None

    def makePlaylist(self) -> None:
        playlist = []
        for i in self.queue:
            try:
                print('Making playlist...')
                with open(i, 'rb') as f:
                    value = f.read()
            except FileNotFoundError:
                if messagebox.showerror('File Not Found', f'The file "{i}" could not be found.\nWould you like to remove it from the queue?', type = 'yesno'):
                    self.take(i)
            except EOFError:
                if messagebox.showerror('EOF', f'The file "{i}" seems to be corrupted.\nWould you like to remove it from the queue?', type = 'yesno'):
                    self.take(i)
            except PermissionError:
                messagebox.showerror('Permission Error', f'Permission could not be obtained to read the file "{i}"')
            else:
                playlist.append(value)
        file = filedialog.asksaveasfilename(confirmoverwrite=True, filetypes=[('Playlist files', '*.plylst'), ('Pickle files', '*.pickle;*.pkl'), ('Any files', '*.*')], initialfile = f'{self.name}.plylst', initialdir = data.lastDir)
        if file:
            playDict = {'title': self.name, 'values': {}}
            for i in range(len(self.queue)):
                playDict['values'].update({os.path.split(self.queue[i])[1]: zlib.compress(playlist[i])})
            try:
                with open(file, 'wb') as f:
                    pickle.dump(playDict, f)
            except (pickle.PickleError, MemoryError):
                messagebox.showerror('Error saving file', f'An error occurred while pickling your data.')
            except PermissionError:
                messagebox.showerror('Permission Error', f'Permission could not be obtained to write to the file "{file}"')
            except IOError:
                messagebox.showerror('I/O Error', f'An error occurred while saving data to "{file}"')
            else:
                messagebox.showinfo('Operation Complete', f'Your playlist has successfully been exported to "{file}"')

    # bring up the queue manager
    def manage(self):
        if not hasattr(self, 'name'):
            self.name = lang['label']['untitled']
        # move an element up
        def moveUp(item):
            index = listbox.curselection()[0]
            if index > 0:
                self.queue.insert(index-1, self.queue.pop(index))
                updateListbox(index = index - 1)

        # move an element down
        def moveDown(item):
            index = listbox.curselection()[0]
            if index < len(self.queue) - 1:
                self.queue.insert(index+1, self.queue.pop(index))
                updateListbox(index = index + 1)

        # update the queue's name
        def update_name(event = None, new = None):
            if new is not None:
                self.name = new
                manager.title(f'{lang["title"]["manager"]} - {lang["title"]["main"]} ({self.name})')
                nameEntry.delete(0, tk.END)
                nameEntry.insert(0, new)
            else:
                self.name = nameEntry.get()
                manager.title(f'{lang["title"]["manager"]} - {lang["title"]["main"]} ({self.name})')
        
        # update the list box with the new values
        def updateListbox(value: bool = False, index: int = 0):
            listbox.delete(0, tk.END)
            for item in self.queue:
                listbox.insert(tk.END, os.path.split(item)[1])
            self.saved = value
            listbox.selection_set(index)
            if listbox.curselection():
                listbox.see(listbox.curselection()[0])

        # get files to add to the queue
        def getFiles() -> None:
            string = ''
            for i in range(len(FORMATS)):
                string += '*.' + FORMATS[i] + ';'
            files = filedialog.askopenfilenames(title = lang['title']['open'], filetypes = [(lang['label']['compatable'], string), (lang['label']['audio_file'], string.removesuffix(';'))], initialdir = data.lastDir)
            if len(files) > 0:
                data.lastDir = os.path.split(files[0])[0]
            for f in files:
                self.add(f)
                updateListbox()

        # right-click function for queue manager
        def managerContextMenu(event: tk.Event):
            contextMenu = tk.Menu(root, tearoff=0)
            contextMenu.add_command(label=lang['context_menu']['remove'], command=lambda: removeButton.invoke())
            contextMenu.add_command(label=lang['context_menu']['add'], command=lambda: addButton.invoke())
            contextMenu.add_command(label=lang['context_menu']['duplicate'], command=lambda: duplicateButton.invoke())
            contextMenu.add_separator()
            contextMenu.add_command(label=lang['context_menu']['move_up'], command=moveUp)
            contextMenu.add_command(label=lang['context_menu']['move_down'], command=moveDown)
            contextMenu.add_separator()
            contextMenu.add_command(label=lang['context_menu']['shuffle'], command=lambda: shuffle.invoke())
            contextMenu.add_command(label=lang['context_menu']['clear_queue'], command=lambda: clear.invoke())
            contextMenu.add_separator()
            contextMenu.add_command(label=lang['context_menu']['new_queue'], command=lambda: new.invoke())
            contextMenu.tk_popup(event.x_root, event.y_root)

        # find feature
        def findWindow(event = None) -> None:
            def close() -> None:
                global managerFindWord
                managerFindWord = findEntry.get()
                findWin.destroy()
            findWin = tk.Toplevel(manager)
            findWin.config(bg = 'white' if data.theme else '#1e1e2e')
            findWin.focus()
            findWin.grab_set()
            findWin.overrideredirect(True)
            # Calculate the center coordinates of the main window
            manager.update_idletasks()
            root_width = manager.winfo_width()
            root_height = manager.winfo_height()
            x_center = manager.winfo_rootx() + root_width // 2
            y_center = manager.winfo_rooty() + root_height // 2
            
            # Calculate the offset to position the Toplevel window in the center of the main window
            findWin_width = findWin.winfo_width()
            findWin_height = findWin.winfo_height()
            x_offset = (x_center - findWin_width // 2 ) - 100
            y_offset = (y_center - findWin_height // 2) + 20
            
            findWin.geometry(f"+{x_offset}+{y_offset}")
            findEntry = ttk.Entry(findWin, width = 50)
            findEntry.pack(side = 'left')
            findEntry.focus()
            findEntry.insert(0, managerFindWord)
            findEntry.select_range(0, tk.END)
            nextBtn = ttk.Button(findWin, text = '↓', command = lambda: findNext(findEntry.get()), width = 5, takefocus = False)
            nextBtn.pack(side = 'left')
            Hovertip(nextBtn, lang['tooltip']['find_next'])
            prevBtn = ttk.Button(findWin, text = '↑', command = lambda: findPrev(findEntry.get()), width = 5, takefocus = False)
            prevBtn.pack(side = 'left')
            Hovertip(prevBtn, lang['tooltip']['find_prev'])
            closeBtn = ttk.Button(findWin, text = '×', command = close, width = 5, takefocus = False)
            closeBtn.pack(side = 'left')
            Hovertip(closeBtn, 'close')
            findWin.bind('<Return>', lambda event: findNext(findEntry.get()))
            findWin.bind('<Down>', lambda event: findNext(findEntry.get()))
            findWin.bind('<Up>', lambda event: findPrev(findEntry.get()))

        # find next
        def findNext(searchKey: str):
            if searchKey:
                items = listbox.get(0, 'end')
                if listbox.curselection():
                    current_index = listbox.curselection()[0]
                    if current_index is None:
                        current_index = -1
                    found = False
                    for i in range(current_index + 1, len(items)):
                        if searchKey.lower() in items[i].lower():
                            listbox.selection_clear(0, 'end')
                            listbox.selection_set(i)
                            listbox.see(i)
                            found = True
                            break
                    if not found:
                        for i in range(len(items)):
                            if searchKey.lower() in items[i].lower():
                                listbox.selection_clear(0, 'end')
                                listbox.selection_set(i)
                                listbox.see(i)
                                break

        # find previous
        def findPrev(searchKey: str):
            if searchKey:
                items = items = listbox.get(0, 'end')
                if listbox.curselection():
                    current_index = listbox.curselection()[0]
                if current_index is None:
                    current_index = len(items)
                found = False
                for i in range(current_index - 1, -1, -1):
                    if searchKey.lower() in items[i].lower():
                        listbox.selection_clear(0, 'end')
                        listbox.selection_set(i)
                        listbox.see(i)
                        found = True
                        break
                if not found:
                    for i in range(len(items) - 1, -1, -1):
                        if searchKey.lower() in items[i].lower():
                            listbox.selection_clear(0, 'end')
                            listbox.selection_set(i)
                            listbox.see(i)
                            break

        
        manager = tk.Toplevel(root, takefocus = True)
        manager.config(bg = 'white' if data.theme else '#1e1e2e')
        manager.focus()
        manager.bind(f'<{Control}-f>', findWindow)
        manager.resizable(False, False)
        manager.title(f'{lang["title"]["manager"]} - {lang["title"]["main"]} ({self.name})')
        manager.grab_set()
        manager.geometry(f'+{root.winfo_x()}+{root.winfo_y()}')
        manager.bind('<Button-3>', managerContextMenu)
        nameEntry = ttk.Entry(manager, width=30)
        nameEntry.pack()
        nameEntry.insert(tk.END, self.name)
        nameEntry.bind("<Return>", update_name)
        nameEntry.bind("<FocusOut>", update_name)
        listbox = tk.Listbox(manager, height = 4, width = 50, bg = 'white' if data.theme else '#1e1e2e', fg = 'black' if data.theme else 'white')
        listbox.pack()
        updateListbox(self.saved)
        
        removeButton = ttk.Button(manager, text=lang['button']['remove'],
                           command=lambda: [self.take(self.queue[listbox.curselection()[0]]) if listbox.curselection() else None, updateListbox()], cursor='hand2')
        removeButton.pack()
        Hovertip(removeButton, lang['tooltip']['remove'])
        moveUpButton = ttk.Button(manager, text=lang['button']['move_up'],
                                   command=lambda: moveUp(self.queue[listbox.curselection()[0]]) if listbox.curselection() else None, cursor = 'hand2')
        moveUpButton.pack()
        Hovertip(moveUpButton, lang['tooltip']['move_up'])
        moveDownButton = ttk.Button(manager, text=lang['button']['move_down'],
                                     command=lambda: moveDown(self.queue[listbox.curselection()[0]]) if listbox.curselection() else None, cursor = 'hand2')
        moveDownButton.pack()
        Hovertip(moveDownButton, lang['tooltip']['move_down'])
        addButton = ttk.Button(manager, text=lang['button']['add'],
                               command=getFiles, cursor = 'hand2')
        addButton.pack()
        Hovertip(addButton, lang['tooltip']['add'])
        duplicateButton = ttk.Button(manager, text=lang['button']['duplicate'],
                                     command=lambda: [self.add(self.queue[listbox.curselection()[0]]) if listbox.curselection() else None, updateListbox()], cursor = 'hand2')
        duplicateButton.pack()
        Hovertip(duplicateButton, lang['tooltip']['duplicate'])
        shuffle = ttk.Button(manager, text=lang['button']['shuffle'],
                                     command=lambda: [random.shuffle(self.queue), updateListbox()], cursor = 'hand2')
        shuffle.pack()
        Hovertip(shuffle, lang['tooltip']['shuffle'])
        clear = ttk.Button(manager, text = lang['button']['clear_queue'], command = lambda: [self.queue.clear(), updateListbox()], cursor = 'hand2')
        clear.pack()
        Hovertip(clear, lang['tooltip']['clear_queue'])
        new = ttk.Button(manager, text = lang['button']['new_queue'], command = lambda: [self.queue.clear(), updateListbox(), update_name(new = lang['label']['untitled']), self.clear()], cursor = 'hand2')
        new.pack()
        playlist = ttk.Button(manager, text = lang['button']['export_playlist'], command = self.makePlaylist, cursor = 'hand2')
        playlist.pack()
        Hovertip(playlist, lang['tooltip']['export_playlist'])
        find = ttk.Button(manager, text = lang['button']['find'], command = findWindow, cursor = 'hand2')
        find.pack()
        Hovertip(find, lang['tooltip']['find'])
        done = ttk.Button(manager, text = lang['button']['done'], command = manager.destroy, cursor = 'hand2')
        done.pack()
        Hovertip(done, lang['tooltip']['done_queue'])
        manager.mainloop()

# an object for save data
class SaveData:
    def __init__(self, directories: list, loops: int, volup: str, voldown: str, pause: str, mute: str, queue: Queue, saveQueue: int, loopQueue: int, lastDir: Path, loopAll: int, directory, theme: int, loopPlaylist: int, startNext: int, wrap: int, getLen: int, playlist: int, index: int) -> None:
        self.loops = loops
        self.volup = volup
        self.voldown = voldown
        self.pause = pause
        self.mute = mute
        self.queue = queue
        self.saveQueue = saveQueue
        self.loopQueue = loopQueue
        self.lastDir = lastDir
        self.loopAll = loopAll
        self.theme = theme
        self.loopPlaylist = loopPlaylist
        self.startNext = startNext
        self.wrap = wrap
        self.getLen = getLen
        self.playlist = playlist
        self.index = index
        for i in directories:
            if not os.path.exists(i):
                directories.remove(i)
        if directories:
            self.directories = directories
        else:
            self.directories = [musicDir]
        if os.path.exists(directory):
            self.directory = musicDir
        else:
            self.directory = directory
    
    # save the data
    def save(self, quitting: bool = False) -> bool:
        if quitting:
            if not self.saveQueue:
                self.queue = []
        while True:
            try:
                with open(os.path.join(str(dataFolder), 'WeaveSound', 'data.pickle'), 'wb') as file:
                    pickle.dump(self, file, pickle.HIGHEST_PROTOCOL)
            except (pickle.PickleError, PermissionError, IOError):
                ans = messagebox.showerror(lang['title']['save_error'], lang['popup']['save_error_1'].format(os.path.join(str(dataFolder), "WeaveSound", 'data.pickle')), type = 'retrycancel')
                if ans == 'cancel':
                    return False
            else:
                return True

# an editable hovertip
class EditableHovertip(Hovertip):
    def __init__(self, anchor_widget, text, hover_delay=1000):
        super().__init__(anchor_widget, text, hover_delay)
    
    # change the text of the hovertip
    def change(self, text: str):
        self.text = text

# clickable hyperlink, subclass of tkinter label widget
class Hyperlink(tk.Label):
    '''A simple hyperlink that opens a website when clicked.\n
    New parameters:\n
    • url - the website that is connected to the hyperlink\n
    • showHovertip - whether or not to show a tooltip for the website\n
    • changeColor - whether or not to change color when hovered over\n
    • same - if true and no text or textvariable is given, text is the same as url'''
    def __init__(self, master: tk.Misc | None = None, *, url: str, font: str | list | tuple = 'Helvetica 10 underline', highlightcolor: str = 'blue', showHovertip: bool = True, same: bool = True, changeColor: bool = True, **kwargs) -> None:
        if not (url.startswith('https://') or url.startswith('http://')):
            url = 'http://' + url
        if kwargs['text'] is None:
            if same:
                kwargs['text'] = url
            else:
                kwargs['text'] = ''
        self.changeColor = changeColor
        self.showHovertip = showHovertip
        self.same = same
        self.url = url
        super().__init__(master, activeforeground='#4FC3F7', disabledforeground='#4FC3F7', fg='#4FC3F7', font=font, foreground='#4FC3F7', highlightcolor=highlightcolor, **kwargs)
        if showHovertip:
            Hovertip(self, url)
    
    # handle url clicked
    def _onClick(self, event = None) -> None:
        webbrowser.open_new_tab(self.url)

    # handle mouse enters url
    def _onEnter(self, event = None) -> None:
        self.config(foreground = '#0077FF', activeforeground = '#0077FF')

    # handle mouse leave url
    def _onLeave(self, event = None) -> None:
        self.config(foreground = '#4FC3F7', activeforeground = '#4FC3F7')

    def _addBindings(self) -> None:
        self.bind('<Button-1>', self._onClick)
        if self.changeColor:
            self.bind('<Enter>', self._onEnter, '+')
            self.bind('<Leave>', self._onLeave, '+')

    def pack(self, **kwargs) -> None:
        super().pack(**kwargs)
        self._addBindings()
        super().pack_configure(**kwargs)

    def place(self, **kwargs) -> None:
        super().place(**kwargs)
        self._addBindings()
        super().place_configure(**kwargs)

    def grid(self, **kwargs) -> None:
        super().grid(kwargs)
        self._addBindings()
        super().grid_configure(kwargs)

    def configure(self, **kwargs) -> None:
        self.configure(**kwargs)
        if 'url' in kwargs:
            self.url = kwargs['url']
        if 'same' in kwargs:
            self.same = kwargs['same']
        if 'changeColor' in kwargs:
            self.changeColor = kwargs['changeColor']

os.makedirs(os.path.join(str(dataFolder), 'WeaveSound', 'queues'), exist_ok = True)# create the data folders if they don't exist

# check to make sure lang file is valid
lang = lang_.check()
if not lang:
    exit()

# load the data file
try:
    with open(os.path.join(str(dataFolder), 'WeaveSound', 'data.pickle'), 'rb') as file:
        data = pickle.load(file)
    if not isinstance(data, SaveData):
        raise TypeError
except FileNotFoundError:
    data = SaveData([str(musicDir)], -1, 'Up', 'Down', 'k', 'm', Queue([]), 1, 1, 1, 1, str(musicDir), 0, 1, 0, 0, 1, 0, 0)
    print('Created new data file')
    data.save()
except (pickle.PickleError, TypeError, EOFError, AttributeError, MemoryError) as e:
    messagebox.showinfo('Error Loading File', f'An error occured loading your save data from the file\n"{os.path.join(str(dataFolder), "WeaveSound", "data.pickle")}"\n{e}\nBecause of this, your data has been reset.')
    data = SaveData([str(musicDir)], -1, 'Up', 'Down', 'k', 'm', Queue([]), 1, 1, 1, 1, str(musicDir), 0, 1, 0, 0, 1, 0, 0)
    print('Recreated corrupted data file')
    data.save()

# try to load the recent files file
try:
    with open(os.path.join(str(dataFolder), 'WeaveSound', 'recent.txt'), 'r') as file:
        recent = [line.strip() for line in file.readlines()]
except:
    recent = []
else:
    seen = set()
    result = []
    for item in recent:
        if item not in seen:
            result.append(item)
            seen.add(item)
    recent = result

# fix older data files
if not hasattr(data, 'loopAll'):
    data.loopAll = 1
    print('Added property "loopAll" with integer value of "1" to data')
if not hasattr(data, 'volup'):
    data.volup = 'up'
    print('Added property "volup" with string value of "up" to data')
if not hasattr(data, 'voldown'):
    data.voldown = 'down'
    print('Added property "voldown" with string value of "down" to data')
if not hasattr(data, 'pause'):
    data.pause = 'k'
    print('Added property "pause" with string value of "k" to data')
if not hasattr(data, 'mute'):
    data.mute = 'm'
    print('Added property "mute" with string value of "m" to data')
if not hasattr(data, 'queue'):
    data.queue = Queue([])
    print('Added property "queue" with class.Queue value to data')
if not hasattr(data, 'saveQueue'):
    data.saveQueue = 1
    print('Added property "saveQueue" with integer value of "1" to data')
if not hasattr(data, 'loopQueue'):
    data.loopQueue = 1
    print('Added property "loopQueue" with integer value of "1" to data')
if not hasattr(data, 'lastDir'):
    data.lastDir = musicDir
    print(f'Added property "lastDir" with string value of "{musicDir}" to data')
if not hasattr(data, 'directories'):
    data.directories = []
    print('Added property "directories" with empty list to data')
if not data.directories:
    if hasattr(data, 'directory'):
        data.directories = [str(data.directory)]
        print(f'Modified property "directory" to with string value "{data.directory}" in data')
    else:
        data.directories = [str(musicDir)]
        data.directory = str(musicDir)
        print(f'Added property "directory" with string value of "{musicDir}" to data')
if not hasattr(data, 'theme'):
    data.theme = 0
    print('Added property "theme" with integer value of "0" to data')
if not hasattr(data, 'loopPlaylist'):
    data.loopPlaylist = 1
    print('Added property "loopPlaylist" with integer value of "1" to data')
if not hasattr(data, 'startNext'):
    data.startNext = 0
    print('Added property "startNext" with integer value of "0" to data')
if not hasattr(data, 'wrap'):
    data.wrap = 0
    print('Added property "wrap" with integer value of "0" to data')
if not hasattr(data, 'getLen'):
    data.getLen = 1
    print('Added property "getLen" with integer value of "1" to data')
if not hasattr(data, 'playlist'):
    data.playlist = 0
    print('Added property "playlist" with integer value of "1" to data')
if not hasattr(data, 'index'):
    data.index = 0
    print('Added property "index" with integer value of "0" to data')

# dictionary for filters, not used unless filters are applied
filterDict = {'types': {'midi': 1, 'wav': 1, 'ogg': 1, 'flac': 1, 'opus': 1, 'aiff': 1, 'mp3': 1, 'mid': 1, 'aif': 1, 'mod': 1, 'xm': 1}, 'contains': '', 'nocontains': '', 'begins': '', 'nobegins': '', 'ends': '', 'noends': '', 'inqueue': 0, 'folder': {'include': data.directories, 'exclude': []}}# filters

# get the file
files, shortened, beginning = getFiles()
if len(files) > 0:
    played = shortened[0]
else:
    played = ''

print('Initializing GUI displays...')
# selection window
root = tk.Tk()# root window
style = ttk.Style()
setTheme(data.theme, False) 
root.config(bg = 'white' if data.theme else '#1e1e2e')
root.title(f'{lang["title"]["selection"]} - {lang["title"]["main"]}')
root.geometry(calculateWindowPosition(100, 50))
root.resizable(False, False)
img = tk.PhotoImage(data = b64decode(ICON))# load the image
root.iconphoto(True, img)
root.focus()# gives root window the focus
choose = ttk.Label(root, text = lang['label']['choose'])
choose.pack()
# all the music files added to a combobox
box = ttk.Combobox(root, width = 45)
box['values'] = sorted(tuple(shortened)) if len(files) > 0 else tuple(' ')
box.pack()
box.current(data.index)
rand = ttk.Button(root, text = lang['button']['random'], command = lambda: [box.delete(0, 'end'), box.insert(0, random.choice(box['values']))], cursor = 'hand2')
rand.pack()
Hovertip(rand, lang['tooltip']['random'])
mess = ttk.Label(root, text = '' if len(files) > 0 else lang['message']['empty'])
box.bind('<Return>', lambda event: tryLoad(os.path.join(beginning[shortened.index(box.get())] if box.get() in shortened else '', box.get())))
refresh = ttk.Button(root, text = lang['button']['refresh'], command = refreshDir, cursor = 'hand2')
refresh.pack()
Hovertip(refresh, f'{lang["tooltip"]["refresh"]} ({ctrl}+r)')
ok = ttk.Button(root, text = lang['button']['play_track'], command = lambda: [tryLoad(os.path.join(beginning[shortened.index(box.get())] if box.get() in shortened else '', box.get())), control.geometry(f'+{root.winfo_x()}+{root.winfo_y()}')], cursor = 'hand2')
ok.pack()
Hovertip(ok, lang['tooltip']['play_track'])
playQueue = ttk.Button(root, text = lang['button']['play_queue'], command = startQueue, cursor = 'hand2')
playQueue.pack()
Hovertip(playQueue, lang['tooltip']['play_queue'])
playAllBtn = ttk.Button(root, text = lang['button']['play_all'], command = playAll, cursor = 'hand2')
playAllBtn.pack()
Hovertip(playAllBtn, lang['tooltip']['play_all'])
browse = ttk.Button(root, text = lang['button']['browse'], command = openFile, cursor = 'hand2')
browse.pack()
Hovertip(browse, lang['tooltip']['browse'])
find = ttk.Button(root, text = lang['button']['find'], command = findWindow, cursor = 'hand2')
find.pack()
Hovertip(find, lang['tooltip']['find'])
setting = ttk.Button(root, text = lang['button']['settings'], cursor = 'hand2', command = settings)
setting.place(x = x, y = 42 + spacing / 2)
Hovertip(setting, lang['tooltip']['settings'])
filters = ttk.Button(root, text = lang['button']['filters'], command = filterWin, cursor = 'hand2')
filters.place(x = x, y = 67 + spacing)
Hovertip(filters, lang['button']['filters'])
licenseBtn = ttk.Button(root, text = lang['button']['license'], command = license, cursor = 'hand2')
licenseBtn.place(x = x, y = 92 + spacing * 1.5)
Hovertip(licenseBtn, lang['tooltip']['license'])
creditBtn = ttk.Button(root, text = lang['button']['credits'], command = credits, cursor = 'hand2')
creditBtn.place(x = x, y = 117 + spacing * 2)
Hovertip(creditBtn, lang['tooltip']['credits'])
aboutBtn = ttk.Button(root, text = lang['button']['about'], command = about, cursor = 'hand2')
aboutBtn.place(x = x, y = 142 + spacing * 2.5)
Hovertip(aboutBtn, lang['tooltip']['credits'])
addQueue = ttk.Button(root, text = lang['button']['queue_add'], cursor = 'hand2', command = lambda: data.queue.add(os.path.join(beginning[shortened.index(box.get())] if box.get() in shortened else '', box.get())), width = 14)
addQueue.place(x = 2, y = 42 + spacing / 2)
Hovertip(addQueue, lang['tooltip']['queue_add'].format(ctrl))
manage = ttk.Button(root, text = lang['button']['queue_manage'], cursor = 'hand2', command = lambda: data.queue.manage(), width = 14)
manage.place(x = 2, y = 67 + spacing)
Hovertip(manage, lang['tooltip']['queue_manage'])
saveQueue = ttk.Button(root, text = lang['button']['queue_save'], cursor = 'hand2', command = lambda: data.queue.save(), width = 14)
saveQueue.place(x = 2, y = 92 + spacing * 1.5)
Hovertip(saveQueue, lang['button']['queue_save'])
saveQueueAs = ttk.Button(root, text = lang['button']['queue_save_as'], command = lambda: data.queue.save(True), width = 14, cursor = 'hand2')
saveQueueAs.place(x = 2, y = 117 + spacing * 2)
Hovertip(saveQueueAs, lang['tooltip']['queue_save_as'])
load = ttk.Button(root, text = lang['button']['queue_load'], cursor = 'hand2', command = loadQueue, width = 14)
load.place(x = 2, y = 142 + spacing * 2.5)
Hovertip(load, lang['tooltip']['queue_load'])
toggle = ttk.Button(text = 'Show recent', command = switchBox, cursor = 'hand2')
toggle.pack()
playlistBtn = ttk.Button(root, text = lang['button']['playlist'], command = playlist, cursor = 'hand2')
playlistBtn.pack()
Hovertip(playlistBtn, lang['tooltip']['playlist'])
mess.pack()
root.bind(f'<{Control}-f>', findWindow)
root.bind(f'<{Control}-p>', lambda event: ok.invoke())
root.bind(f'<{Control}-r>', lambda event: refresh.invoke())
root.bind(f'<{Control}-Alt-KeyPress-p>', lambda event: playAllBtn.invoke())
root.bind(f'<Alt-p>', lambda event: playQueue.invoke())
root.bind(f'<{Control}-a>', lambda event: addQueue.invoke())
root.bind('<Button-3>', rootContextMenu)
root.protocol('WM_DELETE_WINDOW', onClose)

# control window
control = tk.Toplevel(root, takefocus = False)
control.config(bg = 'white' if data.theme else '#1e1e2e')
control.geometry(f'{size}x{size + 26}' + calculateWindowPosition(100, 50))
control.title(f'{lang["title"]["control"]} - {lang["title"]["main"]}')
control.focus()# gives control window the focus
control.resizable(False, False)# makes the window non-resizable
if played != '':
    name = ttk.Label(control, text = os.path.splitext(os.path.split(played)[1])[0] if len(os.path.split(played)[1]) <= length else os.path.split(played)[1][0:length - 1] + '…')
else:
    name = ttk.Label(control, text = '')
name.pack()
upvol = ttk.Button(control, text = lang['button']['volume_up'], command = up, cursor = 'hand2')
upvol.pack()# volume up button
uptip = EditableHovertip(upvol, f'{lang["tooltip"]["volume_up"]} ({data.volup.lower()})')
vol = tk.IntVar()
dwnvol = ttk.Button(control, text = lang['button']['volume_down'], command = down, cursor = 'hand2')
dwnvol.pack()# volume down button
dwntip = EditableHovertip(dwnvol, f'{lang["tooltip"]["volume_down"]} ({data.voldown.lower()})')
slider = ttk.Scale(control, command = volume, variable = vol, cursor = 'hand2', to = 0, from_ = 10, orient = 'vertical', length = 75, style = 'TScale')
slider.set(10)
slider.place(x = 120 + shift * 2, y = 21)
mutebtn = ttk.Button(control, text = lang['button']['unmute'] if muted else lang['button']['mute'], command = mute, cursor = 'hand2')
mutebtn.pack()# mute/unmute button
mutetip = EditableHovertip(mutebtn, f'{lang["tooltip"]["mute"]} ({data.mute.lower()})')
label = ttk.Label(control, text = '00:00:00')
label.pack()
# seekbar, not yet finished
# seekbar = ttk.Scale(control, orient = 'horizontal', from_ = 0, to = 1000)
# seekbar.pack()

prev = ttk.Button(control, text = lang['button']['prev_track'], cursor = 'hand2', width = 6, command = prevTrack)
# prev.place(x = 13 - shift, y = 120 + shift)
if OS == 'Linux':
    prev.pack(side = tk.TOP, anchor = tk.W)
else:
    prev.place(x = 13 - (shift + 2), y = 120 + (shift + 5))
Hovertip(prev, lang['tooltip']['prev_track'])
next = ttk.Button(control, text = lang['button']['next_track'], cursor = 'hand2', width = 5, command = nextTrack)
next.place(x = 110 + (shift - 1), y = 125 + shift)
# next.pack(side = tk.TOP, anchor = tk.E)
Hovertip(next, lang['tooltip']['next_track'])
rewindbtn = ttk.Button(control, text = lang['button']['rewind'], command = rewind, cursor = 'hand2', width = 6)
rewindbtn.pack(side = tk.LEFT, anchor = tk.S) # rewind button
rewindtip = Hovertip(rewindbtn, lang['tooltip']['rewind'])
pause = ttk.Button(control, text = lang['button']['pause'], command = pauseplay, cursor = 'hand2', width = width)
pause.pack(side = tk.LEFT, anchor = tk.S) # pause/play button
pausetip = EditableHovertip(pause, f'{lang["tooltip"]["pause"]} ({data.pause.lower()})')
stop = ttk.Button(control, text = lang['button']['stop'], command = lambda: [control.withdraw(), root.deiconify(), music.unload(), setPlaying(), root.geometry(f'+{control.winfo_x()}+{control.winfo_y()}')], cursor = 'hand2', width = 6)
stop.pack(side = tk.LEFT, anchor = tk.S) # stop button
Hovertip(stop, lang['tooltip']['stop'])
control.bind('<Pause>', pauseplay)# pause/break key
control.bind('=', up)# plus key
control.bind('-', down)# minus key
control.bind('<Button-3>', controlContextMenu)
control.bind('<Key>', onPress)# other keys

control.withdraw()
control.protocol('WM_DELETE_WINDOW', onClose)
print('Finished')

# a thread that allows the program to continually run the update function
print('Creating daemon thread to run certain updates...')
thread = Thread(target = update, daemon = True)
thread.start()
print('Done')

root.focus()# give root window the focus

# check for files opened with the program, check for compatibilty, and start any valid track
print('Checking for opened files...')
if len(sys.argv) > 1:
    print('File found.')
    if sys.argv[1].endswith('.queue'):
        try:
            with open(sys.argv[1], 'rb') as f:
                file = pickle.load(f)
        except (TypeError, pickle.PickleError):
            mess.config(text = lang['message']['bad_queue'])
        else:
            if not isinstance(file, Queue):
                mess.config(text = lang['message']['bad_queue'])
            else:
                data.queue = file
                data.save()
                startQueue()
    else:
        tryLoad(sys.argv[1])
        if os.path.split(os.path.normpath(sys.argv[1]))[0].replace('\\', '/') in data.directories:
            box.current(box['values'].index(os.path.split(sys.argv[1])[1]))
else:
    print('No file found')

del ICON, img
root.mainloop()# start the mainloop of tk
isClosing = True

# stop and unload music
music.stop()
music.unload()
data.save(True)
print('Exiting program')