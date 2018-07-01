import logging

log = logging.getLogger('flask_flatearth.ext')


class ContentGeneratorExtension(object):
    """
    Extensions for FlatEarth ContentGenerators

    Extensions are similar to content generators, the difference being that
    they are called and return a set of the generated pages. They have the
    opportunity to process each page that the ContentGenerator has processed
    since setup and must have a ContentGenerator to operate.

    Actions that require a flask application instance should be limited to
    when the instance is being called to generate the pages when the
    ContentGenerator is running with a flask app context.

    :ivar name: Name of extension
    :type name: `str`

    :ivar generators: Additional page generators
    :type generators: `dict` of {<name `str`>: \
            :class:<generator `PageGenerator`>}

    :ivar meta_processors: Dictionary of metadata processors
    :type meta_processors: `dict` of {<label `str`>: \
            :class:<processor `MetaProcessor`>}

    :ivar pages: Dictionary of pages
    :type pages: `dict` of {<slug `str`>: :class:<page \
            `ContentPage`>}

    :ivar set_generators: Page set generators
    :type set_generators: `dict` of {<lable `str`: \
            :class:<generator `PageGenerator`>}
    """
    EXTENSION_NAME = "generator_extension"

    def __init__(self, name=None, generator=None):
        """
        Initialize the extension

        :param name: Name of extension
        :type name: `str`
        """
        self.name = name if name else self.EXTENSION_NAME
        msg = "Initializing Extension {cls} as "\
              "{name}".format(cls=self.__class__.__name__,
                              name=self.name)
        log.debug(msg)
        self.extensions = {}
        self.g = None
        self.generators = {}
        self.is_registered = False
        self.is_setup = False
        self.meta_processors = {}
        self.pages = {}
        self.set_generators = {}
        self.setup()
        if generator is not None:
            self.register(generator)

    def __call__(self):
        msg = "Extension {e} called".format(e=self)
        log.debug(msg)
        self.load_pages()
        msg = "Extension {e} returns {p}".format(e=self, p=self.pages)
        log.debug(msg)
        return self.pages

    def __repr__(self):
        msg = "{cls}(name={n}, generator={g}" \
              ")".format(cls=self.__class__.__name__,
                         n=self.name,
                         g=self.g)
        return msg

    def __str__(self):
        msg = "<{cls} name={n}>".format(cls=self.__class__.__name__,
                                        n=self.name)
        return msg

    def generate_context(self):
        """
        Returns a context to be passed through to templates.

        :return: :class:`dict`
        """
        return {}

    def load_pages(self):
        msg = "Extension {e} loading pages.".format(e=self)
        log.debug(msg)
        if not self.is_registered:
            msg = "Extension {ext} not yet registered. Call register() or " \
                  "init with generator.".format(ext=self)
            raise RuntimeError(msg)
        self._load_pages()
        for g in self.set_generators:
            pg = self.set_generators
            gen_pages = pg[g](app=self.g.app,
                              slug=pg[g].PAGE_CLS.SLUG,
                              generator=self)
            msg = "Extension {e} load_pages adds gen_pages " \
                  "{g}".format(e=self, g=gen_pages)
            log.debug(msg)
            for p in gen_pages:
                if p in self.pages:
                    msg = "Page {p} already present. Attempted" \
                       "duplicate by {g}".format(p=p, g=pg[g])
                    raise RuntimeError(msg)
                self.pages.update(gen_pages)

    def setup(self):
        """
        Setup extension context.

        The `_setup()` method should be overridden to setup sane defaults and
        non-standard instance variables needed for processing.

        .. warn::
            The ContentGenerator instance is not available during this call.
        """
        msg = "Setting up Extension {obj}".format(obj=self)
        log.debug(msg)
        self._setup()
        self.is_setup = True
        return self

    def register(self, generator):
        """
        Register extension to ContentGenerator.

        The `_register()` method should be overridden to add any methods to
        the ContentGenerator, such as adding custom PageGenerators to be
        processed in the generators after all pages have been added.

        .. warn::
            Any pages processed by the ContentGenerator prior to the extension
            being registered will not be processed by the extension.
        """
        if self.is_setup is False:
            msg = "Extension {obj} registration failed. Extension not setup." \
                  " Initialize with setup().".format(obj=self)
            raise RuntimeError(msg)
        self.g = generator
        msg = "Registering Extension {obj} with ContentGenerator " \
              "{g}".format(obj=self,
                           g=self.g)
        log.debug(msg)
        generator.add_extension(self)
        self._register()
        self.is_registered = True
        return self

    def _register(self):
        """
        .. see::
            :meth:`ContentGeneratorExtension.register`
        """
        pass

    def _setup(self):
        """
        This is called to setup object attributes used to instantiate
        MetaProcessors and PageGenerators to the extension.
        """
        pass

    def _process_page(self, meta, html, file_name):
        """
        Process page through extension
        """
        pass
