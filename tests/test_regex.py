import importlib

import sublime
from unittesting import DeferrableTestCase

from SublimeLinter.lint.linter import get_linter_settings
from SublimeLinter.lint import events, util

from SublimeLinter.tests.parameterized import parameterized as p


LinterModule = importlib.import_module('SublimeLinter-annotations.linter')
Linter = LinterModule.Annotations


class TestRegex(DeferrableTestCase):
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

    @p.expand(
        [
            (
                "# {} The {} message".format(word, error_type),
                "scope:source.python",
                {
                    "line": 0,
                    "start": 2,
                    "msg": "The {} message".format(error_type),
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
    def test_end_to_end(self, view_content, syntax, expected):
        window = self.create_window()
        view = self.create_view(window)
        view.assign_syntax(syntax)
        fname = util.get_filename(view)
        actual = None

        @events.on("LINT_RESULT")
        def on_result(filename, linter_name, errors, **kwargs):
            nonlocal actual, fname
            if linter_name == "annotations" and filename == fname:
                actual = errors[0]

        self.addCleanup(events.off, on_result)
        view.run_command('append', {'characters': view_content})
        yield lambda: actual is not None
        assert actual
        self.assertEqual({k: actual[k] for k in expected.keys()}, expected)

    @p.expand(
        [
            (
                "# NOTE The note message\n" "# ERROR The error message\n",
                "scope:source.python",
                [
                    {
                        "line": 1,
                        "col": 2,
                        "message": "The error message",
                        "error_type": "error",
                    }
                ],
            )
        ]
    )
    def test_set_word_group_to_null_issue_39(
        self, view_content, syntax, expected
    ):
        window = self.create_window()
        view = self.create_view(window)
        view.assign_syntax(syntax)
        view.run_command('append', {'characters': view_content})

        settings = get_linter_settings(Linter, view, context=None)
        settings["infos"] = []
        linter = Linter(view, settings)
        actual = list(linter.find_errors("_ignored by plugin"))
        for i, error in enumerate(expected):
            self.assertEqual({k: actual[i][k] for k in error.keys()}, error)
