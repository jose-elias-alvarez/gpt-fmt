import difflib
import os
import sys
import tempfile
import time

from gpt_fmt.chat import GptFmtChat
from gpt_fmt.config import GptFmtConfig
from gpt_fmt.prompts import EXAMPLE_PROMPT, SYSTEM_PROMPT, USER_PROMPT


class GptFormatter:
    def __init__(self, config: GptFmtConfig, source: str):
        self.config = config
        self.source = source
        self.prompt = config.prompt
        self.chat = GptFmtChat(
            # doesn't really make sense to allow configuring these,
            # since the formatter becomes even less reliable
            temperature=0,
            top_p=0.01,
            timeout=self.config.timeout,
            model=self.config.model,
        )
        self.start_time = time.perf_counter()
        self.debug_log(f"Initializing with config: {config}")

    def debug_log(self, msg: str):
        if not self.config.debug:
            return
        sys.stdout.write(msg + "\n")

    def get_diff(self, code: str, edited_code: str):
        diff = list(
            difflib.unified_diff(
                code.splitlines(),
                edited_code.splitlines(),
                lineterm="",
                fromfile=self.source,
                tofile=self.source,
            )
        )
        return diff, len(diff) > 0

    def stream(self, chunk: str):
        if (
            not self.config.stream
            or self.config.write
            or self.config.debug
            or self.config.diff
            or self.config.quiet
        ):
            return
        sys.stdout.write(chunk)

    def write(self, edited: str):
        if self.config.debug:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp:
                temp.write(edited)
                self.debug_log(f"Output at {temp.name}")
        elif self.config.write:
            with open(self.source, "w") as file:
                file.write(edited)
        elif not self.config.quiet and not self.config.stream:
            sys.stdout.write(edited)

    def read(self):
        if self.source == "-":
            self.debug_log("Reading code from stdin")
            return sys.stdin.read()
        self.debug_log(f"Reading code from {self.source}")
        with open(self.source, "r") as file:
            return file.read()

    @property
    def filename(self):
        if self.source == "-":
            return self.config.stdin_filename or "unknown (infer from code)"
        return self.source

    def get_edited(self, original: str):
        self.debug_log(f"Getting edited code for prompt: {self.prompt}")
        edited = self.chat.complete(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": EXAMPLE_PROMPT},
                {"role": "user", "content": f"Name: {self.filename}"},
                {"role": "user", "content": f"Code: {original}"},
                {"role": "user", "content": f"Prompt: {self.prompt}"},
                {"role": "user", "content": USER_PROMPT},
            ],
            on_chunk=self.stream,
            on_done=lambda _: self.stream("\n"),
        )
        if original.endswith(os.linesep) and not edited.endswith(os.linesep):
            edited += os.linesep
        self.debug_log(f"Received edited code: {edited}")
        return edited

    def format(self):
        original = self.read()
        edited = self.get_edited(original)
        diff, did_change = self.get_diff(original, edited)
        if self.config.diff and not self.config.quiet:
            for line in diff:
                sys.stdout.write(line + "\n")
        else:
            self.write(edited)
        self.debug_log(
            f"Formatting complete in {time.perf_counter() - self.start_time:0.4f} seconds"
        )

        return edited, did_change
