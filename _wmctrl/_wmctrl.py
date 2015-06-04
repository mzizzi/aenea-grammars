import aenea.configuration
import aenea

from aenea import (
    Grammar,
    MappingRule,
)

import dragonfly


def window_select():
    aenea.communications.server.window_select()


def show_dragon():
    aenea.communications.server.show_dragon()


class WindowSelectCommand(MappingRule):
    mapping = aenea.configuration.make_grammar_commands('wmctrl', {
        'window select': dragonfly.Function(window_select),
        'show dragon': dragonfly.Function(show_dragon)
    }, 'commands')


window_manager_control_grammar = Grammar('wmctrl')
window_manager_control_grammar.add_rule(WindowSelectCommand())
window_manager_control_grammar.load()


def unload():
    global window_manager_control_grammar
    if window_manager_control_grammar:
        window_manager_control_grammar.unload()
    window_manager_control_grammar = None
