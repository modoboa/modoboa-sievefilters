"""Sievefilters tests."""

from __future__ import unicode_literals

import mock

from django.core.urlresolvers import reverse

from modoboa.admin import factories as admin_factories
from modoboa.core import models as core_models
from modoboa.lib.tests import ModoTestCase

from . import mocks


class SieveFiltersTestCase(ModoTestCase):
    """Check sieve filters."""

    @classmethod
    def setUpTestData(cls):
        """Create some users."""
        super(SieveFiltersTestCase, cls).setUpTestData()
        admin_factories.populate_database()
        cls.user = core_models.User.objects.get(username="user@test.com")

    def setUp(self):
        """Connect with a simpler user."""
        patcher = mock.patch("sievelib.managesieve.Client")
        self.mock_client = patcher.start()
        self.mock_client.return_value = mocks.ManagesieveClientMock()
        self.addCleanup(patcher.stop)

        patcher = mock.patch("imaplib.IMAP4")
        self.mock_client = patcher.start()
        self.mock_client.return_value = mocks.IMAP4Mock()
        self.addCleanup(patcher.stop)

        url = reverse("core:login")
        data = {
            "username": self.user.username, "password": "toto"
        }
        self.client.post(url, data)

    def test_index(self):
        """Test index view."""
        response = self.client.get(reverse("modoboa_sievefilters:index"))
        self.assertContains(response, "main_script (active)")
