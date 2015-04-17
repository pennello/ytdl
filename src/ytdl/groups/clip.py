# chris 032615

'''Clipboard command group.

Attempts to import clipboard and notify modules.  If imports fail, the
functionality is not available.  If clipboard functionality is not
available, clip listen command will not work.  If notification
functionality is not available, then just output user notifications to
standard out instead of both that as well as OS notifications.
'''

import time
import subprocess
try: from .. import clipboard
except ImportError: clipboard = None
try: from ..notify import notify
except ImportError: notify = None
from .. import youtubedl
from .bases import Group,Error

class Clip(Group):
  # These are in seconds.
  thresh = 10 # Minimum time after which to start youtube-dl.
  period = .2 # Period with which to poll clipboard.

  patterns = (
    'youtu.be/',
    'youtube.com/watch?v=',
  )

  @classmethod
  def match(cls,x):
    '''Check whether given string matches any of the pattern strings.'''
    return any(p in x for p in cls.patterns)

  def parse(self,cmdgrp):
    descr = 'Clipboard functionality. Not available on all platforms.'
    clip = cmdgrp.add_parser('clip',description=descr,help=descr)
    clip_commands = clip.add_subparsers(dest='command',metavar='command')
    descr = ('Listen for YouTube URLs, launch youtube-dl (roughly) on-demand, '
      'and download videos to current working directory.  If available, will '
      'trigger OS graphical notifications when new URLs are found and when '
      'youtube-dl is invoked.')
    listen = clip_commands.add_parser('listen',description=descr,help=descr)

  def reset(self):
    '''Reset internal state after launching youtube-dl.'''
    self.data = ()    # Will store content from the clipboard.
    self.stamp = None # Time of the most recent data addition.

  def notify(self,msg):
    '''
    Notify user with message via both OS notifications, if available, as
    well as standard out.
    '''
    if notify is not None: notify(self.prog(),'clip listen',msg)
    self.out(msg)

  def popen(self, wait):
    '''Launch youtube-dl.'''
    args = youtubedl.args(self.data)
    self.notify('invoking %s' % args[0])
    p = subprocess.Popen(args)
    if wait: p.wait()

  def check(self):
    '''Return whether we should launch youtube-dl.'''
    return (self.stamp is not None and
      self.data and time.time() > self.stamp + self.thresh)

  def poll(self):
    '''Poll clipboard for new data, potentially launch youtube-dl.'''
    x = clipboard.paste()
    if x != self.last:
      self.last = x
      if self.match(x):
        self.stamp = time.time()
        self.data += x,
        self.notify('got %s' % x)
    if self.check():
      self.popen(False)
      self.reset()

  def sleep(self):
    '''Sleep for the period.'''
    time.sleep(self.period)

  def listen(self,args):
    '''
    Launch youtube-dl soon after last paste, but not so soon as to
    preclude batching a group of pastes into a single youtube-dl call.
    '''
    if clipboard is None:
      raise Error(1,'clipboard unavailable on this platform')
    self.reset()
    self.last = clipboard.paste()
    try:
      while True:
        self.poll()
        self.sleep()
    except KeyboardInterrupt:
      self.out() # Make line break after ^C on-screen.
      if self.data: self.popen(True)
