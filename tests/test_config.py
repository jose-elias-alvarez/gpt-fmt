import unittest
from pathlib import Path

from gpt_fmt.args import GptFmtArgs, parse_args
from gpt_fmt.config import GptFmtConfig


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config_file_path = Path(Path.cwd() / ".gptfmtrc")

    def tearDown(self):
        if self.config_file_path.exists():
            self.config_file_path.unlink()

    def write_rc(self, content: str):
        self.config_file_path.write_text(content)

    def get_args(self) -> GptFmtArgs:
        # required positional argument
        return parse_args("dummy-source")

    def test_init(self):
        args = self.get_args()
        args.model = "gpt-5o"
        args.timeout = 9999

        config = GptFmtConfig(args)

        self.assertEqual(config.model, args.model)
        self.assertEqual(config.timeout, args.timeout)

    def test_get_prompt_from_args(self):
        args = self.get_args()
        args.prompt = "I am a prompt from the CLI!"

        config = GptFmtConfig(args)

        self.assertEqual(config.prompt, args.prompt)

    def test_get_prompt_from_rc(self):
        prompt = "I am a prompt in a .gptfmtrc file!"
        self.write_rc(prompt)

        config = GptFmtConfig(self.get_args())

        self.assertEqual(config.prompt, prompt)


if __name__ == "__main__":
    unittest.main()
