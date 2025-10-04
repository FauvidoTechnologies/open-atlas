"""
Custom Trufflehog module, modified for Atlas

Changes made:

`__init__.py file`
1. Import path for helper removed and replaced with custom logger
2. Name changed to trufflehog
3. Removed report outputs because those won't be needed, the only thing useful inside static dir is the rules yaml
4. `.trufflehog3.yml` becomes the `.trufflehog.yml` file
5. Removed set_debug because not required
6. Removed unsused logging import
7. Removed __version__ cause why not

`helper.py`
1. Deleted the helper function
2. Moved the helper functions to `atlas.utils.common`

`search.py`
1. Changed import to the right ones.

`source.py`
1. Changed imports to the right ones

`render.py`
1. Kept only raw text rendering, removed the color feature
2. Removed all other json and html renders

"""

import re

from pathlib import Path

from oatlas.logger import get_logger

__NAME__ = "trufflehog"

HERE = Path(__file__).parent
STATIC_DIR = HERE / "static"
DEFAULT_RULES_FILE = STATIC_DIR / "rules.yml"
TEXT_TEMPLATE_FILE = "report.text.j2"


DEFAULT_CONFIG_FILE = f".{__NAME__}.yml"
DEFAULT_EXCLUDE_SET = {DEFAULT_CONFIG_FILE, ".git"}

# Inline 'nosecret' comment implementation taken from semgrep:
# https://github.com/returntocorp/semgrep/blob/master/semgrep/semgrep/constants.py
NOSECRET_INLINE_RE = re.compile(
    # We're looking for items that look like this:
    # ' nosecret'
    # ' nosecret: example-pattern-id'
    # ' nosecret: pattern-id1,pattern-id2'
    # ' NOSECRET:pattern-id1, pattern-id2'
    #
    # * We do not want to capture the ': ' that follows 'nosecret'
    # * We do not care about the casing of 'nosecret'
    # * We want a comma-separated list of ids
    # * We want multi-language support, so we cannot strictly look for
    #   Python comments that begin with '# '
    #
    r" nosecret(?::[\s]?(?P<ids>([^,\s](?:[,\s]+)?)+))?",
    re.IGNORECASE,
)
IGNORE_NOSECRET = False

log = get_logger()  # Our own logger, make sure the calls are correct later on
