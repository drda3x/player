#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
import pymedia.muxer as muxer
import pymedia.audio.acodec as acodec
import pymedia.audio.sound as sound

from multiprocessing import Process, Queue

from mutagen.mp3 import MP3


class Sound(object):

    u"""
    Класс для работы со звуком.
    """

    __EMULATE = 0
    __demuxer = None
    __devises = sound.getODevices()
    sound_file = None
    __sound = None
    __card = None
    __rate = None
    __tt = None
    __queue = None
    __paused = None

    def __init__(self, card, rate, tt):
        self.__card = card
        self.__rate = rate
        self.__tt = tt

        if self.__card not in range(len(self.__devises)):
            raise 'Cannot play sound to non existent device %d out of %d' % (self.__card + 1, len(self.__devises))

    def __player(self):
        self.__sound = re_sampler = dec = None
        t = 0
        stream = self.sound_file.read(32000)
        i = 0

        while len(stream):

            frames = self.__demuxer.parse(stream)
            if frames:

                for frame in frames:

                    dec = acodec.Decoder(self.__demuxer.streams[frame[0]]) if not dec else dec
                    r = dec.decode(frame[1])

                    if r and r.data:

                        if not self.__sound:
                            self.__sound = sound.Output(int(r.sample_rate * self.__rate), r.channels, sound.AFMT_S16_LE, self.__card)

                            if 1 < self.__rate < 1:
                                re_sampler = sound.Resampler((r.sample_rate, r.channels), (int(r.sample_rate / self.__rate), r.channels))

                            self.__sound.setVolume(65535)
                        data = re_sampler.resample(r.data) if re_sampler else r.data

                        if self.__EMULATE:
                            # Calc delay we should wait to emulate snd.play()

                            d = len(data) / float(r.sample_rate * r.channels * 2)
                            time.sleep(d)
                            t += d

                        else:
                            self.__sound.play(data)
            yield

            stream = self.sound_file.read(512)

        try:
            while self.__sound.isPlaying():
                time.sleep(.05)

        except AttributeError:
            pass

    def play(self):

        if self.__paused:
            self.__sound.unpause()
            self.__paused = False

        if self.__queue:
            self.__queue.next()

        else:
            self.__queue = self.__player()

    def pause(self):
        self.__sound.pause()
        self.__paused = True
 
    def stop(self):
        if self.__sound:
            self.__sound.stop()

        self.__queue = None

    def load(self, file_path):
        self.sound_file.close() if self.sound_file else None
        self.__demuxer = muxer.Demuxer(file_path.split('.')[-1].lower())
        self.sound_file = file(file_path, 'rb')

    def volume(self, value):
        self.__sound.setVolume(value) if self.__sound else None


class SoundManager(object):

    u"""
    Управляющий класс.
    Предоставляет интерфейсные функции для управления воспроизведением
    """

    # todo Вообще, это жесть!!!! Один класс на два потока.... WTF?????

    sound = Sound(0, 1, -1)
    __play_id = None
    __status = None
    __fade_out_status = False
    __volume_level = 65535
    __sound_stream = None
    __connection = Queue()
    fade_out_config = {
        'start_time': None,
        'duration': 4,
        'normal_volume': 65535,
        'current_volume': 65535,
        'decrease_value': None,
        'time_step': 200
    }

    PLAY_STATUS = 'play'
    STOP_STATUS = 'stop'
    PAUSE_STATUS = 'pause'

    def __init__(self):
        self.__sound_stream = Process(target=self.manager, args=(self.__connection,))

    def manager(self, request):
        u"""
        Метод для перенаправления управляющих комманд в поток воспроизведения
        """

        def get_new_fade_out_action():

            normal_volume_level = 65535
            duration = 4
            step = 200
            to_ms = lambda x: x * 1000
            dec = normal_volume_level / (to_ms(duration) / step)

            if self.sound:
                self.sound.volume(normal_volume_level)

            def action():

                current_time = time.time()

                if to_ms(current_time - action.last_started_time) >= step:
                    action.volume_value -= dec
                    self.sound.volume(action.volume_value if action.volume_value > 0 else 0)
                    action.last_started_time = current_time

            action.volume_value = normal_volume_level
            action.last_started_time = time.time()

            return action

        caller = None

        def stop_action():
            self.sound.stop()
            actions['fade_out'][0] = get_new_fade_out_action()

        actions = {
            self.PLAY_STATUS: self.sound.play,
            self.STOP_STATUS: stop_action,
            self.PAUSE_STATUS: self.sound.pause,
            'fade_out': [get_new_fade_out_action(), self.sound.play]
        }

        get_new_fade_out_action()
        block_stream = False

        while True:

            if not request.empty() or block_stream:

                if block_stream:
                    while not request.empty():
                        request.get()

                data = request.get()

                if 'action' in data:
                    caller = data['action']

                elif 'load' in data:
                    self.sound.load(data['load'])

                block_stream = False

            if caller:
                try:
                    funcs = actions[caller]
                    map(lambda x: x(), funcs) if hasattr(funcs, '__iter__') else funcs()

                    # block_stream = False if caller in (self.PLAY_STATUS, 'fade_out') else True

                except StopIteration:
                    actions[self.STOP_STATUS]()
                    block_stream = True

    def play(self):
        u"""
        Управляющая комманда 'ВОСПРОИЗВЕДЕНИЕ'
        """
        self.__status = self.PLAY_STATUS
        self.__sound_stream.start() if not self.__sound_stream.is_alive() else None
        self.__connection.put({'action': self.__status})

    def stop(self):
        u"""
        Управляющая комманда 'ОСТАНОВКА'
        """
        try:
            self.__status = self.STOP_STATUS
            self.__connection.put({'action': self.__status})

        except Exception:
            print 'Error in stop-command'

    def pause(self):
        u"""
        Управляющая комманда 'ПАУЗА'
        """
        if self.__status != self.STOP_STATUS:

            if self.__status == self.PLAY_STATUS:
                self.__status = self.PAUSE_STATUS
                self.__connection.put({'action': self.__status})

            else:
                self.play()

    def load(self, file_name):
        u"""
        Загрузка файла
        """
        self.__sound_stream.start() if not self.__sound_stream.is_alive() else None
        self.__connection.put({'load': file_name})
        self.sound.length = MP3(file_name).info.length

    def fade_out(self):
        u"""
        Управляющая комманда на 'FADE_OUT'
        """
        self.__connection.put({'action': 'fade_out'})

    def __fade_out_action(self):
        cur_time = time.time()

        def decrease_or_reset():
            u"""
            Понижает или восстанавливает уровень звука
            """

            if self.fade_out_config['current_volume'] >= 0:
                self.fade_out_config['current_volume'] -= self.fade_out_config['decrease_value']
                self.sound.volume(self.fade_out_config['current_volume'])

            else:
                self.sound.volume(self.fade_out_config['normal_volume'])

            return self.fade_out_config['current_volume']

        if not self.fade_out_config['start_time']:

            self.fade_out_config['start_time'] = cur_time
            self.fade_out_config['decrease_value'] = self.fade_out_config['normal_volume'] / (self.fade_out_config['duration'] * 1000 / self.fade_out_config['time_step'])
            self.fade_out_config['current_volume'] = self.fade_out_config['normal_volume']
            decrease_or_reset()

        elif (cur_time - self.fade_out_config['start_time']) * 1000 >= self.fade_out_config['time_step']:

            self.fade_out_config['start_time'] = cur_time
            decrease_or_reset()

    @property
    def length(self):
        return self.sound.length

    def destroy(self):
        u"""
        Уничтожение всех потоков при закрытии
        """
        try:
            self.__sound_stream.terminate() if self.__sound_stream else None

        except AttributeError:
            pass