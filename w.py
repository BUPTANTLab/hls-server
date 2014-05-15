#!/usr/bin/env python

import random
import threading
import pickle
import os

class W:
    def loadQ(self):
        with open('qsaving.bin','rb') as f:
            self.Q=pickle.load(f)
        
    def dumpQ(self):
        with open('qsaving.bin','wb') as f:
            pickle.dump(self.Q, f,-1)
        
    def __init__(self):
        self.Gamma=0.95
        self.N=28#//Max quality levels/Actions-1
        self.BWlevels=30
        self.BFlevels=2
        self.BFmax=12
        if not os.path.exists("qsaving.bin"):
            self.Q=[[0 for x in range(61)] for y in range(58)] #0-29*2+1 0-28*2+1
        else:
            self.loadQ()
        self.rate=range(200,3100,100)
        self.mutex = threading.Lock()
    
    def getrate(self,bw1,buf1,bw2,buf2,oldrate):
        #init
        if bw1>3000:
            bw1=3000
        if bw1<200:
            bw1=200
        if buf1>13:
            buf1=13
        if buf1<0:
            buf1=0
        if bw2>3000:
            bw2=3000
        if bw2<200:
            bw2=200
        if buf2>13:
            buf2=13
        if buf2<0:
            buf2=0
        #calc state
        bf=int(buf2/7)
        self.BF=bf
        bw=int((bw2-200)/94)
        state=bw*2+bf
        max=0
        action=0
        #choose the point
        for i in range(58):
            if self.Q[i][state]>max:
                max=self.Q[i][state]
                action=i
        if max==0:
            action=random.randint(0,57)
        #calc the rate
        ares=int(action/2)
        oldp=int((oldrate-200)/100)
        #prepare update
        Rq=ares-self.N
        Rs=-1*int(abs(ares-oldp))
        if self.BF==0:
            Rb=-100
        else:
            Rb=self.BF-self.BFmax
        res=Rq+Rs+Rb
        #calc oldstate
        obf=int(buf1/7)
        obw=int((bw1-200)/94)
        oldstate=obw*2+obf
        #updateQ
        self.mutex.acquire()
        self.Q[oldp*2+bf][oldstate]=max*self.Gamma+res
        self.dumpQ()
        self.mutex.release()  
        #count
        self.Q[action][60]=self.Q[action][60]+1
        return self.rate[ares]

if __name__ == '__main__':
        w=W()
        old=100
        for i in range(100):
            m=random.randint(200,3000)
            old = w.getrate(m,10,m,10,old)
