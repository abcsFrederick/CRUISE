"""
Entrypoint for CRISPIN CLI

Check out the wiki for a detailed look at customizing this file:
https://github.com/beardymcjohnface/Snaketool/wiki/Customising-your-Snaketool
"""

import os
import click
from .util import (
    nek_base,
    get_version,
    copy_config,
    OrderedCommands,
    run_nextflow,
    print_citation,
)


def common_options(func):
    """Common options decorator for use with click commands."""
    options = [
        click.argument("nextflow_args", nargs=-1),
    ]
    for option in reversed(options):
        func = option(func)
    return func


@click.group(
    cls=OrderedCommands, context_settings=dict(help_option_names=["-h", "--help"])
)
@click.version_option(get_version(), "-v", "--version", is_flag=True)
@click.option(
    "--citation",
    is_flag=True,
    callback=print_citation,
    expose_value=False,
    is_eager=True,
    help="Print the citation in bibtex format and exit.",
)
def cli():
    """CRISPR screen pipeline

    For more options, run:
    crispin [command] --help

    See the docs website for more details:
    https://ccbr.github.io/CRISPIN/
    """
    pass


help_msg_extra = """
\b
EXAMPLES:
Execute with slurm:
    crispin run ... --mode slurm
Preview the processes that will run:
    crispin run ... --mode local -preview
Add nextflow args (anything supported by `nextflow run`):
    crispin run ... -work-dir path/to/workDir
Run with a specific installation of crispin:
    crispin run --main path/to/crispin/main.nf ...
Run with a specific tag, branch, or commit from GitHub:
    crispin run --main CCBR/CRISPIN -r v0.1.0 ...

See the docs website for more details:
https://ccbr.github.io/CRISPIN/
"""


@click.command(
    epilog=help_msg_extra,
    context_settings=dict(
        help_option_names=["-h", "--help"], ignore_unknown_options=True
    ),
)
@click.option(
    "--main",
    "main_path",
    help="Path to the crispin main.nf file or the GitHub repo (CCBR/CRISPIN). Defaults to the version installed in the $PATH.",
    type=str,
    default=nek_base(os.path.join("main.nf")),
    show_default=True,
)
@click.option(
    "--mode",
    "_mode",
    help="Run mode (slurm, local)",
    type=str,
    default="local",
    show_default=True,
)
@common_options
def run(main_path, _mode, **kwargs):
    """Run the workflow"""
    if (  # this is the only acceptable github repo option for crispin
        main_path != "CCBR/CRISPIN"
    ):
        # make sure the path exists
        if not os.path.exists(main_path):
            raise FileNotFoundError(
                f"Path to the crispin main.nf file not found: {main_path}"
            )

    run_nextflow(
        nextfile_path=main_path,
        mode=_mode,
        **kwargs,
    )


@click.command()
def init(**kwargs):
    """Initialize the working directory by copying the system default config files"""
    paths = ("nextflow.config", "conf/", "assets/")
    copy_config(paths)
    if not os.path.exists("log/"):
        os.mkdir("log/")


cli.add_command(run)
cli.add_command(init)


def main():
    cli()


if __name__ == "__main__":
    main()
