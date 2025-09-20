import os
from importlib.resources import files

import click
import yaml
from jinja2 import Environment, PackageLoader

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
@click.option(
    '--profile',
    default='FinOps++',
    type=click.Choice(list(profiles().keys())),
    help='Which assessment profile to generate. Defaults to "FinOps++"',
)
@click.option(
    '--markdown-type',
    default='framework',
    help='Which markdown to generate',
)
def markdown(profile, markdown_type):
    """Generate Markdown files from the specifications"""
    env = Environment(loader=PackageLoader('finopspp', 'templates'))
    template = env.get_template(f'{markdown_type}.md.j2')

    domain_files = files('finopspp.specifications.domains')
    cap_files = files('finopspp.specifications.capabilities')
    action_files = files('finopspp.specifications.actions')
    domains = []
    for spec in domain_files.iterdir():
        with open(domain_files.joinpath(spec.name), 'r') as yaml_file:
            doc = yaml.safe_load(yaml_file).get('Specification')

        capabilities = []
        domains.append({
            'name': doc.get('Title'),
            'capabilities': capabilities
        })
        for capability in doc.get('Capabilities'):
            cap_id = capability.get('ID')
            if not cap_id:
                continue

            cap_id = str(cap_id)
            file = '0'*(3-len(cap_id)) + cap_id
            with open(cap_files.joinpath(f'{file}.yaml'), 'r') as yaml_file:
                doc = yaml.safe_load(yaml_file).get('Specification')

            actions = []
            capabilities.append({
                'name': doc.get('Title'),
                'actions': actions
            })
            for action in doc.get('Actions'):
                action_id = action.get('ID')
                if not action_id:
                    continue

                action_id = str(action_id)
                file = '0'*(3-len(action_id)) + action_id
                with open(action_files.joinpath(f'{file}.yaml'), 'r') as yaml_file:
                    description = yaml.safe_load(
                        yaml_file
                    ).get('Specification').get('Description')

                actions.append(description)

    output = template.render(profile=profile, domains=domains)
    with open(f'{profile} (test).md', 'w') as outfile:
        outfile.write(output)

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
        domain_id = domain.get('ID')
        if not domain_id:
            continue

        domain_id = str(domain_id)
        file = '0'*(3-len(domain_id)) + domain_id
        with open(domain_files.joinpath(f'{file}.yaml'), 'r') as yaml_file:
            capabilities = yaml.safe_load(
                yaml_file
            ).get('Specification').get('Capabilities')

        for capability in capabilities:
            capability_id = capability.get('ID')
            if not capability_id:
                continue

            capability_id = str(capability_id)
            file = '0'*(3-len(capability_id)) + capability_id
            with open(cap_files.joinpath(f'{file}.yaml'), 'r') as yaml_file:
                actions = yaml.safe_load(
                    yaml_file
                ).get('Specification').get('Actions')

            for action in actions:
                action_id = action.get('ID')
                unique_id = f'{domain_id}.{capability_id}-{action_id}'
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
