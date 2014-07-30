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

    def Add(self, sample):
        if self.m_numSamples > 0 and self.m_currentKernel != 0:
            fraction = (sample - self.m_currentKernel) / self.m_currentKernel
            if fraction > self.m_upFraction or fraction < self.m_downFraction:
                self.ResetSlidingWindow()
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
        self.m_currentTime = datetime.datetime.now()
        self.m_previousKernel = self.m_currentKernel
        self.m_currentKernel = self.m_sum / self.m_numSamples
        elapsedTime = (self.m_currentTime - self.m_previousTime) / 1000
        if elapsedTime.seconds > 0:
            self.m_currentSlope = (self.m_currentKernel - self.m_previousKernel) / elapsedTime.seconds

    def ResetSlidingWindow(self):
        self.m_numSamples = 0
        self.m_nextSample = 0
        self.m_sum = 0
        self.m_currentSlope = 0
        self.m_currentKernel = 0
        self.m_currentTime = datetime.datetime.now()

    def __init__(self, windowSize, upFraction, downFraction, slopeThreshold):
        self.ResetSlidingWindow()
        self.m_upFraction = upFraction
        self.m_downFraction = downFraction
        self.m_slopeThreshold = slopeThreshold
        self.m_samples = [0] * windowSize
        self.Length = windowSize

class MediaChunk:
    def __init__(self, d, i, cd, b):
        self.downloadBandwidth = d
        self.ChunkId = i
        self.chunkDuration = cd
        self.buffer = b

class NetworkMediaInfo:
    PreviousBitrate = 0
    NextBitrate = 0
    DownloadBandwidthWindow = sWin(3, 0.4, 0.2, 0)
    BufferFullnessWindow = sWin(3, 0.5, 0.2, 0.5)
    DownloadState = 0
    IsLimitBitrateSteps = False
    PreviousAttempt = 0
    bitrate = []
    PreviousAttempt = 0
    TotalStreamDownloaded = 0

    def __init__(self, m):
        m.sort()
        self.bitrate = m

    def AttemptImprovingBitRate(self):
        elapsedTimeSinceLastAttempt = self.TotalStreamDownloaded - self.PreviousAttempt
        newBitRate = self.PreviousBitrate
        if elapsedTimeSinceLastAttempt >= 5:
            newBitRate = self.GetNextBitRate(1)
            if newBitRate > self.PreviousBitrate:
                if newBitRate >= self.DownloadBandwidthWindow.m_currentKernel:
                    newBitRate = self.PreviousBitrate
                else:
                    self.PreviousAttempt = self.TotalStreamDownloaded
            else:
                newBitRate = self.PreviousBitrate
        return self.FindClosestBitrateByValue(newBitRate)

    def GetNextBitRate(self, step):
        index = 0
        for i in self.bitrate:
            if self.PreviousBitrate == i:
                break
            index += 1
        index += step
        return self.FindClosestBitrateByIndex(index)

    def ResetImprovingBitRate(self):
        self.PreviousAttempt = 0

    def FindClosestBitrateByIndex(self, index):
        if index < 0:
            return self.FindDefaultBitrate()
        elif index >= len(self.bitrate):
            return self.bitrate[len(self.bitrate)-1]
        else:
            return self.bitrate[index]
        return self.FindDefaultBitrate()

    def FindClosestBitrateByValue(self, b):
        for i in self.bitrate[::-1]:
            if i <= b:
                return i
        return self.FindDefaultBitrate()

    def FindDefaultBitrate(self):
        return self.bitrate[0]

def GetNextBitRateUsingBandwidth(networkMediaInfo, chunkDuration):
#    pdb.set_trace()
    bitRateCond1 = int(networkMediaInfo.DownloadBandwidthWindow.m_currentKernel / 1.25)
    bitRateCond2 = int(networkMediaInfo.DownloadBandwidthWindow.m_currentKernel * networkMediaInfo.BufferFullnessWindow.m_currentKernel * (0.8 * 0.8 / chunkDuration))
    bitRateFinal = bitRateCond2 if bitRateCond2 < bitRateCond1 else bitRateCond1
    bitRateCond3 = 1e9
    if networkMediaInfo.IsLimitBitrateSteps == True:
        bitRateIndex = networkMediaInfo.PreviousBitrate + 1
        bitRateCond3 = bitRateIndex
        if bitRateFinal <bitRateCond3:
            bitRateFinal = bitRateCond3
    return bitRateFinal

class H:
   # networkMediaInfo = NetworkMediaInfo([256000, 512000, 768000, 1024000])
    networkMediaInfo = NetworkMediaInfo([100000, 200000, 300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000, 1100000])
    m_packetPairBandwidth = 0

    def process(self, chunk):
#       pdb.set_trace()
        self.networkMediaInfo.PreviousBitrate = self.networkMediaInfo.NextBitrate
        bufferFullness = chunk.buffer
        self.networkMediaInfo.BufferFullnessWindow.Add(bufferFullness)
        downloadBandwidth = chunk.downloadBandwidth
        if downloadBandwidth > 1e9:
            downloadBandwidth = 1e9
        if chunk.ChunkId < 2:
            if chunk.ChunkId == 0:
                self.m_packetPairBandwidth = downloadBandwidth
            else:
                if downloadBandwidth > self.m_packetPairBandwidth:
                    self.m_packetPairBandwidth = downloadBandwidth
            self.m_cacheBandwidth = 5 * self.m_packetPairBandwidth
            if self.m_cacheBandwidth < 2 * 1000 * 1000:
                self.m_cacheBandwidth = 2 * 1000 * 1000
        if downloadBandwidth < self.m_cacheBandwidth:
            self.networkMediaInfo.DownloadBandwidthWindow.Add(downloadBandwidth)
        else:
            downloadBandwidth = self.networkMediaInfo.DownloadBandwidthWindow.m_currentKernel
        self.networkMediaInfo.TotalStreamDownloaded += chunk.chunkDuration
        currentBitRateSelected = 0

        if self.networkMediaInfo.DownloadState == 0:
            self.networkMediaInfo.IsLimitBitrateSteps = False
            if downloadBandwidth > 20 * 1000 * 1000:
                self.networkMediaInfo.IsLimitBitrateSteps = True
            if self.networkMediaInfo.IsLimitBitrateSteps == False and (self.networkMediaInfo.BufferFullnessWindow.IsDecreasing == True or self.networkMediaInfo.BufferFullnessWindow.IsSlowChanging == True):
                self.networkMediaInfo.IsLimitBitrateSteps = True
            currentBitRateSelected = GetNextBitRateUsingBandwidth(self.networkMediaInfo, chunk.chunkDuration)
            currentBitRateSelected = self.networkMediaInfo.FindClosestBitrateByValue(currentBitRateSelected)
            if bufferFullness >= 14.5:
                self.networkMediaInfo.RelativeContentDownloadSpeed = 1.25
                self.networkMediaInfo.DownloadState = 1
        else:
            self.networkMediaInfo.IsLimitBitrateSteps = False
            if downloadBandwidth >= 20 * 1000 * 1000:
                self.networkMediaInfo.IsLimitBitrateSteps = True
            if bufferFullness < 7:
                currentBitRateSelected = self.networkMediaInfo.FindDefaultBitrate()
                self.networkMediaInfo.ResetImprovingBitRate()
                self.networkMediaInfo.DownloadState = 0
            elif self.networkMediaInfo.BufferFullnessWindow.IsSlowChanging:
                if bufferFullness < 12:
                    currentBitRateSelected = self.networkMediaInfo.GetNextBitRate(-1)
                    self.networkMediaInfo.ResetImprovingBitRate()
                elif bufferFullness > 17:
                    currentBitRateSelected = self.networkMediaInfo.AttemptImprovingBitRate()
                else:
                    currentBitRateSelected = self.networkMediaInfo.FindClosestBitrateByValue(self.networkMediaInfo.PreviousBitrate)
            elif self.networkMediaInfo.BufferFullnessWindow.IsFastDecreasing:
                if bufferFullness < 12:
                    currentBitRateSelected = self.networkMediaInfo.FindDefaultBitrate()
                    self.networkMediaInfo.ResetImprovingBitRate()
                    self.networkMediaInfo.DownloadState = 0
                else:
                    currentBitRateSelected = self.networkMediaInfo.FindClosestBitrateByValue(self.networkMediaInfo.PreviousBitrate)
            else:
                currentBitRateSelected = self.networkMediaInfo.AttemptImprovingBitRate()
        self.networkMediaInfo.NextBitrate = currentBitRateSelected
    
if __name__ == '__main__':
        try:
            h = H()
            buffer = 0
            limit = 900000.0
            for i in range(300):
                if i > 100:
                    limit = 500000.0
                if i > 200:
                    limit = 800000.0
                buffer = buffer + 2 - h.networkMediaInfo.NextBitrate * 2.0 / limit
                h.process(MediaChunk(limit, i, 2, buffer))
                print i, h.networkMediaInfo.NextBitrate, limit, buffer
        except KeyboardInterrupt:
            print 'over!'
        exit(0)
