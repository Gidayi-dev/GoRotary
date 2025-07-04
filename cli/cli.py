import click
from db.connection import get_connection

def execute_sql_file(filename):
    with open(filename, "r") as f:
        sql = f.read()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()

@click.group()
def cli():
    pass

@cli.command()
def init():
    """Initialize the GoRotary database schema"""
    click.echo("Initializing GoRotary DB...")
    execute_sql_file("db/schema.sql")
    click.echo("Done. Database initialized.")

@cli.command()
@click.option('--text', prompt='What is your thought?', help='The main thought content.')
@click.option('--source', prompt='Source (optional)', default='', help='Optional source of the thought.')
@click.option('--mood', prompt='Mood (optional)', default='', help='Optional mood when the thought occurred.')
def add_thought(text, source, mood):
    """Add a new thought to the database"""
    conn = get_connection()
    cur = conn.cursor()

    source_id = None
    if source:
        cur.execute("SELECT id FROM sources WHERE label = %s", (source,))
        existing = cur.fetchone()
        if existing:
            source_id = existing[0]
        else:
            cur.execute("INSERT INTO sources (label) VALUES (%s) RETURNING id", (source,))
            source_id = cur.fetchone()[0]

    cur.execute(
        "INSERT INTO thoughts (text, source_id, mood) VALUES (%s, %s, %s)",
        (text, source_id, mood if mood else None)
    )

    conn.commit()
    conn.close()
    click.echo("Thought added successfully.")