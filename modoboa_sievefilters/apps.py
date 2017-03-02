"""AppConfig for stats."""

from django.apps import AppConfig


class SieveFiltersConfig(AppConfig):
    """App configuration."""

    name = "modoboa_sievefilters"
    verbose_name = "Sieve filters editor for Modoboa"

    def ready(self):
        from . import handlers
