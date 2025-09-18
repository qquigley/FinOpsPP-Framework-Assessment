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
    '--specification-type',
    type=click.Choice(['profiles', 'domains', 'capabilities', 'actions']),
    help='Which specification type to show. Defaults to "profiles"'
)
@click.option(
    '--value',
    help='Optional value to use with key. Defaults to null'
)
@click.option(
    '--start',
    default=1,
    type=click.INT,
    help='Specification ID to start on. Default is 1'
)
@click.argument('after')
@click.argument('key')
def update(after, key, specification_type, value, start):
    """Mass update the Specification format per type
    
    The AFTER argument is to be given in dot-format for the accessor path from which
    to insert the new key-value pair. Ex "Specification.ID"
    """
    specs = files(f'finopspp.specifications.{specification_type}')
    for spec in specs.iterdir():
        number, _ = os.path.splitext(spec.name)
        if int(number) < start:
            continue

        path = specs.joinpath(spec.name)
        with open(path, 'r') as yaml_file:
            base_doc = yaml.safe_load(yaml_file)

        doc = base_doc
        accessors = after.split('.')
        target = accessors.pop()
        for accessor in accessors:
            doc = doc.get(accessor)

        position = list(doc.keys()).index(target)
        items = list(doc.items())
        items.insert(position + 1, (key, value))
        doc.clear()
        doc.update(dict(items))
        
        with open(path, 'w') as yaml_file:
            yaml.dump(
                base_doc,
                yaml_file,
                default_flow_style=False,
                sort_keys=False,
                indent=2
            )

@specifications.command(name='list')
@click.option(
    '--profile',
    default='FinOps++',
    type=click.Choice(list(profiles().keys())),
    help='Which assessment profile to use. Defaults to "FinOps++"'
)
def list_specs(profile):
    """List all Specifications by fully qualified ID per profile
    
    Fully qualified ID is of the format Domain.Capability-Action"""
    with open(PROFILES_MAP[profile], 'r') as yaml_file:
        spec = yaml.safe_load(
            yaml_file
        ).get('Specification')
        domains = spec.get('Domains')
        profile_id = spec.get('ID')

    domain_files = files('finopspp.specifications.domains')
    cap_files = files('finopspp.specifications.capabilities')
    click.echo(f'Fully qualified IDs for {profile}. Profile ID: {profile_id}')
    for domain in domains:
        domain_number = domain.get('Number')
        if not domain_number:
            continue

        domain_number = str(domain_number)
        file = '0'*(3-len(domain_number)) + domain_number
        with open(domain_files.joinpath(f'{file}.yaml'), 'r') as yaml_file:
            capabilities = yaml.safe_load(
                yaml_file
            ).get('Specification').get('Capabilities')

        for capability in capabilities:
            capability_number = capability.get('Number')
            if not capability_number:
                continue

            capability_number = str(capability_number)
            file = '0'*(3-len(capability_number)) + capability_number
            with open(cap_files.joinpath(f'{file}.yaml'), 'r') as yaml_file:
                actions = yaml.safe_load(
                    yaml_file
                ).get('Specification').get('Actions')

            for action in actions:
                action_number = action.get('Number')
                unique_id = f'{domain_number}.{capability_number}-{action_number}'
                click.echo(unique_id)

@specifications.command()
@click.option(
    '--metadata',
    is_flag=True,
    help='Show the Metadata for a Specifications'
)
@click.option(
    '--specification-type',
    type=click.Choice(['profiles', 'domains', 'capabilities', 'actions']),
    default='profiles',
    help='Which specification type to show. Defaults to "profiles"'
)
@click.argument('id')
def show(id, metadata, specification_type):
    """Show information on a given specification by ID by type"""
    data_type = 'Specification'
    if metadata:
        data_type = 'Metadata'

    file = '0'*(3-len(id)) + id
    specification_file = files(
        f'finopspp.specifications.{specification_type}'
    ).joinpath(f'{file}.yaml')

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
