import os
from pathlib import Path

from gpt_fmt.args import GptFmtArgs


class GptFmtConfig:
    cli_prompt: str | None
    model: str
    timeout: int
    write: bool
    diff: bool
    stream: bool
    stdin_filename: str | None
    check: bool
    debug: bool
    quiet: bool

    rc_paths = [
        Path.cwd() / ".gptfmtrc",
        Path(os.environ.get("GPT_FMT_RC", "")),
        Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "gptfmtrc",
        Path.home() / ".gptfmtrc",
    ]

    def load_rc(self):
        for path in self.rc_paths:
            if path.is_file():
                try:
                    return path.read_text()
                except (FileNotFoundError, PermissionError):
                    continue
        return None

    @property
    def prompt(self):
        if self.cli_prompt:
            return self.cli_prompt
        rc = self.load_rc()
        if rc:
            return rc
        raise ValueError("Unable to get prompt from CLI arguments or .gptfmrc")

    def __init__(self, args: GptFmtArgs):
        self.model = args.model
        self.timeout = args.timeout
        self.write = args.write
        self.diff = args.diff
        self.stream = args.stream
        self.stdin_filename = args.stdin_filename
        self.check = args.check
        self.debug = args.debug
        self.quiet = args.quiet
        self.cli_prompt = args.prompt  # rename to avoid conflict w/ getter
