import json
from pprint import pprint

search_tree_object = {}
with open('search_tree.json', 'r') as f:
    search_tree_object = json.load(f)

pprint(search_tree_object)