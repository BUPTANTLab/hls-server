#! /usr.bin/env python2

# zzz

import os.path
from subprocess import Popen, PIPE
import logging

real_transcode = True

class Transcoder(object):
    """
    call x264 in system, transcode for HLS
    """

    def __init__(self, ffmpeg_path=None):
        if ffmpeg_path is None:
            ffmpeg_path = 'x264'
        self.ffmpeg_path = ffmpeg_path

    def transcode(self, input_file, output_file, opts):
        """
        transcode input file to output
        """
        if not os.path.exists(input_file):
            raise Exception("Input file does not exist: " + input_file)
        cmds = [self.ffmpeg_path, '--input-res', '1280x720', '--preset', 'ultrafast', '-B']
        cmds.extend(opts)
        cmds.extend(['-o', output_file, input_file])
        try:
            p = Popen(cmds, shell=False, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        except OSError:
            raise Exception('Error calling x264')
        ret = ''
        while True:
            buf = p.stderr.read(10)
            if not buf:
                break
            ret += buf
        return 0
