#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Aparajita Fishman
# Copyright (c) 2015-2016 The SublimeLinter Community
# Copyright (c) 2013-2014 Aparajita Fishman
#
# License: MIT
#

"""This module exports the Annotations plugin class."""

from itertools import accumulate, chain
import re

from SublimeLinter.lint import Linter, LintMatch


MYPY = False
if MYPY:
    from typing import Iterator, List, Union
    from SublimeLinter.lint import util


def _escape_words(values):
    for value in values:
        # Add \b word separator fences around the value
        # if it begins or ends with a word character.
        value = re.escape(value)

        if value[0].isalnum() or value[0] == '_':
            value = r'\b' + value

        if value[-1].isalnum() or value[-1] == '_':
            value += r'\b'

        yield value


class Annotations(Linter):
    """Discovers and marks FIXME, NOTE, README, TODO, @todo, and XXX annotations."""

    cmd = None

    # We use this to do the matching
    mark_regex_template = (
        r'(?P<word>{}):?\s*'r'(?P<message>.*)'
    )

    # Words to look for
    defaults = {
        'selector': '',  # select all views
        'errors': ['FIXME', 'ERROR'],
        'warnings': [
            'TODO', '@todo', 'XXX', 'WIP', 'WARNING',
            'todo!',  # Rust macro
        ],
        'infos': ['NOTE', 'README', 'INFO'],
        'mark_message': False,
        'selector_': 'comment - punctuation.definition.comment, support.macro.rust',
    }

    def run(self, cmd, code):
        # type: (Union[List[str], None], str) -> Union[util.popen_output, str]
        return 'something so SublimeLinter will not assume this view to be `ok`'

    def find_errors(self, output):
        # type: (str) -> Iterator[LintMatch]
        options = {
            option: '|'.join(_escape_words(self.settings[option]))
            for option in ('errors', 'warnings', 'infos')
            if self.settings[option]
        }
        if not options:
            return

        mark_regex = re.compile(self.mark_regex_template.format(
            "|".join(
                "(?P<{}>{})".format(key, value)
                for key, value in options.items()
            )
        ))

        regions = self.view.find_by_selector(self.settings['selector_'])
        for region in regions:
            region_text = self.view.substr(region)
            lines = region_text.splitlines(keepends=True)
            offsets = accumulate(chain([region.a], map(len, lines)))
            for line, offset in zip(lines, offsets):
                match = mark_regex.search(line.rstrip())
                if not match:
                    continue

                message = match.group('message') or '<no message>'
                word = match.group('word')
                match_groups = match.groupdict()
                error_type = next(
                    error_type_
                    for error_type_ in ('errors', 'warnings', 'infos')
                    if error_type_ in match_groups
                )

                row, col = self.view.rowcol(offset + match.start())
                text_to_mark = match.group() if self.settings.get('mark_message') else word
                yield LintMatch(
                    line=row,
                    col=col,
                    near=text_to_mark,
                    error_type=error_type,
                    code=word,
                    message=message
                )
