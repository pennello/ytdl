# chris 032515

'''
Package-relative entry point.

An instance of Main is constructed by __main__ (in the parent
directory), and its run method is invoked.
'''

import errno
import os.path

from ConfigParser import ConfigParser
from argparse import ArgumentParser
from collections import OrderedDict

from . import client,groups,ssl,util
from .error import Error
from .subs import Db

class Main(object):
  '''
  A single instance of the Main class serves as a context for the
  application.  When constructed, it loads the configuration, constructs
  and initializes an instance of the subscription database interface,
  constructs the command group interfaces, kicks off the command-line
  parsing, and constructs an instance of the YouTube API client.

  Its run method locates and runs the command specified on the
  command-line.
  '''

  def __init__(self,prog,*argv):
    self.prog = os.path.basename(prog)
    self.conf = self.makeconf()
    self.db = Db(self)
    self.db.init()
    self.groups = OrderedDict(
      id  =groups.Id(self),
      subs=groups.Subs(self),
      clip=groups.Clip(self),
      cron=groups.Cron(self),
    )
    self.args = self.parse(argv)

  def basepath(self):
    '''
    Base path used by all other runtime paths.  Uses user's home
    directory.
    '''
    return os.path.expanduser('~')
  def path(self,*path):
    '''Return path joined with base path.'''
    return os.path.join(self.basepath(),*path)
  def dbpath(self,*path):
    '''Return path joined with namespaced db path.'''
    return self.path('var','db',self.prog,*path)
  def logpath(self,*path):
    '''Return path joined with namespaced log path.'''
    return self.path('var','log',self.prog,*path)

  def confpath(self):
    '''Return config path.'''
    return self.path('etc','%s.conf' % self.prog)
  def makeconf(self):
    '''
    Make and return ConfigParser instance with parsed configuration
    information from the config file.  Return None if no config found.
    '''
    conf = ConfigParser()
    try:
      with open(self.confpath(),'rb') as f:
        conf.readfp(f)
    except IOError,e:
      if e.errno != errno.ENOENT: raise
      return None
    return conf
  def key(self):
    '''Return auth key from config.  Return None if no config.'''
    if self.conf is None: return None
    return self.conf.get('auth','key')

  def client(self):
    '''
    Dynamically construct client instance from auth key.  Error if no
    key available.
    '''
    key = self.key()
    if key is None: raise Error(3,'no api key (set up conf first)')
    return client.Client(key)

  def parse(self,argv):
    '''
    Parse command-line arguments.  Relies on command groups to add their
    own commands to the main command group subparser.
    '''
    descr = 'YouTube download manager.'
    parser = ArgumentParser(self.prog,description=descr)
    parser.add_argument('-v','--verbose',action='store_true',default=False,
      help='enable verbose logging to standard error')
    cmdgrp = parser.add_subparsers(dest='group',metavar='command_group')
    for group in self.groups.itervalues(): group.parse(cmdgrp)
    return parser.parse_args(argv)

  def log(self,x):
    '''Log object to standard error if verbose mode is enabled.'''
    if self.args.verbose: util.log(x)
  def error(self,x):
    '''Log object to standard error with error prefix.'''
    util.log('error: %s' % x)

  def run(self):
    '''Locate and runs the command specified on the command-line.'''
    if ssl.needshack(): ssl.noverify()
    group = self.groups[self.args.group]
    if self.args.command == 'import':
      self.args.command = 'import_' # Hacky, hacky.
    command = getattr(group,self.args.command)
    try: command(self.args)
    except Error,e:
      self.error(e.msg)
      return e.code
    except KeyboardInterrupt:
      self.error('caught interrupt')
      return 1
    return 0
