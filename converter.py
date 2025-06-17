#!/usr/bin/env python3
"""
converter.py
────────────
Convert any document (local file or URL) to Markdown with Docling and save
the result in a chosen folder.

• Run with no arguments to convert perf-report.html → ./converted/
• Override input or output folder on the command line.

Examples
--------
python3 converter.py
python3 converter.py other.pdf --out-dir ~/tmp
"""

# ── Docling / Pydantic compatibility shim ──────────────────────────────
# Docling-core expects StringConstraints(strict=True, pattern=…).
# Older Pydantic builds ship a stub that rejects those kwargs.
# We provide a minimal stand-in and register it in BOTH places *without*
# replacing the original pydantic.types module.
import pydantic, pydantic.types as _pt  # _pt is the existing submodule

class _StringConstraints:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)  # accept any keyword args

    def __get_pydantic_core_schema__(self, source, handler):
        # Let Pydantic generate the usual schema for the wrapped type
        return handler(source)

    def __get_pydantic_json_schema__(self, core_schema, handler):
        return handler(core_schema)

# Patch only the missing attribute
pydantic.StringConstraints = _StringConstraints
_pt.StringConstraints = _StringConstraints
# ────────────────────────────────────────────────────────────────────────

import argparse
import pathlib
import sys
from docling.document_converter import DocumentConverter

# ---------------------------------------------------------------------
# Default locations – edit once here if you move the files later
# ---------------------------------------------------------------------
DEFAULT_SOURCE = "/Users/pawelluszynski/Desktop/perf-report.html"
DEFAULT_OUTDIR = "/Users/pawelluszynski/docling-demo/converted"

# ---------------------------------------------------------------------
def main() -> None:
    # 1. CLI arguments --------------------------------------------------
    ap = argparse.ArgumentParser(
        description="Convert a document to Markdown with Docling."
    )
    ap.add_argument(
        "source",
        nargs="?",                       # optional
        default=DEFAULT_SOURCE,
        help=f"Path or URL to the input file (default: {DEFAULT_SOURCE})",
    )
    ap.add_argument(
        "--out-dir",
        default=DEFAULT_OUTDIR,
        help=f"Directory to write the .md file (default: {DEFAULT_OUTDIR})",
    )
    args = ap.parse_args()

    # 2. Prepare output directory --------------------------------------
    out_dir = pathlib.Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 3. Derive output filename ----------------------------------------
    in_path = pathlib.Path(args.source)
    out_file = out_dir / (in_path.stem + ".md" if in_path.suffix else "output.md")

    # 4. Convert with Docling ------------------------------------------
    try:
        doc = DocumentConverter().convert(args.source).document
        out_file.write_text(doc.export_to_markdown(), encoding="utf-8")
    except Exception as exc:
        sys.exit(f"❌  Conversion failed: {exc}")

    # 5. Success message -----------------------------------------------
    print(f"✓ saved → {out_file}")

# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()