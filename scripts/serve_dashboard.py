#!/usr/bin/env python3
"""Serve the dashboard directory with Python's built-in HTTP server."""

from __future__ import annotations

import argparse
import os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the dashboard website.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", type=int, default=8080, help="Bind port")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[1] / "dashboard"
    os.chdir(root)
    httpd = ThreadingHTTPServer((args.host, args.port), SimpleHTTPRequestHandler)
    print(f"Dashboard available at http://{args.host}:{args.port}")
    print(f"Serving directory: {root}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
