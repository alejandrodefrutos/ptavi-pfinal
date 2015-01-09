#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor de eco
en UDP simple
"""

import os
import time
import sys
import SocketServer
import socket
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

try:
    config = sys.argv[1]
except IndexError:
    print 'Usage: python proxy_registrar.py config'
    sys.exit()


class XMLHandler(ContentHandler):

    def __init__(self):

        self.dicc_config = {}

    def startElement(self, name, attrs):

        if name == 'server':
            self.dicc_config['name'] = attrs.get('name', "")
            self.dicc_config['ip_proxy'] = attrs.get('ip', "")
            self.dicc_config['puerto_proxy'] = attrs.get('puerto', "")
        elif name == 'database':
            self.dicc_config['path_proxy'] = attrs.get('path', "")
            self.dicc_config['password_proxy'] = attrs.get('passwdpath', "")
        elif name == 'log':
            self.dicc_config['path_log'] = attrs.get('path', "")

    def get_tags(self):

        return self.dicc_config


class EchoHandler(SocketServer.DatagramRequestHandler):
    def handle(self):
        while 1:
            linearecibida = self.rfile.read()
            if not linearecibida:
                break
            lineascliente = linearecibida.split(' ')
            if lineascliente[0] == 'REGISTER':
                name = lineascliente[1].split(':')[1]
                puerto = lineascliente[1].split(':')[2]
                expires = lineascliente[3]
                datos_cliente = self.client_address[0],\
                    puerto, expires, time.time()
                d_usuarios[name] = datos_cliente
                database = open(path_proxy, 'w')
                for key in d_usuarios:
                    database.write(key + " ")
                    for element in d_usuarios[key]:
                        database.write(str(element) + " ")
                    database.write('\r\n')
                log = open(path_log, 'a')
                LineaLog = time.strftime('%Y%m%d%H%M%S') +\
                    'Received from ' + self.client_address[0] +\
                    ':' + str(self.client_address[1])
                log.write(LineaLog.replace('\r\n', ' ') + '\r\n')
                print 'Received from ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) + '\r\n' +\
                    linearecibida + '\r\n'
                LineaLog = time.strftime('%Y%m%d%H%M%S') + ' Sent to ' +\
                    self.client_address[0] + ':' +\
                    str(self.client_address[1]) + ' SIP/2.0 200 OK\r\n'
                log.write(LineaLog.replace('\r\n', ' ') + '\r\n')
                self.wfile.write('SIP/2.0 200 OK\r\n')
                print 'Sent to ' + self.client_address[0] + ':' +\
                    str(self.client_address[1]) + '\r\n' + 'SIP/2.0 200 OK\r\n'
                log.close()

            elif lineascliente[0] == 'INVITE':
                name = lineascliente[1].split(':')[1]
                log = open(path_log, 'a')
                LineaLog = time.strftime('%Y%m%d%H%M%S') +\
                    ' Received from ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) + ' ' +\
                    linearecibida.replace('\r\n', ' ')
                log.write(LineaLog.replace('\r\n', ' ') + '\r\n')
                print 'Received from ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) + ' ' +\
                    '\r\n' + linearecibida
                log.close()
                usuario = 0
                for key in d_usuarios:
                    if key == name:
                        usuario = 1
                        t_es = int(d_usuarios[name][2]) +\
                            int(d_usuarios[name][3])

                        socket1 = socket.AF_INET
                        socket2 = socket.SOCK_DGRAM
                        my_socket = socket.socket(socket1, socket2)
                        socket3 = socket.SOL_SOCKET
                        socket4 = socket.SO_REUSEADDR
                        my_socket.setsockopt(socket3, socket4, 1)
                        ip = str(d_usuarios[name][0])
                        puerto = int(d_usuarios[name][1])
                        my_socket.connect((ip, puerto))

                        if t_es > time.time():
                            log = open(path_log, 'a')
                            LineaLog = 'Sent to ' + str(d_usuarios[name][0])\
                                + ':' + d_usuarios[name][1] + ' ' +\
                                linearecibida.replace('\r\n', ' ') + '\r\n'
                            registro = time.strftime('%Y%m%d%H%M%S') +\
                                ' ' + LineaLog.replace('\r\n', ' ') + '\r\n'
                            log.write(registro)
                            log.close()

                            my_socket.send(linearecibida)

                            print 'Sent to ' + str(d_usuarios[name][0])\
                                + ':' + d_usuarios[name][1] + ' ' +\
                                '\r\n' + linearecibida

                            try:
                                data = my_socket.recv(1024)
                            except socket.error:
                                error = 'Error: no server listening at ' + \
                                    str(d_usuarios[name][0]) + \
                                    " port " + d_usuarios[name][1]
                                log = open(path_log, 'a')
                                registro = time.strftime('%Y%m%d%H%M%S') + \
                                    ' ' + error + '\r\n'
                                log.write(registro)
                                log.close()
                                print error
                                break

                            lineaservidor = data.split('\r\n')
                            log = open(path_log, 'a')
                            LineaLog = time.strftime('%Y%m%d%H%M%S') +\
                                'Received from ' + \
                                str(d_usuarios[name][0]) +\
                                ':' + d_usuarios[name][1] + ' ' +\
                                data.replace('\r\n', ' ') + \
                                '\r\n'
                            registro = time.strftime('%Y%m%d%H%M%S') +\
                                ' ' + LineaLog.replace('\r\n', ' ') + '\r\n'
                            log.write(registro)
                            print 'Received from ' +\
                                str(d_usuarios[name][0]) + \
                                ':' + d_usuarios[name][1] + ' ' + '\r\n' + data
                            self.wfile.write(data)

                            LineaLog = 'Sent to ' + self.client_address[0] +\
                                ':' + str(self.client_address[1]) + ' ' +\
                                data.replace('\r\n', ' ') + \
                                '\r\n'
                            registro = time.strftime('%Y%m%d%H%M%S') + \
                                ' ' + LineaLog.replace('\r\n', ' ') + '\r\n'
                            log.write(registro)
                            log.close()
                            print 'Sent to ' + self.client_address[0] +\
                                ':' + str(self.client_address[1]) +\
                                ' ' + '\r\n' + data

                        elif t_es < time.time():
                            log = open(path_log, 'a')
                            LineaLog = 'Sent to ' + self.client_address[0] +\
                                ':' + str(self.client_address[1]) + ' ' +\
                                'SIP/2.0 404 User Not Found\r\n'
                            registro = time.strftime('%Y%m%d%H%M%S') +\
                                ' ' + LineaLog.replace('\r\n', ' ') + '\r\n'
                            log.write(registro)
                            log.close()
                            self.wfile.write('SIP/2.0 404 User Not Found\r\n')
                            print 'Sent to ' + self.client_address[0] +\
                                ':' + str(self.client_address[1]) + '\r\n' +\
                                'SIP/2.0 404 User Not Found\r\n'
                            del d_usuarios[name]

                            database = open(path_proxy, 'w')
                            for key in d_usuarios:
                                database.write(key + " ")
                                for element in d_usuarios[key]:
                                    database.write(str(element) + " ")
                        break
                if usuario == 0:
                    log = open(path_log, 'a')
                    send_to = 'Sent to ' + self.client_address[0] +\
                        ':' + str(self.client_address[1]) + ' '
                    LineaLog = send_to + 'SIP/2.0 404 User Not Found\r\n'
                    registro = time.strftime('%Y%m%d%H%M%S') + ' ' +\
                        LineaLog.replace('\r\n', ' ') + '\r\n'
                    log.write(registro)
                    log.close()
                    self.wfile.write('SIP/2.0 404 User Not Found\r\n')
                    print send_to + '\r\n' + 'SIP/2.0 404 User Not Found\r\n'
            elif lineascliente[0] == 'ACK':
                name = lineascliente[1].split(':')[1]
                log = open(path_log, 'a')
                re_fr = 'Received from ' + self.client_address[0] + ':' +\
                    str(self.client_address[1]) + ' '
                LineaLog = re_fr + linearecibida.replace('\r\n', ' ') + '\r\n'
                registro = time.strftime('%Y%m%d%H%M%S') + ' ' +\
                    LineaLog.replace('\r\n', ' ') + '\r\n'
                log.write(registro)
                print re_fr + '\r\n' + linearecibida
                log.close()
                usuario = 0
                for key in d_usuarios:
                    if key == name:
                        usuario = 1
                        socket1 = socket.AF_INET
                        socket2 = socket.SOCK_DGRAM
                        my_socket = socket.socket(socket1, socket2)
                        socket3 = socket.SOL_SOCKET
                        socket4 = socket.SO_REUSEADDR
                        my_socket.setsockopt(socket3, socket4, 1)
                        ip = str(d_usuarios[name][0])
                        puerto = int(d_usuarios[name][1])
                        my_socket.connect((ip, puerto))

                        log = open(path_log, 'a')
                        send_to = 'Sent to ' + str(d_usuarios[name][0]) +\
                            ':' + d_usuarios[name][1] + ' '
                        LineaLog = send_to +\
                            linearecibida.replace('\r\n', ' ') + '\r\n'
                        registro = time.strftime('%Y%m%d%H%M%S') + ' ' +\
                            LineaLog.replace('\r\n', ' ') + '\r\n'
                        log.write(registro)
                        log.close()
                        my_socket.send(linearecibida)
                        print send_to + '\r\n' + linearecibida
            elif lineascliente[0] == 'BYE':
                name = lineascliente[1].split(':')[1]
                log = open(path_log, 'a')
                LineaLog = 'Received from ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) + ' ' +\
                    linearecibida.replace('\r\n', ' ') + '\r\n'
                registro = time.strftime('%Y%m%d%H%M%S') + ' ' +\
                    LineaLog.replace('\r\n', ' ') + '\r\n'
                log.write(registro)
                print 'Received from ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) +\
                    ' \r\n' + linearecibida
                log.close()
                usuario = 0
                for key in d_usuarios:
                    if key == name:
                        usuario = 1
                        socket1 = socket.AF_INET
                        socket2 = socket.SOCK_DGRAM
                        my_socket = socket.socket(socket1, socket2)
                        socket3 = socket.SOL_SOCKET
                        socket4 = socket.SO_REUSEADDR
                        my_socket.setsockopt(socket3, socket4, 1)
                        ip = str(d_usuarios[name][0])
                        puerto = int(d_usuarios[name][1])
                        my_socket.connect((ip, puerto))
                        log = open(path_log, 'a')
                        LineaLog = 'Sent to ' + str(d_usuarios[name][0]) +\
                            ':' + d_usuarios[name][1] + ' ' +\
                            linearecibida.replace('\r\n', ' ') + '\r\n'
                        registro = time.strftime('%Y%m%d%H%M%S') + ' ' +\
                            LineaLog.replace('\r\n', ' ') + '\r\n'
                        log.write(registro)
                        log.close()
                        my_socket.send(linearecibida)
                        print 'Sent to ' + str(d_usuarios[name][0]) +\
                            ':' + d_usuarios[name][1] + '\r\n' + linearecibida
                        try:
                            data = my_socket.recv(1024)
                        except socket.error:
                            error = 'Error: no server listening at ' +\
                                str(d_usuarios[name][0]) +\
                                " port " + d_usuarios[name][1]
                            log = open(path_log, 'a')
                            registro = time.strftime('%Y%m%d%H%M%S') +\
                                ' ' + error + '\r\n'
                            log.write(registro)
                            log.close()
                            print error
                            break
                        lineaservidor = data.split('\r\n')
                        if lineaservidor[0] == 'SIP/2.0 200 OK':
                            log = open(path_log, 'a')
                            LineaLog = 'Received from ' +\
                                str(d_usuarios[name][0]) +\
                                ':' + d_usuarios[name][1] + ' ' +\
                                data.replace('\r\n', ' ') + '\r\n'
                            registro = time.strftime('%Y%m%d%H%M%S') +\
                                ' ' + LineaLog.replace('\r\n', ' ') + '\r\n'
                            log.write(registro)
                            print 'Received from ' +\
                                str(d_usuarios[name][0]) +\
                                ':' + d_usuarios[name][1] + '\r\n' + data
                            self.wfile.write(data)
                            LineaLog = 'Sent to ' +\
                                self.client_address[0] + ':' +\
                                str(self.client_address[1]) + ' ' +\
                                data.replace('\r\n', ' ') +\
                                '\r\n'
                            registro = time.strftime('%Y%m%d%H%M%S') +\
                                ' ' + LineaLog.replace('\r\n', ' ') + '\r\n'
                            log.write(registro)
                            print 'Sent to ' + self.client_address[0] +\
                                ':' + str(self.client_address[1]) +\
                                '\r\n' + data
                            log.close()
            elif lineascliente[0] == 'INFO':
                log = open(path_log, 'a')
                LineaLog = 'Received from ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) + ' ' +\
                    linearecibida.replace('\r\n', ' ') + '\r\n'
                registro = time.strftime('%Y%m%d%H%M%S') + ' ' +\
                    LineaLog.replace('\r\n', ' ') + '\r\n'
                log.write(registro)
                print 'Received from ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) +\
                    ' \r\n' + linearecibida
                LineaLog = 'Sent to ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) +\
                    ' SIP/2.0 405 Method Not Allowed\r\n'
                registro = time.strftime('%Y%m%d%H%M%S') +\
                    ' ' + LineaLog.replace('\r\n', ' ') + '\r\n'
                log.write(registro)
                self.wfile.write('SIP/2.0 405 Method Not Allowed\r\n')
                print 'Sent to ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) + ' ' + '\r\n' +\
                    'SIP/2.0 405 Method Not Allowed\r\n'
                log.close()
            else:

                log = open(path_log, 'a')
                LineaLog = 'Received from ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) + ' ' +\
                    linearecibida.replace('\r\n', ' ') + '\r\n'
                registro = time.strftime('%Y%m%d%H%M%S') + ' ' +\
                    LineaLog.replace('\r\n', ' ') + '\r\n'
                log.write(registro)
                print 'Received from ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) + '\r\n' + linearecibida
                LineaLog = 'Sent to ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) +\
                    ' SIP/2.0 400 Bad Request\r\n'
                registro = time.strftime('%Y%m%d%H%M%S') + ' ' +\
                    LineaLog.replace('\r\n', ' ') + '\r\n'
                log.write(registro)
                self.wfile.write('SIP/2.0 400 Bad Request\r\n')
                print 'Sent to ' + self.client_address[0] +\
                    ':' + str(self.client_address[1]) +\
                    '\r\n' + 'SIP/2.0 400 Bad Request\r\n'
                log.close()

if __name__ == "__main__":
    parser = make_parser()
    cHandler = XMLHandler()
    parser.setContentHandler(cHandler)
    try:
        parser.parse(open(config))
    except IOError:
        print "Usage: python proxy_registrar.py config"
        raise SystemExit

    name = cHandler.dicc_config['name']
    ip_proxy = cHandler.dicc_config['ip_proxy']
    puerto_proxy = cHandler.dicc_config['puerto_proxy']
    path_proxy = cHandler.dicc_config['path_proxy']
    password_proxy = cHandler.dicc_config['password_proxy']
    path_log = cHandler.dicc_config['path_log']

    d_usuarios = {}

    serv = SocketServer.UDPServer((ip_proxy, int(puerto_proxy)), EchoHandler)
    print "Server MiServidor" + name + " listening at port " +\
        puerto_proxy + "...\r\n"
    log = open(path_log, 'a')
    registro = time.strftime('%Y%m%d%H%M%S') + " Server miservidor" +\
        name + "listening at port " + puerto_proxy + "...\r\n"
    log.write(registro)
    log.close()
    serv.serve_forever()
