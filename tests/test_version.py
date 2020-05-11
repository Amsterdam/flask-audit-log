import re
from unittest import TestCase

import flask_audit_log


class TestVersion(TestCase):

    # Regex for a semver version
    _REGEX = re.compile(
        r"""
            ^
            (?P<major>0|[1-9]\d*)
            \.
            (?P<minor>0|[1-9]\d*)
            \.
            (?P<patch>0|[1-9]\d*)
            (?:-(?P<prerelease>
                (?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)
                (?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*
            ))?
            (?:\+(?P<build>
                [0-9a-zA-Z-]+
                (?:\.[0-9a-zA-Z-]+)*
            ))?
            $
        """,
        re.VERBOSE,
    )

    def test_version_exists(self):
        self.assertTrue(hasattr(flask_audit_log, '__version__'))

    def test_version_type(self):
        self.assertTrue(isinstance(flask_audit_log.__version__, str))

    def test_semver(self):
        # Check if the version is a valid semver
        print(flask_audit_log.__version__)
        version_match = self._REGEX.match(flask_audit_log.__version__)
        print(version_match)
        self.assertIsNotNone(version_match)
