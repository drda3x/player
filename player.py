#! /usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os, sys
from Tkinter import Tk, Button, Frame, Label, Listbox, SINGLE, END, X
from tkSnack import Sound, initializeSnack


root = Tk()
initializeSnack(root)


class Song(object):
    u"""
    Класс для работы с песенками
    """

    __stop_time = 90
    __id = None

    sound = Sound()

    def play(self):

        root.after_cancel(self.__id) if self.__id else None

        self.sound.play()
        __id = root.after(self.__stop_time * 1000, self.stop)

    def stop(self):
        root.after_cancel(self.__id) if self.__id else None
        self.__id = None
        self.sound.stop()

    def pause(self):
        self.sound.pause()

    def load(self, filename):
        self.sound.load(filename)

    def set_stop_time(self, stop_time_value):
        self.__stop_time = stop_time_value


class PlayList():

    def __init__(self, frame, path):
        self.__lb = Listbox(frame, selectmode=SINGLE, height=25, width=90)
        self.dir = path

        self.songs_list = os.listdir(self.dir)
        for song in self.songs_list:
            self.__lb.insert(END, song)

        self.__lb.pack()

    @property
    def selected(self):
        try:
            return self.songs_list[self.__lb.curselection()[0]]
        except IndexError:
            return None


Frame(root).pack(pady=5)
upLabel = Label(root, text='My super player', font='Helvetica 12 bold')
upLabel.pack()

f0 = Frame(root)
f1 = Frame(root)
f0.pack(pady=5)
f1.pack(pady=5)

song = Song()
play_list = PlayList(f1, u'D:\\Da3x\\Music\\хастл')


def play():

    stop()

    filename = play_list.dir + '\\' + play_list.selected if play_list.selected else None

    if filename:
        song.load(filename)
        song.play()


def stop():
    song.stop()


def pause():
    song.pause()

timelab = Label(f0, text='0.00 sec', width=10)
timelab.pack(side='left')
Button(f0, bitmap='snackPlay', command=play, height=50, width=50).pack(side='left')
Button(f0, bitmap='snackStop', command=stop, height=50, width=50).pack(side='left')
Button(f0, bitmap='snackPause', command=pause, height=50, width=50).pack(side='left')

root.mainloop()