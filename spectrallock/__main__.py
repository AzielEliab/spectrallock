"""Allow ``python -m spectrallock`` to invoke the CLI."""

from spectrallock.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
