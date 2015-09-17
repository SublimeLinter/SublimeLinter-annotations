#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Aparajita Fishman
# Copyright (c) 2015 The SublimeLinter Community
#
# License: MIT
#

"""This module exports the Annotations plugin class."""

import os
import re
from SublimeLinter.lint import highlight, Linter, persist


class Annotations(Linter):

    """Discovers and marks FIXME, NOTE, README, TODO, @todo, and XXX annotations."""

    syntax = '*'
    cmd = None
    regex = '.*'  # Placeholder so that linter will activate

    # We use this to do the matching
    match_re = r'^.*?(?P<message>(?:(?P<warning>{warnings})|(?P<error>{errors})).*)'

    # We are only interested in comments
    selectors = {
        '*': 'comment'
    }

    defaults = {
        '-errors:,': ['FIXME'],
        '-warnings:,': ['NOTE', 'README', 'TODO', 'XXX', '@todo']
    }

    def run(self, cmd, code):
        """
        Search code for annotations, mark lines that contain them.

        We do the marking here since there is no point in searching
        the lines twice.

        We return nothing (None) to abort any further processing.

        """

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

        regex = re.compile(self.match_re.format_map(options))

        output = []

        for i, line in enumerate(code.splitlines()):
            match = regex.match(line)

            if match:
                col = match.start('message')
                word = match.group('error')
                message = match.group('message')

                if word:
                    error_type = highlight.ERROR
                else:
                    word = match.group('warning')
                    error_type = highlight.WARNING

                if persist.debug_mode():
                    output.append('line {}, col {}: {}'.format(i + 1, col + 1, message))

                self.highlight.range(i, col, length=len(word), error_type=error_type)
                self.error(i, col, message, error_type)

        if output and persist.debug_mode():
            persist.printf('{}: {} output:\n{}'.format(self.name, os.path.basename(self.filename), '\n'.join(output)))
