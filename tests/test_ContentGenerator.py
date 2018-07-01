import mock
import pytest

import flask
from flask_flatearth import ContentGenerator
from flask_flatearth import MetaProcessor
from flask_flatearth import PageGenerator
from flask_flatearth import ContentPage
from flask_flatearth.ext import ContentGeneratorExtension

app = None
ext = None
search = ContentGenerator.SEARCH_PATH
filext = ContentGenerator.FILE_EXT

@pytest.fixture
def cg_with_noapp():
    """Returns ContentGenerator instance initialized with None"""
    return ContentGenerator(app), app, ext, search, filext

@pytest.fixture
def cg_with_noapp_path():
    """Returns ContentGenerator instance initialized with None"""
    search = 'mypages'
    return ContentGenerator(app, search_path=search), app, ext, search, filext

@pytest.fixture
def cg_with_noapp_filext():
    """Returns a ContentGenerator instance initialized with file extension"""
    filext = '.html'
    return ContentGenerator(app, file_ext=filext), app, ext, search, filext


@pytest.fixture
def cg_with_noapp_extensions():
    """Returns ContentGenerator instance initialized with extensions"""
    ext1 = mock.Mock(spec=ContentGeneratorExtension)
    ext2 = mock.Mock(spec=ContentGeneratorExtension)
    ext = [ext1, ext2]
    return ContentGenerator(app, extensions=ext), app, ext, search, filext

@pytest.fixture
def cg_with_app():
    app = mock.Mock(spec=flask.Flask, config={})
    ext1 = mock.Mock(spec=ContentGeneratorExtension)
    ext2 = mock.Mock(spec=ContentGeneratorExtension)
    ext = [ext1, ext2]
    return ContentGenerator(app, extensions=ext), app, ext, search, filext

@pytest.fixture
def cg_with_app_extensions():
    app = mock.Mock(spec=flask.Flask, config={})
    return ContentGenerator(app), app, ext, search, filext

@pytest.fixture
def cg_with_mpsg():
    cg = ContentGenerator(None)
    mps = {'mp1': mock.Mock(spec=MetaProcessor, return_value={})}
    pgs = {'pg1': mock.Mock(spec=PageGenerator, return_value={})}
    sgs = {'sg1': mock.Mock(spec=PageGenerator, return_value={})}
    cg.meta_processors = mps
    cg.page_generators = pgs
    cg.set_generators = sgs
    return cg

@pytest.fixture
def cg_with_mpsg_page():
    cg = ContentGenerator(None)
    pg1 = mock.Mock(spec=ContentPage)
    pg2 = mock.Mock(spec=ContentPage)
    mps = {'mp1': mock.Mock(spec=MetaProcessor, return_value={})}
    pgs = {'pg1': mock.Mock(spec=PageGenerator, return_value={})}
    sgs = {'sg1': mock.Mock(spec=PageGenerator, return_value={})}
    cg.meta_processors = mps
    cg.page_generators = pgs
    cg.set_generators = sgs
    cg.pages = {'page1': pg1, 'page2': pg2}
    return cg

@pytest.fixture
def cg_with_mpsg_page_dupe():
    cg = ContentGenerator(None)
    pg1 = mock.Mock(spec=ContentPage)
    pg2 = mock.Mock(spec=ContentPage)
    mps = {'mp1': mock.Mock(spec=MetaProcessor, return_value={})}
    pgs = {'pg1': mock.Mock(spec=PageGenerator, return_value={'page2': pg2})}
    sgs = {'sg1': mock.Mock(spec=PageGenerator, return_value={})}
    cg.meta_processors = mps
    cg.page_generators = pgs
    cg.set_generators = sgs
    cg.pages = {'page1': pg1, 'page2': pg2}
    return cg

@pytest.mark.parametrize("contentgenerator", [
    cg_with_noapp,
    cg_with_noapp_path,
    cg_with_noapp_filext,
    cg_with_noapp_extensions,
    cg_with_app,
    cg_with_app_extensions,
])
@mock.patch("flask_flatearth.ContentGenerator.init_app")
def test_contentgenerator_init(init_app_fn, contentgenerator):
    init_app_fn.return_value = None
    cg, app, ext, search, filext = contentgenerator()
    if app is not None:
        assert init_app_fn.called
    if ext is not None:
        assert False not in [e.register.called for e in ext]
    assert cg._app is app
    assert cg.search_path is search
    assert cg.file_ext is filext

def test_contentgenerator_add_meta_processor(cg_with_mpsg):
    cg = cg_with_mpsg
    pytest.raises(RuntimeError, cg.add_meta_processor, 'mp1', None)
    cg.add_meta_processor('mp2', mock.Mock())
    assert 'mp2' in cg.meta_processors

def test_contentgenerator_add_page_generator(cg_with_mpsg):
    cg = cg_with_mpsg
    pytest.raises(RuntimeError, cg.add_page_generator, 'pg1', None)
    cg.add_page_generator('pg2', None)
    assert 'pg2' in cg.page_generators

def test_contentgenerator_add_set_generator(cg_with_mpsg):
    cg = cg_with_mpsg
    pytest.raises(RuntimeError, cg.add_set_generator, 'sg1', None)
    cg.add_set_generator('sg2', None)
    assert 'sg2' in cg.set_generators

def test_contentgenerator_generate(cg_with_mpsg):
    cg = cg_with_mpsg
    with mock.patch('flask_flatearth.ContentGenerator.load_pages') as lp_fn:
        new_p = [p for s in [cg.generators, cg.set_generators] for p in s]
        if any([n in x for n in new_p for x in cg.pages ]):
            pytest.raises(RuntimeError, cg.generate)
        else:
            cg.generate()
            assert lp_fn.called
            for s in cg.set_generators:
                assert cg.set_generators[s].called
            for g in cg.generators:
                assert cg.generators[g].called
