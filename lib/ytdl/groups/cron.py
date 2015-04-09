# chris 040115

import os
import subprocess
from .. import youtubedl
from .bases import Group

class Cron(Group):
  def logname(self,name): return 'cron_%s.log' % name

  def parse(self,cmdgrp):
    descr = 'Cron jobs.'
    cron = cmdgrp.add_parser('cron',description=descr,help=descr)
    cron_commands = cron.add_subparsers(dest='command',metavar='command')
    logpath = self.logpath(self.logname('dlsubs'))
    descr = (
      'Change to output directory and pull in latest subscriptions, saving the '
      'seen state afterwards. Passes the latest subscriptions to youtube-dl, '
      'which is set to ignore errors. Its standard out will be logged to '
      '%r.'
    ) % logpath
    dlsubs = cron_commands.add_parser('dlsubs',description=descr,help=descr)
    dlsubs.add_argument('outdir',help='output directory')
    dlsubs.add_argument('-s','--save',action='store_true',default=False,
      help="same as '-s' option for 'subs latest'")

  def subs(self): return self.main.groups['subs']

  # Sort of like:
  # ytdl subs latest [-s] | xargs youtube-dl --no-progress
  def dlsubs(self,args):
    vids = tuple(self.subs().latesti(args.save))
    if not vids: return
    self.log('got video ids:\n%s' % '\n'.join(vids))
    os.chdir(args.outdir)
    args = youtubedl.args(('--no-progress','--') + vids)
    with self.logfile(self.logname('dlsubs')) as logfile:
      subprocess.check_call(args,stdout=logfile)
