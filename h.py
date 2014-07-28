#!/usr/bin/env python

class MediaChunk:
    def __init__(self):

class NetworkMediaInfo:
    def __init__(self):

class H:
    def __init__(self):
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
                networkMediaInfo.RelativeContentDownloadSpeed = sm_NetworkHeuristicsParams.RelativeContentDownloadSpeed
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
