from app.movie_crawler_douban import DoubanMovieCrawler
from multiprocessing import Pool

import codecs
import json
import configparser

from app.movie_porter import MoviePorter


def read_movie():
    config = configparser.ConfigParser()
    config.read_file(codecs.open("app/properties.ini", "r", "utf8"))
    crawler = config['crawler']
    pages = crawler['pages'].split(',')
    current_page = pages[int(crawler['current_running'])]
    next_page_index = (int(crawler['current_running']) + 1) % len(pages)
    min_rating = float(crawler['min_rating'])
    movies = getMovieMisc(current_page, min_rating)
    crawler['current_running'] = str(next_page_index)
    with codecs.open("app/properties.ini", "wb+", "utf8") as configfile:
        config.write(configfile)
    print("start collect movie details")
    pool = Pool(4)
    movies = pool.map(getMovieDetail, movies)
    print("done")
    porter = config['porter']
    host = porter['host']
    port = int(porter['port'])
    index_name = porter['index_name']
    doc_type = porter['doc_type']
    mappings = {'mappings': {
        doc_type: json.loads(porter['mappings'])
    }}

    movie_porter = MoviePorter(host, port, index_name, doc_type, mappings)
    response = movie_porter.bulk_insert(movies)
    print(response)


def getMovieMisc(current_page, min_rating):
    crawler = DoubanMovieCrawler()
    return crawler.extract_info(current_page, min_rating)


def getMovieDetail(movie):
    crawler = DoubanMovieCrawler()
    return crawler.extract_detail(movie)


# if __name__ == '__main__':
    # movies = getMovieMisc()

read_movie()
