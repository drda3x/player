#! /usr/bin/env python
# -*- coding: utf-8 -*-

from Sound import SoundManager as Sound
from Tkinter import *


root = Tk()

Frame(root).pack(pady=5)
f0 = Frame(root)
f0.pack(pady=5)

s = Sound()
s.load('zv.mp3')

is_playing = True
_id = [None]


def play():
    s.play()


def stop():
    s.stop()


def pause():
    s.pause()

Button(f0, text='play', command=play).pack(pady=5)
Button(f0, text='stop', command=stop).pack(pady=5)
Button(f0, text='pause', command=pause).pack(pady=5)

root.mainloop()