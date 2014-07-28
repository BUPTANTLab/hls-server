#!/usr/bin/env python

class sWin:
    m_currentKernel
    m_currentSlope
    m_currentTime = DateTime.Now
    m_downFraction
    m_nextSample
    m_numSamples
    m_previousKernel
    m_previousTime
    m_samples = []
    m_slopeThreshold
    m_sum
    m_upFraction
    
    def __init__(self, windowSize, upFraction, downFraction, slopeThreshold):
        ResetSlidingWindow()
        m_upFraction = upFraction
        m_downFraction = downFraction
        m_slopeThreshold = slopeThreshold
        m_samples = new double[windowSize]

    def IsDecreasing(self):
        return m_currentSlope < 0

    def IsFastDecreasing(self):
        return m_currentSlope < -m_slopeThreshold

    def IsFastIncreasing(self):
        return m_currentSlope > m_slopeThreshold

    def IsIncreasing(self):
        return m_currentSlope > 0

    def IsSlowChanging(self):
        return m_currentSlope >= -m_slopeThreshold && m_currentSlope <= m_slopeThreshold

    def IsSlowDecreasing(self):
        return m_currentSlope < 0 && m_currentSlope >= -m_slopeThreshold

    def IsSlowIncreasing(self):
        return m_currentSlope > 0 && m_currentSlope <= m_slopeThreshold

    def Add(self, sample):
        if m_numSamples > 0 && m_currentKernel != 0:
            fraction = (sample - m_currentKernel) / m_currentKernel
            if fraction > m_upFraction || fraction < m_downFraction:
                ResetSlidingWindow()
        if m_numSamples < m_samples.Length:
            m_numSamples++
            m_sum += sample
        else:
            m_sum -= m_samples[m_nextSample]
            m_sum += sample
        m_samples[m_nextSample] = sample
        m_nextSample++
        if m_nextSample >= m_samples.Length:
            m_nextSample = 0
        m_previousTime = m_currentTime
        m_currentTime = DateTime.Now
        m_previousKernel = m_currentKernel
        m_currentKernel = m_sum / m_numSamples
        elapsedTime = (m_currentTime - m_previousTime) / 1000
        if elapsedTime > 0:
            m_currentSlope = (m_currentKernel - m_previousKernel) / elapsedTime

    def ResetSlidingWindow(self):
        m_numSamples = 0
        m_nextSample = 0
        m_sum = 0
        m_currentSlope = 0
        m_currentKernel = 0
        m_currentTime = DateTime.Now

class MediaChunk:
    def __init__(self):
        Length = 0
        downloadDuration = 0
        ChunkId = 0

class NetworkMediaInfo:
    PreviousBitrate = 0
    NextBitrate = 0
    DownloadBandwidthWindow = sWin()
    BufferFullnessWindow = sWin()
    DownloadState = 0
    IsLimitBitrateSteps = False
    PreviousAttempt = 0

    def ResetImprovingBitRate(self):
        PreviousAttempt = 0

class H:
    networkMediaInfo = NetworkMediaInfo()

    def process(self, chunk):
        networkMediaInfo.PreviousBitrate = networkMediaInfo.NextBitrate
        downloadSize = chunk.Length
        downloadBandwidth = downloadSize * 8 / chunk.downloadDuration
        if downloadBandwidth > 1e9:
            downloadBandwidth = 1e9
        if chunk.ChunkId < 2:
            if chunk.ChunkId == 0:
                m_packetPairBandwidth = downloadBandwidth
            else:
                if downloadBandwidth > m_packetPairBandwidth:
                    downloadBandwidth = m_packetPairBandwidth
            m_cacheBandwidth = 5 * m_packetPairBandwidth
            if m_cacheBandwidth < 2 * 1000 * 1000:
                m_cacheBandwidth = 2 * 1000 * 1000
        if downloadBandwidth < m_cacheBandwidth:
            networkMediaInfo.DownloadBandwidthWindow.Add(downloadBandwidth)
        else:
            downloadBandwidth = networkMediaInfo.DownloadBandwidthWindow.CurrentKernel
        currentBitRateSelected = 0

        if networkMediaInfo.DownloadState == 0:
            networkMediaInfo.IsLimitBitrateSteps = False
            if downloadBandwidth > 20 * 1000 * 1000:
                networkMediaInfo.IsLimitBitrateSteps = true
            if networkMediaInfo.IsLimitBitrateSteps == false && (networkMediaInfo.BufferFullnessWindow.IsDecreasing == true || networkMediaInfo.BufferFullnessWindow.IsSlowChanging == true):
                networkMediaInfo.IsLimitBitrateSteps = true
            currentBitRateSelected = GetNextBitRateUsingBandwidth(networkMediaInfo, chunkDuration)
            if bufferFullness >= (12 + ((17 - 12) / 2)):
                networkMediaInfo.RelativeContentDownloadSpeed = 1.25
                networkMediaInfo.DownloadState = 1
        else:
            networkMediaInfo.IsLimitBitrateSteps = false
            if downloadBandwidth >= 20 * 1000 * 1000:
                networkMediaInfo.IsLimitBitrateSteps = true
            if bufferFullness < 7:
                currentBitRateSelected = 0
                networkMediaInfo.ResetImprovingBitRate()
                networkMediaInfo.DownloadState = 0
            elif networkMediaInfo.BufferFullnessWindow.IsSlowChanging:
                if bufferFullness < 12:
                    currentBitRateSelected = -1
                    networkMediaInfo.ResetImprovingBitRate()
                elif bufferFullness > 17:
                    currentBitRateSelected = 1
                else:
                    currentBitRateSelected = networkMediaInfo.PreviousBitrate
            elif networkMediaInfo.BufferFullnessWindow.IsFastDecreasing:
                if bufferFullness < 12:
                    currentBitRateSelected = 0
                    networkMediaInfo.ResetImprovingBitRate()
                    networkMediaInfo.DownloadState = 0
                else:
                    currentBitRateSelected = networkMediaInfo.PreviousBitrate
            else:
                currentBitRateSelected = 1
        networkMediaInfo.NextBitrate = currentBitRateSelected
    
if __name__ == '__main__':
        try:
            h = H()
        except KeyboardInterrupt:
            print 'over!'
        exit(0)
