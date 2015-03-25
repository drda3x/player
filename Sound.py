#! /usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Пакет для работы со звуком
1. Воспроизведение
2. Остановка
3. Пауза
"""

import time
import pymedia.muxer as muxer
import pymedia.audio.acodec as acodec
import pymedia.audio.sound as sound

from multiprocessing import Process, Queue

from mutagen.mp3 import MP3


class Sound(object):

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

        while self.__sound.isPlaying():
            time.sleep(.05)

    def play(self):

        if self.__paused:
            self.__sound.unpause()
            self.__paused = False

        try:
            if self.__queue:
                self.__queue.next()

            else:
                self.__queue = self.__player()

        except StopIteration:
            self.stop()

    def pause(self):
        self.__sound.pause()
        self.__paused = True

    def stop(self):
        self.__sound.stop() if self.__sound else None
        self.sound_file.seek(0) if self.__sound else None
        self.__queue = None

    def load(self, file_path):
        self.__demuxer = muxer.Demuxer(file_path.split('.')[-1].lower())
        self.sound_file = file(file_path, 'rb')

    def volume(self, value):
        self.__sound.setVolume(value)

    @property
    def is_playing(self):
        return self.__sound.isPlaying() > 0 and self.__queue is not None


class SoundManager(object):

    sound = Sound(0, 1, -1)
    __play_id = None
    __status = None
    __fade_out_status = False
    __volume_level = 65535
    __sound_stream = None
    __connection = {
        'send': Queue(),
        'get': Queue()
    }
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

    def manager(self, request, response, file_name):

        caller = None
        data = None
        actions = {
            self.PLAY_STATUS: self.sound.play,
            self.STOP_STATUS: self.sound.stop,
            self.PAUSE_STATUS: self.sound.pause,
            'fade_out': [self.__fade_out_action, self.sound.play]
            }

        self.sound.load(file_name)

        while True:

            try:
                data = request.get(block=False)
            except Exception:
                pass

            if data and 'action' in data:
                caller = data['action']

            if caller:
                funcs = actions[caller]
                map(lambda x: x(), funcs) if hasattr(funcs, '__iter__') else funcs()

            try:

                while not response.empty():
                    response.get(block=False)

                response.put({'is_playing': self.sound.is_playing})
            except AttributeError:
                pass

    def play(self):
        self.__status = self.PLAY_STATUS
        self.__sound_stream.start() if not self.__sound_stream.is_alive() else None
        self.__connection['send'].put({'action': self.__status})

    def stop(self):
        try:
            self.__status = self.STOP_STATUS
            self.__connection['send'].put({'action': self.__status})

        except Exception:
            pass

    def pause(self):
        if self.__status != self.STOP_STATUS:

            if self.__status == self.PLAY_STATUS:
                self.__status = self.PAUSE_STATUS
                self.__connection['send'].put({'action': self.__status})

            else:
                self.play()

    def load(self, file_name):
        self.__sound_stream.terminate() if self.__sound_stream else None
        self.__sound_stream = Process(target= self.manager, args=(self.__connection['send'], self.__connection['get'], file_name))
        self.sound.load(file_name)
        self.sound.length = MP3(file_name).info.length

    def __fade_out_action(self):
        cur_time = time.time()

        def decrease_or_reset():
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

    def fade_out(self):
        self.__connection['send'].put({'action': 'fade_out'})

    @property
    def is_playing(self):
        return self.__connection['get'].get()['is_playing'] if not self.__connection['get'].empty() else False

    @property
    def length(self):
        return self.sound.length

    def destroy(self):
        self.__sound_stream.terminate() if self.__sound_stream else None