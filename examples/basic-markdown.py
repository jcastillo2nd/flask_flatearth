import logging

from flask import Flask
from flask_flatearth import BASEPATH
from flask_flatearth.ext.topics import TopicExtension
from flask_flatearth.generators.markdown import MarkdownGenerator

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, template_folder=BASEPATH+'/examples/template')

app.config.update(SERVER_NAME='localhost:8080')

mdg = MarkdownGenerator(app=app, search_path=BASEPATH+'/examples/pages')

tpe = TopicExtension(generator=mdg)

mdg.generate()

app.run(host='localhost', port=8080)
