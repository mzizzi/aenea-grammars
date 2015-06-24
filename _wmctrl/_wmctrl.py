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


class WmctrlRule(MappingRule):
    mapping = aenea.configuration.make_grammar_commands('wmctrl', {
        'window select': dragonfly.Function(lambda: server.window_select()),
        'focus dragon': dragonfly.Function(lambda: server.show_dragon()),
        'focus chrome': dragonfly.Function(lambda: server.show_chrome()),
        'focus intellij': dragonfly.Function(lambda: server.show_intellij()),
        'focus hipchat': dragonfly.Function(lambda: server.show_hipchat()),
        'focus terminal': dragonfly.Function(lambda: server.show_terminal()),
        'focus G edit': dragonfly.Function(lambda: server.show_gedit())
    }, 'commands')


window_manager_control_grammar = Grammar('wmctrl')
window_manager_control_grammar.add_rule(WmctrlRule())
window_manager_control_grammar.load()


def unload():
    global window_manager_control_grammar
    if window_manager_control_grammar:
        window_manager_control_grammar.unload()
    window_manager_control_grammar = None
