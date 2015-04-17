# chris 041515 

'''Cross-platform notification support.'''

import json

__all__ = 'notify',

class Impl(object):
  '''Base class for notification implementations.'''
  # Make subtitle optional if needed.
  def notify(self,title,subtitle,message): raise NotImplementedError()
clss = ()

class MacImpl(Impl):
  def __init__(self): self.Foundation = __import__('Foundation')

  def notify(self,title,subtitle,message):
    # Ensure strings are properly double-quoted and escaped.
    title = json.dumps(title)
    subtitle = json.dumps(subtitle)
    message = json.dumps(message)
    src = u'display notification %s with title %s subtitle %s' % (
      message,title, subtitle)
    script = self.Foundation.NSAppleScript.alloc().initWithSource_(src)
    descriptor,error = script.executeAndReturnError_(None)
    if error is not None: raise Exception(error)
clss += MacImpl,

for cls in clss:
  try: impl = cls()
  except ImportError: pass
  else: break
else:
  raise ImportError('no implementation available')

notify = impl.notify
'''Notify user.'''

if __name__ == '__main__':
  from argparse import ArgumentParser
  parser = ArgumentParser(description='Test notifications.')
  parser.add_argument('title')
  parser.add_argument('subtitle')
  parser.add_argument('message')
  args = parser.parse_args()
  notify(args.title,args.subtitle,args.message)
