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

    def __init__(self, card, rate, tt):
        self.__card = card
        self.__rate = rate
        self.__tt = tt

        if self.__card not in range(len(self.__devises)):
            raise 'Cannot play sound to non existent device %d out of %d' % (self.__card + 1, len(self.__devises))

    def play(self):
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

    def pause(self):
        pass

    def stop(self):
        self.__sound.stop()

    def load(self, file_path):
        self.__demuxer = muxer.Demuxer(file_path.split('.')[-1].lower())
        self.__sound_file = file(file_path, 'rb')
