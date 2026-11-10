"""CLI entrypoint."""
from __future__ import annotations

import typer

app = typer.Typer(help="Upload Consciousness - UCC CLI")


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
    """Run the UCC API server."""
    import uvicorn

    uvicorn.run("interfaces.api.main:app", host=host, port=port, reload=reload)


@app.command()
def initdb() -> None:
    """Initialize the database schema."""
    import asyncio

    from storage.database import init_db

    asyncio.run(init_db())
    typer.echo("database initialized")


if __name__ == "__main__":
    app()
