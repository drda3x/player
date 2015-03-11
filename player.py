#! /usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os, sys
from Tkinter import Tk, Button, Frame, Label, Listbox, SINGLE, END, Y, Scrollbar, VERTICAL, RIGHT, LEFT, BOTH
from tkSnack import Sound, initializeSnack


root = Tk()
initializeSnack(root)


class Song(object):
    u"""
    Класс для работы с песенками
    """

    __stop_time = 15  # seconds
    __started_at = 0
    __stop_flag = False

    def __init__(self, _timer):
        self.timer = _timer

    sound = Sound()

    def __check_limit(self):
        if not self.__stop_flag:

            if self.__stop_time < self.__started_at:
                self.stop()
                self.__stop_flag = True
                return

            self.__started_at += 1
            root.after(1000, self.__check_limit)

    def play(self):
        self.stop()
        self.sound.play()
        self.timer.start()
        self.__stop_flag = False
        self.__check_limit()

    def stop(self):
        self.__stop_flag = True
        self.__started_at = 0
        self.sound.stop()
        self.timer.stop()

    def pause(self):
        self.sound.pause()
        self.timer.pause()

        if not self.__stop_flag:
            self.__stop_flag = True

        else:
            self.__stop_flag = False
            self.__check_limit()

    def load(self, filename):
        self.sound.load(filename)

    def set_stop_time(self, stop_time_value):
        self.__stop_time = stop_time_value


class PlayList():

    def __init__(self, frame, path):
        self.__scroll_bar = Scrollbar(frame, orient=VERTICAL)
        self.__lb = Listbox(frame, selectmode=SINGLE, yscrollcommand=self.__scroll_bar.set,  height=25, width=90, font=5)
        self.dir = path
        self.__scroll_bar.config(command=self.__lb.yview)
        self.__scroll_bar.pack(side=RIGHT, fill=Y)
        self.__lb.pack(side=LEFT, fill=BOTH, expand=1)

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


class Timer(Label):

    __started = None
    __id = None
    __paused = False

    def __init__(self, frame):
        Label.__init__(self, frame, text='00:00', padx=15)
        self.pack(side='right')

    def __update(self):
        add_zero = lambda x: '0' + str(x) if x < 10 else str(x)

        minutes = int(self.__started/60)
        view = add_zero(minutes) + ':' + add_zero(int(self.__started - minutes*60))
        self.config(text=view)
        self.__started += 1

        self.__id = root.after(1000, self.__update)

    def __reset(self):
        self.config(text='00:00')
        self.__started = None

    def start(self):
        self.__reset()
        self.__started = 0
        self.__update()

    def stop(self):
        self.__reset()
        root.after_cancel(self.__id) if self.__id else None
        self.__id = None

    def pause(self):
        if self.__started:
            if not self.__paused:
                root.after_cancel(self.__id)
                self.__id = None
                self.__paused = True

            else:
                root.after(1000, self.__update)
                self.__paused = False

Frame(root).pack(pady=5)
song_label = Label(root, text='No song loaded', font='Helvetica 11 bold')
song_label.pack()

f0 = Frame(root)
f1 = Frame(root)
f0.pack(pady=5)
f1.pack(pady=5)

timer = Timer(f0)
song = Song(timer)
play_list = PlayList(f1, u'D:\\Da3x\\Music\\хастл')


def play():
    stop()
    filename = play_list.dir + '\\' + play_list.selected if play_list.selected else None

    if filename:
        song_label.config(text=play_list.selected)
        song.load(filename)
        song.play()


def stop():
    song.stop()


def pause():
    song.pause()


Button(f0, bitmap='snackPlay', command=play, height=50, width=50).pack(side='left')
Button(f0, bitmap='snackStop', command=stop, height=50, width=50).pack(side='left')
Button(f0, bitmap='snackPause', command=pause, height=50, width=50).pack(side='left')

root.mainloop()