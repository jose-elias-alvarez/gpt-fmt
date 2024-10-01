import os
import tempfile
import textwrap
import unittest
from contextlib import contextmanager, redirect_stdout
from dataclasses import dataclass
from io import StringIO
from unittest.mock import Mock, patch

from gpt_fmt import main
from gpt_fmt.args import GptFmtArgs, parse_args


@dataclass
class Fixtures:
    # keep short to avoid time + costs
    prompt = "use single quotes, add semicolons"
    original = 'console.log("test")'
    edited = "console.log('test');"


# imagine paying each time you run a test
class TestE2E(unittest.TestCase):
    fixtures = Fixtures()

    @contextmanager
    def redirect_stdout(self):
        string_io = StringIO()
        with redirect_stdout(string_io):
            yield string_io

    def make_args(self, args: list[str] = []) -> GptFmtArgs:
        sources = [self.source]
        if not any(prompt_arg in args for prompt_arg in ("--prompt", "-p")):
            args.append("--prompt")
            args.append(self.fixtures.prompt)
        return parse_args(sources + args)

    def setUp(self):
        if not os.getenv("OPENAI_API_KEY"):
            raise unittest.SkipTest("Skipping E2E test (OPENAI_API_KEY not set)")

        temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
        temp_file.write(self.fixtures.original)
        temp_file.flush()
        temp_file.close()
        self.source = temp_file.name

    def tearDown(self):
        try:
            os.unlink(self.source)
        except FileNotFoundError:
            pass

    @patch("sys.exit")
    def test_e2e(self, mock_exit: Mock):
        with self.redirect_stdout() as output:
            main(self.make_args(["--no-stream"]))

        mock_exit.assert_called_once_with(0)
        self.assertEqual(output.getvalue(), self.fixtures.edited)

    @patch("sys.exit")
    def test_diff(self, mock_exit: Mock):
        with self.redirect_stdout() as output:
            main(self.make_args(["--diff"]))

        mock_exit.assert_called_once_with(0)
        self.assertEqual(
            output.getvalue(),
            textwrap.dedent(
                f"""\
--- {self.source}
+++ {self.source}
@@ -1 +1 @@
-{self.fixtures.original}
+{self.fixtures.edited}
"""
            ),
        )

    @patch("sys.exit")
    def test_check(self, mock_exit: Mock):
        main(self.make_args(["--check"]))

        mock_exit.assert_called_once_with(1)

    @patch("sys.exit")
    def test_check_no_change(self, mock_exit: Mock):
        main(self.make_args(["--check", "--prompt", "do nothing"]))

        mock_exit.assert_called_once_with(0)


if __name__ == "__main__":
    unittest.main()
