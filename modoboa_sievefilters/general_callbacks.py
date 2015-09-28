"""General event callbacks."""

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from modoboa.lib import events


@events.observe("UserMenuDisplay")
def menu(target, user):
    if target != "options_menu":
        return []
    if not hasattr(user, "mailbox"):
        return []
    return [
        {"name": "sievefilters",
         "label": _("Message filters"),
         "url": reverse("modoboa_sievefilters:index"),
         "img": "fa fa-filter"}
    ]


@events.observe("UserLogout")
def userlogout(request):
    from .lib import SieveClient

    if not hasattr(request.user, "mailbox"):
        return
    try:
        sc = SieveClient(user=request.user.username,
                         password=request.session["password"])
    except Exception:
        pass
    else:
        sc.logout()
