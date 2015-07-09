from aenea import (
    Grammar,
    MappingRule,
    RuleRef,
    Repetition,
    CompoundRule,
    Key
)

import base.characters


class HotkeyRule(CompoundRule):
    def __init__(self):
        spec = 'hot [con] [alt] [shift] [win] <keystrokes>'

        mapping = {}
        mapping.update(base.characters.LOWERCASE)
        mapping.update(base.characters.SYMBOLS)
        mapping.update(base.characters.DIGITS)

        extras = [Repetition(
            RuleRef(MappingRule(mapping=mapping)),
            min=1,
            max=3,
            name='keystrokes'
        )]

        CompoundRule.__init__(self, spec=spec, extras=extras)
        
    def _process_recognition(self, node, extras):
        words = node.words()

        key_specs = [key_spec for key_spec in extras['keystrokes']]

        if 'win' in words:
            key_specs.insert(0, 'win:down')
            key_specs.append('win:up')
        if 'shift' in words:
            key_specs.insert(0, 'shift:down')
            key_specs.append('shift:up')
        if 'alt' in words:
            key_specs.insert(0, 'alt:down')
            key_specs.append('alt:up')
        if 'con' in words:
            key_specs.insert(0, 'ctrl:down')
            key_specs.append('ctrl:up')

        spec = ', '.join(key_specs)
        Key(spec).execute()


hotkey_grammar = Grammar('hotkey')
hotkey_grammar.add_rule(HotkeyRule())
hotkey_grammar.load()


def unload():
    global hotkey_grammar
    if hotkey_grammar:
        hotkey_grammar.unload()
    hotkey_grammar = None
