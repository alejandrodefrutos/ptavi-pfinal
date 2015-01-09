#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import SocketServer
import time
import socket
import sys
import os

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

try:
    config = sys.argv[1]
except IndexError:
    print 'Usage: python uaserver.py config'
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


class EchoHandler(SocketServer.DatagramRequestHandler):

    def handle(self):
        while 1:

            linearecibida = self.rfile.read()
            if not linearecibida:
                break
            lineacliente = linearecibida.split(' ')

            if lineacliente[0] == 'INVITE':
                log = open(path_log, 'a')
                LineaLog = 'Received from ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) + ' ' +\
                    '\r\n' + linearecibida
                registro = time.strftime('%Y%m%d%H%M%S') + ' ' +\
                    LineaLog.replace('\r\n', ' ') + '\r\n'
                log.write(registro)
                print LineaLog

                LineaLog = 'Sent to ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) + ' ' +\
                    'SIP/2.0 100 Trying\r\n'
                registro = time.strftime('%Y%m%d%H%M%S') +\
                    ' ' + LineaLog.replace('\r\n', ' ') + '\r\n'
                log.write(registro)
                self.wfile.write('SIP/2.0 100 Trying\r\n')
                print LineaLog

                LineaLog = 'Sent to ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) + ' ' +\
                    'SIP/2.0 180 Ringing\r\n'
                registro = time.strftime('%Y%m%d%H%M%S') +\
                    ' ' + LineaLog.replace('\r\n', ' ') + '\r\n'
                log.write(registro)
                self.wfile.write('SIP/2.0 180 Ringing\r\n')
                print LineaLog

                Content = 'Content-Type: application/sdp\r\n\r\n'
                version = 'v=o\r\n'
                o = 'o=' + name + ' ' + ip_server + '\r\n'
                sesion = 's=Domin_Sesion\r\n'
                t = 't=0\r\n'
                rtp_linea = 'm=audio' + ' ' + puerto_rtp + ' ' + 'RTP\r\n'
                LineaEnvio = Content + version + o + sesion + t + rtp_linea

                name_sdp = lineacliente[3].split('=')[2]
                ip_sdp = lineacliente[4].split('\r\n')[0] + ' '
                puerto_sdp = lineacliente[5] + ' '
                lista_sdp = [ip_sdp, puerto_sdp]
                d_sdp['key'] = lista_sdp

                LineaLog = 'Sent to ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) + ' ' +\
                    'SIP/2.0 200 OK\r\n' + LineaEnvio
                registro = time.strftime('%Y%m%d%H%M%S') + ' ' +\
                    LineaLog.replace('\r\n', ' ') + '\r\n'
                log.write(registro)
                self.wfile.write('SIP/2.0 200 OK\r\n' + LineaEnvio)
                print LineaLog

            elif lineacliente[0] == 'ACK':
                log = open(path_log, 'a')
                LineaLog = time.strftime('%Y%m%d%H%M%S') + 'Received from ' +\
                    self.client_address[0] + ':' +\
                    str(self.client_address[1]) + ' \r\n'
                log.write(LineaLog)
                print 'Received from ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) +\
                    ' \r\n' + linearecibida

                PedirPermisos = "chmod +x mp32rtp"
                os.system(PedirPermisos)
                aEjecutar = "./mp32rtp -i " + d_sdp['key'][0] + " -p " +\
                    d_sdp['key'][1] + " < " + str(path_audio)
                print "Vamos a ejecutar", aEjecutar
                os.system(aEjecutar)

                LineaLog = time.strftime('%Y%m%d%H%M%S') + ' Sent to ' +\
                    str(d_sdp['key'][0]) + ':' +\
                    str(d_sdp['key'][1]) + ' RTP\r\n'
                log.write(LineaLog)

                print 'Cancion enviada\r\n'

            elif lineacliente[0] == 'BYE':
                log = open(path_log, 'a')
                LineaLog = time.strftime('%Y%m%d%H%M%S') + ' Received from ' +\
                    self.client_address[0] + ':' +\
                    str(self.client_address[1]) + ' ' +\
                    linearecibida.replace('\r\n', ' ') + '\r\n'
                print 'Received from ' + self.client_address[0] + ':' +\
                    str(self.client_address[1]) + '\r\n' +\
                    linearecibida.replace('\r\n', ' ') + '\r\n'

                LineaLog = time.strftime('%Y%m%d%H%M%S') + ' Sent to ' +\
                    self.client_address[0] +\
                    ':' + str(self.client_address[1]) + ' SIP/2.0 200 OK\r\n'
                self.wfile.write('SIP/2.0 200 OK\r\n')
                print 'Sent to ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) + ' SIP/2.0 200 OK\r\n'

            elif lineacliente[0] == 'INFO':
                log = open(path_log, 'a')
                LineaLog = 'Received from ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) + ' ' +\
                    linearecibida.replace('\r\n', ' ') + '\r\n'
                registro = time.strftime('%Y%m%d%H%M%S') + ' ' +\
                    LineaLog.replace('\r\n', ' ') + '\r\n'
                log.write(registro)
                print 'Received from ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) + ' \r\n' + linearecibida
                LineaLog = 'Sent to ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) +\
                    ' SIP/2.0 400 Bad Request\r\n'
                registro = time.strftime('%Y%m%d%H%M%S') + ' ' +\
                    LineaLog.replace('\r\n', ' ') + '\r\n'
                log.write(registro)
                self.wfile.write('SIP/2.0 400 Bad Request\r\n')
                print 'Sent to ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) +\
                    ' \r\nSIP/2.0 400 Bad Request\r\n'
                log.close()
            else:
                log = open(path_log, 'a')
                LineaLog = time.strftime('%Y%m%d%H%M%S') + ' Received from ' +\
                    self.client_address[0] + ':' +\
                    str(self.client_address[1]) + ' ' +\
                    linearecibida.replace('\r\n', ' ') + '\r\n'
                print 'Received from ' + self.client_address[0] + ':' +\
                    str(self.client_address[1]) + ' '

                LineaLog = time.strftime('%Y%m%d%H%M%S') +\
                    ' Sent to ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) +\
                    ' SIP/2.0 400 Bad Request\r\n'
                self.wfile.write('SIP/2.0 400 Bad Request\r\n')
                print ' Sent to ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) +\
                    ' SIP/2.0 400 Bad Request\r\n'
        log.close()


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

    d_sdp = {}
    log = open(path_log, 'a')
    log.write(time.strftime('%Y%m%d%H%M%S') + ' Listening...\r\n')
    log.close()
    print 'Listening...\r\n'
    serv = SocketServer.UDPServer(('', int(puerto_server)), EchoHandler)
    serv.serve_forever()
