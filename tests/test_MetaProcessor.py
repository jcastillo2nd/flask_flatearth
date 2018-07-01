import pytest

from flask_flatearth import MetaProcessor

g = None
ext = None

@pytest.fixture
def mp_with_none():
    """Returns a MetaProcessor instance initialized with None"""
    return MetaProcessor(g), g, ext

@pytest.fixture
def mp_with_object():
    """Returns a MetaProcessor instance initialized with g"""
    g = object()
    return MetaProcessor(g), g, ext

@pytest.fixture
def mp_with_object_and_ext():
    """Returns a MetaProcessor instance initialized with g with ext"""
    g = object()
    ext = object()
    return MetaProcessor(g, ext=ext), g, ext

@pytest.mark.parametrize("metaprocessor", [
    mp_with_none,
    mp_with_object,
    mp_with_object_and_ext
])
def test_metaprocessor_init(metaprocessor):
    mp, g, ext = metaprocessor()
    assert mp.g is g
    assert mp.ext is ext

@pytest.mark.parametrize("metaprocessor", [
    mp_with_none,
    mp_with_object,
    mp_with_object_and_ext
])
def test_metaprocessor_called_without_data_raises(metaprocessor):
    mp, obj, ext = metaprocessor()
    pytest.raises(TypeError, mp)

@pytest.mark.parametrize("metaprocessor", [
    mp_with_none,
    mp_with_object,
    mp_with_object_and_ext
])
def test_metaprocessor_called_raises(metaprocessor):
    mp, obj, ext = metaprocessor()
    pytest.raises(NotImplementedError, mp, None)
