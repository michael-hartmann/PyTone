# -*- coding: ISO-8859-1 -*-

# Copyright (C) 2002, 2019 J�rg Lehmann <joerg@luga.de>
#
# This file is part of PyTone (http://www.luga.de/pytone/)
#
# PyTone is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2
# as published by the Free Software Foundation.
#
# PyTone is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyTone; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import curses
import config
import hub, events
import help
import window
import events
import encoding

# indicator which can be used to signalise that the statusbar
# has to be terminated here
terminate = [("TERMINATE", 0)]

def generatedescription(section, name):
    primarykey = config.keybindings[section][name][0]
    keyname = help.getkeyname(primarykey)

    # save some space
    if keyname.startswith("<") and keyname.endswith(">"):
        keyname = keyname[1:-1]

    return [(keyname, config.colors.statusbar.key),
            (":"+help.descriptions[section][name][0],
             config.colors.statusbar.description)]


class statusbar(window.window):
    def __init__(self, screen, line, width, channel):
        self.channel = channel
        # self.content[0]: local info
        # self.content[1]: player info
        # self.content[2]: global info
        self.content = [[], [], []]

        # message overriding contents
        self.message = None
        # for identification purposes, we only generate this once
        self.removemessageevent = events.statusbar_showmessage(None)
        window.window.__init__(self, screen,
                               1, width, line, 0,
                               config.colors.statusbar,
                               None)
        self.channel.subscribe(events.statusbar_update, self.statusbar_update)
        self.channel.subscribe(events.statusbar_showmessage, self.statusbar_showmessage)

        # hack to export some properties of the statusbar singleton into
        # the module namespace
        global separator
        if width<=80:
            separator = [(" ", self.colors.background)]
        else:
            separator = [("  ", self.colors.background)]


    def resize(self, line, width):
        window.window.resize(self, 1, width, line, 0)

        global separator
        if width<=80:
            separator = [(" ", self.colors.background)]
        else:
            separator = [("  ", self.colors.background)]

    # event handler

    def statusbar_update(self, event):
        self.content[event.pos] = event.content
        self.update()

    def statusbar_showmessage(self, event):
        self.message = event.message
        if self.message:
            # make message disappear after a certain time
            hub.notify(events.sendeventin(self.removemessageevent, 2, replace=1))
        self.update()

        # we want to get a message out immediately, so we force its output
        curses.panel.update_panels()
        curses.doupdate()

    # update method

    def update(self):
        window.window.update(self)
        self.move(0,0)
        self.clrtoeol()

        if self.message:
            self.addstr(encoding.encode(self.message), config.colors.statusbar.key)
        else:
            for element in self.content[0]+separator+self.content[1]+separator+self.content[2]:
                if element==terminate[0]:
                    break
                self.addstr(encoding.encode(element[0]), element[1])
