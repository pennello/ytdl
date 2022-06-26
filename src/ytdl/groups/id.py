# chris 032615

'''Identity command group.'''

from .. import client
from .bases import Group,Error

class Id(Group):
  def parse(self,cmdgrp):
    descr = 'Manage channel IDs.'
    id = cmdgrp.add_parser('id',description=descr,help=descr)
    id_commands = id.add_subparsers(dest='command',required=True,
      metavar='command')
    descr = 'Get user channel ID.'
    getuser = id_commands.add_parser('getuser',description=descr,help=descr)
    getuser.add_argument('name',help='username of user itse channel id to '
      'get')
    descr = 'Get video channel ID.'
    getvideo = id_commands.add_parser('getvideo',description=descr,help=descr)
    getvideo.add_argument('id',help='video id of video itse channel id to '
      'get')

  def getuser(self,args):
    try: chid = self.client().userchannelid(args.name)
    except client.NotFound: raise Error(127,'user not found')
    self.out(chid)

  def getvideo(self,args):
    try: chid = self.client().videochannelid(args.id)
    except client.NotFound: raise Error(127,'video not found')
    self.out(chid)
