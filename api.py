import json
import pprint
import yaml
from bson import json_util
from flask import request, Flask, jsonify
from pymongo import MongoClient
from elasticsearch import Elasticsearch

app = Flask(__name__)

#Hi there
@app.route('/')
def hello_world():
   return 'Hello World'

#GetData method allows for searching the database with a query
@app.route('/getdata',methods=['GET'])
def get_data():
    values = {}
    with open('config.yaml', 'r') as stream:
        try:
            values = (yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print(exc)

    query = request.args['query']
    es = Elasticsearch([values['conn']])
    # coll = get_mongo_object()
    res = es.search(index="demo", body={"query": {
                            "multi_match" : {
                            "query":    query,
                            "fields": [ "content", "author",'source','title' ]
                            }
                     }})
    pprint.pprint(res)
    return jsonify(json.loads(json_util.dumps(res))), 200

if __name__ == '__main__':
   app.run(host='0.0.0.0', port='5000')