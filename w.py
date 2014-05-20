#!/usr/bin/env python

import random
import threading
import pickle
import os

class W:
    def loadQ(self):
        with open('qsaving.bin','rb') as f:
            self.Q = pickle.load(f)
        
    def dumpQ(self):
        with open('qsaving.bin','wb') as f:
            pickle.dump(self.Q,f,-1)
        
    def __init__(self):
        self.Gamma = 0.95
        self.Alpha = 0.3
        self.N = 28#//Max quality levels/Actions-1
        self.BFmax = 40
        if not os.path.exists("qsaving.bin"):
            self.Q=[[50.0 for x in range(29 + 1)] for y in range(29 * 9)]
        else:
            self.loadQ()
        self.rate = range(200,3100,100)
        self.mutex = threading.Lock()
    
    def getrate(self,bw1,bf1,bw2,bf2,rate,brate):
        #init
        bw1 = min(3000, max(bw1, 200))
        bw2 = min(3000, max(bw2, 200))
        bf1 = min(40, max(bf1, 0))
        bf2 = min(40, max(bf2, 0))
        Qbf1 = int(bf1 / 10)
        Qbw1 = int((bw1 - 200) / 100)
        state1 = Qbw1 * 9 + Qbf1
        Qbf2 = int(bf2 / 10)
        Qbw2 = int((bw2 - 200) / 100)
        state2 = Qbw2 * 9 + Qbf2
        #calc the rate
        Rq = 0.0 + int((rate - 200) / 100) - self.N
        Rs = 0.0 - 1 * int(abs((rate - brate) / 100))
        if bf2 == 0:
            Rb = -500.0
        else:
            Rb = 0.0 + bf2 - bf1
        R = Rq / 28 + Rs / 5 + Rb / 40
        amax = -10000
        action = 0
        #choose the point
        for i in range(29):
            if i < int((rate - 200) / 100) - 5 and (bf2 > 10 and bf1 > 10):
                continue
            if i > int((rate - 200) / 100) + 3:
                break
#           print self.Q[state2][i],i,action,state1,int((rate - 200) / 100)
            if self.Q[state2][i] > amax:
                amax = self.Q[state2][i]
                action = i
        #updateQ
        self.mutex.acquire()
        self.Q[state1][int((rate - 200) / 100)] = (1 - self.Alpha) * self.Q[state1][int((rate - 200) / 100)] + self.Alpha * (amax * self.Gamma + R)
        self.dumpQ()
        self.mutex.release()  
        #count
        self.Q[state1][29] = self.Q[state1][29] + 1
        return self.rate[action]

if __name__ == '__main__':
        try:
            w=W()
            limit=1500
            bw=limit
            bf=0
            orate=200
            nrate=200
            for i in range(100):
                bw2=limit-100+random.randint(0,100)
                bf2=max(bf,0)+10-nrate*10/bw2
                print bw,bf,bw2,bf2,orate,nrate
                r = w.getrate(bw,bf,bw2,bf2,nrate,orate)
                bw=bw2
                bf=bf2
                orate=nrate
                nrate=r
        except KeyboardInterrupt:
            print 'over!'
        exit(0)
