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

    def lint(self, _code, _view_has_changed):
        self.logger.info(
            "%s: linting '%s'",
            self.name,
            util.canonical_filename(self.view),
        )

        options = {}
        for option in ('errors', 'warnings', 'infos'):
            words = self.settings.get(option)
            options[option] = '|'.join(_escape_words(words))

        mark_regex = re.compile(self.mark_regex_template.format_map(options))

        output = []
        regions = self.view.find_by_selector(self.settings['selector_'])

        for region in regions:
            region_offset = self.view.rowcol(region.a)
            region_text = self.view.substr(region)
            offset_until_line = region.a
            for i, line in enumerate(region_text.splitlines()):
                match = mark_regex.search(line)
                if not match:
                    offset_until_line += len(line) + 1  # for \n
                    continue

                row = region_offset[0] + i
                # Need to account for region column offset only in first row
                col = match.start() + (region_offset[1] if i == 0 else 0)
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

                output.append(dict(
                    line=row,
                    start=col,
                    region=match_region,
                    # linter=,
                    error_type=error_type,
                    code=word,
                    msg=message,
                    filename=util.get_filename(self.view),
                    # uid=,
                    # priority=,
                    # panel_line=,
                    offending_text=word,
                ))
                offset_until_line += len(line) + 1  # for \n

        return output
