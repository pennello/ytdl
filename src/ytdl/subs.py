# chris 041215 Types for and interface to subscriptions.

import errno
import os
from . import util

class Error(Exception): pass
class NotFound(Error): pass
class AlreadyExists(Error): pass

class Sub(object):
  types = () # populated below, transformed into dict

  # subclasses are expected to define lsmax: the number of seen videos
  # to list

  @classmethod
  def type(cls): return cls.__name__.lower()
  def key(self): return self.type(),self.id

  def __init__(self,client,id,seen):
    self.client = client
    self.id = id
    self.seen = seen

  def latest(self): raise NotImplementedError()

  def __str__(self):
    def formatseen():
      if self.seen is None: return ''
      el = len(self.seen) > self.lsmax
      seen = ' '.join(self.seen[:self.lsmax])
      if el: seen += ' ...'
      return seen
    return '%s %s seen %s' % (self.type(),self.id,formatseen())

class Channel(Sub):
  lsmax = 3
  seenmax = 100

  def latest(self):
    newseen = []
    for vid in self.client.uploads(self.id):
      # If we've never seen anything from this channel before, don't
      # yield anything; instead, just populate seen list.
      if self.seen is None:
        newseen.append(vid)
        if len(newseen) == self.seenmax: break
      else:
        if vid in self.seen: break
        yield vid
        #self.log('new video %s' % vid)
        newseen.append(vid)
      if newseen:
        self.seen = newseen if self.seen is None else newseen + self.seen
        self.seen = self.seen[:self.seenmax]
Sub.types += Channel,

class Playlist(Sub):
  lsmax = 2

  def latest(self):
    newseen = list(self.client.items(self.id))
    if not newseen: return
    if self.seen:
      for vid in set(newseen) - set(self.seen): yield vid
    self.seen = newseen
Sub.types += Playlist,

Sub.types = dict((cls.type(),cls) for cls in Sub.types)

class Db(object):
  def __init__(self,main): self.main = main

  def typetopath(self,type):
    root = self.main.dbpath('subs')
    return os.path.join(root,type)
  def keytopath(self,key):
    return os.path.join(self.typetopath(key[0]),key[1])

  def init(self):
    for type in Sub.types.iterkeys():
      util.makedirs(self.typetopath(type),exist_ok=True)

  def save(self,sub):
    with open(self.keytopath(sub.key()),'wb') as f:
      if sub.seen: f.write('\n'.join(sub.seen) + '\n')

  def allkeys(self):
    for type in Sub.types.iterkeys():
      for id in os.listdir(self.typetopath(type)):
        # ignore junk
        if id.startswith('.') and 'DS_Store' in id: continue
        yield type,id

  def load(self,key):
    with open(self.keytopath(key),'rb') as f: data = f.read()
    data = data.strip()
    if data: data = data.split('\n')
    else: data = None
    return Sub.types[key[0]](self.main.client,key[1],data)

  def loadall(self):
    for key in self.allkeys(): yield self.load(key)

  def add(self,key):
    try: fd = os.open(self.keytopath(key),os.O_CREAT | os.O_EXCL)
    except OSError,e:
      if e.errno != errno.EEXIST: raise
      raise AlreadyExists()
    os.close(fd)

  def rm(self,key):
    try: os.unlink(self.keytopath(key))
    except OSError,e:
      if e.errno != errno.ENOENT: raise
      raise NotFound()
