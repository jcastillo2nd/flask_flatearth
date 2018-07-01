from .. import ContentGenerator, PageGenerator
from .. import ArticlePage, ArticleListingPage, AuthorPage, AuthorListingPage
from .. import IndexPage


class ArticlePageGenerator(PageGenerator):
    PAGE_CLS = ArticlePage


class ArticleListingPageGenerator(PageGenerator):
    PAGE_CLS = ArticleListingPage


class AuthorPageGenerator(PageGenerator):
    PAGE_CLS = AuthorPage


class AuthorListingPageGenerator(PageGenerator):
    PAGE_CLS = AuthorListingPage


class IndexPageGenerator(PageGenerator):
    PAGE_CLS = IndexPage


class BasicContentGenerator(ContentGenerator):
    def _setup(self):
        article_pg = ArticlePageGenerator(self)
        self.add_page_generator('article', article_pg)

        article_sg = ArticleListingPageGenerator(self)
        self.add_set_generator('articles', article_sg)

        author_pg = AuthorPageGenerator(self)
        self.add_page_generator('author', author_pg)

        author_sg = AuthorListingPageGenerator(self)
        self.add_set_generator('authors', author_sg)

        content_pg = PageGenerator(self)
        self.add_page_generator('page', content_pg)

        index_pg = IndexPageGenerator(self)
        self.add_page_generator('index', index_pg)
