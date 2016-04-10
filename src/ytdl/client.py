# chris 031815

'''Simple YouTube API (v3) client.'''

# TODO Use `yield from` when available (Python 3?).

import json
import urllib2
from contextlib import closing
from urllib import urlencode
from . import util

class Error(Exception):
  '''Base class for API errors.'''
  pass
class NotFound(Error):
  '''Error for when an entitty is not found.'''
  pass

class Client(object):
  apibase = 'https://www.googleapis.com/youtube/v3'
  # Batch size when making batched calls.
  batchsize = 25

  def __init__(self,key):
    '''
    Pass in an application server key, created on the Google developers
    console.
    '''
    self.key = key

  def call(self,path,params):
    '''Utility function for making calls against YouTube API.'''
    params = params.copy()
    params['key'] = self.key
    url = '%s/%s?%s' % (self.apibase,path,urlencode(params))
    try:
      with closing(urllib2.urlopen(url)) as u:
        return json.load(u)
    except urllib2.HTTPError,e:
      try: util.log('client call http error; body: %r' % e.read())
      except Exception: pass
      raise

  def pcall(self,path,params,itemfn):
    '''Utility function for making paginated calls.'''
    token = None
    params = params.copy()
    while True:
      if token is not None: params['pageToken'] = token
      data = self.call(path,params)
      for item in data['items']:
        x = itemfn(item)
        if x is None: continue
        yield x
      if 'nextPageToken' not in data: break
      token = data['nextPageToken']

  def userchannelid(self,username):
    '''Return channel ID of user with the given username.'''
    params = dict(part='id',forUsername=username)
    items = self.call('channels',params)['items']
    if not items: raise NotFound()
    return items[0]['id']

  def videochannelid(self,videoid):
    '''Return channel ID of video with the given ID.'''
    params = dict(part='id,snippet',id=videoid)
    items = self.call('videos',params)['items']
    if not items: raise NotFound()
    return items[0]['snippet']['channelId']

  def subs(self,channelid):
    '''
    Yield channel IDs of channels to whom the channel with the given
    channel ID is subscribed.
    '''
    params = dict(part='snippet',channelId=channelid)
    def itemfn(item):
      return item['snippet']['resourceId']['channelId']
    for x in self.pcall('subscriptions',params,itemfn): yield x

  def titles(self,type,ids,safe=False):
    '''
    Yield titles for channels, playlists, or videos, indicated by
    channel, playlist, or video IDs.  type: 'channel', 'playlist', or
    'video'.  Performs batched calls.

    safe: whether to throw an exception or not if an entity is not
    found.
    '''
    # The YouTube API gives us back items potentially out-of-order from
    # what we requested, so we have to rectify the ordering ourselves.
    def call(ids):
      params = dict(part='snippet',id=','.join(ids))
      def itemfn(item):
        return item['id'],item['snippet']['title']
      for x in self.pcall(type + 's',params,itemfn): yield x
    for seg in util.segment(ids,self.batchsize):
      titles = {id:title for id,title in call(seg)}
      for id in seg:
        if id in titles: yield titles[id]
        else:
          if safe:
            msg = ('--(title error) entity %s %s '
              'not found in API call--') % (type,id)
            yield msg
          else: raise NotFound(type,id)

  def uploads(self,channelid):
    '''
    Yield YouTube video IDs of uploads made by the channel with the
    given channel ID.
    '''
    params = dict(part='contentDetails',channelId=channelid)
    def itemfn(item):
      # XXX Sometimes contentDetails is not present despite having been
      # requested...
      cd = item.get('contentDetails')
      if cd is None: return None
      if 'upload' not in cd: return None
      return cd['upload']['videoId']
    for x in self.pcall('activities',params,itemfn): yield x

  def items(self,playlistid):
    '''
    Yield YouTube video IDs of videos in the playlist with the given
    playlist ID.
    '''
    params = dict(part='contentDetails',playlistId=playlistid)
    def itemfn(item):
      return item['contentDetails']['videoId']
    for x in self.pcall('playlistItems',params,itemfn): yield x

  def isvalid(self,(type,id)):
    '''
    Return whether specified object is valid.  type: 'channel' or
    'playlist'.
    '''
    params = dict(part='id',id=id)
    return bool(self.call(type + 's',params)['pageInfo']['totalResults'])
