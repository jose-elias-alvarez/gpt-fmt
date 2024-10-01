import argparse
import sys
from typing import List, Optional, Sequence

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TIMEOUT = 5000


class GptFmtArgs(argparse.Namespace):
    sources: List[str]
    prompt: Optional[str]
    model: str
    timeout: int
    stdin_filename: Optional[str]
    write: bool
    diff: bool
    stream: bool
    check: bool
    debug: bool
    quiet: bool


def parse_args(args: Sequence[str] = sys.argv[1:]) -> GptFmtArgs:
    parser = argparse.ArgumentParser(prog="gpt-fmt")
    parser.add_argument(
        "sources",
        nargs="+",
        help="One or more sources to format. Use '-' for stdin.",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        required=False,
        help="Editing prompt. Loaded from gptfmtrc if unset.",
    )
    parser.add_argument(
        "-w",
        "--write",
        required=False,
        action="store_true",
        help="Write results to source file (default false).",
    )
    parser.add_argument(
        "-d",
        "--diff",
        required=False,
        action="store_true",
        help="Output results in unified diff format (default false). Redirect to file to save as patch.",
    )
    parser.add_argument(
        "-s",
        "--stream",
        required=False,
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Stream results to stdout as they're received (default true).",
    )
    parser.add_argument(
        "-m",
        "--model",
        default=DEFAULT_MODEL,
        help=f"OpenAI API model (default '{DEFAULT_MODEL}').",
    )
    parser.add_argument(
        "--stdin-filename",
        required=False,
        help="Name of source file when passing through stdin.",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        default=DEFAULT_TIMEOUT,
        help=f"Timeout to retrieve completion (default {DEFAULT_TIMEOUT}).",
    )
    parser.add_argument(
        "-c",
        "--check",
        required=False,
        action="store_true",
        help="Return 1 if any of the source(s) has changed.",
    )
    parser.add_argument(
        "--debug", required=False, action="store_true", help=argparse.SUPPRESS
    )
    parser.add_argument(
        "-q",
        "--quiet",
        required=False,
        action="store_true",
        help="Do not output anything to stdout.",
    )
    return parser.parse_args(args, GptFmtArgs())
