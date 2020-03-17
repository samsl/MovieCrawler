import elasticsearch
from elasticsearch import helpers


class MoviePorter:
    def __init__(self, host, port, index_name, doc_type, mappings):
        self.es = elasticsearch.Elasticsearch([
            {'host': host, 'port': port}
        ])
        self.mappings = mappings
        self.index_name = index_name
        self.doc_type = doc_type


    def create_index(self):
        self.es.indices.delete(index=self.index_name, ignore_unavailable=True)
        self.es.indices.create(index=self.index_name, body=self.mappings, include_type_name=True)

    def bulk_insert(self, data):
        actions = []
        for movie in data:
            id = f'{"_".join(movie["director"])}_{movie["name"]}_{movie["year"]}'
            actions.append({
                "_index": self.index_name,
                "_type": self.doc_type,
                "_id": id,
                "_source": movie
            })
            # es.index(index=index_name, doc_type="movie", id=id, body=movie)
        helpers.bulk(self.es, actions)

    def search(self, query_body):
        print(self.es.search(index=self.index_name, body=query_body))
