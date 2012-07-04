#!/usr/bin/env python
# coding: utf-8

import sys

_httplib = dict()


def stub(name='httplib'):
    _httplib[name] = sys.modules.get(name, None)
    sys.modules[name] = sys.modules[__name__]


def restore(name='httplib'):
    old = _httplib.pop(name)
    if old:
        sys.modules[name] = old
    else:
        del sys.modules[name]


class HTTPConnection(object):
    scheme = 'http'

    def _callback(self, path, method, body, headers):
        """To get it works properly, you need to override
        HTTPConnection._callback.  This method received the instance, the path,
        method and request body as parameter, and it has to return a tuple with
        headers dictionary and body response string.

        @param self object instance reference
        @param URL the parsed URL
        @param method the http method
        @param body the request body
        @param headers the request headers

        @return tuple containing status integer, headers dictionary and body
        response"""
        return (0, {}, '', )

    def __init__(self, host, port=None, strict=None, timeout=None,
                 source_address=None):
        self.host = host
        self.port = port
        self.strict = strict
        self.timeout = timeout
        self.source_address = source_address
        self.__response = None

    def request(self, method, url, body=None, headers=None):
        status, headers, body = self._callback(url, method, body, headers)
        self.__response = HTTPResponse('HTTP/1.1', 200, 'OK', body, headers)

    def getresponse(self):
        response = self.__response
        self.__response = None
        return response

    def set_debuglevel(self, level):
        pass

    def set_tunnel(self, host, port=None, headers=None):
        pass

    def connect(self):
        pass

    def close(self):
        pass

    def putrequest(self, request, selector, skip_host=None,
                   skip_accept_encoding=None):
        pass

    def putheader(self, *args):
        pass

    def endheaders(self):
        pass

    def send(self, data):
        pass


class HTTPSConnection(HTTPConnection):
    scheme = 'https'

    def __init__(self, host, port=None, key_file=None, cert_file=None,
                 strict=None, timeout=None, source_address=None):
        super(HTTPSConnection, self).__init__(host, port, strict, timeout,
            source_address)


class HTTPResponse(object):
    def __init__(self, version, status, reason, content, headers=()):
        self.version = version
        self.status = status
        self.reason = reason
        self.__headers = headers
        self.__content = content

    def read(self, amt=None):
        result = None
        if amt is None:
            result = self.__content
            self.__content = ''
        else:
            end = max(amt, len(self.__content))
            result = self.__content[:end]
            del self.__content[:end]
        return result

    def getheader(self, name, default=None):
        return self.__headers.get(name, default)

    def getheaders(self):
        pass
