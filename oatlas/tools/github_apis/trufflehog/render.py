"""Render reports in all supported formats."""

from typing import Iterable, Tuple

import jinja2

from oatlas.tools.github_apis.trufflehog import STATIC_DIR, TEXT_TEMPLATE_FILE
from oatlas.tools.github_apis.trufflehog.models import Issue, Severity  # noqa: F401 doctest


def text(issues: Iterable[Issue]) -> str:
    """Render issues as text.

    Examples
    --------
    Basic usage examples

    >>> rule = Pattern(
    ...     id="bad-password-letmein",
    ...     message="Bad Password 'letmein'",
    ...     pattern="letmein",
    ...     severity="high",
    ... )
    >>> issue = Issue(
    ...     rule=rule,
    ...     path="/path/to/code.py",
    ...     line="10",
    ...     secret="letmein",
    ...     context={
    ...         "9":  "username = 'admin'",
    ...         "10": "password = 'letmein'",
    ...         "11": "response = authorize(username, password)",
    ...     },
    ... )
    >>> s = text([issue])

    """
    environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(STATIC_DIR),
        autoescape=False,  # no need to escape anything for plaintext format
        auto_reload=False,
    )
    template = environment.get_template(TEXT_TEMPLATE_FILE)
    return template.render(issues=sorted(issues, key=_sort_keys))


def _sort_keys(issue) -> Tuple[Severity, str, str]:
    """Return rule severity, message and issue path for sorting."""
    return (-issue.rule.severity, issue.rule.message.lower(), issue.path)
