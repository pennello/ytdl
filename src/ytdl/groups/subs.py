# chris 032615

from ..subs import Sub,NotFound,AlreadyExists
from .bases import Group,Error

class Subs(Group):
  # data format: [chid,...]
  dbname = 'subs.db'

  errinval = 'invalid id (not found in youtube api call)'

  def parse(self,cmdgrp):
    descr = 'Manage subscriptions.'
    subs = cmdgrp.add_parser('subs',description=descr,help=descr)
    subs_commands = subs.add_subparsers(dest='command',metavar='command')

    descr = ('Import subscriptions from YouTube. '
      'Adds to, but does not overwrite local DB.')
    import_ = subs_commands.add_parser('import',description=descr,help=descr)
    import_.add_argument('channelid',help='channel id of user whose '
      'subscriptions to import')

    descr = ('List subscriptions. Optionally, list all seen video IDs for a '
     'given subscription.')
    ls = subs_commands.add_parser('ls',description=descr,help=descr)
    ls.add_argument('type',nargs='?',choices=Sub.types.keys(),
      help='subscription type')
    ls.add_argument('id',nargs='?',help='subscription id')

    descr = 'Add subscription. Performs validation.'
    add = subs_commands.add_parser('add',description=descr,help=descr)
    add.add_argument('type',choices=Sub.types.keys(),help='subscription type')
    add.add_argument('id',help='subscription id')

    descr = 'Remove subscription.'
    rm = subs_commands.add_parser('rm',description=descr,help=descr)
    rm.add_argument('type',choices=Sub.types.keys(),help='subscription type')
    rm.add_argument('id',help='subscription id')

    descr=('Fetch and print video IDs of latest uploads from subscriptions. '
      'Uses seen state to avoid re-printing video IDs of uploads already '
      'seen. Combined with the -s option, makes for ideal periodic input to '
      "youtube-dl. See 'cron dlsubs'.")
    latest = subs_commands.add_parser('latest',description=descr,help=descr)
    latest.add_argument('-s','--save',action='store_true',default=False,
      help='save latest video ids; defaults to %(default)s')

  def import_(self,args):
    if not self.client().isvalid(('channel',args.channelid)):
      raise Error(1,self.errinval)
    for chid in self.client().subs(args.channelid):
      self.db().add(('channel',chid))

  def ls(self,args):
    if args.type and args.id:
      sub = self.db().load((args.type,args.id))
      for vid in sub.seen:
        self.out(vid)
    else:
      for sub in self.db().loadall(): self.out(sub)

  def add(self,args):
    key = args.type,args.id
    if not self.client().isvalid(key):
      raise Error(1,self.errinval)
    try: self.db().add(key)
    except AlreadyExists:
      raise Error(1,'subscription already present')

  def rm(self,args):
    key = args.type,args.id
    try: self.db().rm(key)
    except NotFound:
      raise Error(1,'channel id not found')

  def latest(self,args):
    for vid in self.latesti(args.save): self.out(vid)

  def latesti(self,save):
    for sub in self.db().loadall():
      self.log(sub)
      for vid in sub.latest():
        self.log('new video %s' % vid)
        yield vid
      if save: self.db().save(sub)
