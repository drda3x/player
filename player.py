#! /usr/bin/env python
# -*- coding: utf-8 -*-

#todo СТОП-ПАУЗА ... Таймер скачет

import os, sys
from Tkinter import Tk, Button, Frame, Label, Listbox, SINGLE, END, Y, Scrollbar, VERTICAL, RIGHT, LEFT, BOTH
from tkSnack import Sound, initializeSnack


root = Tk()
initializeSnack(root)


class PlayList():

    def __init__(self, frame, path):
        self.__scroll_bar = Scrollbar(frame, orient=VERTICAL)
        self.__lb = Listbox(frame, selectmode=SINGLE, yscrollcommand=self.__scroll_bar.set,  height=25, width=90, font=5)
        self.dir = path
        self.__scroll_bar.config(command=self.__lb.yview)
        self.__scroll_bar.pack(side=RIGHT, fill=Y)
        self.__lb.pack(side=LEFT, fill=BOTH, expand=1)

        self.songs_list = filter(lambda x: x.endswith('.mp3'), os.listdir(self.dir))
        for song in self.songs_list:
            self.__lb.insert(END, song)

        self.__lb.pack()

    @property
    def selected(self):
        try:
            return self.songs_list[int(self.__lb.curselection()[0])]
        except IndexError:
            return None


class Timer(Label):

    __limit = 0
    __started = 0
    __paused = False
    __id = None
    song = None

    def __init__(self, frame, limit):
        Label.__init__(self, frame, padx=15)
        self.__reset()
        self.pack(side='right')
        self.__limit = limit

    def __update_view(self):
        u"""
        Обновить таймер на экране
        """

        add_zero = lambda x: '0' + str(x) if x < 10 else str(x)

        minutes = int(self.__started/60)
        view = add_zero(minutes) + ':' + add_zero(int(self.__started - minutes*60))
        self.config(text=view)

    def __reset(self):
        u"""
        Обнулить таймер
        """

        self.__unset()
        self.config(text='00:00')
        self.__started = 0
        self.__paused = False

    def __exit(self):
        u"""
        Проверка таймера на выполнение следующих условий
        1.Окончание отсчетного времени
        2.Пауза
        """

        if not self.__paused and self.__check_time():

            self.__started += 1
            self.__update_view()
            self.__set()

        elif not self.__check_time():
            self.stop()

    def __check_time(self):
        return self.__limit > self.__started

    def __set(self):
        self.__id = root.after(1000, self.__exit)

    def __unset(self):
        root.after_cancel(self.__id) if self.__id else None

    def start(self):
        u"""
        Запустить таймер
        """

        self.__reset()
        self.song.play()
        self.__set()

    def stop(self):
        u"""
        Остановить таймер
        """

        self.song.stop()
        self.__unset()

    def pause(self):
        u"""
        Поставить на паузу
        """

        if self.__paused:
            self.__paused = False
            self.__set()

        else:
            self.__paused = True

        self.song.pause()

Frame(root).pack(pady=5)
song_label = Label(root, text='No song loaded', font='Helvetica 11 bold')
song_label.pack()

f0 = Frame(root)
f1 = Frame(root)
f0.pack(pady=5)
f1.pack(pady=5)

song = Sound()
timer = Timer(f0, 30)
timer.song = song

play_list = PlayList(f1, u'D:\\Music\\Хастл')


def play():
    stop()
    filename = play_list.dir + '\\' + play_list.selected if play_list.selected else None

    if filename:
        song_label.config(text=play_list.selected)
        song.load(filename)
        timer.start()


def stop():
    timer.stop()


def pause():
    timer.pause()


Button(f0, bitmap='snackPlay', command=play, height=50, width=50).pack(side='left')
Button(f0, bitmap='snackStop', command=stop, height=50, width=50).pack(side='left')
Button(f0, bitmap='snackPause', command=pause, height=50, width=50).pack(side='left')

root.mainloop()