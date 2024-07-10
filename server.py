#!/usr/bin/env python3
"""
License: MIT License
Copyright (c) 2023 Miel Donkers

Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from collections import defaultdict
from enum import Enum
import json
import logging


class ConfigKey(str, Enum):
    HEADER      = "header"
    BODY        = "body"
    STATUS_CODE = "status"


class S(BaseHTTPRequestHandler):

    def _init_response_(self):
        self.resp_status = 200
        self.resp_headers = defaultdict(list)
        self.resp_body = ""

    def _build_response(self, config="resp.json"):
        self._init_response_()

        with open(config, "r") as f:
            resp_data = json.load(f)
            for key in resp_data:
                if ConfigKey.STATUS_CODE == key:
                    self.resp_status = int(resp_data[ConfigKey.STATUS_CODE])
                elif ConfigKey.HEADER == key:
                    self.resp_headers = resp_data[ConfigKey.HEADER]
                elif ConfigKey.BODY == key:
                    self.resp_body = resp_data[ConfigKey.BODY]


    def _set_response(self):
        self._build_response()
        self.send_response(self.resp_status)

        for hdr in self.resp_headers:
            value = self.resp_headers[hdr]
            if type(value) is str:
                self.send_header(hdr, value)
            elif type(value) is list:
                for v in value: 
                    self.send_header(hdr, v)
        self.end_headers()


    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))
        #self.wfile.write("GET request for {}".format(self.resp_body).encode('utf-8'))


    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))
        # self.wfile.write("POST request for {}".format(self.resp_body).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=S, port=80):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
