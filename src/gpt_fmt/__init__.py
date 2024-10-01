#!/usr/bin/env python3
import difflib
import os
import sys
import tempfile
import time

from gpt_fmt.args import GptFmtArgs, parse_args
from gpt_fmt.chat import Chat
from gpt_fmt.config import GptFmtConfig


class GptFormatter:
    def __init__(self, config: GptFmtConfig, source: str):
        self.config = config
        self.source = source
        self.prompt = config.prompt
        self.chat = Chat(
            temperature=0,
            top_p=0.01,
            timeout=self.config.timeout,
            model=self.config.model,
        )

        self.debug_log(f"Initalizing with config: {config}")

    def debug_log(self, msg: str):
        if self.config.debug is False:
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
        if self.config.write is True:
            with open(self.source, "w") as file:
                file.write(edited)
        elif self.config.debug is True:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp:
                temp.write(edited)
                self.debug_log(f"Output at {temp.name}")
        elif not self.config.quiet and not self.config.stream:
            sys.stdout.write(edited)

    def read(self):
        if self.source == "-":
            self.debug_log("Reading code from stdin")
            code = sys.stdin.read()
        else:
            self.debug_log(f"Reading code from {self.source}")
            with open(self.source, "r") as file:
                code = file.read()
        return code

    @property
    def filename(self):
        if self.source == "-":
            if self.config.stdin_filename is None:
                return "unknown (infer from code)"
            return self.config.stdin_filename
        return self.source

    def get_edited(self, original: str):
        self.debug_log(f"Getting edited code for prompt {self.prompt}")
        edited = self.chat.complete(
            [
                {
                    "role": "system",
                    "content": """
                                You are a formatting tool for programming languages.
                                You will receive the name of the file, the code to be formatted, and instructions from the user.
                                Return ONLY syntactically valid code, formatted according to the prompt.
                                Do not use wrap the returned code in a code block.
                                Do not make any edits other than those specified in the prompt.
                                Do not edit comments or other text unless the prompt specifies otherwise.
                                Use the original style from the code, including indentation and whitespace, unless otherwise specified.
                                """,
                },
                {
                    "role": "system",
                    "content": """
                                Example:
                                Name: log.js
                                Code: console.log('hello world')
                                Prompt: Use double quotes, capitalize words, and add semicolons
                                Result: console.log("HELLO WORLD");
                                """,
                },
                {"role": "user", "content": f"Name: {self.filename}"},
                {"role": "user", "content": f"Code: {original}"},
                {"role": "user", "content": f"Prompt: {self.prompt}"},
                {
                    "role": "user",
                    "content": "Double-check your code before returning it. It must follow my instructions precisely and contain no errors.",
                },
            ],
            on_chunk=self.stream,
            on_done=lambda _: self.stream("\n"),
        )
        if original.endswith(os.linesep) and not edited.endswith(os.linesep):
            edited += os.linesep
        self.debug_log(f"Received edited code {edited}")
        return edited

    def format(self):
        tic = time.perf_counter()

        original = self.read()
        edited = self.get_edited(original)

        diff, did_change = self.get_diff(original, edited)
        if self.config.diff and not self.config.quiet:
            for line in diff:
                sys.stdout.write(line + "\n")
        else:
            self.write(edited)

        toc = time.perf_counter()
        self.debug_log(f"Formatting complete in {toc - tic:0.4f} seconds")

        return edited, did_change


def main(args: GptFmtArgs | None = None):
    if args is None:
        args = parse_args()
    config = GptFmtConfig(args)

    exit_code = 0
    for source in args.sources:
        formatter = GptFormatter(config, source)
        _, did_change = formatter.format()
        if did_change and config.check:
            exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
