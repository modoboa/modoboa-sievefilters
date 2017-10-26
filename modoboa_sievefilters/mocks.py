"""Mock objects."""


class ManagesieveClientMock(object):
    """Fake managesieve client."""

    def connect(self, *args, **kwargs):
        return True

    def listscripts(self):
        return ("main_script", ["second_script"])


class IMAP4Mock(object):
    """Fake IMAP4 client."""

    def __init__(self, *args, **kwargs):
        self.untagged_responses = {}

    def _quote(self, data):
        return data

    def _simple_command(self, name, *args, **kwargs):
        if name == "CAPABILITY":
            self.untagged_responses["CAPABILITY"] = [b""]
        elif name == "LIST":
            self.untagged_responses["LIST"] = [b"() \".\" \"INBOX\""]
        return "OK", None

    def append(self, *args, **kwargs):
        pass

    def create(self, name):
        return "OK", None

    def delete(self, name):
        return "OK", None

    def list(self):
        return "OK", [b"() \".\" \"INBOX\""]

    def rename(self, oldname, newname):
        return "OK", None
