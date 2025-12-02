from pathlib import Path

from typer import Typer

ROOT = Path(__file__).parents[1] / "sysexes"

app = Typer(
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)


def to_name(p: Path, root: Path | None = None) -> str:
    if p.is_absolute():
        if not root:
            return p.stem
        p = p.relative_to(root)
    return str(p.with_suffix(""))
