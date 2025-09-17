import os
from importlib.resources import files

import click
import yaml

PROFILES_MAP = {}
def profiles():
    """Return all profiles. Including proposed one"""
    global PROFILES_MAP
    if PROFILES_MAP:
        return PROFILES_MAP

    profiles = files('finopspp.specifications.profiles')
    for file in profiles.iterdir():
        path = profiles.joinpath(file.name)
        with open(path, 'r') as yaml_file:
            title = yaml.safe_load(yaml_file).get('Specification').get('Title')
            PROFILES_MAP[title] = path
    
    return PROFILES_MAP

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
    default='FinOps++',
    type=click.Choice(list(profiles().keys())),
    help='Which assessment profile to generate. Defaults to "FinOps++',
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
@click.option(
    '--profile',
    default='FinOps++',
    type=click.Choice(list(profiles().keys())),
    help='Which assessment profile to use. Defaults to "FinOps++"',
)
def list(profile):
    """List all Specifications by fully qualified ID per profile"""
    with open(PROFILES_MAP[profile], 'r') as yaml_file:
        domains = yaml.load(
            yaml_file, Loader=yaml.BaseLoader
        ).get('Specification').get('Domains')

    domain_files = files('finopspp.specifications.domains')
    for domain in domains:
        number = domain.get('Number')
        click.echo(domain_files.joinpath(f'{number}.yaml'))

@specifications.command()
@click.option(
    '--metadata',
    is_flag=True,
    help='Show the Metadata for a Specifications',
)
@click.option(
    '--specification-type',
    type=click.Choice(['profiles', 'domains', 'capabilities', 'actions']),
    help='Which specification type to show. Defaults to "profiles"',
)
@click.argument('id')
def show(id, metadata, specification_type):
    """Show information on a given specification by ID by type"""
    data_type = 'Specification'
    if metadata:
        data_type = 'Metadata'

    specification_file = files(
        f'finopspp.specifications.{specification_type}'
    ).joinpath(f'{id}.yaml')

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
