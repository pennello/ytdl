# chris 032615

'''Identity command group.'''

from .. import client
from .bases import Group,Error

class Id(Group):
  def parse(self,cmdgrp):
    descr = 'Manage channel IDs.'
    id = cmdgrp.add_parser('id',description=descr,help=descr)
    id_commands = id.add_subparsers(dest='command',metavar='command')
    descr = 'Get user channel ID.'
    get = id_commands.add_parser('get',description=descr,help=descr)
    get.add_argument('username', help='username of user whose channel id to '
      'get')

  def get(self,args):
    try: chid = self.client().userchannelid(args.username)
    except client.NotFound: raise Error(127,'user not found')
    self.out(chid)
