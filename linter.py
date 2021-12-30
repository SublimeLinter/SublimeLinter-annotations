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

import re

import sublime
from SublimeLinter.lint import Linter, ERROR, WARNING, util


MYPY = False
if MYPY:
    from typing import List, Iterator, Union
    from SublimeLinter.lint import VirtualView
    from SublimeLinter.persist import LintError


def _escape_words(values):
    if not values:
        return
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
    line_col_base = (0, 0)

    # We use this to do the matching
    mark_regex_template = r'(?:(?P<info>{infos})|(?P<warning>{warnings})|(?P<error>{errors})):?\s*(?P<message>.*)'

    # Words to look for
    defaults = {
        'selector': '',  # select all views
        'errors': ['FIXME', 'ERROR'],
        'warnings': [
            'TODO', '@todo', 'XXX', 'WIP', 'WARNING',
            'todo!',  # Rust macro
        ],
        'infos': ['NOTE', 'README', 'INFO'],
        'selector_': 'comment - punctuation.definition.comment, support.macro.rust',
    }

    def run(self, _cmd, _code):
        # type: (Union[List[str], None], str) -> Union[util.popen_output, str]
        # Override default and do nothing instead.
        return ''

    def parse_output(self, _proc, _virtual_view):
        # type: (Union[str, util.popen_output], VirtualView) -> Iterator[LintError]
        # Emulates parse_output, find_errors, split_match, process_match.
        # We don't care about the virtual view here
        # since we operate on the entire actual view,
        # which is much more efficient.
        options = {
            option: '|'.join(_escape_words(self.settings.get(option)))
            for option in ('errors', 'warnings', 'infos')
        }

        mark_regex = re.compile(self.mark_regex_template.format_map(options))

        regions = self.view.find_by_selector(self.settings['selector_'])

        for region in regions:
            region_text = self.view.substr(region)
            offset_until_line = region.a
            for line in region_text.splitlines():
                match = mark_regex.search(line)
                if not match:
                    offset_until_line += len(line) + 1  # for \n
                    continue

                match_region = sublime.Region(offset_until_line + match.start(),
                                              offset_until_line + match.end())
                message = match.group('message').strip() or '<no message>'
                word = match.group('error')
                if word:
                    error_type = ERROR
                else:
                    word = match.group('warning')
                    if word:
                        error_type = WARNING
                    else:
                        word = match.group('info')
                        error_type = 'info'

                row, col = self.view.rowcol(match_region.a)
                # matches output of process_match
                yield dict(
                    filename=util.get_filename(self.view),
                    line=row,
                    start=col,
                    region=match_region,
                    error_type=error_type,
                    code=word,
                    msg=message,
                    offending_text=match.group(0),
                )
                offset_until_line += len(line) + 1  # for \n
