#!/usr/bin/python2
# -*- coding: utf8 -*-

import BaseHTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
from urlparse import urlparse, parse_qs
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import base64
import cgi
import seabattle
import ConfigParser
import time

game = None

class SeaBattleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        mimetype = None
        content = None
        url = urlparse(self.path)
        query_components = parse_qs(url.query)
        if url.path == '/':
            mimetype = 'text/html'
            global game
            content = game.build_html(query_components.get("secret", [None])[0])
        elif url.path == '/style.css':
            mimetype = 'text/css'
            content = open("style.css").read()
        elif url.path.startswith('/img/') and url.path.endswith('.png'):
            try:
                content = open(url.path[1:]).read()
                mimetype = 'image/png'
            except:
                content = None
                raise
        if content is None:
            mimetype = 'text/html'
            content = 'Invalid request!'
        self.send_header('Content-type', mimetype)
        self.end_headers()
        self.wfile.write(content)

class ThreadingHTTPServer(SocketServer.ThreadingMixIn, HTTPServer):
    pass

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: main.py <port> <config path>"
        sys.exit(1)
    port = int(sys.argv[1])
    config_path = sys.argv[2]
    config = ConfigParser.ConfigParser()
    config.read(config_path)
    game = seabattle.Game(config)
    server = ThreadingHTTPServer(('', port), SeaBattleHandler)
    server.serve_forever()
