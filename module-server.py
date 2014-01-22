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
#from transcoder import Transcoder
from capSeq import capSeq
#from controller import Controller

q = capSeq(100)
ipgroup = {}
leng = {}
mutex = threading.Lock()

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
                bandgroup = 800
                bitrate = bandgroup / num
                bandbefore = ipgroup[key].index(ip)  * bitrate
                if bandbefore < 0:
                    bandbefore=0
                #content = 'startover!' * bandgroup * 128
                bitrate += 1
                print ip, '\t>>> net speed : %d sum : %d before : %d '%(bitrate,bandgroup,bandbefore) , file[-10:]
                return ('''%d\r\n%d\r\n%d\r\n''' % ( bitrate , bandgroup , bandbefore ),  bitrate )
            else:
                leng[key][file] = {}
                for ii in ipgroup[key]:
                    bandgroup += q.getoutput(ii)
                #content = 'startover!' * bandgroup * 128
                for ii in ipgroup[key]:
                    print ii, '\t>>> net speed : %d sum : %d before : %d '%(q.getoutput(ii),bandgroup,bandbefore) , file[-10:]
                    #leng[key][file][ii] = '''%d\r\n%d\r\n%d\r\n%s'''%(q.getoutput(ii),bandgroup,bandbefore,content[bandbefore * 128 * 10 : (bandbefore + q.getoutput(ii)) * 128 * 10])
                    leng[key][file][ii] = ('''%d\r\n%d\r\n%d\r\n'''%(q.getoutput(ii),bandgroup,bandbefore), q.getoutput(ii) )
                    bandbefore += q.getoutput(ii)
                return leng[key][file][ip]

    def do_GET(self):
        server_name = 'my_simple_server/0.01'
        self.log_request()
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
            queryParams['key'] = hashlib.sha512(now.strftime(GMT_FORMAT)+self.client_address[0]).hexdigest()
            ipgroup[queryParams['key']] = []
#            print 'new group',queryParams['key']
        if not ipgroup.has_key(queryParams['key']):
            ipgroup[queryParams['key']] = []
        if self.client_address[0] not in ipgroup[queryParams['key']]:
            ipgroup[queryParams['key']].append(self.client_address[0])
 #           print 'add',queryParams['key'],ipgroup[queryParams['key']]
        if leng.has_key(queryParams['key']):
            if not action.endswith('-1.ts'):
                leng[queryParams['key']]['num'] = len(ipgroup[queryParams['key']])
        else:
            leng[queryParams['key']] = {}
            leng[queryParams['key']]['num'] = queryParams['num']

        if action.endswith('.m3u8'):
            fp = open(os.getcwd() + action)
            content = fp.read()
            fp.close()
            content = queryParams['key'] + '\r\n' + content
            response = '''HTTP/1.1 206 Partial Content\r\nServer: %s\r\nDate: %s\r\nContent-Type: application/x-mpegURL\r\nContent-Length: %s\r\nConnection: close\r\nContent-Range: bytes 0-%s/%s\r\n\r\n%s''' % (server_name, now.strftime(GMT_FORMAT), len(content), len(content)-1, len(content), content)
            print self.client_address[0],'\t>>> send response with .m3u8 file'
            self.connection.send(response)
        if action.endswith('.ts'):
            # cal net speed here
            if action.endswith('-1.ts'):
                q.clear(self.client_address[0])
            mutex.acquire()
            #resc = self.genResc(self.client_address[0],queryParams['key'],action)
            resc1 = self.genResc(self.client_address[0],queryParams['key'],action)
            mutex.release()
            resc = resc1[0] + ( '0' * 1278 + '\r\n' ) * resc1[1] 
            response = '''HTTP/1.1 200 OK\r\nServer: %s\r\nDate: %s\r\nContent-Type: video/MP2T\r\nContent-Length: %s\r\nConnection: close\r\n\r\n%s''' % (server_name, now.strftime(GMT_FORMAT), len(resc), resc)
            #print response
            self.connection.send(response)
            self.connection.close()
            now2 = datetime.datetime.now() - now1
            print self.client_address[0], '\t>>>' , action[-10:] , len(response) , now2
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
