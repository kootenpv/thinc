import pytest

from ....neural._classes.window_encode import MaxoutWindowEncode
from ....neural.ops import NumpyOps


@pytest.mark.xfail
def test_init_succeeds():
    model = MaxoutWindowEncode(10)


@pytest.mark.xfail
def test_init_defaults_and_overrides():
    model = MaxoutWindowEncode(10)
    assert model.nr_piece == MaxoutWindowEncode.nr_piece
    assert model.nr_feat == MaxoutWindowEncode.nr_feat
    assert model.nr_out == 10
    assert model.nr_in == None
    model = MaxoutWindowEncode(10, nr_piece=MaxoutWindowEncode.nr_piece-1)
    assert model.nr_piece == MaxoutWindowEncode.nr_piece-1
    model = MaxoutWindowEncode(10, nr_feat=MaxoutWindowEncode.nr_feat-1)
    assert model.nr_feat == MaxoutWindowEncode.nr_feat-1
