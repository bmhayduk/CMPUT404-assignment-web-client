#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
#
# Modifications by Brandon Hayduk per cmput 410 lectures, slides, and lab materials
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
from urlparse import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def parseURL(self, url):
        """
        Method to take a url and use the urlparse method to
        analyze and store the relevant aspects of the url. 
       
        """
        print "URL: %s" % url
        self.u = urlparse(url)

        #Get Path 
        if self.u.path == "":
            self.path = "/"
        else:
            self.path = self.u.path

        
        #get Query (set parameters - encoded) 
        if self.u.query:
         
            self.parameters = self.u.query.split("&")

            q = ""
            for param in self.parameters:
                p = param.split("=")
                key = urllib.quote_plus(p[0])
                
                if q != "":
                    q = q + "&"
                q = q + key
                if len(p) > 1:
                    value = urllib.quote_plus(p[1])
                    q = q + "=" + value
            self.parameters = q
        

    def connect(self):
        # Create the socket 
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('Socket Creation Error:' + str(msg[0]) + '-' + msg[1])
            sys.exit()

        #Get the hostname and port from the parsed url 
        self.host = self.u.hostname
        self.port = self.u.port
    
        if self.port == None:
            self.port = 80

        try:
            self.remote_ip = socket.gethostbyname(self.host)
        except socket.gaierror:
            print('Hostname \'' + host+ '\' could not be resolved')
            sys.exit()
        
        print("host by name is:"+ self.host )
       # print("port is: " + self.port)

        self.socket.connect((self.remote_ip, self.port))
        
    def get_code(self, data):
        #validate
        if not data:
            return None

        #code first
        code = int(data.split(' ',2)[1])
        print("Responded with Code: %d" % code)
        return code
     
    def get_headers(self,data):
        #?
        return None
        

    def get_body(self, data):
        if not data:
            return None

        return data.split("\r\n\r\n",2)[1]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def create_header(self, method):

        if self.parameters:
            length = len(self.parameters)
        else:
            length = 0

        header = ("%s %s HTTP/1.1\r\n" % (method, self.path))
        header += ("Host: %s:%d \r\n" % (self.host, self.port))
        header += ("User-Agent: Ubuntu VM \r\n")
        
        if method == 'POST':
            header += ("Content-Type: application/x-www-form-urlencoded\r\n")
            header += ("Content-Length: %d \r\n" % length)
            
        header += ("Connection: \"close\"\r\n\r\n")

        return header

    def GET(self, url, args=None):

        if args:
            self.parameters = urllib.urlencode(args)
        else:
            self.parameters = "" 
        

        #Step one: verify URL:
        self.parseURL(url)
        self.connect()
        
        header = self.create_header("GET")
        self.socket.sendall(header.encode("UTF8"))

        if self.parameters:
            self.socket.sendall("%s\r\n\r\n" % self.parameters)
        
        #get response
        resp = self.recvall(self.socket)
        
        #grab info from response
        code = self.get_code(resp)
        body = self.get_body(resp)
        self.socket.close()
        
        #connection = self.connect(url)
        return HTTPRequest(code, body)

    def POST(self, url, args=None):

        if args:
            self.parameters = urllib.urlencode(args)
        else:
            self.parameters = ""
        
        self.parseURL(url)
        self.connect()
        
        header = self.create_header("POST")
        self.socket.sendall(header.encode("UTF8"))

        if self.parameters:
            self.socket.sendall("%s\r\n\r\n" % self.parameters)

        resp = self.recvall(self.socket)
        code = self.get_code(resp)
        body = self.get_body(resp)

        self.socket.close()

        return HTTPRequest(code, body)


    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[1], sys.argv[2] )
    else:
        print client.command( command, sys.argv[1] )    
