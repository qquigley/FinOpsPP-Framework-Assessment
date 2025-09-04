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
def controls():
    """Informational command on Controls"""
    pass

@controls.command()
def list():
    """List all Controls by ID"""
    for file in files('finopspp.controls').iterdir():
        root, _ = os.path.splitext(file.name)
        click.echo(root)

@controls.command()
@click.option(
    "--metadata",
    is_flag=True,
    help='Show the Metadata for a Control.',
)
@click.argument('name')
def show(name, metadata):
    """Show information on a given Control"""
    data_type = 'Control'
    if metadata:
        data_type = 'Metadata'

    control_file = files('finopspp.controls').joinpath(f'{name}.yaml')
    click.echo(control_file)
    with open(control_file, 'r') as file:
        control_data = yaml.safe_load(file)
        click.echo(
            yaml.dump(
                control_data[data_type],
                default_flow_style=False,
                indent=4
            )
        )

if __name__ == "__main__":
    cli()
