#!/usr/bin/env python
# coding: utf-8
# Modifications by Brandon Hayduk per cmput 410 lectures, slides, and lab materials
# Copyright 2013 Abram Hindle
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

    
    def connect(self):
        """
        Use sockets to create a connection based on the 
        pared URL analyzed in the parseURL method
        """
        # Create the socket 
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('Socket Creation Error:' + str(msg[0]) + '-' + msg[1])
            sys.exit()

        #Get the hostname and port from the parsed url 
        self.host = self.url.hostname
        self.port = self.url.port
    
        if self.port == None:
            self.port = 80

        #Handle remote IP
        try:
            self.remote_ip = socket.gethostbyname(self.host)
        except socket.gaierror:
            print('Hostname \'' + host+ '\' could not be resolved')
            sys.exit()

        self.socket.connect((self.remote_ip, self.port))
       

    def get_code(self, data):
        #validate
        if not data:
            return None

        #code first
        code = int(data.split(' ',2)[1])
       # print("Responded with Code: %d" % code)
        return code
     

    def get_headers(self,data):
        #?
        return None
        

    def get_body(self, data):
        if not data:
            return None

        return data.split("\r\n\r\n",2)[1]

  
    def recvall(self, sock):
        """
        Read everything from the socket

        """
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)


    def parseURL(self, url):
        """
        Method to take a url and use the urlparse method to
        analyze and store the relevant aspects of the url. 
        """

        print "URL: %s" % url
        self.url = urlparse(url)
       
        #Get Path 
        if self.url.path == "":
            self.path = self.url.path + '/'
        else:
            self.path = self.url.path
       
        #Get Query from URL:
        #If someone sends a query encode the relevant parts with quote_plus from urllib
        if self.url.query:
            self.tokens = self.url.query.split("&")
            #
            query = ""
            for param in self.tokens:
                p = param.split("=")
                key = urllib.quote_plus(p[0])
                
                if query != "":
                    query = query + "&"
                query = query + key
                if len(p) > 1:
                    value = urllib.quote_plus(p[1])
                    query = query + "=" + value
            self.tokens = query


    def create_header(self, method):
        """
        Create the header based on request type
        
        """
        header = ("%s %s HTTP/1.1\r\n" % (method, self.path))
        header += ("Host: %s:%d \r\n" % (self.host, self.port))
        header += ("User-Agent: Ubuntu VM \r\n")
        
        if method == 'POST':
            header += ("Content-Type: application/x-www-form-urlencoded\r\n")
            header += ("Content-Length: %d \r\n" % len(self.tokens))
            
        header += ("Connection: close\r\n\r\n")

        return header


    def GET(self, url, args=None):

        if args:
            self.tokens = urllib.urlencode(args)
        else:
            self.tokens = "" 
        
        #Step one: verify URL:
        self.parseURL(url)
        self.connect()
        
        header = self.create_header("GET")
        
        print(header)
        self.socket.sendall(header.encode("UTF8"))
       
        if self.tokens:
            self.socket.sendall("%s\r\n\r\n" % self.tokens)
       
        #get response
        resp = self.recvall(self.socket)
       
        #grab info from response
        code = self.get_code(resp)
        body = self.get_body(resp)

        self.socket.close()
       
        return HTTPRequest(code, body)

    def POST(self, url, args=None):

        if args:
            self.tokens = urllib.urlencode(args)
        else:
            self.tokens = ""
        
        self.parseURL(url)
        self.connect()
        
        header = self.create_header("POST")

        print(header)
        self.socket.sendall(header.encode("UTF8"))

        if self.tokens:
            self.socket.sendall("%s\r\n\r\n" % self.tokens)

        #Get Response and analyze
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
