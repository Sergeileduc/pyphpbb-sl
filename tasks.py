import os
import shutil
import subprocess
from itertools import chain
from pathlib import Path
from platform import uname

from invoke import task

"""'Makefile' equivalent for invoke tool (invoke or inv).
# Installation
`pip install invoke`
# Usage
> inv test
> inv build
etc...
# Autocompletion
For auto completion, just run:
`source <(inv --print-completion-script bash)`
or
`source <(inv --print-completion-script zsh)`
(or add it to ~/.zshrc or ~/.bashrc)
"""


# UTILS -----------------------------------------------------------------------

def get_platform():
    """Check the platform (Windos, Linux, or WSL)."""
    u = uname()
    if u.system == 'Windows':
        return 'windows'
    elif u.system == 'Linux' and 'microsoft' in u.release:
        return 'wsl'
    else:
        return 'linux'


def get_index_path():
    """Get full path for ./htmlcov/index.html file."""
    platform = get_platform()
    if platform == "wsl":
        # TODO: this part with .strip().replace() is ugly...
        process = subprocess.run(['wslpath', '-w', '.'], capture_output=True, text=True)
        pathstr = process.stdout.strip().replace('\\', '/')
        path = Path(pathstr) / 'htmlcov/index.html'
    else:
        path = Path('.').resolve() / 'htmlcov' / 'index.html'
    return path


# TASKS------------------------------------------------------------------------

@task
def lint(c):
    """flake8 - static check for python files"""
    c.run("flake8 .")


@task
def cleantest(c):
    """Clean artifacts like *.pyc, __pycache__, .pytest_cache, etc..."""
    # Find .pyc or .pyo files and delete them
    exclude = ('venv', '.venv')
    p = Path('.')
    genpyc = (i for i in p.glob('**/*.pyc') if not str(i.parent).startswith(exclude))
    genpyo = (i for i in p.glob('**/*.pyo') if not str(i.parent).startswith(exclude))
    artifacts = chain(genpyc, genpyo)
    for art in artifacts:
        os.remove(art)

    # Delete caches folders
    cache1 = (i for i in p.glob('**/__pycache__'))
    cache2 = (i for i in p.glob('**/.pytest_cache'))
    cache3 = (i for i in p.glob('**/.mypy_cache'))
    caches = chain(cache1, cache2, cache3)
    for cache in caches:
        shutil.rmtree(cache)

    # Delete coverage artifacts
    try:
        os.remove('.coverage')
        shutil.rmtree('htmlcov')
    except FileNotFoundError:
        pass


@task(cleantest)
def clean(c):
    """Equivalent to both cleanbuild and cleantest..."""
    pass


@task
def test(c):
    """Run tests with pytest."""
    c.run("pytest tests/")
