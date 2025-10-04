"""Core trufflehog3 logic."""

import multiprocessing
import sys
from functools import partial
from itertools import chain
from pathlib import Path
from typing import Iterable, List, Union

import attr
import yaml

from oatlas.tools.github_apis.trufflehog import DEFAULT_CONFIG_FILE, DEFAULT_RULES_FILE, log
from oatlas.tools.github_apis.trufflehog.models import (
    Config,
    Entropy,
    Issue,
    Model,
    Pattern,
    Rule,
    Severity,
)
from oatlas.tools.github_apis.trufflehog.render import text
from oatlas.tools.github_apis.trufflehog.search import search
from oatlas.tools.github_apis.trufflehog.source import diriter, gititer


def scan(
    target: str,
    config: Config,
    rules: Iterable[Union[Entropy, Pattern]],
    processes: int,
) -> Iterable[Issue]:
    """Return issues found during target path scan."""
    if config.no_entropy:  # pragma: no cover
        rules = [r for r in rules if not isinstance(r, Entropy)]

    if config.no_pattern:  # pragma: no cover
        rules = [r for r in rules if not isinstance(r, Pattern)]

    if not rules:  # pragma: no cover
        raise ValueError("empty ruleset")

    exclude = []
    for e in config.exclude or []:
        if e.id is None and e.pattern is None:
            exclude.extend(e.paths)

    files = []
    if not config.no_history:  # pragma: no cover
        files.extend(
            gititer(
                target,
                exclude=exclude,
                branch=config.branch,
                depth=config.depth,
                since=config.since,
            )
        )

    if not config.no_current:  # pragma: no cover
        files.extend(diriter(target, exclude))

    worker = partial(
        search,
        rules=rules,
        exclude=config.exclude,
        ignore_nosecret=config.ignore_nosecret,
        context=config.context,
    )

    with multiprocessing.Pool(processes) as pool:
        issues = pool.map(worker, files)

    return set(chain.from_iterable(issues))


def diff(
    old: Iterable[Issue],
    new: Iterable[Issue],
    only_new: bool = False,
) -> Iterable[Issue]:  # pragma: no cover
    """Return diff from the given lists of issues.

    By default, full diff will be returned, i.e. issues that are not found in
    either of the given lists. In case `only_new` is True, only issues that
    are present in the `new` list, but not in the `old` one will be returned.

    """
    old_set = set(old)
    new_set = set(new)

    if only_new:
        d = new_set - old_set
    else:
        d = new_set ^ old_set

    return list(d)


def load_config(path: str, **kwargs) -> Config:
    """Load config from file or search for it in the specified directory.

    Note
    ----
    Uses `DEFAULT_CONFIG_FILE` filename for searching config file in directory.

    All `kwargs` are passed to `Config.update` method after loading.

    Examples
    --------
    Basic usage examples. Load config from file

    >>> path = Path() / DEFAULT_CONFIG_FILE
    >>> config = load_config(path)
    >>> config.ignore_nosecret
    False

    Provide values to override config

    >>> config = load_config(path, ignore_nosecret=True)
    >>> config.ignore_nosecret
    True

    Search config in directory

    >>> config = load_config(Path())
    >>> config.ignore_nosecret
    False

    """
    path = Path(path)
    for config_path in (path, path / DEFAULT_CONFIG_FILE):
        if config_path.is_file():
            log.info(f"loading config from {config_path.absolute()}")
            config = load(Config, config_path)
            break
    else:
        config = Config()  # pragma: no cover

    return attr.evolve(config, **kwargs)


def load_rules(
    path: str,
    severity: Severity = Severity.LOW,
) -> Iterable[Union[Entropy, Pattern]]:
    """Load rules from file.

    Examples
    --------
    Basic usage examples

    >>> len(load_rules(DEFAULT_RULES_FILE))
    31
    >>> len(load_rules(DEFAULT_RULES_FILE, Severity.MEDIUM))
    28
    >>> len(load_rules(DEFAULT_RULES_FILE, Severity.HIGH))
    2
    """
    rules = []
    for r in load(Rule.fromargs, path or DEFAULT_RULES_FILE):
        if r.severity >= severity:
            rules.append(r)
        else:
            log.warn(f"skipping rule {r.id}")

    return rules


def load(cls: type, file: str = None) -> Union[Model, List[Model]]:
    """Load any model from YAML file.

    Note
    ----
    File defaults to `sys.stdin`. See `core.loads` for more details.

    Examples
    --------
    Define a class with the necessary properties

    >>> @attr.s
    ... class Test(Model):
    ...     version: str = attr.ib()
    ...     numbers: List[int] = attr.ib()

    Load model

    >>> obj = load(Test, "tests/data/test_load.yml")
    >>> obj.asdict()
    {'version': 'v1', 'numbers': [1, 2]}

    Load list of models

    >>> objs = load(Test, "tests/data/test_load_list.yml")
    >>> [obj.asdict() for obj in objs]
    [{'version': 'v1', 'numbers': [1, 2]}, {'version': 'v2', 'numbers': [3]}]

    """
    if file:
        raw = Path(file).read_text()
    else:
        raw = sys.stdin.read()  # pragma: no cover

    return loads(cls, raw)


def loads(cls: type, raw: str) -> Union[Model, List[Model]]:
    """Load any model from YAML string.

    Note
    ----
    Model is instantiated using provided `cls`.
    If YAML contains a list, each item is instantiated using `cls`

    Examples
    --------
    Define a class with the necessary properties

    >>> @attr.s
    ... class Test(Model):
    ...     version: str = attr.ib()
    ...     numbers: List[int] = attr.ib()

    Load model

    >>> raw = '''
    ... version: v1
    ... numbers:
    ... - 1
    ... - 2
    ... '''
    >>> obj = loads(Test, raw)
    >>> obj.asdict()
    {'version': 'v1', 'numbers': [1, 2]}

    Load list of models

    >>> raw = '''
    ... - version: v1
    ...   numbers:
    ...   - 1
    ...   - 2
    ... - version: v2
    ...   numbers:
    ...   - 3
    ... '''
    >>> objs = loads(Test, raw)
    >>> [obj.asdict() for obj in objs]
    [{'version': 'v1', 'numbers': [1, 2]}, {'version': 'v2', 'numbers': [3]}]

    """
    data = yaml.safe_load(raw)
    if isinstance(data, list):
        model = [cls(**item) for item in data]
    else:
        model = cls(**data)

    return model


def render(issues: Iterable[Issue], file: str = None):
    """
    Changing render to return the raw formatted text instead of actually rendering it

    1. Not using the write function. Removed it completely
    2. Removed renders and implemented here itself
    3. Returning the raw data instead of writing it to std.out
    """
    f = text
    return f(issues)
