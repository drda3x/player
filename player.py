#! /usr/bin/env python
# -*- coding: utf-8 -*-

#todo СТОП-ПАУЗА ... Таймер скачет

import os, sys, re
from Tkinter import *
from Sound import SoundManager as Sound


if __name__ == '__main__':

    root = Tk()

    # =================================================================

    try:
        from settings import MUSIC_DIR

        folder = MUSIC_DIR

    except Exception:
        raise 'No music folder. Define music folder in the settings.py file'

    # =================================================================


    class PlayList():

        def __init__(self, frame, path):
            self.__scroll_bar = Scrollbar(frame, orient=VERTICAL)
            self.__lb = Listbox(frame, selectmode=SINGLE, yscrollcommand=self.__scroll_bar.set,  height=25, width=90, font=5)
            self.dir = path
            self.__scroll_bar.config(command=self.__lb.yview)
            self.__scroll_bar.pack(side=RIGHT, fill=Y)
            self.__lb.pack(side=LEFT, fill=BOTH, expand=1)

            num = re.compile('^\d{2,3}')

            def bpm(file_name):
                _bpm = num.search(file_name)
                return int(file_name[0:_bpm.end()]) if _bpm else 0

            self.songs_list = [(bpm(elem), elem) for elem in filter(lambda x: x.endswith('.mp3'), os.listdir(self.dir))]

            try:
                self.songs_list.sort(key=lambda x: x[0])
            except Exception:
                pass

            for song in self.songs_list:
                self.__lb.insert(END, song[1])

            self.__lb.pack()

        @property
        def selected(self):
            try:
                return self.songs_list[int(self.__lb.curselection()[0])][-1]
            except IndexError:
                return None


    class Timer(Label):

        limit = IntVar()
        __limit = 0
        __started = 0
        __paused = False
        __id = None
        song = None

        def __init__(self, frame):

            def timer_values(start_val, stop_val, step):
                get_secs = lambda x: x[0]*60 + x[1]
                add_zero = lambda x: '0%d' % x if x < 10 else str(x)
                start = map(int, start_val.split(':'))
                stop = map(int, stop_val.split(':'))

                if get_secs(start) - step <= 60 and start[0] > 0:
                    start[0] -= 1
                    start[1] = 60 - step

                for i in ['full'] + range(get_secs(start), get_secs(stop), step):

                    if isinstance(i, int):
                        start[1] += step
                        if start[1] >= 60:
                            start[0] += 1
                            start[1] -= 60

                        yield ('%d:%s' % (start[0], add_zero(start[1])), get_secs(start))

                    else:
                        yield ('full', None)

            Label.__init__(self, frame, padx=15)
            self.__reset()
            self.pack(side='right')

            for i in timer_values('1:00', '2:00', 15):
                Radiobutton(f3, variable=self.limit, indicatoron=0, text=i[0], value=i[1], padx=5, pady=5).pack(side='left', padx=5)

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

                try:
                    if self.__time_left <= self.song.fade_out_config['duration']:
                        self.song.fade_out()

                except TypeError:
                    pass

                self.__started += 1
                self.__update_view()
                self.__set()

            elif not self.__check_time():
                self.stop()

        @property
        def __time_left(self):
            return self.__limit - self.__started

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

            try:
                self.__limit = self.limit.get()
            except ValueError:
                self.__limit = self.song.length

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
    f3 = Frame(f0)
    f0.pack(pady=5)
    f1.pack(pady=5)
    f3.pack(side='left', padx=30)

    song = Sound()
    timer = Timer(f0)
    timer.song = song

    play_list = PlayList(f1, folder)

    def play():
        stop()
        filename = play_list.dir + '\\' + play_list.selected if play_list.selected else None

        if filename:
            song_label.config(text=u'Загрузка...')
            song.load(filename)
            song_label.config(text=play_list.selected)
            timer.start()

    def stop():
        timer.stop()

    def pause():
        timer.pause()

    def on_quit():
        song.destroy()
        root.quit()

    buttons = [
    ('play', play), 
    ('stop', stop), 
    ('pause', pause)
    ]

    for button in buttons:
        Button(f0, text=button[0], command=button[1], height=3, width=5).pack(side='left', padx=5)

    # Button(f0, text='play', command=play, height=3, width=5).pack(side='left')
    # Button(f0, text='stop', command=stop, height=5, width=5).pack(side='left')
    # Button(f0, text='pause', command=pause, height=5, width=5).pack(side='left')

    root.protocol("WM_DELETE_WINDOW", on_quit)

    root.mainloop()