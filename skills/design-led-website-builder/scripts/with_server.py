#!/usr/bin/env python3
"""Start a local static server, run a command, then stop the server.

Replaces a host-specific helper so fixture checks can run from this skill root.
"""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Sequence


def wait_for_port(port: int, timeout: float) -> None:
    deadline = time.time() + timeout
    url = f"http://127.0.0.1:{port}/"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status < 500:
                    return
        except (urllib.error.URLError, TimeoutError, ConnectionError, socket.error):
            time.sleep(0.1)
    raise SystemExit(f"ERROR: server did not become ready on port {port} within {timeout:.0f}s")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", required=True, help="Shell command that serves the fixture.")
    parser.add_argument("--port", type=int, default=4173)
    parser.add_argument("--timeout", type=float, default=15)
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after --")
    args = parser.parse_args(argv)
    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("Provide a command after --")

    server = subprocess.Popen(
        args.server,
        shell=True,
        cwd=os.getcwd(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wait_for_port(args.port, args.timeout)
        env = os.environ.copy()
        env.setdefault("VERTICAL_SLICE_URL", f"http://127.0.0.1:{args.port}")
        return subprocess.call(command, env=env)
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()


if __name__ == "__main__":
    raise SystemExit(main())
