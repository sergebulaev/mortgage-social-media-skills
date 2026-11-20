"""Feed parsers. Each module exposes:

    URL / fetch(**params) -> bytes      network access (stdlib, browser-free)
    parse(raw, **params) -> data        pure, works on a saved fixture too
    check(data) -> list[str]            what changed if the source changed shape

`tests/fixtures/feeds/` holds real saved responses; the core's daily CI runs
`check` against the live source so a changed feed is noticed within a day.
"""
