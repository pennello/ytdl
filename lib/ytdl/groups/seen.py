# chris 032615

import os
from .bases import DbGroup

class Seen(DbGroup):
  # data format: {chid:vid,...}
  dbname = 'seen.db'

  def parse(self,cmdgrp):
    descr = 'Seen state management.'
    seen = cmdgrp.add_parser('seen',description=descr,help=descr)
    seen_commands = seen.add_subparsers(dest='command',metavar='command')
    descr = 'List seen state.'
    ls = seen_commands.add_parser('ls',description=descr,help=descr)
    descr = 'Clear entirety of seen state.'
    clear = seen_commands.add_parser('clear',description=descr,help=descr)

  def ls(self,args):
    seen = self.read()
    if seen is None: return 127
    for chid,vid in seen.iteritems():
      self.out('%s %s' % (chid,vid))

  def clear(self,args): os.unlink(self.dbpath())
