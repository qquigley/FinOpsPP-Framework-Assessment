import click

@click.group()
def cli():
    pass

@click.group()
def assessment():
    pass

@assessment.group()
def generate():
    pass

if __name__ == "__main__":
    cli()
