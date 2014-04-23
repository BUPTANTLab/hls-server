#! /usr.bin/env python

# zzz

import os.path
from subprocess import Popen, PIPE
import logging

real_transcode = True

class Transcoder(object):
    """
    call ffmpeg in system, transcode for HLS
    """

    def __init__(self, ffmpeg_path=None):
        if ffmpeg_path is None:
            ffmpeg_path = 'ffmpeg'
        self.ffmpeg_path = ffmpeg_path

    def transcode(self, input_file, output_file, bit, fake = False):
        """
        transcode input file to output
        """
#        if not os.path.exists(input_file):
#            raise Exception("Input file does not exist: " + input_file)
        if fake:
            bit = int(bit/100)*100
            input_file = input_file.replace('repo' , 'repo/' + str(bit))
            cmds = ["cp","-f",os.getcwd() +  input_file , output_file]
            print " ".join(cmds)
            p = Popen(cmds, shell=False, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
            return 0
        cmds = [self.ffmpeg_path, '-i', input_file]
        #cmds.extend(['-vbsf h264_mp4toannexb'])
        cmds.extend(['-vcodec', 'libx264', '-b', str(bit) + 'k', '-ab', '96k', '-vpre', 'ultrafast'])
        cmds.extend(['-y', output_file])
        try:
            #print 'ffmpeg command: ' + ' '.join(cmds)
            p = Popen(cmds, shell=False, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        except OSError:
            raise Exception('Error calling ffmpeg')
        ret = ''
        while True:
            buf = p.stderr.read(10)
            if not buf:
                break
            ret += buf
        return 0
