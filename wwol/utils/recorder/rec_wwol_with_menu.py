# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Mikhail Salin. Contacts: mikesalin@gmail.com
# All rights reserved.
#
"""
This tool is to record videos form a webcam or webcam-alike device according 
to a schedule, i.e. with equal pauses between files and skipping specified 
hours. The first file is recoded immediately, the others are recorded at round
time moments. The files are named according to their starting time. 
All parameters are controlled by a configuration file 'recorder.json'.
Video recording is made by a call to the provided shell command, which is
supposed to be a call to ffmpeg with proper arguments. 

This python script starts with a text menu in the console. 
The other provided script starts at once.
"""

import sys
import os
import glob
import subprocess
import json
from string import Template
import time

import rec_wwol_act as act

__version__='0.1'
__year__ = 2023


platform_specific = {
    'macos':{
        'list_command':'${FFMPEG} -f avfoundation -list_devices true -i ""',
        'work_command':'${FFMPEG} -f avfoundation -framerate 30 -i "0" -vframes ${LENGTH_IN_FRAMES} ${OUT_FORMAT} ${FILENAME}'
    },
    'win':{
        'list_command':'${FFMPEG} -f dshow -list_devices true -i dummy',
        'work_command':'${FFMPEG} -f dshow -r 30 -i video=\"USB Video\" -vframes ${LENGTH_IN_FRAMES} ${OUT_FORMAT} ${FILENAME}'
    },
    'unkn':{
        'list_command':'',
        'work_command':''
    }
}
the_platform = 'unkn'
if (sys.platform == 'win32'):  the_platform = 'win'
if (sys.platform == 'darwin'): the_platform = 'macos'


def ffmpeg_name():
    try:
        with open(act.JSON_FNAME, 'rt') as f:
            config = json.load(f)
        return act.put_quotes_if_needed(config['ffmpeg'])
    except:
        pass
    print('WARN: Cannot get the ffmpeg name (path) form your config file')
    print('This is not a error yet but may cause problems')
    return 'ffmpeg'


def list_devices():
    command_line = Template(
        platform_specific[the_platform]['list_command']).substitute(
        FFMPEG = ffmpeg_name())
    try:
        subprocess.check_call(command_line, shell=True)
    except:
        pass
    print('HINT: the command was:')
    print(command_line)


def backup(filename):
    lst = glob.glob(filename)
    for item in lst:
        if len(item) > 4:
            if item[-4:] == '.bak': continue
        bakname = item+'.bak'
        if os.path.isfile(bakname):
            os.remove(bakname)
        os.rename(item, item+'.bak')


def write_default_config():
    defconfig = {
        "ffmpeg":"ffmpeg",
        "command":platform_specific[the_platform]['work_command'],
        "out_format":"-f mpeg -codec:v mpeg2video -qscale:v 2 -codec:a mp2",
        "save_to_dir":"",\
        "filename_pattern":"%Y-%m-%d_%H-%M-%S.mpg",
        "length_in_frames":90,
        "period_in_seconds":60,
        "skip_hours_from":21,
        "skip_hours_to":6
    }
    json_fname = act.JSON_FNAME
    backup(json_fname)
    with open(json_fname, 'wt') as f:
        json.dump(defconfig, f, indent=0)
    print('Default config has been written to: ' + json_fname)
    print('Edit it for your purposes')


def screenshots():
    try:
        with open(act.JSON_FNAME, 'rt') as f:
            config = json.load(f)
    except:
        print('ERROR: Cannot load config')
        return
    ff = ['-f image2', '-f image2']
    ext= ['.bmp', '.jpg']
    result_names_examples = [ ]
    for turn in range(0,2):
        fname = time.strftime(config['filename_pattern'])
        fname = fname[:fname.rfind('.')] + '_%03d' + ext[turn]
        fname = os.path.join(config['save_to_dir'], fname)
        command_line = Template(config['command']).substitute(
            FFMPEG = act.put_quotes_if_needed(config['ffmpeg']),
            LENGTH_IN_FRAMES = '32',
            FILENAME = act.put_quotes_if_needed(fname),
            OUT_FORMAT = ff[turn])
        try:
            subprocess.check_call(command_line, shell=True)
        except subprocess.CalledProcessError as err:
            print('ERROR: call failed')
            print(str(err))
            return
        result_names_examples.append(fname % 1)
        result_names_examples.append(fname % 32)
    print('Done. Saved files:')
    print(result_names_examples[0] + ' .. ' + result_names_examples[1])
    print(result_names_examples[2] + ' .. ' + result_names_examples[3])


def main():
    print('VIDEO RECORDING UTILITY for WWOL ver. ' + __version__)
    print('(c) %d Mikhail Salin, contacts: mikesalin@gmail.com' % __year__)

    while True:
        # Here comes an endless loop, displaying menu
        print(
"""
1  List devices
2  Write default config to file
3  Make screenshots to test
5  Start recording
0  Quit
"""
        )
        s_val = input('Your choice: ')
        try:
            val = int(s_val)
        except:
            print('Not a number')
            continue
        if val == 0:
            return
        
        val_parsed = False
        if val == 1:
            list_devices()
            val_parsed = True
        if val == 2:
            write_default_config()
            val_parsed = True
        if val == 3:
            screenshots()
            val_parsed = True
        if val == 5:
            act.main()
            val_parsed = True
        
        if not val_parsed:
            print('Not a valid number')
        time.sleep(0.5)


if __name__ == '__main__':
    main()