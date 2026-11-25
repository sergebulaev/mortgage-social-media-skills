"""Shared library of the vertical social media skill bundles (stdlib only).

Shared by the family of vertical bundles and maintained upstream: propose a
change in an issue or pull request here (CONTRIBUTING.md). Everything is optional: every skill also works by
following its SKILL.md with plain file tools.
"""
from .compliance import autofix, check, load_rules  # noqa: F401
from .provenance import unsupported_numbers  # noqa: F401
from .style import lint as style_lint  # noqa: F401
from .utm import publora_link  # noqa: F401
