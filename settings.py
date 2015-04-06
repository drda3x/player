#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re

MUSIC_DIR = u'D:/Da3x/Music/hastle'


def get_music_dir():
    settings_file = file('settings.txt', 'r')
    config = settings_file.read()
    match = re.search('MUSIC_DIR = .*$', config)
    settings_file.close()

    if match:
        return u'' + match.group().split(' = ')[-1]

    else:
        return None


def set_music_dir(folder):

    settings_file = file('settings.txt', 'r')
    config = settings_file.read()
    settings_file.close()

    match = re.search('MUSIC_DIR = .*$', config)

    if match:
        config = re.sub('MUSIC_DIR = .*$', u'MUSIC_DIR = %s\n' % folder, config)
        print config
    else:
        config += u'MUSIC_DIR = %s\n' % folder

    settings_file = file('settings.txt', 'w')
    settings_file.write(config)
    settings_file.close()