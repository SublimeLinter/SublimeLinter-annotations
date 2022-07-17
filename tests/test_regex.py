import sublime
from unittesting import DeferrableTestCase
from SublimeLinter.tests.parameterized import parameterized as p

from SublimeLinter.lint import events, util


MYPY = False
if MYPY:
    from typing import Generator


class LintResultTestCase(DeferrableTestCase):
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

    def prepare_view(self, view_content, syntax):
        window = self.create_window()
        view = self.create_view(window)
        view.assign_syntax(syntax)
        view.run_command('append', {'characters': view_content})
        return view

    def assertResult(self, result, expected):
        for actual, error in zip(result, expected):
            self.assertEqual({k: actual[k] for k in error.keys()}, error)

    def await_lint_result(self, view, linter_name_=None):
        # type: (sublime.View, str) -> Generator[object, object, list[dict]]
        if linter_name_ is None:
            linter_name_ = self.linter_name
        filename_ = util.get_filename(view)
        actual = None

        @events.on("LINT_RESULT")
        def on_result(filename, linter_name, errors, **kwargs):
            # type: (str, str, list[dict], object) -> None
            nonlocal actual
            if linter_name == linter_name_ and filename == filename_:
                actual = errors

        self.addCleanup(events.off, on_result)

        yield lambda: actual is not None
        assert actual
        return actual


class TestAnnotationsLinter(LintResultTestCase):
    linter_name = "annotations"

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
        + [
            (  # extract author of a note #33
                "// NOTE(kaste): a note",
                "scope:source.js",
                {
                    "line": 0,
                    "start": 3,
                    "msg": "(kaste): a note",
                    "error_type": "info",
                },
            )
        ]
    )
    def test_end_to_end(self, view_content, syntax, expected):
        view = self.prepare_view(view_content, syntax)
        result = yield from self.await_lint_result(view)
        self.assertResult(result, [expected])

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
        view = self.prepare_view(view_content, syntax)
        view.settings().set("SublimeLinter.linters.annotations.infos", None)

        result = yield from self.await_lint_result(view)

        self.assertResult(result, expected)
