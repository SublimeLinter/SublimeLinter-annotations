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
from SublimeLinter.lint import Linter, ERROR, WARNING


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
    regex = re.compile(r'^(?P<line>\d+):(?P<col>\d+):'
                       r' (warning \((?P<warning>.+?)\)|error \((?P<error>.+?)\)):'
                       r' (?P<message>.*)')

    # We use this to do the matching
    mark_regex_template = r'(?:(?P<warning>{warnings})|(?P<error>{errors})):?\s*(?P<message>.*)'

    # Words to look for
    defaults = {
        'selector': '',  # select all views
        'errors': ['FIXME'],
        'warnings': ['NOTE', 'README', 'TODO', '@todo', 'XXX', 'WIP'],
    }

    def run(self, cmd, code):
        settings = self.get_view_settings()
        options = {}
        for option in ('errors', 'warnings'):
            words = settings.get(option)
            options[option] = '|'.join(_escape_words(words))

        template_prefix = r'^' if settings.get('onlyStartsWith', False) else r''
        mark_regex = re.compile(template_prefix + self.mark_regex_template.format_map(options))

        output = []
        regions = self.view.find_by_selector('comment - punctuation.definition.comment')

        for region in regions:
            region_offset = self.view.rowcol(region.a)
            region_text = self.view.substr(region)
            for i, line in enumerate(region_text.splitlines()):
                match = mark_regex.search(line)
                if not match:
                    continue

                row = region_offset[0] + i
                # Need to account for region column offset only in first row
                col = match.start() + (region_offset[1] if i == 0 else 0)
                message = match.group('message').strip() or '<no message>'
                word = match.group('error')
                if word:
                    error_type = ERROR
                else:
                    word = match.group('warning')
                    error_type = WARNING

                output.append('{row}:{col}: {error_type} ({word}): {message}'
                              .format(**locals()))

        return '\n'.join(output)
