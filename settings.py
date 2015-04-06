#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re


def get_music_dir():
    settings_file = file('settings.txt', 'r')
    config = settings_file.read().decode('utf-8')
    match = re.search('MUSIC_DIR = .*\n?', config)
    settings_file.close()

    if match:
        return re.sub('\n', '', match.group().split(' = ')[-1])

    else:
        return None


def set_music_dir(folder):

    settings_file = file('settings.txt', 'r')
    config = settings_file.read()
    settings_file.close()

    match = re.search('MUSIC_DIR = .*\n?', config)

    if match:
        config = re.sub('MUSIC_DIR = .*\n?', u'MUSIC_DIR = %s\n' % folder, config)
    else:
        config += u'MUSIC_DIR = %s\n' % folder

    settings_file = file('settings.txt', 'w')
    settings_file.write(config.encode('utf-8'))
    settings_file.close()