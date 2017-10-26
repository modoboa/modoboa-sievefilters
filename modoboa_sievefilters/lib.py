# coding: utf-8

"""Internal tools."""

from __future__ import print_function

import ssl

from sievelib.factory import FiltersSet
from sievelib import managesieve
from sievelib.parser import Parser
import six

from django.utils.encoding import smart_bytes
from django.utils.translation import ugettext as _

from modoboa.lib.connections import ConnectionsManager, ConnectionError
from modoboa.lib.exceptions import ModoboaException
from modoboa.parameters import tools as param_tools


class SieveClientError(ModoboaException):
    http_code = 424


@six.add_metaclass(ConnectionsManager)
class SieveClient(object):
    """Sieve client."""

    def __init__(self, user=None, password=None):
        try:
            ret, msg = self.login(user, password)
        except managesieve.Error as e:
            raise ConnectionError(str(e))
        if not ret:
            raise ConnectionError(msg)

    def login(self, user, password):
        conf = dict(param_tools.get_global_parameters("modoboa_sievefilters"))
        self.msc = managesieve.Client(
            conf["server"], conf["port"], debug=False)
        authmech = conf["authentication_mech"]
        if authmech == "AUTO":
            authmech = None
        try:
            ret = self.msc.connect(
                smart_bytes(user), smart_bytes(password),
                starttls=conf["starttls"], authmech=authmech)
        except managesieve.Error:
            ret = False
        if not ret:
            return False, _(
                "Connection to MANAGESIEVE server failed, check your "
                "configuration"
            )
        return True, None

    def logout(self):
        self.msc.logout()
        self.msc = None

    def refresh(self, user, password):
        if self.msc is not None:
            try:
                self.msc.capability()
            except managesieve.Error as e:
                pass
            else:
                return
        try:
            ret, msg = self.login(user, password)
        except (managesieve.Error, ssl.SSLError) as e:
            raise ConnectionError(e)
        if not ret:
            raise ConnectionError(msg)

    def listscripts(self):
        return self.msc.listscripts()

    def getscript(self, name, format="raw"):
        content = self.msc.getscript(name)
        if content is None:
            raise SieveClientError(self.msc.errmsg.decode())
        if format == "raw":
            return content
        p = Parser()
        if not p.parse(content):
            print("Parse error????")
            return None
        fs = FiltersSet(name)
        fs.from_parser_result(p)
        return fs

    def pushscript(self, name, content, active=False):
        if not self.msc.havespace(name, len(content)):
            error = "%s (%s)" % (
                _("Not enough space on server"), self.msc.errmsg)
            raise SieveClientError(error)
        if not self.msc.putscript(name, content):
            raise SieveClientError(self.msc.errmsg.decode())
        if active and not self.msc.setactive(name):
            raise SieveClientError(self.msc.errmsg)

    def deletescript(self, name):
        if not self.msc.deletescript(name):
            raise SieveClientError(self.msc.errmsg.decode())

    def activatescript(self, name):
        if not self.msc.setactive(name):
            raise SieveClientError(self.msc.errmsg.decode())
