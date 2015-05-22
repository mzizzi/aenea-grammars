# (the original copyright notice is reproduced below)
#
# (c) Copyright 2008 by Christo Butcher
# Licensed under the LGPL, see <http://www.gnu.org/licenses/>
#

import aenea
import aenea.misc
import aenea.configuration
import aenea.format

from aenea.vocabulary import (
    register_dynamic_vocabulary,
    get_static_vocabulary,
    inhibit_global_dynamic_vocabulary,
    refresh_vocabulary
)

from aenea import (
    Alternative,
    CompoundRule,
    DictListRef,
    Grammar,
    IntegerRef,
    MappingRule,
    Repetition,
    RuleRef,
    AeneaContext,
    Key,
    Text,
)

import base.rules

import remote_debug

# Multiedit wants to take over dynamic vocabulary management.
MULTI_TAGS = [
    'multi.abbreviate',
    'multi'
]

inhibit_global_dynamic_vocabulary('multi', MULTI_TAGS)
refresh_vocabulary()


command_table = aenea.configuration.make_grammar_commands('multi', {
    'up [<n>]':    Key('up:%(n)d'),
    'down [<n>]':  Key('down:%(n)d'),
    'left [<n>]':  Key('left:%(n)d'),
    'right [<n>]': Key('right:%(n)d'),

    'gope [<n>]':  Key('pgup:%(n)d'),
    'drop [<n>]':  Key('pgdown:%(n)d'),

    'lope [<n>]':  Key('c-left:%(n)d'),
    'yope [<n>]':  Key('c-right:%(n)d'),

    'care':        Key('home'),
    'doll':        Key('end'),

    'file top':    Key('c-home'),
    'file toe':    Key('c-end'),

    'ace [<n>]':         Key('space:%(n)d'),
    'act':               Key('escape'),
    'chuck [<n>]':       Key('del:%(n)d'),
    'scratch [<n>]':     Key('backspace:%(n)d'),
    'slap [<n>]':        Key('enter:%(n)d'),
    'tab [<n>]':         Key('tab:%(n)d'),

    'line down [<n>]': Key('home:2, shift:down, end:2, shift:up, c-x, del, down:%(n)d, home:2, enter, up, c-v'),
    'lineup [<n>]':    Key('home:2, shift:down, end:2, shift:up, c-x, del, up:%(n)d, home:2, enter, up, c-v'),
    'nab [<n>]':       Key('home:2, shift:down, down:%(n)d, up, end:2, shift:up, c-c, end:2'),
    'plop [<n>]':      Key('c-v:%(n)d'),
    'squishy [<n>]':   Key('end:2, del, space'),
    'strip':           Key('s-end:2, del'),
    'striss':          Key('s-home:2, del'),
    'trance [<n>]':    Key('home:2, shift:down, down:%(n)d, up, end:2, shift:up, c-c, end:2, enter, c-v'),
    'wipe [<n>]':      Key('home:2, shift:down, down:%(n)d, up, end:2, del, shift:up, backspace'),

    'bump [<n>]':      Key('cs-right:%(n)d, del'),
    'whack [<n>]':     Key('cs-left:%(n)d, del'),

    'yank':            Key('c-c'),
    'keep':            Key('c-x'),

    'kink':            Key('c-z'),
}, config_key='commands')


class CommandRule(MappingRule):
    """
    Execute a multi grammar command defined in the commands dictionary. These commands
    can be renamed in the multi.json grammar configuration file.
    """
    mapping = command_table
    extras = [IntegerRef('n', 1, 100)]
    defaults = {'n': 1}


class MultiRepetition(Repetition):
    def __init__(self):
        """
        A combination of all the rules in the multi grammar. This includes
        both text insertion actions and text manipulation actions.  This is
        the core rule of the multi grammar.  Also allows for these elements
        to be repeated in sequence.
        """
        multi_element = Alternative(
            name='multi_element',
            children=[
                RuleRef(rule=base.rules.CharacterInsertionRule()),
                RuleRef(rule=base.rules.IdentifierInsertionRule()),
                RuleRef(rule=CommandRule()),
                DictListRef('dynamic', register_dynamic_vocabulary('multi')),
            ]
        )

        super(MultiRepetition, self).__init__(
            multi_element,
            min=1,
            max=12,
            name='multi_repetition'
        )

    def value(self, node):
        values = super(MultiRepetition, self).value(node)
        flattened_values = Text('')

        for value in values:
            flattened_values += value

        return flattened_values


class MultiRule(CompoundRule):
    """
    This rule processes the recognition of a multi_repetition element. It
    executes each child of the recognition in order.
    """
    spec = '<multi_repetition> [parrot [<m>]]'
    extras = [
        MultiRepetition(),
        IntegerRef('m', 1, 100)
    ]
    defaults = {'m': 1}

    def _process_recognition(self, node, extras):
        multi_repetition = extras['multi_repetition']
        utterance_multiplier = extras['m']
        (multi_repetition * utterance_multiplier).execute()


# Disable the multi grammar in certain contexts. The contexts in which multi is
# disabled are defined in the multi.json grammar configuration file via a regular
# expression. For instance: it is often desirable to disable the multi grammar while
# other grammars such as vim/emacs are active
conf = aenea.configuration.ConfigWatcher(('grammar_config', 'multi')).conf
local_disable_context = aenea.configuration.make_local_disable_context(conf)
proxy_disable_context = aenea.configuration.make_proxy_disable_context(conf)
context = AeneaContext(proxy_disable_context, local_disable_context)

# Load the grammar
grammar = Grammar('multi', context=~context)
grammar.add_rule(MultiRule())
grammar.load()


def unload():
    """
    Unload function which will be called at unload time.  Updates global dynamic
    vocabularies and unloads this grammar.
    """
    global grammar
    aenea.vocabulary.uninhibit_global_dynamic_vocabulary('multi', MULTI_TAGS)
    for tag in MULTI_TAGS:
        aenea.vocabulary.unregister_dynamic_vocabulary(tag)
    if grammar:
        grammar.unload()
    grammar = None
