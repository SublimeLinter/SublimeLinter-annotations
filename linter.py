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
import SublimeLinter.lint

if getattr(SublimeLinter.lint, 'VERSION', 3) > 3:
    from SublimeLinter.lint import const, Linter
    ERROR = const.ERROR
    WARNING = const.WARNING
else:
    from SublimeLinter.lint import highlight, Linter
    ERROR = highlight.ERROR
    WARNING = highlight.WARNING


class Annotations(Linter):
    """Discovers and marks FIXME, NOTE, README, TODO, @todo, and XXX annotations."""

    syntax = '*'
    cmd = None
    regex = re.compile(r'^(?P<line>\d+):(?P<col>\d+):'
                       r' (warning \((?P<warning>.+?)\)|error \((?P<error>.+?)\)):'
                       r' (?P<message>.*)')

    # We use this to do the matching
    match_re = r'^.*?(?:(?P<warning>{warnings})|(?P<error>{errors})):?\s*(?P<message>.*)'

    # We are only interested in comments
    selectors = {
        '*': 'comment'
    }

    defaults = {
        '-errors:,': ['FIXME'],
        '-warnings:,': ['NOTE', 'README', 'TODO', '@todo', 'XXX', 'WIP']
    }

    def run(self, cmd, code):

        options = {}
        type_map = {
            'errors': [],
            'warnings': []
        }

        self.build_options(options, type_map)

        for option in options:
            values = []

            for value in options[option]:
                if value:
                    # Add \b word separator fences around the value
                    # if it begins or ends with a word character.
                    value = re.escape(value)

                    if value[0].isalnum() or value[0] == '_':
                        value = r'\b' + value

                    if value[-1].isalnum() or value[-1] == '_':
                        value += r'\b'

                    values.append(value)

            options[option] = '|'.join(values)

        match_regex = re.compile(self.match_re.format_map(options))

        output = []

        for i, line in enumerate(code.splitlines()):
            match = match_regex.match(line)

            if match:
                col = match.start('error')
                word = match.group('error')
                message = match.group('message') or '<no message>'

                if word:
                    error_type = ERROR
                else:
                    col = match.start('warning')
                    word = match.group('warning')
                    error_type = WARNING

                output.append('{}:{}: {} ({}): {}'
                              .format(i + 1, col + 1, error_type, word, message))

        return ''.join(output)
