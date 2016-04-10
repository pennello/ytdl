# chris 041215

'''Types for and interface to subscriptions.'''

import errno
import os
from collections import defaultdict
from . import util

class Error(Exception):
  '''Base class for errors from this module.'''
  pass
class NotFound(Error):
  '''Error for when a subscription is not found.'''
  pass
class AlreadyExists(Error):
  '''Error for when a subscription already exists.'''
  pass

class Sub(object):
  '''
  Base class for subscription.

  Subclasses are expected to define lsmax: the number of seen videos to
  list.

  A subscription-individual method for getting a title is not provided
  due to the common case of wanting to fetch in bulk, and not
  one-by-one.  However, there is a bulk titles class method which
  populates the title attribute on given subscription objects.
  '''

  types = () # This is populated below, and transformed into a dict.

  @classmethod
  def type(cls):
    '''
    Return the type of the subscription, which is the class's name,
    lower-cased.
    '''
    return cls.__name__.lower()
  def key(self):
    '''Return (type,id) key tuple.'''
    return self.type(),self.id

  @classmethod
  def _popattr(cls,client,subs,apicall,attr):
    '''
    Populate a subscription attribute on given subscription objects by
    making a bulk API call.

    apicall: string specifying client method to call.

    attr: attribute to set on subscription objects.

    If a subscription object already has the specified attribute, this
    is ignored.  This may be updated in the future to avoid superfluous
    API calls.

    Note that a client is required since this is a class method.
    '''
    # First, consolidate into batches by type.
    bytype = defaultdict(list)
    for sub in subs: bytype[sub.type()].append(sub)
    for type,subs in bytype.items():
      result = getattr(client,apicall)(type,[sub.id for sub in subs])
      for sub,x in zip(subs,result): setattr(sub,attr,x)

  @classmethod
  def titles(cls,client,subs):
    '''
    Populate the title attribute on given subscription objects.

    If a subscription object already has a title attribute, this is
    ignored.  This may be updated in the future to avoid superfluous
    API calls.

    Note that a client is required since this is a class method.
    '''
    cls._popattr(client,subs,'titles','title')

  def __init__(self,client,id,seen):
    '''
    The client is supplied by the Db instance.  You never really
    construct these yourself.  Instead, get them through the load
    interfaces on the Db object.
    '''
    self.client = client
    self.id = id
    self.seen = seen

  def latest(self):
    '''
    Yield video IDs of latest subscriptions and update internal seen
    state.  Subclasses are expected to implement.
    '''
    raise NotImplementedError()

  def idview(self):
    '''
    Return string representation of the subscription that includes the
    type of the subscription, its ID, and the seen video IDs.
    '''
    def formatseen():
      if self.seen is None: return ''
      el = len(self.seen) > self.lsmax
      seen = ' '.join(self.seen[:self.lsmax])
      if el: seen += ' ...'
      return seen
    return '%s %s seen %s' % (self.type(),self.id,formatseen())

  def titleview(self):
    '''
    Return string representation of the subscription that includes the
    type of the subscription, its ID, and its title.  It is an error to
    call this without having populated the title attribute for the
    subscription with Subs.titles.
    '''
    return '%s %s title %s' % (self.type(),self.id,self.title)

class Channel(Sub):
  '''Channel subscriptions.'''
  lsmax = 3
  seenmax = 100 # Maximum number of seen videos IDs to store.

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
        newseen.append(vid)
    if newseen:
      self.seen = newseen if self.seen is None else newseen + self.seen
      self.seen = self.seen[:self.seenmax]
Sub.types += Channel,

class Playlist(Sub):
  '''Playlist subscriptions.'''
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
  '''
  Interface to subscription database.  An instance of this class will be
  made available on the Main instance.  Subscriptions are frequently
  referenced by key, which is a (type,id) tuple.
  '''

  @staticmethod
  def isjunk(id):
    '''
    Subscription IDs are stored as files on the filesystem, so if other
    junk files get into the database directories somehow, we want to
    ignore them.  (E.g., .DS_Store garbage.)
    '''
    return id.startswith('.') and 'DS_Store' in id

  def __init__(self,main): self.main = main

  def typetopath(self,type):
    '''Return path to type directory on disk.'''
    root = self.main.dbpath('subs')
    return os.path.join(root,type)
  def keytopath(self,key):
    '''Return path to subscription file on disk.'''
    return os.path.join(self.typetopath(key[0]),key[1])

  def init(self):
    '''Ensure type directory paths exist on disk.'''
    for type in Sub.types.iterkeys():
      util.makedirs(self.typetopath(type),exist_ok=True)

  def save(self,sub):
    '''Save subscription to disk.'''
    with open(self.keytopath(sub.key()),'wb') as f:
      if sub.seen: f.write('\n'.join(sub.seen) + '\n')

  def allkeys(self):
    '''Yield keys of all subscriptions found on disk.'''
    for type in Sub.types.iterkeys():
      for id in os.listdir(self.typetopath(type)):
        if self.isjunk(id): continue
        yield type,id

  def load(self,key):
    '''Load subscription specified by key.'''
    with open(self.keytopath(key),'rb') as f: data = f.read()
    data = data.strip()
    if data: data = data.split('\n')
    else: data = None
    return Sub.types[key[0]](self.main.client(),key[1],data)

  def loadall(self):
    '''
    Yield subscription instances for all subscriptions found on disk.
    '''
    for key in self.allkeys(): yield self.load(key)

  def add(self,key):
    '''Add subscription indicated by key.'''
    try: fd = os.open(self.keytopath(key),os.O_CREAT | os.O_EXCL)
    except OSError,e:
      if e.errno != errno.EEXIST: raise
      raise AlreadyExists()
    os.close(fd)

  def rm(self,key):
    '''Remove subscription indicated by key.'''
    try: os.unlink(self.keytopath(key))
    except OSError,e:
      if e.errno != errno.ENOENT: raise
      raise NotFound()
