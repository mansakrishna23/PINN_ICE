import PINN_ICE as pinn
import pytest

def test_domain_parameter():
    d = pinn.parameters.domain_parameter()
    assert hasattr(d, "param_dict"), "Default attribute 'param_dict' not found"

    newat = {"feature_not_exist_1":1, "feature_not_exist_2": [2,3,4]}
    d.set_parameters(newat)
    assert d.has_keys(newat) == False

    d._add_parameters(newat)
    assert d.has_keys(newat) == True

def test_data_parameter():
    d = pinn.parameters.data_parameter({"name":['u', 'v'], "size":[4000, 4000]})
    assert hasattr(d, "param_dict"), "Default attribute 'param_dict' not found"

    with pytest.raises(Exception):
        d = pinn.parameters.data_parameter({"name":['u', 'v'], "size":[1, 2, 3]})

