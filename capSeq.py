#! /usr/bin/env python

import sys
import pcap
import string
import threading  
import time
import socket
import struct
from dpkt.tcp import TCP
from dpkt.ethernet import Ethernet


class capSeq(threading.Thread):   
    def __init__(self,num=10):  
        threading.Thread.__init__(self)  
        self.thread_stop = False  
        self.list_num = num
        self.list={}
        self.mutex = threading.Lock()
        self.output={}
   
    def run(self):   
        p = pcap.pcapObject()
        dev = "eth0"
        net, mask = pcap.lookupnet(dev)
        p.open_live(dev, 1600, 0, 100)
        p.setfilter("tcp port 8000", 0, 0)

        while not self.thread_stop:  
            p.dispatch(1, self.print_packet)

    def stop(self):  
        self.thread_stop = True  

    def print_packet(self,pktlen, data, timestamp):
        if not data:
            return
    
        if data[12:14]=='\x08\x00':
            p = Ethernet(data)
            if p.data.__class__.__name__ == 'IP':
                data = p.data.data
                if data.__class__.__name__ == 'TCP':
                    if len(data.data) < 5:
                        return
                    d={}
                    d["pktlen"]=pktlen
                    d["timestamp"]=timestamp
                    if data.dport != 8000:
                        self.update('%d.%d.%d.%d'%tuple(map(ord,list(p.data.dst))),d)
                    #else:
                        #self.update('%d.%d.%d.%d'%tuple(map(ord,list(p.data.src))),d)

    def update(self,ipaddr,d):
        if not self.list.has_key(ipaddr):
            self.list[ipaddr]=[]
        al = self.list[ipaddr]
        if len(al)==self.list_num:
            del al[0]
        al.append(d)
#       while(d['timestamp'] - al[0]['timestamp'] > 10):
#           del al[0]
        calcresult = self.calclist(al)
#       if calcresult < 100 and calcresult > 0:
#           print al
        self.mutex.acquire()
        self.output[ipaddr]=calcresult
        self.mutex.release()

    def getoutput(self,ipaddr):
        self.mutex.acquire()
        if self.output.has_key(ipaddr):
            re = self.output[ipaddr]
        else:
            re = 0
        self.mutex.release()
#        return int(re)
        return int(re * 0.97)

    def clear(self,ipaddr):
        self.mutex.acquire()
        if self.output.has_key(ipaddr):
            self.output[ipaddr] = 0
        self.mutex.release()

    def calclist(self,al):
        sum = 0
        for item in al:
            sum += item["pktlen"]
        sum /= 128
        interval = al[len(al)-1]["timestamp"] - al[0]["timestamp"]
        if len(al)!=1:
            return sum / interval
        else:
            return 0

if __name__=='__main__':
    q = capSeq(100)
    q.start()
    try:
        while 1:
            time.sleep(1)
            print q.getoutput("10.105.36.123")
    except KeyboardInterrupt:
        print "\nKeyboardInterrupt Over"
    q.stop()
