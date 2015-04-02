#!/usr/bin/env python

import datetime
import pdb


class sWin:
    def IsDecreasing(self):
        return self.m_currentSlope < 0

    def IsFastDecreasing(self):
        return self.m_currentSlope < -self.m_slopeThreshold

    def IsFastIncreasing(self):
        return self.m_currentSlope > self.m_slopeThreshold

    def IsIncreasing(self):
        return self.m_currentSlope > 0

    def IsSlowChanging(self):
        return self.m_currentSlope >= -self.m_slopeThreshold and self.m_currentSlope <= self.m_slopeThreshold

    def IsSlowDecreasing(self):
        return self.m_currentSlope < 0 and self.m_currentSlope >= -self.m_slopeThreshold

    def IsSlowIncreasing(self):
        return self.m_currentSlope > 0 and self.m_currentSlope <= self.m_slopeThreshold

    def Add(self, sample, milli_time):
        if self.m_numSamples > 0 and self.m_currentKernel != 0:
            fraction = (sample - self.m_currentKernel) / self.m_currentKernel
            if fraction > self.m_upFraction or fraction < self.m_downFraction:
                self.ResetSlidingWindow(self.m_currentTime)
        if self.m_numSamples < self.Length:
            self.m_numSamples += 1
            self.m_sum += sample
        else:
            self.m_sum -= self.m_samples[self.m_nextSample]
            self.m_sum += sample
        self.m_samples[self.m_nextSample] = sample
        self.m_nextSample += 1
        if self.m_nextSample >= self.Length:
            self.m_nextSample = 0
        self.m_previousTime = self.m_currentTime
        self.m_currentTime += milli_time
        self.m_previousKernel = self.m_currentKernel
        self.m_currentKernel = self.m_sum / self.m_numSamples
        elapsedTime = (self.m_currentTime - self.m_previousTime) / 1000
        if elapsedTime > 0:
            self.m_currentSlope = (self.m_currentKernel - self.m_previousKernel) / elapsedTime
        #print self.m_currentKernel - self.m_previousKernel, elapsedTime, self.m_currentSlope

    def ResetSlidingWindow(self, c):
        self.m_numSamples = 0
        self.m_nextSample = 0
        self.m_sum = 0
        self.m_currentSlope = 0
        #self.m_currentKernel = 0
        self.m_currentTime = c

    def __init__(self, windowSize, upFraction, downFraction, slopeThreshold):
        self.ResetSlidingWindow(0)
        self.m_currentKernel = 0
        self.m_upFraction = upFraction
        self.m_downFraction = downFraction
        self.m_slopeThreshold = slopeThreshold
        self.m_samples = [0] * windowSize
        self.Length = windowSize

m = range(200,3100,100)
mm = sWin(3, 0.4, 0.2, 0)
BufferFullnessWindow = sWin(3, 0.5, 0.2, 0.1)

if __name__ == '__main__':
        file_object = open('test2')
        all_the_text = file_object.readlines()
        file_object.close()
        try:
            h = 0
            buffer = 0
            i=0
            for limitstr in all_the_text :
                limit = float(limitstr)
                i = i + 1
                #buffer = buffer + 2 -(0.0237 * m[h]/100 + 2.8)/5.0 - m[h] * 2.0 / limit
                buffer = buffer + 2 - m[h] * 2.0 / limit
#                buffer = buffer + 2 - h.networkMediaInfo.NextBitrate * 2.0 / limit
#               mm.Add(limit, m[h] * 2000.0 / limit)
                BufferFullnessWindow.Add(buffer, m[h] * 2000.0 / limit)
#                if buffer > 18:
#                       h = max(int(mm.m_currentKernel / 100), h + 1)
                if buffer > 16:
                        h += 1
                elif BufferFullnessWindow.IsFastIncreasing():
                        h += 1
                if buffer < 4:
                        h = 0
                elif BufferFullnessWindow.IsDecreasing():
                        h -= 1

                if h < 0:
                        h = 0
                elif h >= len(m):
                        h = len(m) - 1
                print i, m[h], limit, buffer, BufferFullnessWindow.m_currentSlope
        except KeyboardInterrupt:
            print 'over!'
        exit(0)
