import importlib

import sublime
from unittesting import DeferrableTestCase

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

        view.run_command('append', {'characters': view_content})
        result = yield from self.await_lint_result("annotations", fname)
        actual = result[0]
        self.assertEqual({k: actual[k] for k in expected.keys()}, expected)

    def await_lint_result(self, linter_name_, filename_):
        actual = None

        @events.on("LINT_RESULT")
        def on_result(filename, linter_name, errors, **kwargs):
            nonlocal actual
            if linter_name == linter_name_ and filename == filename_:
                actual = errors

        self.addCleanup(events.off, on_result)

        yield lambda: actual is not None
        return actual

    @p.expand(
        [
            (
                "# NOTE The note message\n" "# ERROR The error message\n",
                "scope:source.python",
                [
                    {
                        "line": 1,
                        "start": 2,
                        "msg": "The error message",
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
        fname = util.get_filename(view)
        view.settings().set("SublimeLinter.linters.annotations.infos", None)
        view.run_command('append', {'characters': view_content})

        result = yield from self.await_lint_result("annotations", fname)

        for i, error in enumerate(expected):
            self.assertEqual({k: result[i][k] for k in error.keys()}, error)
