#!/usr/bin/env python3
"""Install the built Spine Animation skill for Codex without overwriting a skill."""

import argparse
import shutil
import tempfile
from pathlib import Path

from build_skill import ROOT, BUNDLE, build


def install(destination: Path) -> Path:
    destination = destination.expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f'Refusing to overwrite existing skill: {destination}')
    if build(check=True):
        raise ValueError('Skill bundle is stale. Run python3 build_skill.py first.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.spine-install-', dir=destination.parent) as temp:
        staged = Path(temp) / 'spine-animation'
        shutil.copytree(ROOT / BUNDLE, staged)
        staged.rename(destination)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path,
                        default=Path.home() / '.agents/skills/spine-animation',
                        help='Skill directory (default: ~/.agents/skills/spine-animation)')
    args = parser.parse_args()
    try:
        destination = install(args.destination)
    except (OSError, ValueError) as error:
        parser.exit(1, f'Error: {error}\n')
    print(f'Installed: {destination}\nStart a new Codex conversation to load the skill.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
