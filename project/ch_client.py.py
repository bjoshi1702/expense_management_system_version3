from flask import Flask
from flask import redirect
import bisect
import md5
from flask import request
import httplib
import json

application = Flask(__name__)

class ConsistentHashRing(object):
    

    def __init__(self, replicas=1):
        self.replicas = replicas
        self._keys = []
        self._nodes = {}

    def _hash(self, key):
        return long(md5.md5(key).hexdigest(), 16)

    def _repl_iterator(self, nodename):
        return (self._hash("%s:%s" % (nodename, i))
                for i in xrange(self.replicas))

    def __setitem__(self, nodename, node):
        for hash_ in self._repl_iterator(nodename):
            if hash_ in self._nodes:
                raise ValueError("Node name %r is "
                            "already present" % nodename)
            self._nodes[hash_] = node
            bisect.insort(self._keys, hash_)

    def __delitem__(self, nodename):
       

        for hash_ in self._repl_iterator(nodename):
            # will raise KeyError for nonexistent node name
            del self._nodes[hash_]
            index = bisect.bisect_left(self._keys, hash_)
            del self._keys[index]

    def __getitem__(self, key):
       
        hash_ = self._hash(key)
        start = bisect.bisect(self._keys, hash_)
        if start == len(self._keys):
            start = 0
        return self._nodes[self._keys[start]]

r = ConsistentHashRing()
r.__setitem__("node1",3000)
r.__setitem__("node2",4000)
r.__setitem__("node3",5000)

#POST request
for i in xrange(1,11):
    server_port = r.__getitem__(str(i))
    url = "localhost:" + str(server_port)
    server_connection = httplib.HTTPConnection(url)

    header = {'Content-type': 'application/json'}
    req = {
        "id": i,
        "name": "Foo 1",
        "email": "foo1@bar.com",
        "category": "office supplies",
        "description": "iPad for office use",
        "link": "http://www.apple.com/shop/buy-ipad/ipad-pro",
        "estimated_costs": "700",
        "submit_date": "12-10-2016"
    }
    json_req = json.dumps(req)
    url2 = "/v1/expenses"
    server_connection.request('POST', url2, json_req, header)
    response = server_connection.getresponse()
    print(response.read().decode())

