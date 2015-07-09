import aenea.config
import aenea.configuration

from aenea import (
    AeneaContext,
    AppContext,
    Dictation,
    Grammar,
    IntegerRef,
    Key,
    MappingRule,
    ProxyAppContext,
    Text
    )

proxy_context = (ProxyAppContext(executable='chromium-browse') |
                 ProxyAppContext(cls_name='chromium-browser', cls='chromium-browser'))
local_context = (AppContext(executable='chrome') |
                 AppContext(executable='chromium'))
chromium_context = aenea.AeneaContext(proxy_context, local_context)

chromium_grammar = Grammar('chromium', context=chromium_context)


class ChromiumRule(MappingRule):
    mapping = aenea.configuration.make_grammar_commands('chromium', {
        'address':                           Key('c-l'),
        'close [<n>] ( frame | frames )':    Key('c-w:%(n)d'),
        'open frame':                        Key('c-t'),
        'open window':                       Key('c-n'),
        'reopen [<n>] ( frame | frames )':   Key('cs-t:%(n)d'),
        '[ go to ] frame [<n>]':             Key('c-%(n)d'),
        'frame left [<n>]':                  Key('cs-tab:%(n)d'),
        'frame right [<n>]':                 Key('c-tab:%(n)d'),
        'history':                           Key('c-h'),
        'reload':                            Key('c-r'),
        'back [<n>]':                        Key('a-left:%(n)d'),
        'forward [<n>]':                     Key('a-right:%(n)d'),
        'search [<text>]':                   Key('c-f') + Text('%(text)s'),
        'search next [<n>]':                 Key('c-f') + Key('enter:%(n)d)'),
        'search previous [<n>]':             Key('c-f') + Key('s-enter:%(n)d)'),
        })

    extras = [
        IntegerRef('n', 1, 10), Dictation('text'),
        Dictation('text'),
    ]

    defaults = {'n': 1, 'text': ''}


class VimiumRule(MappingRule):
    mapping = aenea.configuration.make_grammar_commands('vimium', {
        'show links': Key('escape, escape, f'),
        'bookmarks': Key('o'),
    })


chromium_grammar.add_rule(ChromiumRule())
chromium_grammar.add_rule(VimiumRule())
chromium_grammar.load()


def unload():
    global chromium_grammar
    if chromium_grammar:
        chromium_grammar.unload()
    chromium_grammar = None
