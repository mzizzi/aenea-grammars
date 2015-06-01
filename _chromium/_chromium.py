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
        'next [<n>]':                        Key('c-g:%(n)d'),
        'previous [<n>]':                    Key('cs-g:%(n)d'),
        'back [<n>]':                        Key('a-left:%(n)d'),
        'forward [<n>]':                     Key('a-right:%(n)d'),
        })
    extras = [IntegerRef('n', 1, 10), Dictation('text')]
    defaults = {'n': 1}


class VimiumRule(MappingRule):
    mapping = aenea.configuration.make_grammar_commands('vimium', {
        'links': Key('f'),
        'search': Key('slash'),
        'search next': Key('n'),
        'search previous': Key('N'),
        'bookmarks': Key('o'),
    })
    extras = [Dictation('text')]
    defaults = {'text': ''}


chromium_grammar.add_rule(ChromiumRule())
chromium_grammar.add_rule(VimiumRule())
chromium_grammar.load()


def unload():
    global chromium_grammar
    if chromium_grammar:
        chromium_grammar.unload()
    chromium_grammar = None
