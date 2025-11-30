from pathlib import Path

from typer import Typer

ROOT = Path(__file__).parents[1] / "sysexes"

app = Typer(
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)
