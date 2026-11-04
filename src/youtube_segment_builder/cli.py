from __future__ import annotations

from pathlib import Path

import typer

app = typer.Typer(add_completion=False)


@app.callback()
def _root() -> None:
    """YouTube audio segment builder."""


@app.command("validate-input")
def validate_input(
    input: Path = typer.Option(
        Path("data/input/confirmed_segments.csv"),
        "--input",
        help="Path to confirmed_segments.csv",
        show_default=True,
    ),
) -> None:
    """Validate technical fields in confirmed_segments.csv."""
    from youtube_segment_builder.input_manifest import validate_csv

    typer.echo(f"Input : {input}")
    typer.echo("-" * 40)

    result = validate_csv(str(input))

    typer.echo(f"Total rows : {result.total_rows}")
    typer.echo(f"Valid rows : {result.valid_rows}")

    if result.warnings:
        typer.echo(f"\nWarnings ({len(result.warnings)}):")
        for w in result.warnings:
            typer.echo(f"  [WARN] {w}")

    if result.errors:
        typer.echo(f"\nErrors ({len(result.errors)}):")
        for e in result.errors:
            typer.echo(f"  [ERROR] {e}")
        typer.echo("\nValidation FAILED.")
        raise typer.Exit(code=1)

    typer.echo("\nValidation PASSED.")


@app.command("download-audio")
def download_audio(
    input: Path = typer.Option(
        Path("data/input/confirmed_segments.csv"),
        "--input",
        help="Path to confirmed_segments.csv",
        show_default=True,
    ),
    raw_dir: Path = typer.Option(
        Path("data/downloads/raw"),
        "--raw-dir",
        help="Directory for raw downloaded audio files",
        show_default=True,
    ),
    log: Path = typer.Option(
        Path("logs/download_log.csv"),
        "--log",
        help="Path to download log CSV",
        show_default=True,
    ),
) -> None:
    """Download audio for all valid rows using yt-dlp."""
    from youtube_segment_builder.downloader import download_audio as _download
    from youtube_segment_builder.input_manifest import validate_csv

    typer.echo(f"Input   : {input}")
    typer.echo(f"Raw dir : {raw_dir}")
    typer.echo(f"Log     : {log}")
    typer.echo("-" * 40)

    validation = validate_csv(str(input))
    typer.echo(f"Rows total / valid: {validation.total_rows} / {validation.valid_rows}")

    if validation.errors:
        typer.echo(f"Validation errors ({len(validation.errors)}) — skipping invalid rows:")
        for e in validation.errors:
            typer.echo(f"  [ERROR] {e}")

    if validation.valid_df.empty:
        typer.echo("\nNo valid rows to download.")
        raise typer.Exit(code=1)

    typer.echo(f"\nDownloading {validation.valid_rows} rows ...\n")
    result = _download(validation.valid_df, str(raw_dir), str(log))

    typer.echo(
        f"\nDone — downloaded: {result.downloaded}  "
        f"skipped: {result.skipped}  "
        f"failed: {result.failed}"
    )
    typer.echo(f"Log: {log}")

    if result.failed:
        raise typer.Exit(code=1)


@app.command("download-audioset-csv")
def download_audioset_csv(
    split: str = typer.Option(
        "default",
        "--split",
        help="default (balanced+eval) | balanced | eval | unbalanced | all",
        show_default=True,
    ),
    dest: Path = typer.Option(
        Path("data/audioset"),
        "--dest",
        help="Directory to save AudioSet CSVs",
        show_default=True,
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Re-download even if the file already exists",
    ),
) -> None:
    """Download official AudioSet metadata CSVs (class labels + segment splits)."""
    from youtube_segment_builder.audioset import (
        SPLIT_TO_SEGMENTS,
        download_audioset_csv as _download,
    )

    if split not in SPLIT_TO_SEGMENTS:
        typer.echo(
            f"Invalid --split {split!r}. Choose from {sorted(SPLIT_TO_SEGMENTS)}"
        )
        raise typer.Exit(code=1)

    typer.echo(f"Split : {split}")
    typer.echo(f"Dest  : {dest}")
    typer.echo("-" * 40)

    result = _download(split, str(dest), overwrite)

    typer.echo(
        f"\nDone — downloaded: {len(result.downloaded)}  "
        f"skipped: {len(result.skipped)}  "
        f"failed: {len(result.failed)}"
    )
    if result.failed:
        for name, msg in result.failed:
            typer.echo(f"  [ERROR] {name}: {msg}")
        raise typer.Exit(code=1)


@app.command("make-audioset-candidates")
def make_audioset_candidates(
    audioset_dir: Path = typer.Option(
        Path("data/audioset"),
        "--audioset-dir",
        help="Directory containing downloaded AudioSet CSVs",
        show_default=True,
    ),
    targets: Path = typer.Option(
        Path("data/config/audioset_targets.csv"),
        "--targets",
        help="Target label config CSV",
        show_default=True,
    ),
    output: Path = typer.Option(
        Path("data/candidates/audioset_candidates.csv"),
        "--output",
        help="Output candidates CSV",
        show_default=True,
    ),
) -> None:
    """Build audioset_candidates.csv from AudioSet CSVs and the target label config."""
    from youtube_segment_builder.audioset import (
        CLASS_LABELS_FILE,
        SEGMENT_FILES,
        make_candidates,
        write_example_targets,
    )

    typer.echo(f"AudioSet dir : {audioset_dir}")
    typer.echo(f"Targets      : {targets}")
    typer.echo(f"Output       : {output}")
    typer.echo("-" * 40)

    if not targets.exists():
        write_example_targets(targets)
        typer.echo(f"No targets config found — wrote an example to {targets}")
        typer.echo("Edit it (target_label / label_code / audioset_mids ...) and re-run.")
        raise typer.Exit(code=1)

    class_labels_path = audioset_dir / CLASS_LABELS_FILE
    if not class_labels_path.exists():
        typer.echo(f"Missing {class_labels_path}. Run download-audioset-csv first.")
        raise typer.Exit(code=1)

    present = [f for f in SEGMENT_FILES.values() if (audioset_dir / f).exists()]
    if not present:
        typer.echo(
            f"No segment CSVs found in {audioset_dir}. Run download-audioset-csv first."
        )
        raise typer.Exit(code=1)
    typer.echo(f"Segment files: {present}")

    result = make_candidates(str(audioset_dir), str(targets), str(output))

    typer.echo(f"\nSegments scanned : {result.total_segments}")
    typer.echo(f"Candidates       : {result.matched}")
    for label, count in result.per_target.items():
        typer.echo(f"  {label}: {count}")
    if result.preserved:
        typer.echo(f"Preserved edits  : {result.preserved} (matched by candidate_id)")
    if result.dropped:
        typer.echo(
            f"[WARN] {result.dropped} existing candidate(s) no longer match current "
            f"targets and were dropped (any selected=YES on them is lost)."
        )
    typer.echo(f"\nWrote {output}")


@app.command("build-confirmed-from-candidates")
def build_confirmed_from_candidates(
    candidates: Path = typer.Option(
        Path("data/candidates/audioset_candidates.csv"),
        "--candidates",
        help="Path to audioset_candidates.csv",
        show_default=True,
    ),
    output: Path = typer.Option(
        Path("data/input/confirmed_segments.csv"),
        "--output",
        help="Path to confirmed_segments.csv to write",
        show_default=True,
    ),
    backup: bool = typer.Option(
        True,
        "--backup/--no-backup",
        help="Back up an existing output to <output>.bak before overwriting",
        show_default=True,
    ),
    validate: bool = typer.Option(
        True,
        "--validate/--no-validate",
        help="Run validate-input on the output after building",
        show_default=True,
    ),
) -> None:
    """Build confirmed_segments.csv from selected=YES rows in the candidates CSV."""
    from youtube_segment_builder.build_confirmed import (
        build_confirmed_from_candidates as _build,
    )
    from youtube_segment_builder.input_manifest import validate_csv

    typer.echo(f"Candidates : {candidates}")
    typer.echo(f"Output     : {output}")
    typer.echo("-" * 40)

    if not candidates.exists():
        typer.echo(f"Candidates file not found: {candidates}")
        typer.echo("Run make-audioset-candidates first, then mark rows selected=YES.")
        raise typer.Exit(code=1)

    try:
        result = _build(str(candidates), str(output), backup=backup)
    except ValueError as exc:
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(code=1)

    typer.echo(f"Candidates scanned : {result.total_candidates}")
    typer.echo(f"Selected (=YES)    : {result.selected_rows}")
    if result.backup_path:
        typer.echo(f"Backed up existing : {result.backup_path}")
    typer.echo(f"\nWrote {output}")

    if result.selected_rows == 0:
        typer.echo(
            "\n[WARN] No rows had selected=YES "
            "(accepted: YES/yes/Y/y/true/TRUE). Nothing to confirm."
        )

    if not validate:
        typer.echo(
            "\nSkipped validation. Verify with:\n"
            f"  python -m youtube_segment_builder.cli validate-input "
            f"--input {output}"
        )
        return

    typer.echo("\nRunning validate-input ...")
    typer.echo("-" * 40)
    validation = validate_csv(str(output))
    typer.echo(f"Total rows : {validation.total_rows}")
    typer.echo(f"Valid rows : {validation.valid_rows}")

    if validation.warnings:
        typer.echo(f"\nWarnings ({len(validation.warnings)}):")
        for w in validation.warnings:
            typer.echo(f"  [WARN] {w}")

    if validation.errors:
        typer.echo(f"\nErrors ({len(validation.errors)}):")
        for e in validation.errors:
            typer.echo(f"  [ERROR] {e}")
        typer.echo("\nValidation FAILED.")
        raise typer.Exit(code=1)

    typer.echo("\nValidation PASSED.")


if __name__ == "__main__":
    app()
