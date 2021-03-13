# -*- coding: utf-8 -*-

import sys, os ,re
import xbmc
import xbmcgui as iooiI1I11i11
import xbmcplugin
import xbmcaddon
import xbmcvfs
import base64
import hashlib
import json
import copy
import time
import zlib



from threading import Lock

from six.moves import urllib_parse
from six.moves import reload_module
from six.moves import urllib_request
from six.moves import reduce
import six
if six.PY3:
    long = int

try:
    translatePath = xbmcvfs.translatePath
except:
    translatePath =  xbmc.translatePath
addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')
localize = addon.getLocalizedString
runtime_path = translatePath(addon.getAddonInfo('Path'))
data_path = translatePath(addon.getAddonInfo('Profile'))
image_path = os.path.join(runtime_path, 'resources', 'media')

kodi_version = re.match("\d+\.\d+", xbmc.getInfoLabel('System.BuildVersion'))
kodi_version = float(kodi_version.group(0)) if kodi_version else 0.0

try:
    try:
        try:
            from Cryptodome.Cipher import AES as ii11
            #logger("Cryptodome ok")
        except:
            try:
                from Crypto.Cipher import AES as ii11
            except:
                from CryptoPy.Cipher import AES as ii11
            #logger("Crypto ok")
    except:
        from subprocess import check_call
        platform = get_system_platform()
        logger(platform)
        try:
            logger("pip: instalando paquete pycryptodome")
            check_call([sys.executable, "-m", "pip", "install", "pycryptodome"])
            logger("1")
        except:
            logger("2")
            if 'linux' in platform:
                logger("apt-get: actualizando lista de paquetes...")
                check_call(['sudo', 'apt-get', 'update'])
                logger("4")
                logger("apt-get: instalando paquete python-pycryptodome")
                check_call(['sudo', 'apt-get', 'install', '-y', 'python-pycryptodome'])
                logger("5")
            else:
                logger("3")
            logger("6")
        try:
            logger("7")
            from Cryptodome.Cipher import AES as ii11
            logger("Cryptodome ok")
        except:
            try:
                logger("8")
                from Crypto.Cipher import AES as ii11
            except:
                logger("9")
                from CryptoPy.Cipher import AES as ii11
            logger("Crypto ok")

except Exception as e:
    logger("%s: %s" % (localize(30056),e), "error")
    iooi11i1.ok(addon_name, localize(30056))
    exit()
else:
    O011 = ii11.MODE_OFB





# Clases auxiliares
class Item(object):
    defaults = {}

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __contains__(self, item):
        return item in self.__dict__

    def __getattribute__(self, item):
        return object.__getattribute__(self, item)

    def __getattr__(self, item):
        if item.startswith("__"):
            return object.__getattribute__(self, item)
        else:
            return self.defaults.get(item, '')

    def __eq__(self, other):
        return isinstance(other, Item) and self.action == other.action and self.content == other.content and \
               self.tmdb == other.tmdb and self.season == other.season and self.episode == other.episode

    def __str__(self):
        return '{%s}' % (', '.join(['\'%s\': %s' % (k, repr(self.__dict__[k])) for k in sorted(self.__dict__.keys())]))

    def getart(self):
        if 'fanart' not in self.__dict__:
            self.__dict__['fanart'] = os.path.join(runtime_path,'fanart.gif')
        d = {k:self.__dict__.get(k) for k in ['poster', 'icon', 'fanart', 'thumb'] if k in self.__dict__}
        if not d.get('thumb'):
            d['thumb'] = d.get('poster') or d.get('icon')
        if not d.get('icon'):
            d['icon'] = d.get('poster','')
        return d

    def tourl(self):
        value = self.__str__()
        if not isinstance(value, six.binary_type):
            value = six.binary_type(value, 'utf8')
        return six.ensure_str(urllib_parse.quote(base64.b64encode(value)))

    def fromurl(self, url):
        str_item = base64.b64decode(urllib_parse.unquote(url))
        self.__dict__.update(eval(str_item))
        return self

    def tojson(self, path=""):
        if path:
            open(path, "wb").write(six.ensure_binary(dump_json(self.__dict__)))
        else:
            return six.ensure_str(dump_json(self.__dict__))

    def fromjson(self, json_item=None, path=""):
        if path:
            json_item = six.ensure_str(open(path, "rb").read())

        if isinstance(json_item, dict):
            item = json_item
        else:
            item = load_json(json_item)
        self.__dict__.update(item)
        return self

    def is_label(self):
        return not self.__dict__.get('action') and not self.__dict__.get('sql')

    def clone(self, **kwargs):
        newitem = copy.deepcopy(self)
        if 'label' in newitem.__dict__:
            newitem.__dict__.pop('label')
        if 'sql' in newitem.__dict__:
            newitem.__dict__.pop('sql')
        if 'contextMenu' in newitem.__dict__:
            newitem.__dict__.pop('contextMenu')
        for k, v in kwargs.items():
            setattr(newitem, k, v)
        return newitem


class Video(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __str__(self):
        return repr(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)

    def __getattr__(self, name):
        if name.startswith("__"):
            return super(Video, self).__getattribute__(name)

        elif name == 'type':
            return self._get_type()

        elif name == 'is_mpd':
            if self.type == 'mpd':
                return True
            return False

        elif name == 'label':
            if 'label' in self.__dict__:
                return self.label
            else:
                lng = {'es': u'Castellano', 'fr': u'Frances', 'en': u'Ingles', 'ru': u'Ruso', 'de': u'Aleman'} #ISO_639-1
                label = ("%s: " % self.server) if 'server' in self.__dict__ else ''
                label += ("%s " % lng.get(self.lang, localize(30045))) if self.lang else ''
                if self.res:
                    res_num = re.findall(r'(\d+)', self.res)
                    label += "[%s]" % (res_num[0] + 'p') if res_num else self.res
                else:
                    label += ("(%s)" % self.type.upper())
                return label

        else:
            return ''

    def __deepcopy__(self, memo):
        new = Video(**self.__dict__)
        return new

    def _get_type(self):
        if self.url.startswith('rtmp'):
            return 'rtmp'
        else:
            ext = os.path.splitext(self.url.split('?')[0].split('|')[0])[1]
            if ext.startswith('.'): ext = ext[1:]
            return ext
        
    def clone(self, **kwargs):
        newvideo = copy.deepcopy(self)
        for k, v in kwargs.items():
            setattr(newvideo, k, v)
        return newvideo


# Funciones auxiliares


LOGINFO = xbmc.LOGINFO if six.PY3 else xbmc.LOGNOTICE


def logger(message, level=None):
    def format_message(data=""):
        try:
            value = str(data)
        except Exception:
            value = repr(data)

        if isinstance(value, six.binary_type):
            value = six.text_type(value, 'utf8', 'replace')


        """if isinstance(value, unicode):
            
            return [value]
        else:
            return value"""
        return value

    texto = '[%s] %s' %(xbmcaddon.Addon().getAddonInfo('id'), format_message(message))

    try:
        if level == 'info':
            xbmc.log(texto, LOGINFO)
        elif level == 'error':
            xbmc.log("######## ERROR #########", xbmc.LOGERROR)
            xbmc.log(texto, xbmc.LOGERROR)
        else:
            xbmc.log("######## DEBUG #########", LOGINFO)
            xbmc.log(texto, LOGINFO)
    except:
        #xbmc.log(six.ensure_str(texto, encoding='latin1', errors='strict'), LOGINFO) 
        xbmc.log(str([texto]), LOGINFO)


def load_json(*args, **kwargs):
    if "object_hook" not in kwargs:
        kwargs["object_hook"] = set_encoding

    try:
        value = json.loads(*args, **kwargs)
    except Exception as e:
        #logger(e)
        value = {}

    return value


def dump_json(*args, **kwargs):
    if not kwargs:
        kwargs = {
            'indent': 4,
            'skipkeys': True,
            'sort_keys': True,
            'ensure_ascii': False
        }

    try:
        value = json.dumps(*args, **kwargs)
    except Exception:
        logger.error()
        value = ''

    return value


def set_encoding(dct):
    if isinstance(dct, dict):
        return dict((set_encoding(key), set_encoding(value)) for key, value in dct.items())

    elif isinstance(dct, list):
        return [set_encoding(element) for element in dct]

    elif isinstance(dct, six.string_types):
        return six.ensure_str(dct)

    else:
        return dct


def get_setting(name, default=None):
    value = xbmcaddon.Addon().getSetting(name)

    if not value:
        return default

    elif value == 'true':
        return True

    elif value == 'false':
        return False

    else:
        try:
            value = int(value)
        except ValueError:
            try:
                value = long(value)
            except ValueError:
                try:
                    aux = load_json(value)
                    if aux: value=aux
                except ValueError:
                    pass

        return value


def set_setting(name, value):
    try:
        if isinstance(value, bool):
            if value:
                value = "true"
            else:
                value = "false"

        elif isinstance(value, (int, long)):
            value = str(value)

        elif not isinstance(value, str):
            value = dump_json(value)

        xbmcaddon.Addon().setSetting(name, value)

    except Exception as ex:
        logger("Error al convertir '%s' no se guarda el valor \n%s" % (name, ex), 'error')
        return None

    return value


def is_mpd_enabled():
    if not get_setting('MPD_hidde'):
        ret = bool(xbmc.getCondVisibility('System.HasAddon("inputstream.adaptive")'))
    else:
        ret = False
    return ret


def get_system_platform():
    xbmc.getInfoLabel('System.OSVersionInfo')
    xbmc.sleep(1000)
    OSVersionInfo = xbmc.getInfoLabel('System.OSVersionInfo')
    logger(OSVersionInfo)
    platform = "unknown"
    if xbmc.getCondVisibility('system.platform.linux') and not xbmc.getCondVisibility('system.platform.android'):
        if xbmc.getCondVisibility('system.platform.linux.raspberrypi'):
            platform = "linux raspberrypi"
        else:
            platform = "linux"
    elif xbmc.getCondVisibility('system.platform.linux') and xbmc.getCondVisibility('system.platform.android'):
        platform = "android"
    elif xbmc.getCondVisibility('system.platform.uwp'):
        platform = "uwp"
        if 'Xbox' in OSVersionInfo:
            platform = "xbox"
    elif xbmc.getCondVisibility('system.platform.windows'):
        platform = "windows"
    elif xbmc.getCondVisibility('system.platform.osx'):
        platform = "osx"
    elif xbmc.getCondVisibility('system.platform.ios'):
        platform = "ios"
    elif xbmc.getCondVisibility('system.platform.tvos'):  # Supported only on Kodi 19.x
        platform = "tvos"

    return platform


# Main
from libs import httptools
httptools.load_cookies()
reload_module(httptools)

