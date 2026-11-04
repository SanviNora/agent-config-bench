from pathlib import Path

from agent_config_bench.analyze import paired, run_analysis, summarize, load_rows

FIX = Path(__file__).parent / "fixtures" / "mini_eval.json"


def test_summarize_and_paired(tmp_path: Path):
    rows = load_rows([FIX])
    summary = summarize(rows, n_boot=500)
    assert set(summary) == {"A_closed_book", "B_tools_only", "C_tools_skills"}
    assert summary["C_tools_skills"]["task_pass_rate"] == 1.0
    p = paired(rows, "A_closed_book", "B_tools_only", n_boot=500)
    assert p is not None
    assert p["n_tasks"] == 2
    # T1 improves, T2 regresses → mean diff ~ 0
    assert abs(p["pass_rate_diff"]) < 0.01

    out = run_analysis([FIX], out_root=tmp_path, n_boot=500)
    assert (tmp_path / "results/summary.json").exists()
    assert (tmp_path / "reports/pass_rate.png").exists()
    assert out["n_rows"] == 6
