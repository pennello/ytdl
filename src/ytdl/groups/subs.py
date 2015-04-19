# chris 032615

'''Subscription command group.'''

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

    # Add subscription argument to parser.  opt is whether it's
    # optional.
    def addsub(p,opt):
      nargs = '?' if opt else None
      p.add_argument('type',nargs=nargs,choices=Sub.types.keys(),
        help='subscription type')
      p.add_argument('id',nargs=nargs,help='subscription id')

    descr = ('List subscriptions. Optionally, list all seen video IDs for a '
     'given subscription.')
    ls = subs_commands.add_parser('ls',description=descr,help=descr)
    addsub(ls,True)

    descr = 'Add subscription. Performs validation.'
    add = subs_commands.add_parser('add',description=descr,help=descr)
    addsub(add,False)

    descr = 'Remove subscription.'
    rm = subs_commands.add_parser('rm',description=descr,help=descr)
    addsub(rm,False)

    descr=('Fetch and print video IDs of latest uploads from subscriptions. '
      'Uses seen state to avoid re-printing video IDs of uploads already '
      'seen. Combined with the -s option, makes for ideal periodic input to '
      "youtube-dl. See 'cron dlsubs'.  Optionally, perform logic for just one "
      'subscription.')
    latest = subs_commands.add_parser('latest',description=descr,help=descr)
    latest.add_argument('-s','--save',action='store_true',default=False,
      help='save latest video ids; defaults to %(default)s')
    addsub(latest,True)

  def import_(self,args):
    '''
    Funny name for this command due to import being a language-reserved
    keyword.  See the Main.run implementation.
    '''
    if not self.client().isvalid(('channel',args.channelid)):
      raise Error(1,self.errinval)
    for chid in self.client().subs(args.channelid):
      self.db().add(('channel',chid))

  def ls(self,args):
    if args.type and args.id:
      sub = self.db().load((args.type,args.id))
      if sub.seen is not None:
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
    key = (args.type,args.id) if args.type and args.id else None
    for vid in self.latesti(args.save,key): self.out(vid)

  def latesti(self,save,key):
    '''
    Internal implementation of latest command.  save is a boolean that
    indicates whether to save newly-seen video IDs.  If key is not None,
    will yield video IDs of just the subscription designated by key.
    Otherwise, will yield latest video IDs for all subscriptions.
    '''
    def impl(sub):
      self.log(sub)
      for vid in sub.latest():
        self.log('new video %s' % vid)
        yield vid
      if save: self.db().save(sub)

    if key is not None:
      for vid in impl(self.db().load(key)): yield vid
    else:
      for sub in self.db().loadall():
        for vid in impl(sub): yield vid
