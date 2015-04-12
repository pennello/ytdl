# chris 032515

import os.path
import sys

from ConfigParser import ConfigParser
from argparse import ArgumentParser
from collections import OrderedDict

from . import client,groups,util
from .ssl import noverify

class Main(object):
  def __init__(self,fullprog,*argv):
    self.prog = os.path.basename(fullprog)
    self.conf = self.makeconf()
    self.groups = OrderedDict(
      id  =groups.Id(self),
      subs=groups.Subs(self),
      seen=groups.Seen(self),
      clip=groups.Clip(self),
      cron=groups.Cron(self),
    )
    self.args = self.parse(argv)
    self.client = client.Client(self.key())

  def basepath(self): return os.path.expanduser('~')
  def path(self,*path): return os.path.join(self.basepath(),*path)
  def dbpath(self,*path): return self.path('var','db',self.prog,*path)
  def logpath(self,*path): return self.path('var','log',self.prog,*path)

  def confpath(self): return self.path('etc','%s.conf' % self.prog)
  def makeconf(self):
    conf = ConfigParser()
    with open(self.confpath(),'rb') as f: conf.readfp(f)
    return conf
  def key(self): return self.conf.get('auth','key')

  def parse(self,argv):
    descr = 'YouTube download manager.'
    parser = ArgumentParser(self.prog,description=descr)
    parser.add_argument('-v','--verbose',action='store_true',default=False,
      help='enable verbose logging; defaults to %(default)s')
    cmdgrp = parser.add_subparsers(dest='group',metavar='command_group')
    for group in self.groups.itervalues(): group.parse(cmdgrp)
    return parser.parse_args(argv)

  def log(self,msg):
    if self.args.verbose: util.log(msg)
  def error(self,msg): util.log('error: %s' % msg)

  def run(self):
    noverify()
    group = self.groups[self.args.group]
    if self.args.command == 'import':
      self.args.command = 'import_' # Hacky, hacky.
    command = getattr(group,self.args.command)
    try: command(self.args)
    except groups.Error,e:
      self.error(e.msg)
      return e.code
    return 0

# argv passed in from wrapper script with name of executable as first
# argument
sys.exit(Main(*sys.argv[1:]).run())
