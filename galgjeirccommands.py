import traceback
import re
import imp

from galgje_utils import debug
import galgje

class Recipient(object):
    def __init__(self, channel, nick):
        self.channel = channel
        self.nick = nick

class Module(object):
    def __init__(self):
        self.quiet = False
        self.auto_galgje = False

    def parse_f00f(self, sender, s):
        assert(s.startswith(':'))
        s = s[1:]
        if s.startswith('Galgjewoord:'):
            debug(s)
            pattern = b'^.*\xe2\x80\x98(?P<template>.*)\xe2\x80\x99( \((?P<letters>.*)\))?\.'.decode('utf-8')
            debug(pattern)
            match = re.match(pattern, s)
            if match:
                debug(match.group('template'))
                template = match.group('template')
                letters = match.group('letters')
                verboden = ''
                if letters:
                    verboden = letters
                self.galgje_guess(sender, template, set(verboden))
        elif s.startswith('Het woord was'):
            if self.auto_galgje:
                self.say_publicly(sender, "!galgje")

    def galgje_guess(self, sender, template, verboden=set()):
        # imp.reload(galgje)
        poging = galgje.galgje_reentrant(template, verboden)
        debug(poging)
        self.respond_publicly(sender, "!raad %s" % (poging,))

    def parse_command(self, sender, s):
        debug("command: %r" % (s,))
        if s.startswith(':`'):
            if ' ' in s:
                command, args = s[2:].split(' ', 1)
            else:
                command = s[2:]
                args = ()
            debug("command = %r" % (command,))
            self.dispatch_command(sender, command, args)

    def say_publicly(self, recipient, message):
        self.sendstring("PRIVMSG %s :%s\r\n" % (recipient.channel, message))

    def respond_publicly(self, recipient, message):
        self.sendstring("PRIVMSG %s :%s: %s\r\n" % (recipient.channel, recipient.nick, message))

    def dispatch_command(self, sender, command, args):
        methodname = 'handle_command_' + command
        if hasattr(self, methodname):
            getattr(self, methodname)(args)
        else:
            self.respond_publicly(sender, "No such command %r" % (command,))

    def parse_recipient(self, source, dest):
        debug(source)
        debug(dest)
        assert(source.startswith(':'))
        source = source[1:]
        if '!' in source:
            source = source[:source.find('!')]
        recipient = Recipient(dest, source)
        return recipient

    def handle(self, source, cmd, dest, args):
        debug("source=%r; cmd=%r; args=%r" % (source, cmd, args))
        recipient = self.parse_recipient(source, dest)
        try:
            if cmd == 'PRIVMSG':
                if recipient.nick == 'zarq':
                    # yay admin
                    # debug("YAY ADMIN")
                    self.parse_command(recipient, args)
                elif recipient.nick == 'f00f':
                    self.parse_f00f(recipient, args)
        except Exception as ex:
            traceback.print_exc()
            recipient = Recipient('#ivo', 'zarq')
            self.respond_publicly(recipient, "HALP %r" % (ex,))

    def handle_command_stil(self):
        self.quiet = True

    def handle_command_auto(self, args):
        self.auto_galgje = not self.auto_galgje
