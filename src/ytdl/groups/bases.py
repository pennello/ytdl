# chris 032615 Bases for command groups.

import os.path
from contextlib import contextmanager
from .. import util

class Error(Exception):
  def __init__(self,code,msg):
    super(Error,self).__init__(code,msg)
    self.code,self.msg = code,msg

class Group(object):
  def __init__(self, main): self.main = main
  def prog(self): return self.main.prog
  def parse(self,cmdgrp): raise NotImplementedError()
  def client(self): return self.main.client
  def log(self,*a): self.main.log(*a)
  def out(self,s=''): util.out(s)
  def logpath(self,name): return self.main.logpath(name)
  @contextmanager
  def logfile(self,name):
    logpath = self.logpath(name)
    util.makedirs(os.path.dirname(logpath),exist_ok=True)
    with open(logpath,'ab') as logfile: yield logfile
  def db(self): return self.main.db
