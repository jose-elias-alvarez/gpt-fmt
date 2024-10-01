import os
import tempfile
import unittest
from contextlib import contextmanager
from dataclasses import dataclass
from io import StringIO
from unittest.mock import patch

from gpt_fmt import GptFormatter
from gpt_fmt.args import parse_args
from gpt_fmt.config import GptFmtConfig


@dataclass
class Fixtures:
    # exact content is irrelevant, since it's all mocked for this suite
    prompt = "use single quotes"
    original = 'print("test")'
    edited = "print('test')"


class TestMain(unittest.TestCase):
    fixtures = Fixtures()

    @contextmanager
    def patch_stdin(self, input: str):
        with patch("sys.stdin", new_callable=StringIO) as mock_stdin:
            mock_stdin.write(input)
            mock_stdin.seek(0)
            yield mock_stdin

    def get_config(self) -> GptFmtConfig:
        config = GptFmtConfig(parse_args(self.source))
        # need a prompt to avoid errors
        config.cli_prompt = self.fixtures.prompt
        return config

    def setUp(self):
        MockChat = patch("gpt_fmt.Chat").start()
        mock_chat = MockChat.return_value
        mock_chat.complete.return_value = self.fixtures.edited
        MockChat.return_value = mock_chat
        self.mock_chat = mock_chat

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

    def test_main(self):
        formatter = GptFormatter(self.get_config(), self.source)
        edited, did_change = formatter.format()

        self.mock_chat.complete.assert_called_once()
        self.assertTrue(did_change)
        self.assertEqual(edited, self.fixtures.edited)

    def test_stdin(self):
        os.unlink(self.source)

        with self.patch_stdin(self.fixtures.original):
            formatter = GptFormatter(self.get_config(), "-")
            edited, _ = formatter.format()

        self.assertEqual(edited, self.fixtures.edited)

    def test_eol(self):
        os.unlink(self.source)

        with self.patch_stdin(self.fixtures.original + os.linesep):
            formatter = GptFormatter(self.get_config(), "-")
            edited, _ = formatter.format()

        self.assertEqual(edited, self.fixtures.edited + os.linesep)

    def test_write(self):
        config = self.get_config()
        config.write = True
        formatter = GptFormatter(config, self.source)
        formatter.format()

        with open(self.source, "r") as file:
            self.assertEqual(file.read(), self.fixtures.edited)


if __name__ == "__main__":
    unittest.main()
