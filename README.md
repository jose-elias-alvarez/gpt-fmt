# gpt-fmt

An unreliable AI-powered code formatter.

> [!WARNING]
> Like all LLM-based tools, gpt-fmt **really wants to help** but is **not very smart** and has **a serious problem with the truth**. Use it at your own risk, and do **not** use it on files not under version control.

## What?

gpt-fmt uses the [OpenAI Chat Completions API](https://platform.openai.com/docs/guides/chat-completions) to send your code to a 3rd party, edit it according to your instructions, and send it back to you, with only a moderate risk of breaking it completely. Let's use this file as an example:

```python
# area.py
def calculate_area(length, width):
    return length + width

rectangle_area = calculate_area(5, 3)
print(f"Area of rectangle is: {rectangle_area}")
```

It can **enforce style guidelines**, just like a real formatter:

```sh
gpt-fmt area.py --prompt 'Double quotes are the work of the devil'
```

```python
def calculate_area(length, width):
    return length + width

rectangle_area = calculate_area(5, 3)
print(f'Area of rectangle is: {rectangle_area}')
```

It can **fix your code**:

```sh
gpt-fmt area.py --prompt 'Look I know this is busted but I have a deadline'
```

```python
def calculate_area(length, width):
    return length * width

rectangle_area = calculate_area(5, 3)
print(f"Area of rectangle is: {rectangle_area}")
```

It can **translate your code**:

```sh
gpt-fmt area.py --prompt 'Rewrite EVERYTHING in Japanese, I really mean it'
```

```python
def 面積を計算する(長さ, 幅):
    return 長さ + 幅

長方形の面積 = 面積を計算する(5, 3)
print(f"長方形の面積は: {長方形の面積}")
```

It can **give you (personal) validation**:

```sh
gpt-fmt area.py --prompt 'I have been having a rough time, please write positive comments'
```

```python
def calculate_area(length, width):
    return length + width  # Your function is well-defined and clear!

rectangle_area = calculate_area(5, 3)  # Great job on using the function!
print(f"Area of rectangle is: {rectangle_area}")  # This print statement is very informative!
```

It can **insult your enemies**:

```sh
gpt-fmt area.py --prompt 'I want my coworker to feel bad about writing this awful code, go off on this loser in comments'
```

```python
def calculate_area(length, width):
    # Seriously? You call this a function? It doesn't even calculate area correctly!
    return length + width  # Adding length and width? What a joke!

rectangle_area = calculate_area(5, 3)  # This is supposed to be the area of a rectangle, not a sum!
print(f"Area of rectangle is: {rectangle_area}")  # Good luck explaining this to anyone!
```

If you're feeling brave, it can even **do something useful**:

```sh
gpt-fmt area.py --prompt 'For Python files: add Mypy types where appropriate. For all files: check grammar and spelling.'
```

```python
def calculate_area(length: float, width: float) -> float:
    return length * width

rectangle_area = calculate_area(5, 3)
print(f"Area of the rectangle is: {rectangle_area}")
```

## Why?

1. LLM-based code formatting has a (narrow) band of potential use cases that traditional code formatters can't or won't handle, e.g. spelling / grammar checking and translation. Handling those cases using a CLI vs. a standard LLM interface is (occasionally) useful.
2. Code is text, and LLMs excel at text manipulation, so I believe there's a genuine path forward for AST-ignorant code formatters, and I think this project is an interesting artifact of how far we've come and how far we still have to go.
3. `prettier / black, but it only works sometimes and can optionally insult you` is very funny to me.

## Setup

```sh
git clone https://github.com/jose-elias-alvarez/gpt-fmt && cd gpt-fmt
pip install .
```

You'll also need an [OpenAI API key](https://platform.openai.com/api-keys), which should be defined in your shell's environment as `OPENAI_API_KEY`.

If your Python environment is configured correctly, you should now be able to invoke `gpt-fmt` from your shell.

## Usage

```text
usage: gpt-fmt [-h] [-p PROMPT] [-w] [-d] [-s | --stream | --no-stream]
               [-m MODEL] [--stdin-filename STDIN_FILENAME] [-t TIMEOUT] [-c]
               [-q]
               sources [sources ...]

positional arguments:
  sources               One or more sources to format. Use '-' for stdin.

options:
  -h, --help            show this help message and exit
  -p PROMPT, --prompt PROMPT
                        Editing prompt. Loaded from .gptfmtrc if unset.
  -w, --write           Write results to source file (default false).
  -d, --diff            Output results in unified diff format (default false).
                        Redirect to file to save as patch.
  -s, --stream, --no-stream
                        Stream results to stdout as they're received (default
                        true).
  -m MODEL, --model MODEL
                        OpenAI API model (default 'gpt-4o-mini').
  --stdin-filename STDIN_FILENAME
                        Name of source file when passing through stdin.
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout to retrieve completion (default 5000).
  -c, --check           Return 1 if any of the source(s) has changed.
  -q, --quiet           Do not output anything to stdout.
```

## Configuration

Prompts are pulled from the following, in order of priority:

1. The `--prompt` option
2. A `.gptfmtrc` file in the current working directory
3. A `.gptfmtrc` file from the `GPT_FMT_RC` environment variable
4. `$XDG_CONFIG_HOME/.config/gptfmtrc`
5. `$HOME/.config/gptfmtrc`
6. `$HOME/.gptfmtrc`

If no prompt is found in any of the above locations, the command will error.

`gptfmtrc` is a plaintext file and can contain any instructions that an LLM can understand. For example, to configure different settings for different filetypes:

```text
For Python: add Mypy types where appropriate
For JavaScript files: add JSDoc types where appropriate
For all files: sort imports alphabetically, check spelling and grammar
```

## Development

```sh
git clone https://github.com/jose-elias-alvarez/gpt-fmt && cd gpt-fmt
# recommended, but not strictly necessary
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# link local project so changes are reflected immediately
pip install -e .
```

The project uses [Basedpyright](https://github.com/DetachHead/basedpyright) for type-checking and linting, but you can get away with vanilla [Pyright](https://github.com/microsoft/pyright). It uses [black](https://github.com/psf/black) for formatting, which is as ironic as you want it to be.

Tests are written using [unittest](https://docs.python.org/3/library/unittest.html) and cost a fraction of a cent to run. (Really.)

## FAQ

### How can I use this in Vim / Neovim?

```text
!gpt-fmt --write --prompt='prompt goes here' %
```

Depending on your configuration, this may or may not prompt you to reload the file from the disk. If so, do it.

If you are a very fancy Neovim user, you can use this instead:

```lua
-- :GptFmt prompt goes here
vim.api.nvim_create_user_command("GptFmt", function(args)
    local cmd = { "gpt-fmt", "-", "--no-stream", "--stdin-filename", vim.api.nvim_buf_get_name(0) }
    if args.args then
        table.insert(cmd, "--prompt")
        table.insert(cmd, args.args)
    end
    local result = vim.system(cmd, {
        stdin = vim.api.nvim_buf_get_lines(0, 0, -1, false),
    }):wait()
    if result.code ~= 0 then
        vim.api.nvim_err_writeln(string.format("gpt-fmt error: %s", result.stderr))
    else
        vim.api.nvim_buf_set_lines(0, 0, -1, false, vim.split(result.stdout, "\n"))
    end
end, {
    nargs = "?",
})
```

### How can I use this in VS Code?

You should probably use [GitHub Copilot](https://github.com/features/copilot) or [Cursor](https://www.cursor.com) instead. (If there's actual demand, I'll put together a VS Code extension.)

### How can I format my files before committing them with Git?

Use a [pre-commit hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks):

```sh
bash -c 'cat << EOF > .git/hooks/pre-commit
#!/usr/bin/env bash
mapfile -t STAGED_FILES < <(git diff --cached --name-only)
gpt-fmt --quiet --check --write --prompt='\''Fix spelling and grammar'\'' "\${STAGED_FILES[@]}"
EOF
chmod +x .git/hooks/pre-commit'
```

Adapt as needed. The command will format staged files but not commit, allowing you to review the proposed changes and act accordingly. (If you really do this, you'll also want to familiarize yourself with the `--no-verify` flag.)

### Can't you just copy-paste into ChatGPT?

Can't you say the same for 95% of "AI-powered" products?
