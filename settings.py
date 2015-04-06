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
        return match.group()

    else:
        return None


def set_music_dir(folder):
