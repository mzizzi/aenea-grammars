import aenea.configuration
import aenea
from aenea.communications import server

from aenea import (
    Grammar,
    MappingRule,
    DictList,
    DictListRef,
    CompoundRule
)

import dragonfly
from time import time


class WmctrlRule(MappingRule):
    mapping = aenea.configuration.make_grammar_commands('wmctrl', {
        'window select': dragonfly.Function(lambda: server.window_select()),
        'focus dragon': dragonfly.Function(lambda: server.show_dragon()),
        'focus chrome': dragonfly.Function(lambda: server.show_chrome()),
        'focus intellij': dragonfly.Function(lambda: server.show_intellij()),
        'focus hipchat': dragonfly.Function(lambda: server.show_hipchat()),
        'focus terminal': dragonfly.Function(lambda: server.show_terminal())
    }, 'commands')


executable_map = DictList('executable')


class FocusRule(CompoundRule):
    spec = 'focus <executable>'
    extras = [DictListRef('executable', executable_map)]

    def _process_begin(self):
        t = time()
        executable_map.clear()
        executable_map.update(
            aenea.communications.server.get_window_executables())
        t = time() - t
        print 'updated executable map %.3fs %s, ' % (t, executable_map.keys())

    def _process_recognition(self, node, extras):
        aenea.communications.server.set_focus(extras['executable'])


window_manager_control_grammar = Grammar('wmctrl')
window_manager_control_grammar.add_rule(WmctrlRule())
# window_manager_control_grammar.add_rule(FocusRule())
window_manager_control_grammar.load()


def unload():
    global window_manager_control_grammar
    if window_manager_control_grammar:
        window_manager_control_grammar.unload()
    window_manager_control_grammar = None
