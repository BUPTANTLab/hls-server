#!/usr/bin/env python

import BaseHTTPServer
import urlparse
import urllib2
import urllib
import os
import hashlib
import sys
import re
import zlib
import gzip
import SocketServer
import StringIO
import datetime
import threading
from transcoder import Transcoder
from capSeq import capSeq
from w import W

q = capSeq(100)
ipgroup = {}
leng = {}
mutex = threading.Lock()
tr = Transcoder()
w=W()
wlist={}

class HLSServer(BaseHTTPServer.BaseHTTPRequestHandler):
    def genResc(self,ip,key,file):
        num = int(leng[key]['num'])
        if leng[key].has_key(file):
            if leng[key][file].has_key(ip):
                return leng[key][file][ip]
            else:
                return ('-1\r\n-1\r\n-1\r\n',5*100)
        else:
            bandgroup = 0
            bandbefore = 0
            bitrate = q.getoutput(ip)
            if bitrate == 0:
                wlist[ip]={}
                wlist[ip]['bw']=0
                wlist[ip]['obf']=10
                wlist[ip]['bf']=10
                wlist[ip]['orate']=800/num
                wlist[ip]['now']=datetime.datetime.now()
                file2 = file.replace('repo' , 'repo/800')
                fp = open(os.getcwd() + file2)
                fcontent = fp.read()
                fp.close()

                bandgroup = len(fcontent)
                bitrate = int(len(fcontent) / num)
                bandbefore = ipgroup[key].index(ip)  * bitrate 
                if bandbefore < 0:
                    bandbefore=0
                bitrate += 1
                print ip, '\t>>> net speed : %d sum : %d before : %d '%(bitrate,bandgroup,bandbefore) , file[-10:]
                return ('''Content-Range: bytes %d-%d/%d\r\n\r\n%s''' % ( bandbefore , min(bandbefore+bitrate,bandgroup) , bandgroup , fcontent[bandbefore:min(bandbefore+bitrate,bandgroup)]),  bitrate )
            else:
                leng[key][file] = {}
                for ii in ipgroup[key]:
                    wlist[ii]['bf']=wlist[ii]['bf']+9-(datetime.datetime.now()-wlist[ip]['now']).seconds
                    if wlist[ii]['bw'] ==0:
                        wlist[ii]['bw']=q.getoutput(ii)
                    leng[key][file][ii]=w.getrate(wlist[ii]['bw'] , wlist[ii]['obf'], q.getoutput(ii), wlist[ii]['bf'], wlist[ii]['orate'])
                    bandgroup += leng[key][file][ii]
                    print ii , wlist[ii]
                    wlist[ii]['bw']=q.getoutput(ii)
                    wlist[ii]['orate']=leng[key][file][ii]
                    wlist[ii]['obf']=wlist[ii]['bf']
                    wlist[ip]['now']=datetime.datetime.now()

#               tr.transcode(os.getcwd() + file, "/tmp" + file , bandgroup * 0.9 - 100)
#               fp = open("/tmp" + file)
                bit = int(bandgroup/100)*100
                if bit > 3000:
                    bit = 3000
                file2 = file.replace('repo' , 'repo/' + str(bit))
                fp = open(os.getcwd() + file2)
                fcontent = fp.read()
                fp.close()

                for ii in ipgroup[key]:
                    conbit = int(leng[key][file][ii] * len(fcontent) / bandgroup) + 1
#                   print ii, '\t>>> conbit : %d\tlen : %d\tbefore : %d\trate : %d\tgroup : %d\t'%(conbit , len(fcontent) , bandbefore , q.getoutput(ii) , bandgroup) , file[-10:]
                    print ii, '\t>>> len : %d\trate : %d\tgroup : %d\t'%(len(fcontent) , leng[key][file][ii] , bandgroup) , bit ,"key:",key,  file[-10:]
                    leng[key][file][ii] = ('''Content-Range: bytes %d-%d/%d\r\n\r\n%s'''%(bandbefore , min(bandbefore+conbit,len(fcontent)) , len(fcontent) , fcontent[bandbefore : min(bandbefore + conbit,len(fcontent))]), conbit)
                    bandbefore += conbit
                return leng[key][file][ip]

    def do_GET(self):
        server_name = 'my_simple_server/0.01'
#        self.log_request()
        action = self.path
        now1 = datetime.datetime.now()
        queryParams = {}
        GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
        now = datetime.datetime.utcnow()
        if '?' in self.path:
            query = urllib.splitquery(self.path)
            action = query[0]
 
            if query[1]:
                for qp in query[1].split('&'):
                    kv = qp.split('=')
                    queryParams[kv[0]] = kv[1] #urllib.unquote(kv[1]).decode("utf-8", 'ignore')

        if not queryParams.has_key('key'):
            queryParams['key'] = hashlib.sha512(self.client_address[0]).hexdigest()
            print hashlib.sha512(self.client_address[0]).hexdigest() , self.client_address[0]
            ipgroup[queryParams['key']] = []
#            print 'new group',queryParams['key']
        if not queryParams.has_key('num'):
                queryParams['num'] = 1
        if not ipgroup.has_key(queryParams['key']):
            ipgroup[queryParams['key']] = []
        if self.client_address[0] not in ipgroup[queryParams['key']]:
            ipgroup[queryParams['key']].append(self.client_address[0])
 #           print 'add',queryParams['key'],ipgroup[queryParams['key']]
        if leng.has_key(queryParams['key']):
            if not action.endswith('_1.mp4'):
                leng[queryParams['key']]['num'] = len(ipgroup[queryParams['key']])
            else:
                leng[queryParams['key']]['num'] = queryParams['num']
        else:
            leng[queryParams['key']] = {}
            leng[queryParams['key']]['num'] = queryParams['num']

        if action.endswith('.m3u8'):
            fp = open(os.getcwd() + action)
            content = fp.read()
            fp.close()
            #content = queryParams['key'] + '\r\n' + content
            response = '''HTTP/1.1 206 Partial Content\r\nServer: %s\r\nDate: %s\r\nContent-Type: application/x-mpegURL\r\nContent-Length: %s\r\nConnection: close\r\nContent-Range: bytes 0-%s/%s\r\n\r\n%s''' % (server_name, now.strftime(GMT_FORMAT), len(content), len(content)-1, len(content), content)
            print self.client_address[0],'\t>>> send response with .m3u8 file'
            self.connection.send(response)
        if action.endswith('.mp4'):
            # cal net speed here
            if action.endswith('_1.mp4'):
                q.clear(self.client_address[0])
            mutex.acquire()
            #resc = self.genResc(self.client_address[0],queryParams['key'],action)
            resc1 = self.genResc(self.client_address[0],queryParams['key'],action)
            mutex.release()
#           resc = resc1[0] + ( '0' * 1278 + '\r\n' ) * resc1[1] 
            resc = resc1[0]
#            response = '''HTTP/1.1 200 OK\r\nServer: %s\r\nDate: %s\r\nContent-Type: video/MP2T\r\nContent-Length: %s\r\nConnection: close\r\n\r\n%s''' % (server_name, now.strftime(GMT_FORMAT), len(resc), resc)
            response = '''HTTP/1.1 206 Partial Content\r\nServer: %s\r\nDate: %s\r\nContent-Type: video/MP2T\r\nContent-Length: %s\r\nConnection: close\r\n%s''' % (server_name, now.strftime(GMT_FORMAT), resc1[1], resc)
            #print response
            self.connection.send(response)
            self.connection.close()
            now2 = datetime.datetime.now() - now1
#            print self.client_address[0], '\t>>>' , action[-10:] , len(response) , now2
        return

class ThreadingHTTPServer(SocketServer.ThreadingMixIn,BaseHTTPServer.HTTPServer): pass

def serving(HandlerClass, ServerClass, protocol="HTTP/1.0"):  
    server_address = ('', 8000)
    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass)
    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], ""        
    httpd.serve_forever()

if __name__ == '__main__':
    try:
        q.start()
        serving(HLSServer, ThreadingHTTPServer)
    except KeyboardInterrupt:
        q.stop()
        print 'over!'
        exit(0)
    except:
        raise Exception('Error starting http server')
