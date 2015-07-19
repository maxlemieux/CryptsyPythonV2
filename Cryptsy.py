""" Provides an interface to the Cryptsy Exchange API """

import hashlib
import hmac
import logging
import requests
import time
import urllib

logging.getLogger("requests").setLevel(logging.NOTSET)

class Cryptsy(object):

    """ API V2 """

    def __init__(self, PublicKey, PrivateKey, domain="api.cryptsy.com"):

        """ Set exchange connect values """

        self.domain = domain
        self.PublicKey = PublicKey
        self.PrivateKey = PrivateKey

    def _query(self, method, query_id=None, action=None, query=None, get_method="GET"):

        """ Basic query formation for API V2 """

        if query is None:
            query = []

        route = "/api/v2/" + method
        if query_id != None:
            route = route + "/" + str(query_id)
            if action != None:
                route = route + "/" + str(action)

        query.append(('nonce', time.time()))
        queryStr = urllib.urlencode(query)
        link = 'https://' + self.domain + route
        sign = hmac.new(self.PrivateKey.encode('utf-8'),
                        queryStr,
                        hashlib.sha512).hexdigest()
        headers = {'Sign': sign, 'Key': self.PublicKey.encode('utf-8')}

        if get_method == "PUT":
            ret = requests.put(link,
                               params=query,
                               headers=headers,
                               verify=True)
        elif get_method == "DELETE":
            ret = requests.delete(link,
                                  params=query,
                                  headers=headers,
                                  verify=True)
        elif get_method == "POST":
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
        """ Returns all active markets on the exchange """
        return self._query(method="markets")

    def market(self, query_id):
        """ Returns market information for a specific market. """
        return self._query(method="markets", query_id=query_id)

    def market_orderbook(self, query_id, limit=100, otype="both", mine=False):
        """ Returns current order book for a given market. """
        return self._query(method="markets", query_id=query_id, action="orderbook", query=[("limit", limit), ("type", otype), ("mine", mine)])

    def market_tradehistory(self, query_id, limit=100, mine=False):
        """ Returns the last x trades from the given market. """
        return self._query(method="markets", query_id=query_id, action="tradehistory", query=[("limit", limit), ("mine", mine)])

    def market_triggers(self, query_id, limit=100):
        """ Returns any triggers you have set for the given market. """
        return self._query(method="markets", query_id=query_id, action="triggers", query=[("limit", limit)])

    def market_ohlc(self, query_id, start=0, stop=time.time(), interval="minute", limit=100):
        """ Provides the OHLC for the given market. """
        intervals = ["minute", "hour", "day"]
        if interval not in intervals:
            interval = intervals[0]
        return self._query(method="markets", query_id=query_id, action="ohlc", query=[("start", start), ("stop", stop), ("interval", interval), ("limit", limit)])


    # Currencies
    def currencies(self):
        """ Returns currency information for all currencies. """
        return self._query(method="currencies")

    def currency(self, query_id):
        """ Returns currency information for a given currency. """
        return self._query(method="currencies", query_id=query_id)

    def currency_markets(self, query_id):
        """ returns possible markets for the given currency. """
        return self._query(method="currencies", query_id=query_id, action="markets")


    # User
    def balances(self, btype="all"):
        """ Returns all balance information for user """
        return self._query(method="balances", query=[("type", btype)])

    def balance(self, query_id, btype="all"):
        """ Not sure why this is here? """
        return self._query(method="balances", query_id=query_id, query=[("type", btype)])

    def deposits(self, query_id=0, limit=100):
        """ Shows all user deposits or specific currency if ID specified. """
        if query_id != 0:
            return self._query(method="deposits", query_id=query_id, query=[("limit", limit)])
        return self._query(method="deposits", query=[("limit", limit)])

    def withdrawals(self, query_id=0, limit=100):
        """ Shows all user withdrawls or specific currency if ID specified. """
        if query_id != 0:
            return self._query(method="withdrawals", query_id=query_id, query=[("limit", limit)])
        return self._query(method="withdrawals", query=[("limit", limit)])

    def addresses(self):
        """ Returns all user deposit addresses """
        return self._query(method="addresses")

    def address(self, query_id):
        """ Returns user deposit address for a specific currency """
        return self._query(method="addresses", query_id=query_id)

    def transfers(self, limit=100):
        """ Returns all user transfers """
        return self._query(method="transfers", query=[("limit", limit)])


    # Orders
    def order(self, query_id):
        """ Returns all current user orders. """
        return self._query(method="order", query_id=query_id)

    def order_create(self, marketquery_id, quantity, ordertype, price):
        """ Creates an order """
        return self._query(method="order", query=[("quantity", quantity), ("ordertype", ordertype), ("price", price), ("marketquery_id", marketquery_id)], get_method="POST")

    def order_remove(self, query_id):
        """ Removes a specific order. """
        return self._query(method="order", query_id=query_id, get_method="DELETE")


    # Triggers
    def trigger(self, query_id):
        """ Returns user triggers for a given currency. """
        return self._query(method="trigger", query_id=query_id)

    def trigger_create(self, marketquery_id, ordertype, quantity, comparison, price, orderprice, expires=''):
        """ Creates a trigger """
        return self._query(method="trigger", query=[("marketquery_id", marketquery_id), ("type", ordertype), ("quantity", quantity), ("comparison", comparison), ("price", price), ("orderprice", orderprice), ("expires", expires)], get_method="POST")

    def trigger_remove(self, query_id):
        """ Removes a trigger """
        return self._query(method="trigger", query_id=query_id, get_method="DELETE")


    # Converter
    def convert(self, query_id):
        """ Returns quote information """
        return self._query(method="converter", query_id=query_id)

    def convert_create(self, fromcurrency, tocurrency, sendingamount=0.0, receivingamount=0.0, tradekey="", feepercent=0.0):
        """ This looks a bit like you could use it for creating payments via trade keys? """
        return self._query(method="converter", query=[("fromcurrency", fromcurrency), ("tocurrency", tocurrency), ("sendingamount", sendingamount), ("receivingamount", receivingamount), ("tradekey", tradekey), ("feepercent", feepercent)], get_method="POST")
