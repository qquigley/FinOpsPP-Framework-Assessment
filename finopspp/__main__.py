import os
from importlib.resources import files

import click
import yaml

@click.group()
def cli():
    """FinOps++ administration tool"""
    pass

@cli.group()
def generate():
    """Generate files from YAML specifications"""
    pass

@generate.command()
@click.option(
    '--profile',
    default='standard',
    type=click.Choice(['standard']), # TODO: probably want to pull the choice from some approved list
    help='Which assessment profile to generate. Defaults to standard profile',
)
@click.option(
    '--name',
    default='FinOps++ Framework (test)',
    help='Name (without extension) of file to generate',
)
def assessment(profile, name):
    """Generate a FinOps++ Assessment from the specifications for a given profile"""
    click.echo(f'Creating "{name}.xlsx" assessment for {profile} profile')

@generate.command()
def markdown():
    """Generate Markdown files from the specifications"""
    pass

@cli.group()
def specifications():
    """Informational command on Specifications"""
    pass

@specifications.command()
def list():
    """List all Specifications by ID"""
    for file in files('finopspp.specifications').iterdir():
        root, _ = os.path.splitext(file.name)
        click.echo(root)

@specifications.command()
@click.option(
    '--metadata',
    is_flag=True,
    help='Show the Metadata for a Specifications',
)
@click.argument('id')
def show(id, metadata):
    """Show information on a given specification by ID"""
    data_type = 'Specification'
    if metadata:
        data_type = 'Metadata'

    specification_file = files('finopspp.specifications').joinpath(f'{id}.yaml')
    click.echo(specification_file)
    with open(specification_file, 'r') as file:
        specification_data = yaml.safe_load(file)
        click.echo(
            yaml.dump(
                specification_data[data_type],
                default_flow_style=False,
                sort_keys=False,
                indent=2
            )
        )

if __name__ == "__main__":
    cli()
