# chris 011915

from __future__ import absolute_import
import sys
import ssl

ver = 2,7,9

# SSL got strict in the above version of Python.  There may be a nicer
# way in the future to prevent SSL verification, or to have the trust
# chain work properly.

# http://stackoverflow.com/questions/27835619/python-error-ssl-certificate-verify-failed-apple-mac-yosemite
# https://github.com/mtschirs/quizduellapi/issues/2
# http://linux.debian.bugs.dist.narkive.com/Fa81q1tS/bug-769542-rss2email-option-for-disabling-certificate-verification

def needshack(): return sys.version_info >= ver

def noverify():
  ssl._create_default_https_context = ssl._create_unverified_context
