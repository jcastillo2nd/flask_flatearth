import logging
import os

import flask


log = logging.getLogger('flask_flatearth')


BASEPATH = os.getcwd()


class ContentPage(object):
    """
    Content page interface object

    :var CONTENT_TYPE: Default ContentPage type
    :type CONTENT_TYPE: `str`

    :var TEMPLATE: Default page template
    :type TEMPLATE: `str`

    :var RULES: Default rules to register page to
    :type RULES: `list` of `str`

    .. note::
        The RULES can be specified with '{slug}' and other named specifiers.
        Only '{slug}' is guaranteed however and if the keyword arguments are
        not passed in at instantiation, a KeyError will be raised.

    :ivar app: Flask application this page is registered with
    :type app: `flask.Flask`

    :ivar slug: Page slug
    :type slug: `str`

    :ivar meta: Metadata from source
    :type meta: `dict`

    :ivar rules: Rules to register page on
    :type rules: `list` of `str`

    :ivar content_type: ContentPage type
    :type content_type: `str`

    :ivar template: Template file for rendering this page
    :type template: `str`

    :ivar html: Rendered HTML content from source
    :type html: `str`

    :ivar file_name: Name of the source file
    :type file_name: `str`

    :ivar rules_set: Rules added to flask app
    :type rules_set: `bool`

    :ivar views_set: Rendered templates added to flask app endpoints
    :type views_set: `bool`

    :ivar refs: References to other objects for iterating in templates
    :type refs: `list`
    """
    CONTENT_TYPE = "page"
    TEMPLATE = "base.html"
    RULES = ['/{slug}/', ]

    def __init__(self,
                 app=None,
                 slug=None,
                 meta=None,
                 rules=None,
                 content_type=None,
                 template=None,
                 html=None,
                 file_name=None):
        """
        Initialize the ContentPage

        :param app: Flask app
        :type app: `flask.Flask`

        :param slug: Slug of page
        :type slug: `str`

        :param rules: Endpoint rules for page
        :type rules: `list` of `str`

        :param content_type: Type of content
        :type content_type: `str`

        :param template: Flask template name
        :type template: `str`
        """
        self._app = app
        if slug is None:
            msg = "Slug cannot be empty or None for {cls}".format(
                cls=self.__class__.__name__)
            raise RuntimeError(msg)
        self.slug = slug
        self.meta = meta
        if rules is None:
            self.rules = self.__class__.RULES
        else:
            if isinstance(rules, str):
                msg = "Rule not single item list for {}.".format(self.slug)
                msg += "Use rules=[rule,] to avoid this warning."
                log.warn(msg)
                self.rules = [rules, ]
            else:
                self.rules = rules
        self.content_type = content_type if content_type \
            else self.__class__.CONTENT_TYPE
        self.template = template if template \
            else self.__class__.TEMPLATE
        self.html = html
        self.file_name = file_name
        self.rules_set = False
        self.views_set = False
        self.refs = []

    @property
    def app(self):
        if self._app:
            return self._app
        else:
            return flask.current_app

    def page_content(self, **kwargs):
        """
        Generate the page_content values
        :param kwargs: Parameters passed to request
        :return: `dict` of parameters
        """
        return kwargs

    def register_rules(self, **kwargs):
        """
        Add rules to app

        Used to ensure that endpoints are registered. This is called prior to
        `register_view()`.
        :param kwargs: Keyword args to be passed to `rule.format(**kwargs)`
        """
        for rule in self.rules:
            r = rule.format(slug=self.slug, **kwargs)
            with self.app.app_context():
                self.app.add_url_rule(r, endpoint=self.slug)
        self.rules_set = True
        return self

    def register_view(self, **kwargs):
        """
        Set view functions
        :param kwargs: Parameters to be passed into view generation
        """
        if not self.rules_set:
            msg = "Attempting to register view function before calling " \
                  "register_rules() for {}".format(self.slug)
            raise RuntimeError(msg)
        params = self.page_content(**kwargs)
        with self.app.app_context():
            content = flask.render_template(self.template, **params)

        def view_fn(content):
            return lambda: content

        self.app.view_functions[self.slug] = view_fn(content)
        self.views_set = True
        return self

    def __repr__(self):
        msg = "{cls}({app}, '{slug}', content_type='{content}')".format(
            cls=self.__class__.__name__,
            app=self.app,
            slug=self.slug,
            content=self.content_type
        )
        return msg

    def __str__(self):
        msg = "<{cls} slug={slug}>".format(
            cls=self.__class__.__name__,
            slug=self.slug
        )
        return msg

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(self.slug)


class ContentListingPage(ContentPage):
    """
    Content Listing interface objects
    """
    CONTENT_TYPE = "page"
    SLUG = "pages"
    TEMPLATE = "pages.html"
    RULES = ['/pages/', ]

    def page_content(self, **kwargs):
        pages = kwargs['generator'].pages_iter(page_type=self.CONTENT_TYPE)
        slug = kwargs.get('slug', self.SLUG)
        kwargs.update({'pages': pages, 'slug': slug})
        return kwargs


class PageGenerator(object):
    """
    PageGenerator callable object

    Implementation for page generators return a dictionary of pages to be added
    to a <generator `ContentGenerator`>.

    :ivar g: ContentGenerator registered with
    :type g: `ContentGenerator`

    :ivar ext: The Extension this belongs to
    :type ext: `ContentGeneratorExtension`

    :return: `dict` of {<slug `str`: <Page `ContentPage`>}
    """
    PAGE_CLS = ContentPage

    def __init__(self, g, ext=None, **kwargs):
        msg = "Initializing PageGenerator {obj} with " \
              "{d}".format(obj=self.__class__.__name__,
                           d={'g': g, 'ext': ext, **kwargs})
        log.debug(msg)
        self.g = g
        self.ext = ext
        self.opts = {p: kwargs[p] for p in kwargs if p not in ['g', 'ext']}
        msg = "PageGenerator {cls} processing options " \
              "{data}".format(cls=self.__class__.__name__,
                              data=self.opts)
        log.debug(msg)
        self._process_options(**self.opts)

    def __call__(self, **kwargs):
        msg = "PageGenerator {obj} generating page with " \
              "{data}".format(obj=self,
                              data=kwargs)
        log.debug(msg)
        return self._generate(**kwargs)

    def __repr__(self):
        if self.opts:
            opts = ", ".join(
                ["{k}={v}".format(k=k, v=self.opts[k]) for k in self.opts])
        msg = "{cls}({g}, ext={ext}".format(self.__class__.__name__,
                                            g=self.g,
                                            ext=self.ext)
        msg = "".join([", ".join([msg, opts]), ")"])
        return msg

    def __str__(self):
        msg = "<{cls} g={g}>".format(cls=self.__class__.__name__,
                                     g=self.g)
        return msg

    def _generate(self, **kwargs):
        """
        Generate content pages

        Additional data may be passed in for processing of page generation.

        :param kwargs: Additional parameters for page generation
        :type kwargs: `dict`
        """
        opts = {kw: kwargs[kw] for kw in ["app",
                                          "slug",
                                          "meta",
                                          "rules",
                                          "content_type",
                                          "template",
                                          "html",
                                          "file_name"] if kw in kwargs}
        page = self.PAGE_CLS(**opts)
        return {page.slug: page}

    def _process_options(self, **kwargs):
        """
        Process options passed into initialization

        This permits handling of instance variable development with named
        parameters during the object initialization.

        :param kwargs: Arguments passed to initialization
        :type kwargs: `dict`
        """
        pass


class MetaProcessor(object):
    """
    MetaProcessor callable object

    Implementation for meta processors return a value that will be assigned to
    the :class:`ContentPage`.meta dictionary. They are registered via the
    `register_meta_processor()` method, and will be called with a single
    argument of data.

    :param data: Data to process
    :type data: `list`

    :return: Any value to be assigned into page metadata
    """
    def __init__(self, g, ext=None):
        msg = "Initializing MetaProcessor {obj} with " \
              "{d}".format(obj=self.__class__.__name__,
                           d={'generator': g, 'extension': ext})
        log.debug(msg)
        self.g = g
        self.ext = ext

    def __call__(self, data):
        msg = "MetaProcessor {obj} processing data " \
              "{data}".format(obj=self,
                              data=data)
        log.debug(msg)
        return self._process(data)

    def __repr__(self):
        msg = "{cls}({g}, ext={ext}".format(cls=self.__class__.__name__,
                                            g=self.g,
                                            ext=self.ext)
        return msg

    def __str__(self):
        msg = "<{cls} g={g}>".format(cls=self.__class__.__name__,
                                     g=self.g)
        return msg

    def _process(self, data):
        raise NotImplementedError


class ContentGenerator(object):
    """
    FlatEarth content generator

    Flask extension that searches a file path to generate content pages from
    static files.

    Example::

        from flask import Flask
        from flask_flatearth.markdown import MarkdownGenerator
        from flask_flatearth.extensions import FeedsExtension

        from .config import DefaultConfig

        app = Flask(__name__)
        app.config.from_object(DefaultConfig)

        feedsext = FeedsExtension()

        md = MarkdownGenerator(app, extensions=[feedsext, ])
        md.generate()

    When initialized, there may not be a <flask app `flask.Flask`> passed to
    initialize with. The `ContentGenerator` however can still proceed with
    registering <extensions `ContentGeneratorExtension`>.

    If the app is passed in, each extension is able to setup with the context
    of the flask app. If not, any calls that require the flask app context to
    be set will raise a RuntimeError until `init_app()` is called explicitly.
    This includes the main `generate()` method.

    :ivar app: Flask application (default `None`)
    :type app: :class:`flask.Flask`

    :ivar extensions: FlatEarth Extensions
    :type extensions: `dict` of {<name `str`> :class:<extension \
            `flask_flatearth.ContentGeneratorExtension`>

    :ivar file_ext: File extension of content page sources
    :type file_ext: `str` or `list` of `str`

    :ivar generators: Additional page generators
    :type generators: `dict` of {<name `str`>: \
            :class:<generator `PageGenerator`>}

    :ivar meta_processors: Dictionary of metadata processors
    :type meta_processors: `dict` of {<label `str`>: \
            :class:<processor `MetaProcessor`>}

    :ivar path: Path to content page sources
    :type path: `str`

    :ivar pages: Dictionary of pages
    :type pages: `dict` of {<slug `str`>: :class:<page \
            `ContentPage`>}

    :ivar page_files: Content file names
    :type page_files: `list` of <file names `str`>

    :ivar set_generators: Page set generators
    :type set_generators: `dict` of {<lable `str`: \
            :class:<generator `PageGenerator`>}
    """
    SEARCH_PATH = os.path.abspath(os.path.join(BASEPATH, "pages"))
    FILE_EXT = '.md'

    def __init__(self,
                 app=None,
                 extensions=[],
                 search_path=None,
                 file_ext=None):
        """
        Initialize ContentGenerator

        :param app: Flask instance
        :type app: `Flask`

        :param extensions: FlatEarth Generator extensions
        :type extensions: `list` of :class:`ContentGeneratorExtension` \
                instances

        :param search_path: Search path for pages
        :type search_path: `str`

        :param file_ext: Pages file extension(s)
        :type file_ext: `str` or `list`
        """
        self._app = app
        self.search_path = search_path if search_path else self.SEARCH_PATH
        self.file_ext = file_ext if file_ext else self.FILE_EXT
        self.page_files = []
        self.meta_processors = {}
        self.generators = {}
        self.set_generators = {}
        self.extensions = {}
        self.pages = {}
        if app is not None:
            self.init_app(app)
        if extensions:
            try:
                for ext in extensions:
                    ext.register(self)
            except TypeError:
                msg = "{ext} not valid. Is it a list of flatearth extension \
                        instances?".format(ext=extensions)
                log.error(msg)
            except AttributeError:
                msg = "{ext} not able to be registered. Is it a valid \
                        extension instance?".format(ext=ext)
                log.error(msg)
        for dirpath, dirnames, files in os.walk(self.search_path):
            for name in files:
                if name.lower().split('.')[-1] == self.file_ext \
                        or name.lower().split('.')[-1] in self.file_ext:
                    self.page_files += [os.path.join(dirpath, name), ]
        self._setup()

    def add_meta_processor(self, label, processor):
        """
        Register a meta processor with this ContentGenerator

        :param label: MetaProcessor label
        :type label: `str`

        :param processor: MetaProcessor to register
        :type processor: `MetaProcessor`

        :raise RuntimeError: on Duplicate label registration
        """
        if label in self.meta_processors:
            msg = "Meta label processor '{}' already registered.".format(label)
            raise RuntimeError(msg)
        else:
            self.meta_processors.update({label: processor})

    def add_page_generator(self, name, generator):
        """
        Register a page generator with this ContentGenerator

        :param name: PageGenerator name
        :type name: `str`

        :param generator: PageGenerator to register
        :type generator: `PageGenerator`

        :raise RuntimeError: on Duplicate name registration
        """
        if name in self.generators:
            msg = "Page generator '{}' already registered.".format(name)
            raise RuntimeError(msg)
        else:
            self.generators.update({name: generator})

    def add_set_generator(self, name, generator):
        """
        Register a page set generator with this ContentGenerator

        :param name: PageGenerator name
        :type name: `str`

        :param generator: PageGenerator to register
        :type generator: `PageGenerator`
        """
        if name in self.set_generators:
            msg = "Set generator {} already registered.".format(name)
            raise RuntimeError(msg)
        else:
            self.set_generators.update({name: generator})

    def add_extension(self, extension):
        """
        Register an extension with this ContentGenerator

        :param extension: The extension
        :type extension: `ContentGeneratorExtension`
        """
        if extension.name in self.extensions:
            msg = "Extension '{}' already registered.".format(extension)
            raise RuntimeError(msg)
        self.extensions.update({extension.name: extension})

    @property
    def app(self):
        if self._app:
            return self._app
        else:
            return flask.current_app

    def generate(self):
        """
        Generate content for flask application

        This first compiles all the pages through the registered PageGenerators
        then iterates the pages to register the url endpoint rules with the
        flask application. Once the rules are all registered, the views are
        then rendered. This ordering is required to all for the operation of
        url_for within the templates.

        :raise RuntimeError: on duplicate page slug

        .. warn::
            If called multiple times, each page will add duplicate rules to the
            flask application. The behavior is undefined and subject to the
            <flask app `flask.Flask`> url_map behavior with duplicate entries
            or behavior of duplicate :func:`flask.Flask.add_url_rule` calls.
        """
        self.load_pages()
        msg = "ContentGenerator {g} has pages {p}".format(g=self, p=self.pages)
        log.debug(msg)
        pages = {**self.pages}
        for e in self.extensions:
            gen_pages = self.extensions[e]()
            for p in gen_pages:
                if p in pages:
                    msg = "Page {p} already present. Attempted duplicate by " \
                        "{e}".format(p=p, g=self.extensions[e])
                    raise RuntimeError(msg)
            pages.update(gen_pages)
        for g in self.set_generators:
            pg = self.set_generators
            gen_pages = pg[g](app=self.app,
                              slug=pg[g].PAGE_CLS.SLUG,
                              generator=self)
            for p in gen_pages:
                if p in pages:
                    msg = "Page {p} already present. Attempted duplicate by " \
                        "{e}".format(p=p, g=self.set_generators[g])
                    raise RuntimeError(msg)
            pages.update(gen_pages)
        msg = "ContentGenerator {g} has pages {p}".format(g=self, p=pages)
        log.debug(msg)
        ctx = {}
        ctx.update({'authors': {a.slug: a for a in
                                self.pages_iter(page_type='author')}})
        ctx.update({'articles': {a.slug: a for a in
                                 self.pages_iter(page_type='article')}})
        ctx.update({'generator': self})
        for ext in self.extensions:
            ctx.update(self.extensions[ext].generate_context())
        for p in pages:
            pages[p].register_rules()
        for p in pages:
            pages[p].register_view(
                page_content=pages[p].html,
                meta=pages[p].meta,
                refs=pages[p].refs,
                **ctx
            )

    def get_page(self, slug):
        """
        Return Content Page
        :param slug: Slug of article
        :type slug: `str`
        :return: `ArticlePage`
        """
        return self.pages[slug]

    def get_renderer(self):
        """
        Return a method used in the Jinja2 template filter renderer for source
        strings.

        :return: :class:`meth`
        """
        return flask.render_template_string

    def init_app(self, app):
        """
        Initialize the flask app environment

        .. note::
            This registers a template filter 'flatearth_render' which by
            default returns :func:`flask.render_template_string`
        """
        self.search_path = app.config.get('FLATEARTH_SEARCH_PATH',
                                          self.search_path)
        self.file_ext = app.config.get('FLATEARTH_FILE_EXT',
                                       self.file_ext)
        app.add_template_filter(self.get_renderer(),
                                name='flatearth_render')

    def load_pages(self):
        raise NotImplementedError

    def pages_iter(self, page_type='page'):
        """
        Iterator for Pages

        Used to cycle through pages of content_type::

            for page in cg.pages_iter():
                print("Loaded page file: {fn}".format(page.file_name))
            for author in cg.pages_iter('author')
                print("Loaded author file: {fn}".format(author.file_name))

        :param page_type: The page type to generator
        :type page_type: `str`
        :return: `ContentPage` of `page_type`
        """
        for page in [p for p in self.pages if
                     self.pages[p].meta['type'] == page_type]:
            yield self.pages[page]

    def _process_meta(self, meta):
        """
        Prepare metadata dictionary
        :param meta: Metadata from source
        :type meta: `dict`
        :return: `dict`
        """
        msg = "Calling `_process_meta` for {m}".format(m=meta)
        log.debug(msg)
        m = {}
        for label in meta:
            if label in self.meta_processors:
                msg = "Found meta_processor for {lbl}.".format(lbl=label)
                log.debug(msg)
                m.update({label: self.meta_processors[label](meta[label])})
            else:
                msg = "No meta_processor found for {lbl}.".format(lbl=label)
                log.debug(msg)
                v = meta[label][0] if len(meta[label]) == 1 \
                    and label not in ['author'] \
                    else meta[label]
                m.update({label: v})
        msg = "Returning `_process_meta` values '{v}' for '{m}'" \
              "data.".format(v=m, m=meta)
        log.debug(msg)
        return m

    def _process_page(self, meta, html, file_name):
        for ext in self.extensions:
            self.extensions[ext]._process_page(meta, html, file_name)

    def _setup(self):
        """
        Setup ContentGenerator

        This can be used to initiate PageGenerators and MetaProcessors
        """
        pass


class IndexPage(ContentPage):
    """
    Index Page
    """
    CONTENT_TYPE = "index"
    TEMPLATE = "article.html"
    RULES = ['/', ]
    pass


class AuthorPage(ContentPage):
    """
    Author Page
    """
    CONTENT_TYPE = "author"
    TEMPLATE = "author.html"
    RULES = ['/authors/{slug}/', ]
    pass


class AuthorListingPage(ContentListingPage):
    """
    Author Listing Page
    """
    CONTENT_TYPE = "author"
    SLUG = "authors"
    TEMPLATE = "authors.html"
    RULES = ['/authors/', ]
    pass


class ArticlePage(ContentPage):
    """
    Article Page
    """
    CONTENT_TYPE = "article"
    TEMPLATE = "article.html"
    RULES = ['/articles/{slug}/', ]
    pass


class ArticleListingPage(ContentListingPage):
    """
    Article Listing Page
    """
    CONTENT_TYPE = "article"
    SLUG = "articles"
    TEMPLATE = "articles.html"
    RULES = ['/articles/', ]
    pass
