"""Mock objects."""


SAMPLE_SIEVE_SCRIPT = """require ["fileinto"];

# Filter: test1
if anyof (header :contains "To" "test1") {
    fileinto "Test1";
}

# Filter: test2
if anyof (header :contains "To" "test2") {
    fileinto "Test2";
}
"""


class ManagesieveClientMock(object):
    """Fake managesieve client."""

    def __init__(self, *args, **kwargs):
        self.scripts = {
            "main_script": SAMPLE_SIEVE_SCRIPT,
            "second_script": SAMPLE_SIEVE_SCRIPT
        }

    def connect(self, *args, **kwargs):
        return True

    def capability(self):
        return """
"IMPLEMENTATION" "Example1 ManageSieved v001"
"VERSION" "1.0"
"SASL" "PLAIN SCRAM-SHA-1 GSSAPI"
"SIEVE" "fileinto vacation"
"STARTTLS"
"""

    def havespace(self, name, size):
        return True

    def listscripts(self):
        return ("main_script", ["second_script"])

    def getscript(self, name):
        return self.scripts.get(name)

    def putscript(self, name, content):
        self.scripts[name] = content
        return True

    def setactive(self, name):
        return True

    def deletescript(self, name):
        return True


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

    def list(self):
        return "OK", [b"() \".\" \"INBOX\""]
