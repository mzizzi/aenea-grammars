from aenea import (
    MappingRule,
    CompoundRule,
    Text,
    Dictation
)

from format import FORMAT

import base.characters

__all__ = [
    'AlphaInsertionRule',
    'DigitInsertionRule',
    'AlphaNumInsertionRule',
    'SymbolInsertionRule',
    'CharacterInsertionRule',
    'IdentifierInsertionRule'
]

letters = base.characters.UPPERCASE.copy()
letters.update(base.characters.LOWERCASE.copy())

digits = base.characters.DIGITS.copy()
digits = {'digit %s' % k: v for k, v in digits.items()}

alpha_num = {}
alpha_num.update(letters)
alpha_num.update(digits)

symbol_chars = {}
symbol_chars.update(base.characters.SYMBOLS_TEXT)

all_chars = alpha_num.copy()
all_chars.update(base.characters.SYMBOLS_TEXT)


class AlphaInsertionRule(MappingRule):
    mapping = {k: Text(v) for k, v in letters.items()}


class DigitInsertionRule(MappingRule):
    mapping = {k: Text(v) for k, v in digits.items()}


class AlphaNumInsertionRule(MappingRule):
    mapping = {k: Text(v) for k, v in alpha_num.items()}


class SymbolInsertionRule(MappingRule):
    mapping = {k: Text(v) for k, v in symbol_chars.items()}


class CharacterInsertionRule(MappingRule):
    mapping = {k: Text(v) for k, v in all_chars.items()}


class IdentifierInsertionRule(CompoundRule):
    """
    Rule which formats a dictation using various formatting functions from
    base.format.FORMAT and base.format.CASE.  Rule expects a dictation in the
    following format

    [ caseFunction ] ( formatFunction ) <dictation>

    Where:
        caseFunction is a key name from base.format.CASE
        formatFunction is a key name from base.format.FORMAT
        <dictation> is the dictation to apply the case and format functions to.

    If no case function is given then assume base.format.lower()
    """
    spec = ('[%s] (%s) [<dictation>]' % (
        ' | '.join(base.format.CASE.keys()),
        ' | '.join(base.format.FORMAT.keys())
    ))
    extras = [Dictation(name='dictation')]

    def value(self, node):
        words = node.words()

        if words[0] in base.format.CASE:
            case = words.pop(0)
            format_key = words.pop(0)
            words = base.format.CASE[case](words)
        else:
            format_key = words.pop(0)
            words = base.format.lower(words)

        # clean up dragon nastyness
        words = [word.split('\\', 1)[0].replace('-', '') for word in words]

        # handle words or phrases from dragon that contain spaces.  this makes
        # them place nice with formatting functions.
        split_words = []
        for word in words:
            split_words += word.split(' ')

        formatted = FORMAT[format_key](split_words)

        return Text(formatted)
