# chris 032615

import time
import subprocess
from .. import youtubedl
try: from .. import clipboard
except ImportError: clipboard = None
from .bases import Group,Error

class Clip(Group):
  # in seconds
  thresh = 10 # to start youtube-dl
  period = .2 # polling pasteboard

  patterns = (
    'youtu.be/',
    'youtube.com/watch?v=',
  )

  @classmethod
  def match(cls,x): return any(p in x for p in cls.patterns)

  def parse(self,cmdgrp):
    descr = 'Clipboard functionality. Not available on all platforms.'
    clip = cmdgrp.add_parser('clip',description=descr,help=descr)
    clip_commands = clip.add_subparsers(dest='command',metavar='command')
    descr = ('Listen for YouTube URLs, launch youtube-dl (roughly) on-demand, '
      'and download videos to current working directory.')
    listen = clip_commands.add_parser('listen',description=descr,help=descr)

  def reset(self):
    self.data = () # will store content from the pasteboard
    self.stamp = None # most recent data addition

  def popen(self, wait):
    args = youtubedl.args(self.data)
    self.out('invoking %s' % args[0])
    p = subprocess.Popen(args)
    if wait: p.wait()

  def check(self):
    return (self.stamp is not None and
      self.data and time.time() > self.stamp + self.thresh)

  def poll(self):
    x = clipboard.paste()
    if x != self.last:
      self.last = x
      if self.match(x):
        self.stamp = time.time()
        self.data += x,
        self.out('got %s' % x)
    if self.check():
      self.popen(False)
      self.reset()

  def sleep(self): time.sleep(self.period)

  # Launch youtube-dl soon after last paste, but not so soon as to
  # preclude batching a group of pastes into a single youtube-dl call.
  def listen(self,args):
    if clipboard is None:
      raise Error(1,'clipboard unavailable on this platform')
    self.reset()
    self.last = clipboard.paste()
    try:
      while True:
        self.poll()
        self.sleep()
    except KeyboardInterrupt:
      self.out() # line break after ^C on-screen
      if self.data: self.popen(True)
