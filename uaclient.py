#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import time
import socket
import sys
import os

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

try:
    config = sys.argv[1]
    method = sys.argv[2]
    option = sys.argv[3]
except IndexError:
    print 'Usage: python uaclient.py config method option'
    sys.exit()


class XMLHandler(ContentHandler):

    def __init__(self):

        self.dicc_config = {}

    def startElement(self, name, attrs):

        if name == 'account':
            self.dicc_config['username'] = attrs.get('username', "")
        elif name == 'uaserver':
            self.dicc_config['ip_server'] = attrs.get('ip', "")
            self.dicc_config['puerto_server'] = attrs.get('puerto', "")
        elif name == 'rtpaudio':
            self.dicc_config['puerto_rtp'] = attrs.get('puerto', "")
        elif name == 'regproxy':
            self.dicc_config['ip_proxy'] = attrs.get('ip', "")
            self.dicc_config['puerto_proxy'] = attrs.get('puerto', "")
        elif name == 'log':
            self.dicc_config['path_log'] = attrs.get('path', "")
        elif name == 'audio':
            self.dicc_config['path_audio'] = attrs.get('path', "")

    def get_tags(self):

        return self.dicc_config

if __name__ == "__main__":
    parser = make_parser()
    cHandler = XMLHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(config))

    name = cHandler.dicc_config['username']
    ip_server = cHandler.dicc_config['ip_server']
    puerto_server = cHandler.dicc_config['puerto_server']
    puerto_rtp = cHandler.dicc_config['puerto_rtp']
    ip_proxy = cHandler.dicc_config['ip_proxy']
    puerto_proxy = cHandler.dicc_config['puerto_proxy']
    path_log = cHandler.dicc_config['path_log']
    path_audio = cHandler.dicc_config['path_audio']

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((str(ip_proxy), int(puerto_proxy)))
    log = open(path_log, 'a')
    print 'Starting...'
    log.write(time.strftime('%Y%m%d%H%M%S') + ' ' + 'Starting...\r\n')

    if method == 'REGISTER':
        LineaEnvio = 'REGISTER sip:' + name + ':' + puerto_server + ' SIP/2.0\r\n' +\
            'Expires: ' + option + '\r\n'
        LineaLog = time.strftime('%Y%m%d%H%M%S') + ' ' + 'Sent to ' +\
            ip_proxy + ':' + puerto_proxy + ' ' +\
            LineaEnvio.replace('\r\n', ' ') + '\r\n'
        LineaImprimir = 'Sent to ' + ip_proxy + ':' +\
            puerto_proxy + '\r\n' + LineaEnvio
        my_socket.send(LineaEnvio)
        log.write(LineaLog)
        print LineaImprimir

    elif method == 'INVITE':
        LineaEnvio = 'INVITE sip:' + option + ' SIP/2.0\r\n' +\
            'Content_Type: application/sdp\r\n\r\n' +\
            'v=0\r\n' +\
            'o=' + name + ' ' + ip_server + '\r\n' +\
            's=misesion\r\n' +\
            't=0\r\n' +\
            'm=audio ' + puerto_rtp + ' RTP\r\n'
        LineaLog = time.strftime('%Y%m%d%H%M%S') + ' Sent to ' +\
            ip_proxy + ':' + puerto_proxy + ' ' +\
            LineaEnvio.replace('\r\n', ' ') + '\r\n'
        LineaImprimir = 'Sent to ' + ip_proxy + ':' +\
            puerto_proxy + ' ' + LineaEnvio
        my_socket.send(LineaEnvio)
        print 'El contenido del invite es: ' + LineaEnvio
        log.write(LineaLog)
        print LineaImprimir

    elif method == 'BYE':
        LineaEnvio = 'BYE sip:' + option + ' SIP/2.0\r\n'
        LineaLog = time.strftime('%Y%m%d%H%M%S') + ' Sent to ' +\
            ip_proxy + ':' + puerto_proxy + ' ' +\
            LineaEnvio.replace('\r\n', ' ') + '\r\n'
        LineaImprimir = 'Sent to ' + ip_proxy + ':' +\
            puerto_proxy + ' ' + LineaEnvio
        my_socket.send(LineaEnvio)
        log.write(LineaLog)
        print LineaImprimir

    try:
        data = my_socket.recv(1024)
    except socket.error:
        error = 'Error: no server listening at ' + ip_proxy + " port "\
            + puerto_proxy
        log.write(time.strftime('%Y%m%d%H%M%S') + ' ' + error + '\r\n')
        print error

    lineasdata = data.split('\r\n')

    if lineasdata[0] == 'SIP/2.0 100 Trying':
        LineaLog = time.strftime('%Y%m%d%H%M%S') + ' ' +\
            'Received from ' + ip_proxy + ':' +\
            puerto_proxy + ' ' + data.replace('\r\n', ' ') + '\r\n'
        log.write(LineaLog)
        LineaEnvio = 'ACK sip:' + option + ' SIP/2.0\r\n'
        LineaLog = time.strftime('%Y%m%d%H%M%S') + ' Sent to ' +\
            ip_proxy + ':' + puerto_proxy + ' ' + LineaEnvio
        LineaImprimir = 'Sent to ' + ip_proxy + ':' + puerto_proxy +\
            '\r\n' + LineaEnvio
        my_socket.send(LineaEnvio)
        log.write(LineaLog)
        print LineaImprimir
        ip_rtp = lineasdata[6].split(' ')[1]
        puerto_rtp = lineasdata[9].split(' ')[1]
        PedirPermisos = "chmod +x mp32rtp"
        os.system(PedirPermisos)
        aEjecutar = "./mp32rtp -i " + ip_rtp + " -p " +\
            puerto_rtp + " < " + str(path_audio)
        print "Vamos a ejecutar", aEjecutar
        os.system(aEjecutar)
        LineaLog = time.strftime('%Y%m%d%H%M%S') + ' Sent to ' +\
            str(ip_rtp) + ':' + str(puerto_rtp) + ' RTP\r\n'
        log.write(LineaLog)
        print "Cancion enviada"

    elif lineasdata[0] == 'SIP/2.0 200 OK':
        LineaLog = time.strftime('%Y%m%d%H%M%S') + ' ' +\
            'Received from ' + ip_proxy + ':' +\
            puerto_proxy + ' ' + data.replace('\r\n', ' ') + '\r\n'
        log.write(LineaLog)
        print 'Received from ' + ip_proxy + ':' +\
            puerto_proxy + '\r\n' + data.replace('\r\n', ' ') + '\r\n'
        if option == '0':
            LineaLog = time.strftime('%Y%m%d%H%M%S') + ' Finishing...\r\n'
            log.write(LineaLog)
    else:
        LineaLog = time.strftime('%Y%m%d%H%M%S') + ' Received from ' + ip_proxy +\
            ':' + puerto_proxy + ' ' + data.replace('\r\n', ' ') + '\r\n'
        log.write(LineaLog)
        print 'Received from ' + ip_proxy +\
            ':' + puerto_proxy + '\r\n' + data.replace('\r\n', ' ') + '\r\n'

    my_socket.close()
