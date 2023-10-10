#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Julian Gallego Franco, Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
import urllib.parse

BUFFER_SIZE = 4096

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
    
    def printSelf(self):
        print(self.code)
        print(self.body)

class HTTPClient(object):
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(10)
        self.socket.connect((host, port))

    def getCode(self, data):
        return int(data.split()[1])

    def getHeaders(self, data):
        headers, _ = data.split('\r\n\r\n', 1)
        return headers

    def getBody(self, data):
        _, body = data.split('\r\n\r\n', 1)
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        try:
            parsedUrl = urllib.parse.urlparse(url)
            host = parsedUrl.hostname
            port = parsedUrl.port if parsedUrl.port else 80
            path = parsedUrl.path if parsedUrl.path else '/'

            if args:
                path += '?' + urllib.parse.urlencode(args)

            req = f"GET {path} HTTP/1.1\r\n"
            req += f"Host: {host}\r\n"
            req += "Connection: close\r\n\r\n"

            self.connect(host, port)
            self.sendall(req)

            res = self.recvall(self.socket)
            self.close()

            code = self.getCode(res)
            body = self.getBody(res)

            return HTTPResponse(code, body)
        
        except ConnectionRefusedError:
            return HTTPResponse(503, "Service Unavailable")

    def POST(self, url, args=None):
        try:
            parsedUrl = urllib.parse.urlparse(url)
            host = parsedUrl.hostname
            port = parsedUrl.port if parsedUrl.port else 80
            path = parsedUrl.path if parsedUrl.path else '/'

            if args:
                body = urllib.parse.urlencode(args)
                contentLength = len(body)
            else:
                body = ""
                contentLength = 0

            req = f"POST {path} HTTP/1.1\r\n"
            req += f"Host: {host}\r\n"
            req += f"Content-Type: application/x-www-form-urlencoded\r\n"
            req += f"Content-Length: {contentLength}\r\n"
            req += "Connection: close\r\n\r\n"
            req += body

            self.connect(host, port)
            self.sendall(req)

            res = self.recvall(self.socket)
            self.close()

            code = self.getCode(res)
            body = self.getBody(res)

            return HTTPResponse(code, body)
        
        except ConnectionRefusedError:
            return HTTPResponse(503, "Service Unavailable")

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            self.POST( url, args ).printSelf()
        else:
            self.GET( url, args ).printSelf()
    
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        client.command( sys.argv[2], sys.argv[1] )
    else:
        client.command( sys.argv[1] )
