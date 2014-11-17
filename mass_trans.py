#!/usr/bin/env python

import os
import time
from transcoder import Transcoder

tr = Transcoder()
for i in range(100,3100,100):
        time1= time.time()
#       success = tr.transcode(input_file="/tmp/test-1.yuv", output_file="/tmp/"+str(i)+".264", opts=[str(i)])
        success = tr.transcode(input_file="/tmp/test-1.264", output_file="/tmp/"+str(i)+".mp4", opts=['-vcodec', 'libx264', '-vpre', 'ultrafast', '-b', str(i)+'k' ])
        print i, time.time() - time1
