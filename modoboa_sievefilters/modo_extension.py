# coding: utf-8
"""Declare and register the sievefilters extension."""

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy

from modoboa.core.extensions import ModoExtension, exts_pool
from modoboa.parameters import tools as param_tools

from . import __version__
from . import forms


class SieveFilters(ModoExtension):
    name = "modoboa_sievefilters"
    label = "Sieve filters"
    version = __version__
    description = ugettext_lazy("Plugin to easily create server-side filters")
    url = "sfilters"
    topredirection_url = reverse_lazy("modoboa_sievefilters:index")

    def load(self):
        param_tools.registry.add(
            "global", forms.ParametersForm, ugettext_lazy("Sieve filters"))
        param_tools.registry.add(
            "user", forms.UserSettings, ugettext_lazy("Message filters"))

exts_pool.register_extension(SieveFilters)
