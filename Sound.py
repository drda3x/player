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


class Sound(object):

    __EMULATE = 0
    __demuxer = None
    __devises = sound.getODevices()
    __sound_file = None
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
        stream = self.__sound_file.read(32000)
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

                        data = re_sampler.resample(r.data) if re_sampler else r.data

                        if self.__EMULATE:
                            # Calc delay we should wait to emulate snd.play()

                            d = len(data) / float(r.sample_rate * r.channels * 2)
                            time.sleep(d)
                            t += d

                        else:
                            self.__sound.play(data)
            yield

            stream = self.__sound_file.read(512)

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
        self.__sound.stop()
        self.__sound_file.seek(0)
        self.__queue = None

    def load(self, file_path):
        self.__demuxer = muxer.Demuxer(file_path.split('.')[-1].lower())
        self.__sound_file = file(file_path, 'rb')

    def volume(self, value):
        self.__sound.setVolume(value)

    @property
    def is_playing(self):
        return self.__sound.isPlaying()


class SoundManager(object):

    sound = Sound(0, 1, -1)
    main_stream = None
    __play_id = None
    __status = None
    __fade_out_status = False
    __volume_level = 65535
    fade_out_dur = 4

    PLAY_STATUS = 'play'
    STOP_STATUS = 'stop'
    PAUSE_STATUS = 'pause'

    def __init__(self, main_stream):
        self.main_stream = main_stream

    def play(self):

        self.__status = self.PLAY_STATUS

        def loop():

            if self.__status == self.PLAY_STATUS:
                self.sound.play()
                self.__play_id = self.main_stream.after(0, loop)
            else:
                self.main_stream.after_cancel(self.__play_id)

        self.__play_id = self.main_stream.after(0, loop)

    def stop(self):
        try:
            self.sound.stop()
            self.__status = self.STOP_STATUS

        except Exception:
            pass

    def pause(self):
        if self.__status != self.STOP_STATUS:

            if self.__status == self.PLAY_STATUS:
                self.__status = self.PAUSE_STATUS
                self.sound.pause()

            else:
                self.play()

    def load(self, file_name):
        self.sound.load(file_name)

    def __get_fade_out_params(self):

        t = 200

        time_int = self.fade_out_dur * 1000 / t

        return {
            'time': t,
            'level': 65535 / time_int
        }

    def fade_out(self):

        if not self.__fade_out_status:

            def action():
                params = self.__get_fade_out_params()
                self.__volume_level -= params['level']
                self.sound.volume(self.__volume_level)

                if self.__volume_level >= 0:
                    self.__fade_out_status = True
                    self.main_stream.after(params['time'], action)

                else:
                    self.__fade_out_status = False
                    self.reset_volume()

            action()

    def reset_volume(self):
        self.__volume_level = 65535
        self.sound.volume(self.__volume_level)

    @property
    def is_playing(self):
        return self.sound.is_playing