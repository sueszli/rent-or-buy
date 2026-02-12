from net_savings import IncomePercentile, net_savings_monthly


def test_stub():
    assert True


def test_import_src():
    ret = net_savings_monthly(IncomePercentile.pct_10th)
    assert isinstance(ret, float)
