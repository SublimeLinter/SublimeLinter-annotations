import unittest
import importlib

import sublime
from SublimeLinter.lint.linter import get_linter_settings

from SublimeLinter.tests.parameterized import parameterized as p


LinterModule = importlib.import_module('SublimeLinter-annotations.linter')
Linter = LinterModule.Annotations


class TestRegex(unittest.TestCase):
    def create_window(self):
        sublime.run_command("new_window")
        window = sublime.active_window()
        self.addCleanup(self.close_window, window)
        return window

    def close_window(self, window):
        window.run_command('close_window')

    def create_view(self, window):
        view = window.new_file()
        self.addCleanup(self.close_view, view)
        return view

    def close_view(self, view):
        view.set_scratch(True)
        view.close()

    def assertMatch(self, string, expected):
        linter = Linter(sublime.View(0), {})
        actual = list(linter.find_errors(string))[0]
        # `find_errors` fills out more information we don't want to write down
        # in the examples
        self.assertEqual({k: actual[k] for k in expected.keys()}, expected)

    def assertNoMatch(self, string):
        linter = Linter(sublime.View(0), {})
        actual = list(linter.find_errors(string))
        self.assertFalse(actual)

    @p.expand(
        [
            (
                "# {} The {} message".format(word, error_type),
                "scope:source.python",
                {
                    "line": 0,
                    "col": 2,
                    "message": "The {} message".format(error_type),
                    "error_type": error_type,
                },
            )
            for error_type, words in (
                ("error", ("FIXME", "ERROR")),
                ("warning", ("TODO", "@todo", "XXX", "WIP", "WARNING")),
                ("info", ("NOTE", "README", "INFO")),
            )
            for word in words
        ]
    )
    def test_a(self, view_content, syntax, expected):
        window = self.create_window()
        view = self.create_view(window)
        view.assign_syntax(syntax)
        view.run_command('append', {'characters': view_content})

        settings = get_linter_settings(Linter, view, context=None)
        linter = Linter(view, settings)
        actual = list(linter.find_errors("_ignored by plugin"))[0]
        self.assertEqual({k: actual[k] for k in expected.keys()}, expected)
