# chris 031815

# TODO Use `yield from` when available (Python 3?).

import json
from contextlib import closing
from urllib import urlencode
from urllib2 import urlopen
from . import util

class Error(Exception): pass
class NotFound(Error): pass

class Client(object):
  base = 'https://www.googleapis.com/youtube/v3'
  batchsize = 25

  def __init__(self,key): self.key = key

  # Utility function for making calls against YouTube API.
  def call(self,path,params):
    params = params.copy()
    params['key'] = self.key
    url = '%s/%s?%s' % (self.base,path,urlencode(params))
    with closing(urlopen(url)) as u: return json.load(u)

  # Utility function for making paginated calls.  A limit of 0 still
  # means no limit.
  def pcall(self,path,params,itemfn,limit=None):
    token = None
    params = params.copy()
    n = 0
    while True:
      if token is not None: params['pageToken'] = token
      data = self.call(path,params)
      for item in data['items']:
        x = itemfn(item)
        if x is None: continue
        yield x
        n += 1
        if n == limit: return
      if 'nextPageToken' not in data: break
      token = data['nextPageToken']

  # Return channel ID of user with the given username.
  def userchannelid(self,username):
    params = dict(part='id',forUsername=username)
    items = self.call('channels',params)['items']
    if not items: raise NotFound()
    return items[0]['id']

  # Yield channel IDs of channels to whom the channel with the given
  # channel ID is subscribed.
  def subs(self,channelid):
    params = dict(part='snippet',channelId=channelid)
    def itemfn(item):
      return item['snippet']['resourceId']['channelId']
    for x in self.pcall('subscriptions',params,itemfn): yield x

  # Yield titles for channels or playlists indicated by channel or
  # playlist IDs.  type: 'channels' or 'playlists'.  Performs batched
  # calls.
  def titles(self,type,ids):
    def call(ids):
      params = dict(part='snippet',id=','.join(ids))
      def itemfn(item):
        return item['snippet']['title']
      for x in self.pcall(type,params,itemfn): yield x
    for seg in util.segment(ids,self.batchsize):
      for x in call(seg): yield x

  # Yield YouTube video IDs of uploads made by the channel with the
  # given channel ID.
  def uploads(self,channelid,limit=None):
    params = dict(part='contentDetails',channelId=channelid)
    def itemfn(item):
      # XXX Sometimes contentDetails is not present despite having been
      # requested...
      cd = item.get('contentDetails')
      if cd is None: return None
      if 'upload' not in cd: return None
      return cd['upload']['videoId']
    for x in self.pcall('activities',params,itemfn,limit): yield x

  # Yield YouTube video IDs of videos in the playlist with the given
  # playlist ID.
  def items(self,playlistid,limit=None):
    params = dict(part='contentDetails',playlistId=playlistid)
    def itemfn(item):
      return item['contentDetails']['videoId']
    for x in self.pcall('playlistitems',params,itemfn,limit): yield x

  # type: 'channels' or 'playlists'
  def isvalid(self,type,id):
    params = dict(part='id',id=id)
    return bool(self.call(type,params)['pageInfo']['totalResults'])
