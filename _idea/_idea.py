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
)

import remote_debug

GRAMMAR_NAME = 'idea'

# idea wants to take over dynamic vocabulary management.
IDEA_TAGS = [
    'idea',
    'idea.abbreviate'
]

inhibit_global_dynamic_vocabulary(GRAMMAR_NAME, IDEA_TAGS)
refresh_vocabulary()


command_table = aenea.configuration.make_grammar_commands(GRAMMAR_NAME, {
    'snap [<n>]':    Key('c-w:%(n)d'),

    'navi mend [<n>]':     Key('a-down:%(n)d'), # next method
    'navi mart [<n>]':     Key('a-up:%(n)d'),   # previous method
    'navi line [<n>]':     Key('c-g/10') + Text('%(n)d') + Key('enter'),
    'navi blart [<n>]':    Key('c-lbracket:%(n)d'), # previous block
    'navi blend [<n>]':    Key('c-rbracket:%(n)d'), # next block
    'navi doc':            Key('c-q'),

    'navi flip':           Key('a-right'),
    'navi flop':           Key('a-left'),
    'navi flake':          Key('c-f4'),
    'navi split':          Key('a-equal'),
    'navi unsplit':        Key('a-hyphen'),
    'navi hike':           Key('a-backslash'),

    'pogo line':           Key('cs-enter'),
    'pogo name':           Key('s-f6'),
    'pogo error':          Key('f2'),
    'pogo error previous': Key('s-f2'),

    'select block': Key('c-lbracket:10, cs-rbracket'),

    # TODO:
    # sticky selection a-s

    }, config_key='commands')


class IdeaRule(MappingRule):
    """
    Execute a multi grammar command defined in the commands dictionary. These commands
    can be renamed in the multi.json grammar configuration file.
    """
    mapping = command_table
    extras = [IntegerRef('n', 1, 2000)]
    defaults = {'n': 1}


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
    aenea.vocabulary.uninhibit_global_dynamic_vocabulary('multi', IDEA_TAGS)
    for tag in IDEA_TAGS:
        aenea.vocabulary.unregister_dynamic_vocabulary(tag)
    if grammar:
        grammar.unload()
    grammar = None
