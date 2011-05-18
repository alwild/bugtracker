"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

class ViewsTests(TestCase):
    def test_anonymous(self):
        response = self.client.get("/issues/search/")
        self.assertEqual(response.status_code, 200)


