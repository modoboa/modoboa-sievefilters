"""Custom forms."""

from __future__ import unicode_literals

from sievelib import commands
from sievelib.managesieve import SUPPORTED_AUTH_MECHS

from django import forms
from django.forms.widgets import (
    RadioFieldRenderer, RadioSelect, RadioChoiceInput)
from django.http import QueryDict
from django.utils.encoding import smart_text
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _, ugettext_lazy

from modoboa.admin.templatetags.admin_tags import gender
from modoboa.lib import form_utils
from modoboa.parameters import forms as param_forms

from .imaputils import get_imapconnector


class FiltersSetForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    active = forms.BooleanField(
        label=gender("Active", "m"), required=False,
        initial=False,
        help_text=ugettext_lazy("Check to activate this filters set")
    )


class CustomRadioInput(RadioChoiceInput):

    def __unicode__(self):
        return self.render()

    def render(self, name=None, value=None, attrs=None, choices=()):
        name = name or self.name
        value = value or self.value
        attrs = attrs or self.attrs
        if 'id' in self.attrs:
            label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        else:
            label_for = ''
        choice_label = conditional_escape(smart_text(self.choice_label))
        return mark_safe(
            u'<label%s class="radio-inline">%s %s</label>'
            % (label_for, self.tag(), choice_label)
        )


class CustomRadioFieldRenderer(RadioFieldRenderer):

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield CustomRadioInput(
                self.name, self.value, self.attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx]
        return CustomRadioInput(
            self.name, self.value, self.attrs.copy(), choice, idx)

    def render(self):
        return mark_safe(u'\n'.join([smart_text(w) for w in self]))


class CustomRadioSelect(RadioSelect):
    renderer = CustomRadioFieldRenderer


class FilterForm(forms.Form):
    """A dynamic form to edit a filter."""

    def __init__(self, conditions, actions, request, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)

        self.field_widths = {
            "match_type": 8
        }

        self.fields["name"] = forms.CharField(label=_("Name"))
        self.fields["match_type"] = forms.ChoiceField(
            choices=[("allof", _("All of the following")),
                     ("anyof", _("Any of the following")),
                     ("all", _("All messages"))],
            initial="anyof",
            widget=CustomRadioSelect()
        )

        self.header_operators = [
            ("contains", _("contains"), "string"),
            ("notcontains", _("does not contain"), "string"),
            ("is", _("is"), "string"),
            ("isnot", _("is not"), "string")
        ]

        self.cond_templates = [
            {"name": "Subject",
             "label": _("Subject"),
             "operators": self.header_operators},
            {"name": "From",
             "label": _("Sender"),
             "operators": self.header_operators},
            {"name": "To",
             "label": _("Recipient"),
             "operators": self.header_operators},
            {"name": "Cc",
             "label": _("Cc"),
             "operators": self.header_operators},
            {"name": "size", "label": _("Size"),
             "operators": [("over", _("is greater than"), "number"),
                           ("under", _("is less than"), "number")]},
        ]

        self.action_templates = [
            {"name": "fileinto", "label": _("Move message to"),
             "args": [{"type": "list", "vloader": "userfolders"}]},
            {"name": "redirect", "label": _("Redirect message to"),
             "args": [{"type": "string"}]},
            {"name": "reject", "label": _("Reject message"),
             "args": [{"type": "string"}]},
            {"name": "stop", "label": _("Stop processing")},
        ]

        self.conds_cnt = 0
        for c in conditions:
            getattr(self, "_build_%s_field" % c[0])(c[1], c[2])
        self.actions_cnt = 0
        for a in actions:
            getattr(self, "_build_%s_field" % a[0])(request, *a[1:])

    def clean_name(self):
        """Check that name does not contain strange chars."""
        if "#" in self.cleaned_data["name"]:
            raise forms.ValidationError(_("Wrong filter name"))
        return self.cleaned_data["name"]

    def _build_header_field(self, name, op, value):
        """Add a new header field to form."""
        targets = []
        ops = []
        vfield = None
        for tpl in self.cond_templates:
            targets += [(tpl["name"], tpl["label"]), ]
            if tpl["name"] != name:
                continue
            for opdef in tpl["operators"]:
                ops += [opdef[:2]]
                if op != opdef[0]:
                    continue
                if opdef[2] in ["string", "number"]:
                    vfield = forms.CharField(max_length=255, initial=value)

        self.fields["cond_target_%d" % self.conds_cnt] = \
            forms.ChoiceField(initial=name, choices=targets)
        self.fields["cond_operator_%d" % self.conds_cnt] = \
            forms.ChoiceField(initial=op, choices=ops)
        self.fields["cond_value_%d" % self.conds_cnt] = vfield
        self.conds_cnt += 1

    def _build_Subject_field(self, op, value):
        self._build_header_field("Subject", op, value)

    def _build_To_field(self, op, value):
        self._build_header_field("To", op, value)

    def _build_From_field(self, op, value):
        self._build_header_field("From", op, value)

    def _build_Cc_field(self, op, value):
        self._build_header_field("Cc", op, value)

    def _build_size_field(self, op, value):
        self._build_header_field("size", op, value)

    def _build_action_field(self, request, name, value=None):
        """Add a new action field to form."""
        actions = []
        args = None
        for tpl in self.action_templates:
            actions += [(tpl["name"], tpl["label"]), ]
            if name == tpl["name"]:
                args = tpl.get("args", [])
        self.fields["action_name_%d" % self.actions_cnt] = (
            forms.ChoiceField(initial=name, choices=actions))
        for cnt in range(0, len(args)):
            arg = args[cnt]
            aname = "action_arg_%d_%d" % (self.actions_cnt, cnt)
            if arg["type"] == "string":
                self.fields[aname] = forms.CharField(
                    max_length=255,
                    initial=value)
            elif arg["type"] == "list":
                choices = getattr(self, arg["vloader"])(request)
                self.fields[aname] = forms.ChoiceField(
                    initial=value,
                    choices=choices)
        self.actions_cnt += 1

    def _build_redirect_field(self, request, value):
        self._build_action_field(request, "redirect", value)

    def _build_reject_field(self, request, value):
        self._build_action_field(request, "reject", value)

    def _build_fileinto_field(self, request, value):
        self._build_action_field(request, "fileinto", value)

    def _build_stop_field(self, request):
        self._build_action_field(request, "stop")

    def __build_folders_list(self, folders, user, imapc, parentmb=None):
        ret = []
        for fd in folders:
            value = fd["path"] if "path" in fd else fd["name"]
            if parentmb:
                ret += [
                    (value, fd["name"].replace(
                        "%s%s" % (parentmb, imapc.hdelimiter), ""))
                ]
            else:
                ret += [(value, fd["name"])]
            if "sub" in fd:
                submboxes = imapc.getmboxes(user, value)
                ret += self.__build_folders_list(submboxes, user, imapc, value)
        return ret

    def userfolders(self, request):
        mbc = get_imapconnector(request)
        ret = mbc.getmboxes(request.user)

        folders = self.__build_folders_list(ret, request.user, mbc)
        return folders

    def tofilter(self):
        conditions = []
        actions = []
        for cpt in range(0, self.conds_cnt):
            conditions += [(self.cleaned_data["cond_target_%d" % cpt],
                            ":" + self.cleaned_data["cond_operator_%d" % cpt],
                            self.cleaned_data["cond_value_%d" % cpt])]
        for cpt in range(0, self.actions_cnt):
            naction = (self.cleaned_data["action_name_%d" % cpt],)
            argcpt = 0
            while True:
                try:
                    naction += (
                        self.cleaned_data[
                            "action_arg_%d_%d" %
                            (cpt, argcpt)],)
                except KeyError:
                    break
                argcpt += 1
            actions += [naction]

        return (conditions, actions)


def build_filter_form_from_qdict(request):
    conditions = []
    actions = []
    qdict = QueryDict("", mutable=True)
    qdict["name"] = request.POST["name"]
    qdict["match_type"] = request.POST["match_type"]
    cpt = 0
    i = 0
    if qdict["match_type"] != "all":
        while True:
            if cpt == int(request.POST["conds"]):
                break
            if "cond_target_%d" % i in request.POST:
                qdict["cond_target_%d" % cpt] = (
                    request.POST["cond_target_%d" % i]
                )
                qdict["cond_operator_%d" % cpt] = (
                    request.POST["cond_operator_%d" % i]
                )
                qdict["cond_value_%d" % cpt] = (
                    request.POST["cond_value_%d" % i])
                condtarget = request.POST["cond_target_%d" % i]
                condop = request.POST["cond_operator_%d" % i]
                condvalue = request.POST["cond_value_%d" % i]
                conditions += [(condtarget, condop, condvalue)]
                cpt += 1
            i += 1
    cpt = 0
    i = 0
    while True:
        if cpt == int(request.POST["actions"]):
            break
        if "action_name_%d" % i in request.POST:
            qdict["action_name_%d" % cpt] = request.POST["action_name_%d" % i]
            action = request.POST["action_name_%d" % i]
            argcpt = 0
            args = []
            while True:
                try:
                    qdict["action_arg_%d_%d" % (cpt, argcpt)] = \
                        request.POST["action_arg_%d_%d" % (i, argcpt)]
                    args += [request.POST["action_arg_%d_%d" % (i, argcpt)]]
                except KeyError:
                    break
                argcpt += 1
            args = [action] + args
            actions += [args]
            cpt += 1
        i += 1

    return FilterForm(conditions, actions, request, qdict)


def build_filter_form_from_filter(request, name, fobj):
    match_type = fobj["test"].name
    conditions = []
    for t in fobj["test"]["tests"]:
        if isinstance(t, commands.TrueCommand):
            match_type = "all"
            conditions += [("Subject", "contains", "")]
            break
        elif isinstance(t, commands.SizeCommand):
            conditions += [("size", t["comparator"][1:], t["limit"])]
        else:
            operator_prefix = ""
            if isinstance(t, commands.NotCommand):
                t = t["test"]
                operator_prefix = "not"
            conditions += [(
                smart_text(t["header-names"]).strip('"'),
                "{}{}".format(
                    operator_prefix, smart_text(t["match-type"])[1:]),
                smart_text(t["key-list"]).strip('"'))
            ]
    actions = []
    for c in fobj.children:
        action = (c.name,)
        for arg in c.args_definition:
            action += (c[arg["name"]].strip('"'),)
        actions += [action]

    form = FilterForm(conditions, actions, request)
    form.fields["name"].initial = name
    form.fields["match_type"].initial = match_type
    return form


def supported_auth_mechs():
    values = [('AUTO', 'auto')]
    for m in SUPPORTED_AUTH_MECHS:
        values += [(m, m.lower())]
    return values


class ParametersForm(param_forms.AdminParametersForm):
    app = "modoboa_sievefilters"

    sep1 = form_utils.SeparatorField(label=_("ManageSieve settings"))

    server = forms.CharField(
        label=_("Server address"),
        initial="127.0.0.1",
        help_text=_("Address of your MANAGESIEVE server"),
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    port = forms.IntegerField(
        label=_("Server port"),
        initial=4190,
        help_text=_("Listening port of your MANAGESIEVE server"),
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    starttls = form_utils.YesNoField(
        label=_("Connect using STARTTLS"),
        initial=False,
        help_text=_("Use the STARTTLS extension")
    )

    authentication_mech = forms.ChoiceField(
        label=_("Authentication mechanism"),
        choices=supported_auth_mechs(),
        initial="auto",
        help_text=_("Prefered authentication mechanism"),
        widget=forms.Select(attrs={"class": "form-control"})
    )

    sep2 = form_utils.SeparatorField(label=_("IMAP settings"))

    imap_server = forms.CharField(
        label=_("Server address"),
        initial="127.0.0.1",
        help_text=_("Address of your IMAP server")
    )

    imap_secured = form_utils.YesNoField(
        label=_("Use a secured connection"),
        initial=False,
        help_text=_("Use a secured connection to access IMAP server")
    )

    imap_port = forms.IntegerField(
        label=_("Server port"),
        initial=143,
        help_text=_("Listening port of your IMAP server")
    )


class UserSettings(param_forms.UserParametersForm):
    app = "modoboa_sievefilters"

    sep1 = form_utils.SeparatorField(label=_("General"))

    editor_mode = forms.ChoiceField(
        initial="gui",
        label=_("Editor mode"),
        choices=[("raw", "raw"), ("gui", "simplified")],
        help_text=_("Select the mode you want the editor to work in"),
        widget=form_utils.InlineRadioSelect(attrs={"type": "checkbox"})
    )

    sep2 = form_utils.SeparatorField(label=_("Mailboxes"))

    trash_folder = forms.CharField(
        initial="Trash",
        label=_("Trash folder"),
        help_text=_("Folder where deleted messages go")
    )

    sent_folder = forms.CharField(
        initial="Sent",
        label=_("Sent folder"),
        help_text=_("Folder where copies of sent messages go")
    )

    drafts_folder = forms.CharField(
        initial="Drafts",
        label=_("Drafts folder"),
        help_text=_("Folder where drafts go")
    )

    @staticmethod
    def has_access(**kwargs):
        return hasattr(kwargs.get("user"), "mailbox")
