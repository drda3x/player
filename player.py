#! /usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os, sys
from Tkinter import *
from tkSnack import *
import tkFileDialog

stop_after = 90  #sec

root = Tkinter.Tk()

initializeSnack(root)

songs_dir = 'C:\\music\\'

if songs_dir not in sys.path:
	sys.path.append(songs_dir)

songs = os.listdir(songs_dir)
songs_list = Listbox(root, height=300, width=200, selectmode=SINGLE)
songs_files = {}
song = {}

options = {}
options['defaultextension'] = '.mp3'
options['filetypes'] = [('mp3 files', '.mp3')]
options['initialdir'] = 'C:\\music\\'
options['parent'] = root
options['title'] = 'This is a title'

k = 0
def _load():
	for i in songs:
		# try:
		name = u'' + i
		songs_list.insert(END, name)

		options['initialfile'] = name
		song_file = tkFileDialog.askopenfilename(**options)

		song = Sound()
		songs_files[k] = song.read(song_file)
		song.play()
		k += 1

		yield
		# except:
		# 	None

		# finally:
		# 	yield

# it = _load()

def load():
	try:
		it.next()
		root.after(100, load)
	except StopIteration:
		pass

	# _file = root.tk.call('eval', 'snack::getOpenFile')
	# song['curent'].read(_file)

def play():

	song['curent'] = Sound()
	song_file = tkFileDialog.askopenfilename(**options)
	if song_file:
		song['curent'].read(song_file)
		song['begin_time'] = datetime.datetime.now()
		song['curent'].play()

		upLabel.configure(text=song_file.split('/')[-1])

		song['timer'] = True
		root.after(1000, timer)
		root.after(stop_after * 1000, stop)

def stop():
	song['timer'] = False
	song['curent'].stop()
	play()

def pause():
    song['curent'].pause()

def timer():
    dur = str(int((datetime.datetime.now() - song['begin_time']).total_seconds())) + ' sec'
    timelab.configure(text=dur)

    if song['timer']:
    	root.after(1000,timer)

Frame(root).pack(pady=5)
upLabel = Label(root, text='My super player',
      font='Helvetica 12 bold')
upLabel.pack()
f0 = Frame(root)
f0.pack(pady=5)
timelab = Label(f0, text='0.00 sec',width=10)
timelab.pack(side='left')
Button(f0, bitmap='snackPlay', command=play, height=50, width=50).pack(side='left')
Button(f0, bitmap='snackStop', command=stop, height=50, width=50).pack(side='left')
Button(f0, bitmap='snackPause', command=pause, height=50, width=50).pack(side='left')

# root.after(100, load)
# songs_list.pack()
root.mainloop()