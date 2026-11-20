import pytest
from render import virtual_texture as mod

CASES = [
    ("merge", 'm.merge_visible_pages([(1, 2, 0, 0), (3, 4, 0, 0)], [(1, 2, 0, 0), (5, 6, 1, 0)]) == [(1, 2, 0, 0), (3, 4, 0, 0), (5, 6, 1, 0)]'),
    ("key", 'm.request_key(3, 4, 2, 1) == "3:4:2:1"'),
    ("index", 'm.table_index(3, 4, 8) == 35'),
    ("resident", 'm.is_resident((1, 2, 0, 0), [(1, 2, 0, 0), (3, 4, 0, 0)]) is True'),
    ("evict", 'm.evict_candidates([((0, 0, 0, 0), 10), ((1, 0, 0, 0), 5), ((2, 0, 0, 0), 9)], {(0, 0, 0, 0)}, 12, 3) == [(1, 0, 0, 0)]'),
    ("bucket", 'm.pool_bucket_size(200, 100, 128) == 256'),
    ("border", 'm.border_rect(10, 20, 30, 40, 2) == (8, 18, 34, 44)'),
    ("fence", '(m.needs_fence("copy", "graphics"), m.needs_fence("graphics", "graphics")) == (True, False)'),
    ("bc7", 'm.bc7_bytes(9, 5) == 96'),
    ("miptail", 'm.mip_tail_extent(256, 128, 5) == (16, 8)'),
    ("layer", '(m.clamp_layer(-1, 4), m.clamp_layer(9, 4)) == (0, 3)'),
    ("stale", '(m.is_stale(10, 12, 1), m.is_stale(9, 12, 3)) == (True, False)'),
    ("priority", 'm.upload_priority((3, 4, 2, 1)) == (2, 1, 4, 3)'),
    ("budget", 'm.page_budget(1024, 128) == 8'),
    ("dedupe", 'm.dedupe_requests([(1, 2, 0, 0), (1, 2, 0, 0), (1, 2, 1, 0), (3, 4, 0, 1)]) == [(1, 2, 0, 0), (1, 2, 1, 0), (3, 4, 0, 1)]')
]

@pytest.mark.parametrize("name,expr", CASES, ids=[c[0] for c in CASES])
def test_contract(name, expr):
    assert eval(expr, {"m": mod, "approx": pytest.approx})
