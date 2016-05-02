# coding: utf-8
"""Declare and register the sievefilters extension."""

from django.utils.translation import ugettext_lazy

from modoboa.core.extensions import ModoExtension, exts_pool
from modoboa.lib import parameters

from . import __version__


class SieveFilters(ModoExtension):
    name = "modoboa_sievefilters"
    label = "Sieve filters"
    version = __version__
    description = ugettext_lazy("Plugin to easily create server-side filters")
    url = "sfilters"
    available_for_topredirection = True

    def load(self):
        from .app_settings import ParametersForm, UserSettings
        parameters.register(ParametersForm, ugettext_lazy("Sieve filters"))
        parameters.register(UserSettings, ugettext_lazy("Message filters"))
        from . import general_callbacks

exts_pool.register_extension(SieveFilters)
