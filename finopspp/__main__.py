import os
from importlib.resources import files

import click
import yaml

@click.group()
def cli():
    pass

@cli.group()
def assessments():
    pass

@assessments.command()
def generate():
    pass

@cli.group()
def guidelines():
    """Informational command on Guidelines"""
    pass

@guidelines.command()
def list():
    """List all Guidelines by ID"""
    for file in files('finopspp.guidelines').iterdir():
        root, _ = os.path.splitext(file.name)
        click.echo(root)

@guidelines.command()
@click.option(
    "--metadata",
    is_flag=True,
    help='Show the Metadata for a Guidelines.',
)
@click.argument('name')
def show(name, metadata):
    """Show information on a given Guidelines"""
    data_type = 'Guideline'
    if metadata:
        data_type = 'Metadata'

    guideline_file = files('finopspp.guidelines').joinpath(f'{name}.yaml')
    click.echo(guideline_file)
    with open(guideline_file, 'r') as file:
        guideline_data = yaml.safe_load(file)
        click.echo(
            yaml.dump(
                guideline_data[data_type],
                default_flow_style=False,
                indent=4
            )
        )

if __name__ == "__main__":
    cli()
