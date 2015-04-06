#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re

MUSIC_DIR = u'D:/Da3x/Music/hastle'


def get_music_dir():
    settings_file = file('settings.txt', 'r')
    config = settings_file.read()
    match = re.search('MUSIC_DIR = u\'.*\'$', config)
    settings_file.close()

    if match:
        return match.group().split(' = ')[-1]

    else:
        return None


def set_music_dir(folder):

    settings_file = file('settings.txt', 'r')
    config = settings_file.read()
    settings_file.close()

    match = re.search('MUSIC_DIR = u\'.*\'$', config)

    if match:
        re.sub('MUSIC_DIR = u\'.*\'$', 'MUSIC_DIR = u\'%s\'\n' % folder, config)

    else:
        config += 'MUSIC_DIR = u\'%s\'\n' % folder

    settings_file = file('settings.txt', 'w')
    settings_file.write(config)
    settings_file.close()