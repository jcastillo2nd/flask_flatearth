import mock
import pytest

from flask_flatearth import PageGenerator

g = None
ext = None
opts = {}

@pytest.fixture
def pg_with_none():
    """Returns a PageGenerator instance initialized with None"""
    return PageGenerator(g), g, ext, opts

@pytest.fixture
def pg_with_object():
    """Returns a PageGenerator instance initialized with g"""
    g = object()
    return PageGenerator(g), g, ext, opts

@pytest.fixture
def pg_with_object_ext():
    """Returns a PageGenerator instance initialized with g and ext"""
    g = object()
    ext =object()
    return PageGenerator(g, ext=ext), g, ext, opts

@pytest.fixture
def pg_with_object_ext_opts():
    """Returns a PageGenerator instance initialized with g, ext and kwargs"""
    g = object()
    ext = object()
    opts = {'test1': 'value1', 'test2': 'value2'}
    return PageGenerator(g, ext=ext, **opts), g, ext, opts

@pytest.mark.parametrize("pagegenerator",[
    pg_with_none,
    pg_with_object,
    pg_with_object_ext,
    pg_with_object_ext_opts,
])
@mock.patch('flask_flatearth.PageGenerator._process_options')
def test_pagegenerator_init(pg_opts, pagegenerator):
    pg, g, ext, opts = pagegenerator()
    assert pg.g is g
    assert pg.ext is ext
    assert False not in [opts[o] is pg.opts[o] for o in opts]
    if opts != {}:
        assert pg_opts.called

@pytest.mark.parametrize("pagegenerator",[
    pg_with_none,
    pg_with_object,
    pg_with_object_ext,
    pg_with_object_ext_opts,
])
def test_pagegenerator_called_raises(pagegenerator):
    pg, g, ext, kwargs = pagegenerator()
    pytest.raises(RuntimeError, pg)
