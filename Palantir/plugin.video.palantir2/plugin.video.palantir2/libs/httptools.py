# -*- coding: utf-8 -*-
from io import BytesIO

from libs.ithil import *

import gzip
import inspect
import ssl

#from StringIO import StringIO
#from threading import Lock
from decimal import Decimal


from six.moves import queue
from six.moves import urllib_parse
from six.moves.http_cookiejar import MozillaCookieJar
from six.moves.http_cookiejar import Cookie
from six.moves.html_parser import HTMLParser
from six.moves.urllib_error import HTTPError
from six.moves import urllib_request
from six.moves import http_client
from six.moves import urllib_response


cookies_lock = Lock()
cj = MozillaCookieJar()
cookies_path = os.path.join(data_path, "cookies.dat")

# Headers por defecto, si no se especifica nada
default_headers = dict()
default_headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0"
default_headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
default_headers["Accept-Language"] = "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"
default_headers["Accept-Charset"] = "UTF-8"
default_headers["Accept-Encoding"] = "gzip"
default_headers["Upgrade-Insecure-Requests"] = '1'

# No comprobar certificados
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


def get_cloudflare_headers(url):
    """
    Añade los headers para cloudflare
    :param url: Url
    :type url: str
    """
    domain_cookies = getattr(cj, '_cookies').get("." + urllib_parse.urlparse(url)[1], {}).get("/", {})

    if "cf_clearance" not in domain_cookies:
        return url

    headers = dict()
    headers["User-Agent"] = default_headers["User-Agent"]
    headers["Cookie"] = "; ".join(["%s=%s" % (c.name, c.value) for c in domain_cookies.values()])

    return url + '|%s' % '&'.join(['%s=%s' % (k, v) for k, v in headers.items()])


def load_cookies():
    """
    Carga el fichero de cookies
    """
    cookies_lock.acquire()

    if os.path.isfile(cookies_path):
        try:
            cj.load(cookies_path, ignore_discard=True)
        except Exception:
            logger("El fichero de cookies existe pero es ilegible, se borra")
            os.remove(cookies_path)

    cookies_lock.release()


def save_cookies():
    """
    Guarda las cookies
    """
    cookies_lock.acquire()
    if not os.path.exists(os.path.dirname(cookies_path)):
        os.makedirs(os.path.dirname(cookies_path))
    cj.save(cookies_path, ignore_discard=True)
    cookies_lock.release()


def get_cookies(domain):
    cookies = dict((c.name, c.value) for c in getattr(cj, '_cookies').get(domain, {}).get("/", {}).values())
    cookies.update(dict((c.name, c.value) for c in getattr(cj, '_cookies').get("." + domain, {}).get("/", {}).values()))
    return cookies


def downloadpage(url, post=None, headers=None, timeout=None, follow_redirects=True, cookies=True, replace_headers=False,
                 add_referer=False, only_headers=False, bypass_cloudflare=True, bypass_testcookie=True, no_decode=False,
                 method=None):
    """
    Descarga una página web y devuelve los resultados
    :type url: str
    :type post: dict, str
    :type headers: dict, list
    :type timeout: int
    :type follow_redirects: bool
    :type cookies: bool, dict
    :type replace_headers: bool
    :type add_referer: bool
    :type only_headers: bool
    :type bypass_cloudflare: bool
    :return: Resultado
    """
    arguments = locals().copy()

    response = {}

    # Post tipo dict
    if type(post) == dict:
        post = urllib_parse.urlencode(post)

    # Url quote
    url = urllib_parse.quote(url, safe="%/:=&?~#+!$,;'@()*[]")

    # Headers por defecto, si no se especifica nada
    request_headers = default_headers.copy()

    # Headers pasados como parametros
    if headers is not None:
        if not replace_headers:
            request_headers.update(dict(headers))
        else:
            request_headers = dict(headers)

    # Referer
    if add_referer:
        request_headers["Referer"] = "/".join(url.split("/")[:3])

    #logger("Headers:")
    #logger(request_headers, 'info')

    # Handlers
    handlers = list()
    handlers.append(HTTPHandler(debuglevel=False))
    handlers.append(HTTPSHandler(debuglevel=False))
    handlers.append(urllib_request.HTTPBasicAuthHandler())

    # No redirects
    if not follow_redirects:
        handlers.append(NoRedirectHandler())
    else:
        handlers.append(HTTPRedirectHandler())

    # Dict con cookies para la sesión
    if type(cookies) == dict:
        for name, value in cookies.items():
            if not type(value) == dict:
                value = {'value': value}
            ck = Cookie(
                version=0,
                name=name,
                value=value.get('value', ''),
                port=None,
                port_specified=False,
                domain=value.get('domain', urllib_parse.urlparse(url)[1]),
                domain_specified=False,
                domain_initial_dot=False,
                path=value.get('path', '/'),
                path_specified=True,
                secure=False,
                expires=value.get('expires', time.time() + 3600 * 24),
                discard=True,
                comment=None,
                comment_url=None,
                rest={'HttpOnly': None},
                rfc2109=False
            )
            cj.set_cookie(ck)

    if cookies:
        handlers.append(urllib_request.HTTPCookieProcessor(cj))

    # Opener
    opener = urllib_request.build_opener(*handlers)

    # Contador
    inicio = time.time()

    # Request
    req = Request(url, six.ensure_binary(post) if post else None, request_headers, method=method)

    try:
        #logger("Realizando Peticion")
        handle = opener.open(req, timeout=timeout)
        #logger('Peticion realizada')

    except HTTPError as handle:
        #logger('Peticion realizada con error')
        response["sucess"] = False
        response["code"] = handle.code
        response["error"] = handle.__dict__.get("reason", str(handle))
        response["headers"] = dict(handle.headers.items())
        response['cookies'] = get_cookies(urllib_parse.urlparse(url)[1])
        if not only_headers:
            #logger('Descargando datos...')
            response["data"] = handle.read()
        else:
            response["data"] = b""
        response["time"] = time.time() - inicio
        response["url"] = handle.geturl()

    except Exception as e:
        #logger('Peticion NO realizada')
        response["sucess"] = False
        response["code"] = e.__dict__.get("errno", e.__dict__.get("code", str(e)))
        response["error"] = e.__dict__.get("reason", str(e))
        response["headers"] = {}
        response['cookies'] = get_cookies(urllib_parse.urlparse(url)[1])
        response["data"] = b""
        response["time"] = time.time() - inicio
        response["url"] = url

    else:
        response["sucess"] = True
        response["code"] = handle.code
        response["error"] = None
        response["headers"] = dict(handle.headers.items())
        response['cookies'] = get_cookies(urllib_parse.urlparse(url)[1])
        if not only_headers:
            #logger('Descargando datos...')
            response["data"] = handle.read()
        else:
            response["data"] = b""
        response["time"] = time.time() - inicio
        response["url"] = handle.geturl()

    response['headers'] = dict([(k.lower(), v) for k, v in response['headers'].items()])

    #logger("Terminado en %.2f segundos" % (response["time"]))
    #logger("url: %s" % url)
    #logger("Response sucess     : %s" % (response["sucess"]))
    #logger("Response code       : %s" % (response["code"]))
    #logger("Response error      : %s" % (response["error"]))
    #logger("Response cookies      : %s" % (response["cookies"]))
    #logger("Response data length: %s" % (len(response["data"])))
    #logger("Response headers:")
    #logger(response['headers'])

    # Guardamos las cookies
    if cookies:
        save_cookies()

    # Gzip
    if response["headers"].get('content-encoding') == 'gzip':
        response["data"] = gzip.GzipFile(fileobj=BytesIO(response["data"])).read()

    # Binarios no se codifican ni se comprueba cloudflare, etc...
    if not is_binary(response):
        response['data'] = six.ensure_str(response['data'], errors='replace')

        if not no_decode:
            response["data"] = six.ensure_str(HTMLParser().unescape(
                six.ensure_text(response['data'], errors='replace')
            ))

        # Anti TestCookie
        if bypass_testcookie:
            if 'document.cookie="__test="+toHex(slowAES.decrypt(c,2,a,b))+"' in response['data']:
                a = re.findall('a=toNumbers\("([^"]+)"\)', response['data'])[0].decode("HEX")
                b = re.findall('b=toNumbers\("([^"]+)"\)', response['data'])[0].decode("HEX")
                c = re.findall('c=toNumbers\("([^"]+)"\)', response['data'])[0].decode("HEX")

                arguments['bypass_testcookie'] = False
                if not type(arguments['cookies']) == dict:
                    arguments['cookies'] = {'__test': ii11.new(a, ii11.MODE_CBC, b).decrypt(c).encode("HEX")}
                else:
                    arguments['cookies']['__test'] = ii11.new(a, ii11.MODE_CBC, b).decrypt(c).encode("HEX")
                response = downloadpage(**arguments).__dict__

        # Anti Cloudflare
        if bypass_cloudflare:
            response = retry_if_cloudflare(response, arguments)


    return HTTPResponse(response)

def is_binary(response):
    text_content_types = [
        'text/html',
        'application/json',
        'text/javascript'
    ]
    content_type = response['headers'].get('content-type', '')

    if 'charset' in content_type:
        charset = response['headers']['content-type'].split('=')[1]
        if charset.lower() != 'utf-8':
            response['data'] = response['data'].decode(charset, errors='replace')
        return False

    content_type = content_type.split(' ')[0]
    if content_type in text_content_types:
        return False

    if isinstance(response['data'], six.binary_type):
        try:
            response['data'].decode('utf8')
        except UnicodeDecodeError:
            return True
        else:
            return False

    if isinstance(response['data'], six.text_type):
        return False

    if '\0' not in response['data']:
        return False

    return True


def retry_if_cloudflare(response, args):
    cf = Cloudflare(response)

    if cf.is_cloudflare:
        logger("cloudflare detectado, esperando %s segundos..." % cf.wait_time)
        auth_url = cf.get_url()
        #logger("Autorizando... url: %s" % auth_url)
        auth_args = args.copy()
        auth_args['url'] = auth_url
        auth_args['follow_redirects'] = False
        auth_args['headers'] = {'Referer': args['url']}
        if not '&s=' in auth_url:
            auth_args['url'] = auth_url.split('?jschl_answer=')[0]
            auth_args['post'] = 'jschl_answer=' + auth_url.split('?jschl_answer=')[1]

        resp = downloadpage(**auth_args)
        if resp.sucess:
            logger("cloudflare: Autorización correcta, descargando página")
            args['bypass_cloudflare'] = False if [a[3] for a in inspect.stack()].count('retry_if_cloudflare') > 2 else True
            return downloadpage(**args).__dict__
        elif resp.code == 403 and resp.headers.get('cf-chl-bypass'):
            if [a[3] for a in inspect.stack()].count('retry_if_cloudflare') > 2:
                logger("cloudflare: No se ha podido autorizar. Demasiados intentos")
                return response
            #logger("Reintentando...")
            return downloadpage(**args).__dict__
        else:
            logger("cloudflare: No se ha podido autorizar")
    return response


class HTTPSHandler(urllib_request.HTTPSHandler):
    def __init__(self, *args, **kwargs):
        urllib_request.HTTPSHandler.__init__(self, *args, **kwargs)

    def https_open(self, req):
        cipher_suite = [
                "ECDHE+AESGCM",
                "ECDHE+CHACHA20",
                "DHE+AESGCM",
                "DHE+CHACHA20",
                "ECDH+AESGCM",
                "DH+AESGCM",
                "ECDH+AES",
                "DH+AES",
                "RSA+AESGCM",
                "RSA+AES",
                "!aNULL",
                "!eNULL",
                "!MD5",
                "!ECDHE+SHA",
                "!AESCCM",
                "!DHE",
                "!ARIA"
            ]

        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.set_ciphers(':'.join(cipher_suite))
        if hasattr(context, 'set_alpn_protocols'):
            context.set_alpn_protocols(['http/1.1'])
        context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)

        return self.do_open(HTTPSConnection, req,
                            context=context)


class HTTPSConnection(http_client.HTTPSConnection):
    def connect(self):
        host = self.host

        if isinstance(host, str):
            setattr(self, 'sock', self._create_connection((host, self.port), self.timeout, self.source_address))
        else:
            for h in host:
                try:
                    setattr(self, 'sock', self._create_connection((h, self.port), self.timeout, self.source_address))
                except Exception:
                    if host.index(h) == len(host) - 1:
                        raise
                else:
                    break

        if self._tunnel_host:
            server_hostname = self._tunnel_host
            self._tunnel()
        else:
            server_hostname = self.host

        setattr(self, 'sock', self._context.wrap_socket(self.sock, server_hostname=server_hostname))


class HTTPHandler(urllib_request.HTTPHandler):
    def http_open(self, req):
        return self.do_open(HTTPConnection, req)


class HTTPConnection(http_client.HTTPConnection):
    def connect(self):
        host = self.host

        if isinstance(host, str):
            setattr(self, 'sock', self._create_connection((host, self.port), self.timeout, self.source_address))
        else:
            for h in host:
                try:
                    setattr(self, 'sock', self._create_connection((h, self.port), self.timeout, self.source_address))
                except Exception:
                    if host.index(h) == len(host) - 1:
                        raise
                else:
                    break

        if self._tunnel_host:
            self._tunnel()

    def _send_request(self, *args, **kwargs):
        from collections import OrderedDict
        order = ["Host", 'User-Agent', 'Accept']
        if len(args) > 3:
            headers = args[3]
        else:
            headers = kwargs['headers']

        headers = OrderedDict([(k, v) for k, v in sorted(
            list(headers.items()),
            key=lambda head: order.index(head[0]) if head[0] in order else len(order),
        )])
        if len(args) > 3:
            args = list(args)
            args[3] = headers
        else:
            kwargs['headers'] = headers
        getattr(http_client.HTTPConnection, '_send_request')(self, *args, **kwargs)


class NoRedirectHandler(urllib_request.HTTPRedirectHandler):
    def __init__(self):
        pass

    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib_response.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl

    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302


class HTTPRedirectHandler(urllib_request.HTTPRedirectHandler):
    def __init__(self):
        pass

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if 'Authorization' in req.headers:
            req.headers.pop('Authorization')
        return urllib_request.HTTPRedirectHandler.redirect_request(self, req, fp, code, msg, headers, newurl)




class Cloudflare:
    def __init__(self, response):
        self.timeout = 5
        self.domain = urllib_parse.urlparse(response["url"])[1]
        self.protocol = urllib_parse.urlparse(response["url"])[0]
        self.response = response
        self.js_data = {}
        self.header_data = {}

        if not "var s,t,o,p,b,r,e,a,k,i,n,g,f" in response["data"] or "chk_jschl" in response["url"]:
            return

        try:
            self.js_data["auth_url"] = \
            re.compile('<form id="challenge-form" action="([^"]+)"').findall(response["data"])[0]
            self.js_data["params"] = {}
            self.js_data["params"]["jschl_vc"] = \
            re.compile('<input type="hidden" name="jschl_vc" value="([^"]+)"').findall(response["data"])[0]
            self.js_data["params"]["pass"] = \
            re.compile('<input type="hidden" name="pass" value="([^"]+)"').findall(response["data"])[0]
            try:
                self.js_data["params"]["s"] = \
                re.compile('<input type="hidden" name="s" value="([^"]+)"').findall(response["data"])[0]
            except:
                pass
            try:
                self.js_data["params"]["r"] = \
                re.compile('<input type="hidden" name="r" value="([^"]+)"').findall(response["data"])[0]
            except:
                pass
            var, self.js_data["value"] = \
            re.compile('var s,t,o,p,b,r,e,a,k,i,n,g,f[^:]+"([^"]+)":([^\n]+)};', re.DOTALL).findall(response["data"])[0]
            # ~ logger(var)
            # ~ logger(self.js_data["value"])

            # Modificar function(p){... per algun valor
            self.js_data["old_way"] = True
            if 'function(p){var p =' in response["data"]:
                var_k = re.compile("k = '([^']+)';").findall(response["data"])[0]
                k_value = re.compile(' id="%s">(.*?)</div>' % var_k).findall(response["data"])[0]
                response["data"] = re.sub('function\(p\)\{var p =.*?\}\(\)', k_value, response["data"])
                self.js_data["old_way"] = False

            if '(function(p){return' in response["data"]:
                var_num = re.compile("\(function\(p\)\{return.*?\}\((.*?)\)\)\);").findall(response["data"])[0]
                var_num = int(self.decode(var_num + '/+(+1)'))
                valor = ord(self.domain[var_num])
                response["data"] = re.sub('\(function\(p\)\{return.*?\}\(.*?\)\)\);', '(' + str(valor) + '));',
                                          response["data"])
                self.js_data["old_way"] = False

            # ~ logger(response["data"])

            self.js_data["op"] = re.compile(var + "([\+|\-|\*|\/])=([^;]+)", re.MULTILINE).findall(response["data"])
            self.js_data["wait"] = int(re.compile("\}, ([\d]+)\);", re.MULTILINE).findall(response["data"])[0]) / 1000
        except:
            logger("Metodo #1 (javascript): NO disponible")
            self.js_data = {}

        if "refresh" in response["headers"]:
            try:
                self.header_data["wait"] = int(response["headers"]["refresh"].split(";")[0])
                self.header_data["auth_url"] = response["headers"]["refresh"].split("=")[1].split("?")[0]
                self.header_data["params"] = {}
                self.header_data["params"]["pass"] = response["headers"]["refresh"].split("=")[2]
            except:
                logger("Metodo #2 (headers): NO disponible")
                self.header_data = {}

    @property
    def wait_time(self):
        if self.js_data.get("wait", 0):
            return self.js_data["wait"]
        else:
            return self.header_data.get("wait", 0)

    @property
    def is_cloudflare(self):
        # return self.response['code'] == 503 and bool(self.header_data or self.js_data)
        return self.header_data.get("wait", 0) > 0 or self.js_data.get("wait", 0) > 0


    def get_url(self):
        # Metodo #1 (javascript)
        if self.js_data.get("wait", 0):
            jschl_answer = self.decode(self.js_data["value"])
            # ~ logger(jschl_answer)

            for op, v in self.js_data["op"]:
                # ~ logger('op: %s v: %s decoded: %f' % (op, v, self.decode(v)))
                if op == '+':
                    jschl_answer = jschl_answer + self.decode(v)
                elif op == '-':
                    jschl_answer = jschl_answer - self.decode(v)
                elif op == '*':
                    jschl_answer = jschl_answer * self.decode(v)
                elif op == '/':
                    jschl_answer = jschl_answer / self.decode(v)
                # ~ logger(jschl_answer)

            if self.js_data["old_way"]:
                self.js_data["params"]["jschl_answer"] = round(jschl_answer, 10) + len(self.domain)
            else:
                self.js_data["params"]["jschl_answer"] = round(jschl_answer, 10)
            # ~ logger(jschl_answer)

            response = "%s://%s%s?%s" % (
            self.protocol, self.domain, self.js_data["auth_url"], urllib_parse.urlencode(self.js_data["params"]))
            # ~ logger(response)

            time.sleep(self.js_data["wait"])

            return response

        # Metodo #2 (headers)
        if self.header_data.get("wait", 0):
            response = "%s://%s%s?%s" % (
                self.protocol, self.domain, self.header_data["auth_url"], urllib_parse.urlencode(self.header_data["params"]))

            time.sleep(self.header_data["wait"])

            return response

    def decode(self, data):
        data = re.sub("\!\+\[\]", "1", data)
        data = re.sub("\!\!\[\]", "1", data)
        data = re.sub("\[\]", "0", data)

        pos = data.find("/")
        numerador = data[:pos]
        denominador = data[pos + 1:]

        aux = re.compile('\(([0-9\+]+)\)').findall(numerador)
        num1 = ""
        for n in aux:
            num1 += str(eval(n))

        aux = re.compile('\(([0-9\+]+)\)').findall(denominador)
        num2 = ""
        for n in aux:
            # ~ num2 += str(eval(n))
            # ~ logger(n)
            if '+' in n:
                num2 += str(eval(n))
            else:
                num2 = str(int(num2) + int(n))

        # ~ logger(num1); logger(num2)
        return Decimal(Decimal(num1) / Decimal(num2)).quantize(Decimal('.0000000000000001'))


class HTTPResponse:
    def __init__(self, response):
        self.sucess = None
        self.code = None
        self.error = None
        self.headers = None
        self.cookies = None
        self.data = None
        self.time = None
        self.url = None
        self.__dict__ = response


class Request(urllib_request.Request):
    def __init__(self, *args, **kwargs):
        if 'method' in kwargs:
            if kwargs.get('method'):
                self.method = kwargs.pop('method')
            else:
                kwargs.pop('method')

        urllib_request.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        default_method = "POST" if self.data is not None else "GET"
        return getattr(self, 'method', default_method)

