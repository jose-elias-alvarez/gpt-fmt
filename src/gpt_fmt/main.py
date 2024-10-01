import sys

from gpt_fmt.args import GptFmtArgs, parse_args
from gpt_fmt.config import GptFmtConfig
from gpt_fmt.formatter import GptFormatter


def main(args: GptFmtArgs | None = None):
    args = args or parse_args()
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
