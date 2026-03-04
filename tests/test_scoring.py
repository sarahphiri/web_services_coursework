from app.scoring import minmax_norm, inverse_minmax, hidden_gem_score


def test_minmax_norm_basic():
    assert minmax_norm(5, 0, 10) == 0.5
    assert minmax_norm(0, 0, 10) == 0.0
    assert minmax_norm(10, 0, 10) == 1.0


def test_inverse_minmax_basic():
    assert inverse_minmax(0, 0, 10) == 1.0  # lowest is best
    assert inverse_minmax(10, 0, 10) == 0.0 # highest is worst


def test_hidden_gem_score_bounds():
    # should always clamp to [0,1]
    s1 = hidden_gem_score(5.0, 0.1)
    s2 = hidden_gem_score(0.0, 9999.0)
    assert 0.0 <= s1 <= 1.0
    assert 0.0 <= s2 <= 1.0


def test_hidden_gem_prefers_lower_visitors():
    # same rating, fewer visitors should score higher
    low_vis = hidden_gem_score(4.5, 1.0)
    high_vis = hidden_gem_score(4.5, 100.0)
    assert low_vis > high_vis