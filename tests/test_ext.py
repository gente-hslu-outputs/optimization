import pytest
from enduseroptimizer import EndUser
from deepdiff import DeepDiff


@pytest.mark.parametrize("include_results", [False, True])
def test_dict(example_enduser, include_results):
    if include_results:
        example_enduser.include_results = True
        example_enduser.optimize()
    exp = example_enduser.to_dict()

    mdl = EndUser()
    mdl.from_dict(exp)
    imp = mdl.to_dict()

    assert len(DeepDiff(imp, exp, ignore_nan_inequality=True)) == 0
