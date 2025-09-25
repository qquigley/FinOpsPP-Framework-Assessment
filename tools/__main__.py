import os
import sys
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


def sub_specification_helper(doc, spec_file):
    """Helps find and pull Specification subsection from a specification"""
    id_ = doc.get('ID')
    # if no ID, assume the full sub-specification is given and return
    if not id_:
        return doc

    # else look up sub-specification file ID
    id_ = str(id_)
    file = '0'*(3-len(id_)) + id_
    with open(spec_file.joinpath(f'{file}.yaml'), 'r') as yaml_file:
        return yaml.safe_load(yaml_file).get('Specification')

def overrides_helper(doc, profile):
    """Helper for receiving the overrides for a profile if they exist
    
    Also ensure that if an override exists, it conforms to the specification of an
    override
    """
    overrides = doc.get('Overrides')
    if not overrides:
        overrides = []

    full_override = {'AddIDs': [], 'DropIDs': [], 'TitleUpdate': None}
    for override in overrides:
        if override.get('Profile') != profile:
            continue

        add_ids = override.get('AddIDs')
        if isinstance(add_ids, list):
            formatted_ids = []
            for add_id in add_ids:
                if not isinstance(add_id, int):
                    click.echo('IDs in AddIDs must be an integer. Exiting')
                    sys.exit(1)

            formatted_ids.append({'ID': add_id})
            full_override['AddIDs'] = formatted_ids
        elif add_ids is not None:
            click.echo('AddIDs, if set, must be null or a list. Exiting')
            sys.exit(1)

        drop_ids = override.get('DropIDs')
        if isinstance(drop_ids, list):
            formatted_ids = []
            for drop_id in drop_ids:
                if not isinstance(drop_id, int):
                    click.echo('IDs in DropIDs must be an integer. Exiting')
                    sys.exit(1)

            formatted_ids.append({'ID': drop_id})
            full_override['DropIDs'] = drop_ids
        elif drop_ids is not None:
            click.echo('DropIDs, if set, must be null or a list. Exiting')
            sys.exit(1)

        title_update = override.get('TitleUpdate')
        if isinstance(title_update, str):
            full_override['TitleUpdate'] = title_update
        elif title_update is not None:
            click.echo('TitleUpdate, if set, must be null or a str. Exiting')
            sys.exit(1)
    
    return full_override

@generate.command()
@click.option(
    '--profile',
    default='FinOps++',
    type=click.Choice(list(profiles().keys())),
    help='Which assessment profile to generate. Defaults to "FinOps++"',
)
def framework(profile):
    """Generate Framework markdown files from their specifications"""
    env = Environment(loader=PackageLoader('finopspp', 'templates'))
    template = env.get_template('framework.md.j2')

    domain_files = files('finopspp.specifications.domains')
    cap_files = files('finopspp.specifications.capabilities')
    action_files = files('finopspp.specifications.actions')
    with open(PROFILES_MAP[profile], 'r') as yaml_file:
        doc = yaml.safe_load(
            yaml_file
        ).get('Specification')

    domains = []
    if not doc.get('Domains'):
        click.echo('Profile includes no domains. Exiting')
        sys.exit(1)

    for domain in doc.get('Domains'):
        capabilities = []

        doc = sub_specification_helper(domain, domain_files)
        override = overrides_helper(doc, profile)

        title = doc.get('Title')
        if override.get('TitleUpdate'):
            title = override.get('TitleUpdate')
        if not doc.get('Capabilities'):
            continue
        if not isinstance(doc.get('Capabilities'), list):
            click.echo(
                'Capabilities for domain={title} must be null or a list. Exiting'
            )
            sys.exit(1)

        doc_id = doc.get('ID')
        if doc_id:
            doc_id = str(doc.get('ID'))
            file = '0'*(3-len(doc_id)) + doc_id
            title = f'<a href="/assessments/domains/{file}.md">{file}</a>: {title}'

        domains.append({
            'name': title,
            'capabilities': capabilities
        })
        doc.get('Capabilities').extend(override.get('AddIDs'))
        for capability in doc.get('Capabilities'):
            actions = []

            doc = sub_specification_helper(capability, cap_files)

            title = doc.get('Title')
            if override.get('TitleUpdate'):
                title = override.get('TitleUpdate')
            if not doc.get('Actions'):
                continue
            if not isinstance(doc.get('Actions'), list):
                click.echo(
                    'Actions for capability={title} must be null or a list. Exiting'
                )
                sys.exit(1)

            doc_id = doc.get('ID')
            if doc_id in override.get('DropIDs'):
                continue
            if doc_id:
                doc_id = str(doc.get('ID'))
                file = '0'*(3-len(doc_id)) + doc_id
                title = f'<a href="/assessments/capabilities/{file}.md">{file}</a>: {title}'

            capabilities.append({
                'name': title,
                'actions': actions
            })
            doc.get('Actions').extend(override.get('AddIDs'))
            for action in doc.get('Actions'):
                doc = sub_specification_helper(action, action_files)

                doc_id = str(doc.get('ID'))
                description = doc.get('Description')
                file = '0'*(3-len(doc_id)) + doc_id
                action = f'<a href="/assessments/actions/{file}.md">{file}</a>: {description}'

                actions.append(action)

    output = template.render(profile=profile, domains=domains)
    outpath = os.path.join(
        os.getcwd(),
        'assessments',
        'frameworks',
        f'{profile}.md'
    )
    with open(outpath, 'w') as outfile:
        outfile.write(output)

@generate.command()
@click.option(
    '--specification-type',
    type=click.Choice(['profiles', 'domains', 'capabilities', 'actions']),
    help='Which specification type to show. Defaults to "profiles"'
)
def specifications(specification_type):
    """Generate Framework markdown files from their specifications"""
    env = Environment(loader=PackageLoader('finopspp', 'templates'))
    template = env.get_template(f'{specification_type}.md.j2')
    spec_files = files(f'finopspp.specifications.{specification_type}')
    for spec in spec_files.iterdir():
        path = spec_files.joinpath(spec.name)
        with open(path, 'r') as yaml_file:
            doc = yaml.safe_load(yaml_file).get('Specification')

        doc_id = doc.get('ID')
        doc_id = str(doc_id)
        file_prefix = '0'*(3-len(doc_id)) + doc_id
        output = template.render(spec=doc)
        outpath = os.path.join(
            os.getcwd(),
            'assessments',
            specification_type,
            f'{file_prefix}.md'
        )
        with open(outpath, 'w') as outfile:
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
    specs_files = files(f'finopspp.specifications.{specification_type}')
    for spec in specs_files.iterdir():
        number, _ = os.path.splitext(spec.name)
        if int(number) < start:
            continue

        path = specs_files.joinpath(spec.name)
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
