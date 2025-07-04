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

@cli.command()
def list_thoughts():
    """List all recent thoughts"""
    from db.connection import get_connection
    conn = get_connection()
    cur = conn.cursor()

    # Join with sources to get the label
    cur.execute("""
        SELECT t.id, t.text, t.timestamp, t.mood, s.label
        FROM thoughts t
        LEFT JOIN sources s ON t.source_id = s.id
        ORDER BY t.timestamp DESC
    """)

    rows = cur.fetchall()

    if not rows:
        click.echo("No thoughts found.")
        return

    for row in rows:
        id, text, timestamp, mood, source = row
        click.echo(f"\n Thought #{id}")
        click.echo(f"Text     : {text}")
        if mood:
            click.echo(f"Mood     : {mood}")
        if source:
            click.echo(f"Source   : {source}")
        click.echo(f"Time     : {timestamp}")

    conn.close()

@cli.command
@click.option('--keyword', prompt='Search keyword', help='Keyword to search for in thoughts')
def search_thoughts(keyword):
    """Search for thoughtd containing a keyword."""
    from db.connection import get_connection
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT t.id, t.text, t.timestamp, t.mood, s.label
        FROM thoughts t
        LEFT JOIN sources s ON t.source_id = s.id
        WHERE LOWER(t.text) LIKE %S
        ORDER BY t.timestamp DESC
    """
    keyword_pattern = f"%{keyword.lower()}%"
    cur.execute(query, (keyword_pattern,))
    results = cur.fetchall()

    if not results:
        click.echo("No thoughts matched that keyword.")
        return
    
    for row in results:
        id, text, timestamp, mood, source = row
        click.echo(f"\n Thought #{id}")
        click.echo(f"Text    : {text}")
        if mood:
            click.echo(f"Mood    : {mood}")
        if source:
            click.echo(f"source   : {source}")
        click.echo(f"Time    : {timestamp}")

    conn.close()