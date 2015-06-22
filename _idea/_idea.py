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
    Sequence,
    Dictation,
    DictList,
)
from base.characters import LOWERCASE, UPPERCASE, SYMBOLS_TEXT, DIGITS

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
    'cart':             Key('end'),

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
    'grab':             Key('c-x'),
    'plop [<n>]':       Key('c-v:%(n)d'),
    'kink':             Key('c-z'),

    'selection mode':   Key('a-s'),

    'expan [<n>]':      Key('c-w:%(n)d'),
    'select block':     Key('c-lbracket:10, cs-rbracket'),

    'method yope [<n>]': Key('a-down:%(n)d'), # next method
    'method lope [<n>]': Key('a-up:%(n)d'),   # previous method
    'block lope [<n>]':  Key('c-lbracket:%(n)d'), # previous block
    'block yope [<n>]':  Key('c-rbracket:%(n)d'), # next block

    'line [<m>]':       Key('c-g/5') + Text('%(m)d') + Key('enter'),
    'search':           Key('c-f/5'),
}, config_key='editor')


terminal_command_table = aenea.configuration.make_grammar_commands(GRAMMAR_NAME, {
    'win flip':             Key('a-right'),
    'win flop':             Key('a-left'),
    'win kill':             Key('c-f4'),
    'win split':            Key('a-equal'),
    'win unsplit':          Key('a-hyphen'),
    'win hike':             Key('a-backslash'),

    'search everything':    Key('shift:down,shift:up,shift:down,shift:up'),
    'reformat code':        Key('a-r'),
    'refactor name':        Key('s-f6'),
    'problem next':         Key('f2'),
    'problem previous':     Key('s-f2'),
    'go to declaration':    Key('c-b'),
    'show docs':            Key('c-q'),

    'auto comp':            Key('a-enter'),
    'idea terminal':        Key('a-f12'),
    'idea project':         Key('a-f1'),
    'idea rerun':           Key('c-f5'),
    'idea run':             Key('a-4'),
    'idea debug':           Key('a-5'),
    'debug over':           Key('f8'),
    'debug into':           Key('f7'),
}, config_key='terminal')


class EditorRule(MappingRule):
    """
    Editor window commands.
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
        A combination of all repeatable elements in the idea grammar. This
        includes both text insertion actions, text manipulation, and
        navigation actions.  This is the workhorse rule of the idea grammar.
        Allows for these elements to be spoken continuously.
        """
        repeatable_element = Alternative(
            name='repeatable_element',
            children=[
                RuleRef(rule=base.rules.CharacterInsertionRule()),
                RuleRef(rule=base.rules.IdentifierInsertionRule()),
                RuleRef(rule=EditorRule()),
                DictListRef('dynamic',
                    register_dynamic_vocabulary(GRAMMAR_NAME)),
                DictListRef(
                    'static idea',
                    DictList('static idea', get_static_vocabulary('idea')),
                ),
            ]
        )

        super(RepeatableRule, self).__init__(
            repeatable_element,
            min=1,
            max=10,
            name='repeatable_rule'
        )

    def value(self, node):
        values = super(RepeatableRule, self).value(node)
        flattened_values = Text('')

        for value in values:
            flattened_values += value

        return flattened_values


class EmacsIdeasAceJumpRule(MappingRule):
    """
    EmacsIdeas plugin bindings.  Currently only a few of the acejump hotkeys
    are implemented.

    "scar alpha" (highlights all 'a' characters for jumping)
    "sword alpha" (highlights all words beginning with 'a' for jumping)
    """
    def __init__(self):
        chars = LOWERCASE.copy()
        chars.update(UPPERCASE)
        chars.update(SYMBOLS_TEXT)
        chars.update(DIGITS)

        single_character_element = RuleRef(
            rule=MappingRule(mapping=chars, name='emacs_ideas_mapping'),
            name='char'
        )

        mapping = {
            'scar <char>':  Key('a-p') + Text('%(char)s'),
            'sword <char>': Key('a-k') + Text('%(char)s'),
        }

        super(EmacsIdeasAceJumpRule, self).__init__(
            mapping=mapping,
            extras=[single_character_element],
            defaults={'char': ''}
        )


class TerminalRule(Alternative):
    """
    Commands that should end a recognition for the idea grammar.  These are
    commands that don't usually require immediate action after speaking them.
    """

    def __init__(self):
        terminal_command_element = RuleRef(
            rule=MappingRule(
                mapping=terminal_command_table,
                name='terminal_command_element'
            )
        )

        emacs_ideas_element = RuleRef(rule=EmacsIdeasAceJumpRule())

        super(TerminalRule, self).__init__(
            children=[
                terminal_command_element,
                emacs_ideas_element
            ],
            name='terminal_rule'
        )


class LiteralRule(CompoundRule):
    spec = 'literal <d>'
    extras = [Dictation(name='d')]

    def value(self, node):
        words = node.words()
        return Text(base.format.natword(words[1:]))


class IdeaRule(CompoundRule):
    """
    Top level idea grammar rule

    <repeatable_rule> is any character, vocabulary word, or formatted
    dictation the grammar allows for these items to be spoken continuously.
    If <repeatable rule> is followed by "parrot <number>" then the entire
    <repeatable_rule> recognition will be multiplied by <number>.

    <terminal_rule> is the set of rules that should aren't frequently used
    in series with other commands.  They may follow repeatable rules without
    pausing.

    <literal_rule> inserts a raw dictation that would otherwise conflict with
     an idea rule.
    """
    spec = '[<repeatable_rule>] [parrot [<i>]] [<terminal_rule>] ' \
           '[<literal_rule>]'
    extras = [
        RepeatableRule(),
        IntegerRef('i', 1, 99),
        TerminalRule(),
        RuleRef(name='literal_rule', rule=LiteralRule()),
    ]
    defaults = {'i': 1}

    def _process_recognition(self, node, extras):
        repeatable = extras.get('repeatable_rule', None)
        if repeatable is not None:
            utterance_multiplier = extras['i']
            (repeatable * utterance_multiplier).execute()

        if 'terminal_rule' in extras:
            extras['terminal_rule'].execute()

        if 'literal_rule' in extras:
            extras['literal_rule'].execute()


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
