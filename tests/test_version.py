from unittest import TestCase

import flask_audit_log


class TestVersion(TestCase):

    def test_version_exists(self):
        self.assertTrue(hasattr(flask_audit_log, '__version__'))

    def test_version_type(self):
        self.assertTrue(isinstance(flask_audit_log.__version__, str))

    def test_semver(self):
        major, minor, patch = flask_audit_log.__version__.split(".")
        self.assertTrue(major.isnumeric())
        self.assertTrue(minor.isnumeric())
        self.assertTrue(patch.isnumeric())
