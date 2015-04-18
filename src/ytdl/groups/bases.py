# chris 032615

'''Base classes for command groups.'''

import os.path
from contextlib import contextmanager
from .. import util
# Convenience import for command groups.
from ..error import Error

class Group(object):
  '''
  Base class for command groups.

  Command group classes inherit from this class and implement commands
  as methods.  There may be other methods as well, in addition.
  '''
  def __init__(self, main): self.main = main
  def prog(self):
    '''Return program name from Main instance.'''
    return self.main.prog
  def parse(self,cmdgrp):
    '''
    Expected to be implemented by subclasses.  The command group parser
    object from the Main instance is passed in, and the command group
    implementation is expected to add its commands, arguments, etc. to
    it.
    '''
    raise NotImplementedError()
  def client(self):
    '''Return client instance form Main instance.'''
    return self.main.client()
  def log(self,*a):
    '''Call log method on Main instance.'''
    self.main.log(*a)
  def out(self,s=''):
    '''Output to standard out.'''
    util.out(s)
  def logpath(self,name):
    '''Given a name, prints full path to log file.'''
    return self.main.logpath(name)
  @contextmanager
  def logfile(self,name):
    '''Context manager for log file.  See logpath.'''
    logpath = self.logpath(name)
    util.makedirs(os.path.dirname(logpath),exist_ok=True)
    with open(logpath,'ab') as logfile: yield logfile
  def db(self):
    '''Return subscriptions database interface from Main instance.'''
    return self.main.db
