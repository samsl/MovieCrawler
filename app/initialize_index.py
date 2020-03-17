from app.movie_porter import MoviePorter

import configparser
import json
import codecs

def initialize_movie_porter():
    config = configparser.ConfigParser()
    config.read_file(codecs.open("app/properties.ini", "r", "utf8"))
    porter = config['porter']
    host=porter['host']
    port = int(porter['port'])
    index_name = porter['index_name']
    doc_type = porter['doc_type']
    mappings = {'mappings': {
        doc_type: json.loads(porter['mappings'])
    }}
    print(mappings)
    movie_porter = MoviePorter(host, port, index_name, doc_type, mappings)
    movie_porter.create_index()
initialize_movie_porter()
