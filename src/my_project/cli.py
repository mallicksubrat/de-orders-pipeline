import click

from my_project.exceptions import ProjectError
from my_project.config import load_config
from my_project.orchestration.tasks import run_orders_pipeline


@click.group()
def cli():
    """Command line entrypoint for the orders pipeline."""


@cli.command()
@click.option("--env", default=None, help="Configuration environment to load.")
def run(env: str | None):
    """Run the batch pipeline once."""
    try:
        cfg = load_config(env=env)
        result = run_orders_pipeline(cfg)
    except ProjectError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(
        "Loaded "
        f"{result.loaded_rows} orders into {result.warehouse_table} "
        f"(artifact={result.artifact_path}, lineage={result.lineage_path})"
    )


@cli.command("show-config")
@click.option("--env", default=None, help="Configuration environment to load.")
def show_config(env: str | None):
    """Print the resolved application configuration."""
    cfg = load_config(env=env)
    click.echo(cfg.model_dump_json(indent=2))


if __name__ == "__main__":
    cli()
