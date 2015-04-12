# chris 032615

import os
from .bases import DbGroup

class Seen(DbGroup):
  dbname = 'seen.db' # data format: {chid:[vid,...],...}
  lsmax = 3          # maximum number of recent videos to list
  seenmax = 100      # maximum number of seen videos per channel to store

  @classmethod
  def short(cls,vids):
    if vids is None: return ''
    el = len(vids) > cls.lsmax
    vids = ' '.join(vids[:cls.lsmax])
    if el: vids += ' ...'
    return vids

  def parse(self,cmdgrp):
    descr = 'Seen state management.'
    seen = cmdgrp.add_parser('seen',description=descr,help=descr)
    seen_commands = seen.add_subparsers(dest='command',metavar='command')
    descr = 'List seen state.'
    ls = seen_commands.add_parser('ls',description=descr,help=descr)
    ls.add_argument('chid',nargs='?',help='specific channel id')
    descr = 'Clear entirety of seen state.'
    clear = seen_commands.add_parser('clear',description=descr,help=descr)

  def saferead(self):
    seen = self.read()
    if seen is None: seen = {}
    return seen

  def ls(self,args):
    seen = self.read()
    if seen is None: return 127
    if args.chid is not None:
      vids = seen.get(args.chid)
      if vids is None: return 127
      for vid in vids: self.out(vid)
    else:
      for chid,vids in seen.iteritems():
        self.out('%s %s' % (chid,self.short(vids)))

  def clear(self,args): os.unlink(self.dbpath())
