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

from aenea.proxy_contexts import ProxyAppContext

from aenea import (
    Alternative,
    CompoundRule,
    DictListRef,
    Grammar,
    IntegerRef,
    MappingRule,
    AeneaContext,
    Key,
    Text,
    AppContext,
    Repetition,
    RuleRef,
)

import base.rules

import remote_debug

GRAMMAR_NAME = 'idea'

# idea wants to take over dynamic vocabulary management.
IDEA_TAGS = [
    'idea',
    'idea.abbreviate'
]

inhibit_global_dynamic_vocabulary(GRAMMAR_NAME, IDEA_TAGS)
refresh_vocabulary()

repeatable_command_table = aenea.configuration.make_grammar_commands('idea', {
    'up [<n>]':         Key('up:%(n)d'),
    'down [<n>]':       Key('down:%(n)d'),
    'left [<n>]':       Key('left:%(n)d'),
    'right [<n>]':      Key('right:%(n)d'),

    'gope [<n>]':       Key('pgup:%(n)d'),
    'drop [<n>]':       Key('pgdown:%(n)d'),

    'lope [<n>]':       Key('c-left:%(n)d'),
    'yope [<n>]':       Key('c-right:%(n)d'),

    'care':             Key('home'),
    'doll':             Key('end'),

    'file top':         Key('c-home'),
    'file toe':         Key('c-end'),

    'ace [<n>]':        Key('space:%(n)d'),
    'act':              Key('escape'),
    'chuck [<n>]':      Key('del:%(n)d'),
    'scratch [<n>]':    Key('backspace:%(n)d'),
    'slap [<n>]':       Key('enter:%(n)d'),
    'lilo':             Key('end, enter'),
    'tab [<n>]':        Key('tab:%(n)d'),

    'line down [<n>]':  Key('as-down'),
    'lineup [<n>]':     Key('as-up'),
    'squish [<n>]':     Key('c-j'),
    'wipe [<n>]':       Key('c-y'),

    'bump [<n>]':       Key('cs-right:%(n)d, del'),
    'whack [<n>]':      Key('cs-left:%(n)d, del'),

    'yank':             Key('c-c'),
    'keep':             Key('c-x'),
    'plop [<n>]':       Key('c-v:%(n)d'),
    'kink':            Key('c-z'),

    'selection mode':   Key('a-s'),

    'snap [<n>]':       Key('c-w:%(n)d'),
    'select block':     Key('c-lbracket:10, cs-rbracket'),

    'navi mend [<n>]':  Key('a-down:%(n)d'), # next method
    'navi mart [<n>]':  Key('a-up:%(n)d'),   # previous method
    'navi blart [<n>]': Key('c-lbracket:%(n)d'), # previous block
    'navi blend [<n>]': Key('c-rbracket:%(n)d'), # next block

    'wiki [<m>]':       Key('c-g/10') + Text('%(m)d') + Key('enter'),
}, config_key='editor')


terminal_command_table = aenea.configuration.make_grammar_commands(GRAMMAR_NAME, {
    'navi flip':           Key('a-right'),
    'navi flop':           Key('a-left'),
    'navi flake':          Key('c-f4'),
    'navi split':          Key('a-equal'),
    'navi unsplit':        Key('a-hyphen'),
    'navi hike':           Key('a-backslash'),

    'pogo name':           Key('s-f6'),
    'pogo error':          Key('f2'),
    'pogo error previous': Key('s-f2'),
}, config_key='terminal')


class EditorRule(MappingRule):
    """
    Commands that can be repeated.  Limited to in-editor-window commands.
    """
    mapping = repeatable_command_table
    extras = [
        IntegerRef('n', 1, 99),
        IntegerRef('m', 1, 2000)
    ]
    defaults = {'n': 1, 'm': 1}


class RepeatableRule(Repetition):
    def __init__(self):
        """
        A combination of all the rules in the idea grammar. This includes
        both text insertion actions and text manipulation actions.  This is
        the core rule of the idea grammar.  Also allows for these elements
        to be repeated in sequence.
        """
        repeatable_element = Alternative(
            name='repeatable_element',
            children=[
                RuleRef(rule=base.rules.CharacterInsertionRule()),
                RuleRef(rule=base.rules.IdentifierInsertionRule()),
                RuleRef(rule=EditorRule()),
                DictListRef('dynamic', register_dynamic_vocabulary(GRAMMAR_NAME)),
            ]
        )

        super(RepeatableRule, self).__init__(
            repeatable_element,
            min=1,
            max=12,
            name='repeatable_rule'
        )

    def value(self, node):
        values = super(RepeatableRule, self).value(node)
        flattened_values = Text('')

        for value in values:
            flattened_values += value

        return flattened_values


class TerminalRule(MappingRule):
    """
    Commands that should end a recognition.
    """
    mapping = terminal_command_table
    extras = []
    defaults = {}


class IdeaRule(CompoundRule):
    """
    """
    spec = '[<repeatable_rule>] [parrot [<i>]] [<terminal>]'
    extras = [
        RepeatableRule(),
        IntegerRef('i', 1, 99),
        RuleRef(rule=TerminalRule(), name='terminal')
    ]
    defaults = {'i': 1}

    def _process_recognition(self, node, extras):
        repeatable = extras['repeatable_rule']
        utterance_multiplier = extras['i']
        (repeatable * utterance_multiplier).execute()

        if 'terminal' in extras:
            extras['terminal'].execute()


context = aenea.wrappers.AeneaContext(
    ProxyAppContext(match='regex', title='(?i).*Intellij IDEA.*'),
    AppContext(title='Intellij IDEA')
)

# Load the grammar
grammar = Grammar(GRAMMAR_NAME, context=context)
grammar.add_rule(IdeaRule())
grammar.load()


def unload():
    """
    Unload function which will be called at unload time.  Updates global dynamic
    vocabularies and unloads this grammar.
    """
    global grammar
    aenea.vocabulary.uninhibit_global_dynamic_vocabulary(
        GRAMMAR_NAME, IDEA_TAGS
    )
    for tag in IDEA_TAGS:
        aenea.vocabulary.unregister_dynamic_vocabulary(tag)
    if grammar:
        grammar.unload()
    grammar = None
