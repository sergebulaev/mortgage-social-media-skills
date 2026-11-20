"""Shared library of the vertical social media skill bundles (stdlib only).

Generated from vertical-skills-core; do not edit in a vertical repo, edit the
core and regenerate. Everything is optional: every skill also works by
following its SKILL.md with plain file tools.
"""
from .compliance import autofix, check, load_rules  # noqa: F401
from .provenance import unsupported_numbers  # noqa: F401
from .style import lint as style_lint  # noqa: F401
from .utm import publora_link  # noqa: F401
