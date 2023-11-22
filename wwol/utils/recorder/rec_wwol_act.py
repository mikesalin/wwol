# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Mikhail Salin. Contacts: mikesalin@gmail.com
# All rights reserved.
#

import os
import glob
import subprocess
import json
from string import Template
import time


JSON_FNAME = 'config.json'


class PrintAndLog:
    def __init__(self):
        self.file_is_open = False
    def __call__(self, text):
        date_time_text = time.strftime('%Y/%m/%d %H:%M:%S  ') + text
        print(date_time_text)
        if not self.file_is_open:
            self.f = open(time.strftime('%Y-%m-%d_%H-%M-%S.log'),'wt')
            self.file_is_open = True
        self.f.write(date_time_text)
        self.f.write('\n')
        self.f.flush()
    def close(self):
        if self.file_is_open:
            self.f.close()
            self.file_is_open = False
print_and_log = PrintAndLog()


def put_quotes_if_needed(text):
    if ' ' in text:
        text = '"' + text + '"'
    return text


def main():
    # load config
    json_fname = JSON_FNAME
    try:
        with open(json_fname, 'rt') as f:
            config = json.load(f)
    except:
        print_and_log('ERROR: Cannot load config')
        print_and_log('HINT: using file: ' + json_fname)
        return
    
    # minor config format check, sorry to say (
    check_int = ['period_in_seconds', 'skip_hours_from', 'skip_hours_to']
    for item_name in check_int:
        if not isinstance(config[item_name], int):
            print_and_log('ERROR: bad config, ' + item_name)
            return

    print_and_log('NEW SESSION')

    # here goes an endless loop for all recording sessions
    while True:
        print_and_log('NEW RECORDING')
        fname = time.strftime(config['filename_pattern'])
        fname = os.path.join(config['save_to_dir'], fname)
        command_line = Template(config['command']).substitute(
            FFMPEG = put_quotes_if_needed(config['ffmpeg']),
            LENGTH_IN_FRAMES = '%d' % config['length_in_frames'],
            FILENAME = put_quotes_if_needed(fname),
            OUT_FORMAT = config['out_format'])
        try:
            subprocess.check_call(command_line, shell=True)
        except subprocess.CalledProcessError as err:
            print_and_log('ERROR: call failed')
            print_and_log(str(err))
            #print_and_log('HINT: the command was:')
            #print_and_log(command_line)
            print_and_log.close()
            return
        print_and_log('Done writing: ' + fname)

        now = time.time()
        period = config['period_in_seconds']
        to_next_rec = period - (now % period)
        for n in range(0, 24*3600//period):
            h = time.localtime(now + to_next_rec).tm_hour
            if _is_good_hour(h,
                             config['skip_hours_from'],
                             config['skip_hours_to']):
                break
            to_next_rec = to_next_rec + period
        print_and_log(
            time.strftime('Next record at %Y/%m/%d %H:%M:%S', 
                time.localtime(now + to_next_rec) ) )
        time.sleep(to_next_rec)


def _is_good_hour(value, skip_hours_from, skip_hours_to):
    over_midnight = skip_hours_to < skip_hours_from
    if over_midnight:
        return (value < skip_hours_from) and (value >= skip_hours_to)
    else:
        return (value < skip_hours_from) or (value >= skip_hours_to)


if __name__ == '__main__':
    main()


