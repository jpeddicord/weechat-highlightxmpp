# HighlightXMPP 0.6 for IRC. Requires WeeChat >= 0.3.0,
# Python >= 2.6, and sendxmpp (https://github.com/lhost/sendxmpp) or
# equivalent.
# Repo: https://github.com/jpeddicord/weechat-highlightxmpp
#
# Copyright (c) 2009-2015 Jacob Peddicord <jacob@peddicord.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#######
#
# You must configure sendxmpp before using this plugin, so you'll be able to
# send message from commandline using format:
#
#   echo "message" | sendxmpp someid@jabber.org
#
# also you will need to provide JID to send messages:
#
#   /set plugins.var.python.highlightxmpp.to myid@jabber.org
#
# finally, you might want to change the sendxmpp binary to some other
# implementation (like https://salsa.debian.org/mdosch/go-sendxmpp) and/or
# provide some additional parameters, i.e.:
#
#   /set plugins.var.python.highlightxmpp.command "/path/to/go-sendxmpp -t"
#
# You can set debug option to "on" if you experience issues regarding sending
# messages via sendxmpp:
#
#   /set plugins.var.python.highlightxmpp.debug off
#
import subprocess

import weechat


SETTINGS = {'command': 'sendxmpp',
            'to': '',
            'debug': 'off'}
INFO = ('highlightxmpp',
        'Jacob Peddicord <jacob@peddicord.net>',
        '0.6',
        'GPL3',
        "Relay highlighted & private IRC messages over XMPP (Jabber)",
        '',
        '')


def send_xmpp(data, signal, message):
    """Send XMPP message using external commandline tool."""
    jid = weechat.config_get_plugin('to')
    command = weechat.config_get_plugin('command').split(' ')
    debug = weechat.config_get_plugin('debug') == 'on'

    if not jid:
        weechat.prnt('', 'You need to provide destination JID to use this '
                     'plugin.')
        return weechat.WEECHAT_RC_OK

    command.append(jid)

    pipe = subprocess.Popen(command, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        message = message.encode()
    except UnicodeDecodeError:
        pass

    _, stderr = pipe.communicate(input=message)
    if pipe.returncode != 0 and debug:
        try:
            stderr = stderr.decode()
        except UnicodeDecodeError:
            pass
        weechat.prnt('', 'Error sending message to %s:\n%s' % (jid, stderr))
    return weechat.WEECHAT_RC_OK


if weechat.register(*INFO):
    for setting in SETTINGS:
        if not weechat.config_is_set_plugin(setting):
            weechat.config_set_plugin(setting, SETTINGS[setting])

    weechat.hook_signal('weechat_highlight', 'send_xmpp', '')
    weechat.hook_signal('weechat_pv', 'send_xmpp', '')
