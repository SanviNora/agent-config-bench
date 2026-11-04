from agent_config_bench.bootstrap import bootstrap_mean


def test_bootstrap_mean_center():
    mean, lo, hi = bootstrap_mean([0.0, 1.0, 0.5, 0.5], n=2000, seed=0)
    assert abs(mean - 0.5) < 1e-9
    assert lo <= mean <= hi
