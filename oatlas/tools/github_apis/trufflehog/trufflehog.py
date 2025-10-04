#!/usr/bin/env python3
"""Trufflehog3 API entrypoint (no CLI)."""

import multiprocessing
import os
from tempfile import TemporaryDirectory
from urllib.parse import urlparse

import git

from oatlas.tools.github_apis.trufflehog import __NAME__, DEFAULT_RULES_FILE
from oatlas.tools.github_apis.trufflehog.core import (
    diff,
    load,
    load_config,
    load_rules,
    render,
    scan,
)
from oatlas.tools.github_apis.trufflehog.models import Format, Issue, Severity

try:
    CPU_COUNT = multiprocessing.cpu_count()
except NotImplementedError:  # pragma: no cover
    CPU_COUNT = 1


def run(
    targets=None,
    zero=False,
    verbose=0,
    config=None,
    rules=DEFAULT_RULES_FILE,
    incremental=None,
    processes=CPU_COUNT,
    exclude=None,
    severity=Severity.LOW,
    ignore_nosecret=False,
    no_entropy=False,
    no_pattern=False,
    branch=None,
    depth=10000,
    since=None,
    no_current=False,
    no_history=False,
    fmt=Format.TEXT,
    context=0,
):
    """
    Run Trufflehog programmatically without CLI.

    Parameters
    ----------
    targets : list[str]
        List of search targets (defaults to current directory).
    zero : bool
        Always exit with zero status code if True.
    verbose : int
        Verbosity level (-v, -vv, -vvv).
    config : str or Path
        Path to config file.
    rules : str or Path
        Path to rules file.
    incremental : str or Path
        Path to previous scan file for incremental diffing.
    processes : int
        Number of subprocesses to run.
    exclude : list[Exclude]
        Exclusion rules.
    severity : Severity
        Minimum severity filter.
    ignore_nosecret : bool
        Ignore inline `nosecret` annotations.
    no_entropy : bool
        Disable entropy checks.
    no_pattern : bool
        Disable pattern checks.
    branch : str
        Repo branch to scan.
    depth : int
        Commit depth limit.
    since : str
        Commit hash to start scanning from.
    no_current : bool
        Disable current status check.
    no_history : bool
        Disable commit history check.
    fmt : Format
        Output format (text/json/html).
    context : int
        Number of context lines to include.
    render_html : bool
        If True, render an HTML report from JSON issues file(s).
    version : bool
        If True, return version and exit.

    Returns
    -------
    int
        Exit code (0 if no issues, 2 if issues found, unless zero=True).
    """

    # Prepare config kwargs
    kw = dict(
        exclude=exclude,
        severity=severity,
        ignore_nosecret=ignore_nosecret,
        no_entropy=no_entropy,
        no_pattern=no_pattern,
        branch=branch,
        depth=depth,
        since=since,
        no_current=no_current,
        no_history=no_history,
        context=context,
    )

    # Load config
    # if config:
    #     config = load_config(config, **{k: v for k, v in kw.items() if v})
    # else:
    #     config = None
    config = None  # I am not going to pass it any config

    # Load rules
    ruleset = load_rules(rules, severity)
    issues = []

    for target in targets or [os.curdir]:
        remote = urlparse(target).scheme in ("http", "https")
        if remote:
            tmp = TemporaryDirectory(prefix=f"{__NAME__}-")
            git.Repo.clone_from(target, tmp.name)
            target = tmp.name

        if not config:
            config = load_config(target, **{k: v for k, v in kw.items() if v})

        issues.extend(scan(target, config, ruleset, processes))

        if remote:
            tmp.cleanup()

    # Incremental diff
    if incremental:
        issues = diff(load(Issue, incremental), issues, only_new=True)

    # Render results
    output = render(issues)  # file=None is default because I am not going to output a file

    # Also now this is completely devoid of color. So that's good.
    return output
