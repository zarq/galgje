import sys
import socket
import select
import queue
import os
import time
import imp
import traceback

from galgje_utils import debug

CONNECTED, NICK_SENT, JOINING, JOINED = range(4)

class IrcClient(object):
    HOST='irc.fruit.je'
    PORT=6667
    NICK='ivobot'
    IDENT='ivobot'
    REALNAME='ivobot'
    CHANNEL = "#ivo"

    def __init__(self):
        self.send_queue = queue.Queue()
        self.readbuffer = bytearray()
        self.writebuffer = bytearray()

        self._module_timestamp = time.time()
        self._module = __import__('galgjeirccommands')
        self.module_filename = self._module.__file__
        self.init_module_handler()

    def connect(self):
        self.s = socket.socket()
        self.s.connect((self.HOST, self.PORT))
        self.s.setblocking(False)
        self.state = CONNECTED
        self.go()


    def sendstring(self, string):
        debug(string, end='')
        self.send_queue.put(string.encode('utf-8'))

    def parse_line(self, line, n=3):
        parts = []
        while n > 0:
            if ' ' in line:
                part, line = line.split(' ', 1)
                n -= 1
                parts.append(part)
            else:
                parts.append(line)
                n -= 1
                break
        if n > 0:
            parts += [None] * n
        return parts

    def dispatch_line(self, line):
        debug(line)
        if line.startswith('PING'):
            self.sendstring("PONG %s\r\n" % line[5:])
        if self.state == CONNECTED:
            self.sendstring("NICK %s\r\n" % (self.NICK,))
            self.sendstring("USER %s %s bla :%s\r\n" % (self.IDENT, self.HOST, self.REALNAME))
            self.state = NICK_SENT
        elif self.state == NICK_SENT:
            if line.startswith(':'):
                server, code, args = self.parse_line(line)
                if code == '001':
                    self.sendstring("JOIN %s\r\n" % (self.CHANNEL,))
                    self.state = JOINING
        elif self.state == JOINING:
            if line.startswith(':'):
                source, cmd, args = self.parse_line(line)
                if cmd == 'JOIN':
                    assert args[1:] == self.CHANNEL
                    self.state = JOINED
        elif self.state == JOINED:
            if line.startswith(':'):
                source, cmd, dest, args = self.parse_line(line, 4)
                self.module.handle(source, cmd, dest, args)

        # if line[0] == 'PING':
        #     sendstring("PONG %s\r\n" % (line[1],))
        # if line[0].startswith(':'):
        #     
        #     sendstring("JOIN #galgje\r\n")

    def check_updated_module(self):
        statinfo = os.stat(self.module_filename)
        if statinfo.st_mtime > self._module_timestamp:
            debug("%s has changed, reloading" % (self.module_filename,))
            try:
                imp.reload(self._module)
            except:
                traceback.print_exc()
                return
            self.init_module_handler()
            self._module_timestamp = statinfo.st_mtime

    def init_module_handler(self):
        self.module = self._module.Module()
        self.module.sendstring = self.sendstring

    def go(self):
        while True:
            if not self.send_queue.empty() or self.writebuffer:
                w = [self.s]
            else:
                w = []
            r, w, e = select.select([self.s], w, [self.s], 1)
            if self.s in r:
                self.readbuffer += self.s.recv(1024)
                while True:
                    idx = self.readbuffer.find(b'\n')
                    if idx == -1:
                        break
                    line = self.readbuffer[:idx].decode('utf-8')
                    if len(line) > 0 and line[-1] == '\r':
                        line = line[:-1]  # strip CR
                    self.readbuffer = self.readbuffer[idx + 1:]
                    self.dispatch_line(line)
            if self.s in w:
                if not self.send_queue.empty():
                    item = self.send_queue.get_nowait()
                    if item:
                        self.writebuffer += item
                if self.writebuffer:
                    n = self.s.send(self.writebuffer)
                    if n:
                        self.writebuffer = self.writebuffer[n:]
            if self.s in e:
                return

            self.check_updated_module()


client = IrcClient()
client.connect()
