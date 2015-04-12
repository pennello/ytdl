# chris 032615

import os
from itertools import izip
from .bases import DbGroup,Error

class Subs(DbGroup):
  # data format: [chid,...]
  dbname = 'subs.db'

  errinval = 'invalid channel id (not found in youtube api call)'
  errnodb = 'subs db not found (import or add first)'

  def parse(self,cmdgrp):
    descr = 'Manage subscriptions.'
    subs = cmdgrp.add_parser('subs',description=descr,help=descr)
    subs_commands = subs.add_subparsers(dest='command',metavar='command')
    descr = 'Import subscriptions from YouTube. Overwrites local DB.'
    import_ = subs_commands.add_parser('import',description=descr,help=descr)
    import_.add_argument('channelid',help='channel id of user whose '
      'subscriptions to import')
    descr = 'Remove subscription.'
    rm = subs_commands.add_parser('rm',description=descr,help=descr)
    rm.add_argument('channelid',help='channel id to remove')
    descr = 'List subscriptions.'
    ls = subs_commands.add_parser('ls',description=descr,help=descr)
    ls.add_argument('-t','--with-titles',action='store_true',default=False,
      help='include channel titles (via api calls); defaults to %(default)s')
    descr = 'Add subscription. Performs validation.'
    add = subs_commands.add_parser('add',description=descr,help=descr)
    add.add_argument('channelid',help='channel id to add')
    descr=('Fetch and print video IDs of latest uploads from subscriptions. '
      'Uses seen state to avoid re-printing video IDs of uploads already '
      'seen. Combined with the -s option, makes for ideal periodic input to '
      "youtube-dl. See 'cron dlsubs'.")
    latest = subs_commands.add_parser('latest',description=descr,help=descr)
    latest.add_argument('-s','--save',action='store_true',default=False,
      help='save latest video ids; defaults to %(default)s')
    descr = 'Clear local subscription database.'
    clear = subs_commands.add_parser('clear',description=descr,help=descr)

  def seen(self): return self.main.groups['seen']

  def import_(self,args):
    if not self.client().isvalid('channels',args.channelid):
      raise Error(1,self.errinval)
    self.write(list(self.client().subs(args.channelid)))
  def rm(self,args):
    chids = self.read()
    if chids is None: raise Error(127,self.errnodb)
    try: chids.remove(args.channelid)
    except ValueError: raise Error(1,'channel id not already present')
    self.write(chids)
  def ls(self,args):
    chids = self.read()
    if chids is None: raise Error(127,self.errnodb)
    if args.with_titles:
      titles = self.client().titles('channels',chids)
      for chid,title in izip(chids,titles):
        self.out('%s %s' % (chid,title))
    else:
      for chid in chids: self.out(chid)
  def add(self,args):
    if not self.client().isvalid('channels',args.channelid):
      raise Error(1,self.errinval)
    chids = self.read() or []
    if args.channelid in chids:
      raise Error(1,'channel id already present')
    chids.append(args.channelid)
    self.write(chids)
  def latest(self,args):
    for vid in self.latesti(args.save):
      self.out(vid)
  def latesti(self,save):
    chids = self.read()
    if chids is None: raise Error(127,self.errnodb)
    seenmap = self.seen().saferead()

    for chid in chids:
      seen = seenmap.get(chid)
      self.log('channel %s seen %s' % (chid,self.seen().short(seen)))
      newseen = []
      for vid in self.client().uploads(chid):
        self.log('video %s' % vid)
        # If we've never seen anything from this channel before, don't
        # yield anything; instead, just populate seen list.
        if seen is None:
          newseen.append(vid)
          if len(newseen) == self.seen().seenmax: break
        else:
          if vid in seen: break
          yield vid
          self.log('new video %s' % vid)
          newseen.append(vid)
      if newseen:
        seen = newseen if seen is None else newseen + seen
        seenmap[chid] = seen[:self.seen().seenmax]

    if save:
      self.seen().write(seenmap)
  def clear(self,args): os.unlink(self.dbpath())
