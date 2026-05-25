"""CLI entrypoint for intel-pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import typer

from pipeline.config.settings import get_settings
from pipeline.ingest.runner import IngestRunner
from pipeline.logging.setup import bind_run_context, clear_run_context, configure_logging
from pipeline.models import RawDocument, RunStatus

app = typer.Typer(
    name="pipeline",
    help="AI Knowledge Pipeline — ingest, evaluate, and deliver intelligence briefings.",
    no_args_is_help=True,
)


@app.callback()
def _root() -> None:
    """Root command group (required so subcommands like `ingest` are registered)."""


@app.command("ingest")
def ingest(
    sources: Path = typer.Option(
        None,
        "--sources",
        "-s",
        help="Path to sources.yaml (default: configs/sources.yaml).",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    run_id: str = typer.Option(
        None,
        "--run-id",
        help="UUID for this ingest run (default: random UUID4).",
    ),
    fixtures: bool = typer.Option(
        False,
        "--fixtures",
        help="Use tests/fixtures/feeds instead of live HTTP (CI/local dev).",
    ),
    limit: int | None = typer.Option(
        None,
        "--limit",
        help="Max RSS items per source.",
        min=1,
    ),
) -> None:
    """Ingest configured RSS sources into local storage and SQLite."""
    settings = get_settings()
    configure_logging(settings.log_level)

    resolved_run_id = run_id or str(uuid4())
    bind_run_context(run_id=resolved_run_id, stage="ingest")

    try:
        summary = IngestRunner(settings).run(
            resolved_run_id,
            sources_path=sources,
            use_fixtures=fixtures,
            max_items_per_source=limit,
        )
    finally:
        clear_run_context()

    typer.echo(
        f"run_id={summary.run_id} status={summary.status.value} "
        f"accepted={summary.documents_accepted} skipped={summary.documents_skipped} "
        f"sources_failed={summary.sources_failed}",
    )

    if summary.status == RunStatus.FAILED:
        raise typer.Exit(code=2)
    if summary.status == RunStatus.COMPLETED_WITH_ERRORS:
        raise typer.Exit(code=1)
    raise typer.Exit(code=0)


@app.command("validate-raw")
def validate_raw(
    path: Path = typer.Argument(
        ...,
        help="Directory to scan (e.g. data/raw).",
        exists=True,
        file_okay=False,
    ),
) -> None:
    """Validate on-disk raw JSON files against the RawDocument schema."""
    files = sorted(path.rglob("*.json"))
    if not files:
        typer.echo(f"No JSON files under {path}")
        raise typer.Exit(code=1)

    failed = 0
    for file_path in files:
        try:
            RawDocument.model_validate(json.loads(file_path.read_text(encoding="utf-8")))
        except Exception as exc:
            failed += 1
            typer.echo(f"FAIL {file_path}: {exc}")

    ok = len(files) - failed
    typer.echo(f"Validated {len(files)} files: {ok} ok, {failed} failed")
    if failed:
        raise typer.Exit(code=1)


def main() -> None:
    app(prog_name="pipeline")


if __name__ == "__main__":
    main()
