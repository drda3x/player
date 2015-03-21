#! /usr/bin/env python
# -*- coding: utf-8 -*-

from Sound import Sound
from Tkinter import *


root = Tk()

Frame(root).pack(pady=5)
f0 = Frame(root)
f0.pack(pady=5)

s = Sound(0, 1, -1)
s.load('zv.mp3')

is_playing = True
_id = [None]


def play():
    global is_playing

    is_playing = True

    player = s.play()

    def next():
        if is_playing:
            player.next()
            _id[0] = root.after(1, next)

        else:
            root.after_cancel(_id[0])

    _id[0] = root.after(1, next)


def stop():

    global is_playing
    is_playing = False
    s.stop()



Button(f0, text='play', command=play).pack(pady=5)
Button(f0, text='stop', command=stop).pack(pady=5)

root.mainloop()