import requests
import time
import hmac,hashlib
import logging
import urllib

logging.getLogger("requests").setLevel(logging.NOTSET)

class Cryptsy:
    def __init__(self, PublicKey, PrivateKey, domain="api.cryptsy.com"):
        self.domain = domain
        self.PublicKey = PublicKey
        self.PrivateKey = PrivateKey

    def _query(self, method, query_id=None, action=None, query=[], get_method="GET"):

        route = "/api/v2/" + method
        if(query_id != None):
            route = route + "/" + str(query_id)
            if(action != None):
                route = route + "/" + str(action)

        query.append(('nonce', time.time()))
        queryStr = urllib.urlencode(query)
        link = 'https://' + self.domain + route
        sign = hmac.new(self.PrivateKey.encode('utf-8'),
                        queryStr,
                        hashlib.sha512).hexdigest()
        headers = {'Sign': sign, 'Key': self.PublicKey.encode('utf-8')}

        if(get_method == "PUT"):
            ret = requests.put(link,
                               params=query,
                               headers=headers,
                               verify=True)
        elif(get_method == "DELETE"):
            ret = requests.delete(link,
                                  params=query,
                                  headers=headers,
                                  verify=True)
        elif(get_method == "POST"):
            ret = requests.post(link,
                                params=query,
                                headers=headers,
                                verify=True)
        else:
            ret = requests.get(link,
                               params=query,
                               headers=headers,
                               verify=True)
        print ret.text
        try:
            jsonRet = ret.json()
            return jsonRet
        except ValueError:
            return {"success": False,
                    "error": {"ValueError": ["Could not load json string."]}}


    # Markets
    def markets(self):
        return self._query(method="markets")

    def market(self, query_id):
        return self._query(method="markets", query_id=query_id)

    def market_orderbook(self, query_id, limit=100, otype="both", mine=False):
        return self._query(method="markets", query_id=query_id, action="orderbook",
            query=[("limit", limit), ("type", otype), ("mine", mine)])

    def market_tradehistory(self, query_id, limit=100, mine=False):
        return self._query(method="markets", query_id=query_id, action="tradehistory",
            query=[("limit", limit), ("mine", mine)])

    def market_triggers(self, query_id, limit=100):
        return self._query(method="markets", query_id=query_id, action="triggers",
            query=[("limit", limit)])

    def market_ohlc(self, query_id, start=0, stop=time.time(),
                                            interval="minute", limit=100):
        intervals = ["minute", "hour", "day"]
        if(interval not in intervals):
            interval = intervals[0]
        return self._query(method="markets",
                           query_id=query_id,
                           action="ohlc",
                           query=[("start", start),
                                  ("stop", stop),
                                  ("interval", interval),
                                  ("limit", limit)])


    # Currencies
    def currencies(self):
        return self._query(method="currencies")

    def currency(self, query_id):
        return self._query(method="currencies", query_id=query_id)

    def currency_markets(self, query_id):
        return self._query(method="currencies", query_id=query_id, action="markets")


    # User
    def balances(self, btype="all"):
        return self._query(method="balances", query=[("type", btype)])

    def balance(self, query_id, btype="all"):
        return self._query(method="balances", query_id=query_id, query=[("type", btype)])

    def deposits(self, query_id=0, limit=100):
        if(query_id != 0):
            return self._query(method="deposits",
                               query_id=query_id,
                               query=[("limit", limit)])
        return self._query(method="deposits", query=[("limit", limit)])

    def withdrawals(self, query_id=0, limit=100):
        if(query_id != 0):
            return self._query(method="withdrawals",
                               query_id=query_id,
                               query=[("limit", limit)])
        return self._query(method="withdrawals", query=[("limit", limit)])

    def addresses(self):
        return self._query(method="addresses")

    def address(self, query_id):
        return self._query(method="addresses", query_id=query_id)

    def transfers(self, limit=100):
        return self._query(method="transfers", query=[("limit", limit)])


    # Orders
    def order(self, query_id):
        return self._query(method="order", query_id=query_id)

    def order_create(self, marketquery_id, quantity, ordertype, price):
        return self._query(method="order", query=[("quantity", quantity),
                                                    ("ordertype", ordertype),
                                                    ("price", price),
                                                    ("marketquery_id", marketquery_id)],
                                            get_method="POST")

    def order_remove(self, query_id):
        return self._query(method="order", query_id=query_id, get_method="DELETE")


    # Triggers
    def trigger(self, query_id):
        return self._query(method="trigger", query_id=query_id)

    def trigger_create(self, marketquery_id, ordertype, quantity,
                                   comparison, price, orderprice, expires=''):
        return self._query(method="trigger",
                           query=[("marketquery_id", marketquery_id),
                                  ("type", ordertype),
                                  ("quantity", quantity),
                                  ("comparison", comparison),
                                  ("price", price),
                                  ("orderprice", orderprice),
                                  ("expires", expires)],
                           get_method="POST")

    def trigger_remove(self, query_id):
        return self._query(method="trigger", query_id=query_id, get_method="DELETE")


    # Converter
    def convert(self, query_id):
        return self._query(method="converter", query_id=query_id)

    def convert_create(self, fromcurrency, tocurrency, sendingamount=0.0,
                            receivingamount=0.0, tradekey="", feepercent=0.0):
        return self._query(method="converter",
                           query=[("fromcurrency", fromcurrency),
                                  ("tocurrency", tocurrency),
                                  ("sendingamount", sendingamount),
                                  ("receivingamount", receivingamount),
                                  ("tradekey", tradekey),
                                  ("feepercent", feepercent)],
                           get_method="POST")