# chris 030415

'''Cross-platform clipboard access.'''

# TODO Windows support.

__all__ = 'copy', 'paste'

class Impl(object):
  '''Base class for clipboard implementations.'''
  def copy(x): raise NotImplementedError()
  def paste(): raise NotImplementedError()
# Implementation classes should be added to this tuple.
clss = ()

class MacImpl(Impl):
  def __init__(self):
    self.AppKit = __import__('AppKit')
    self.Foundation = __import__('Foundation')
    self.pb = self.AppKit.NSPasteboard.generalPasteboard()

  def copy(self, x):
    self.pb.clearContents()
    a = self.Foundation.NSArray.arrayWithObject_(x)
    self.pb.writeObjects_(a)

  def paste(self):
    return self.pb.stringForType_(self.AppKit.NSStringPboardType)
clss += MacImpl,

# Search through implementations for ones that can be "imported".  If
# none can, raise ImportError for this module.
for cls in clss:
  try: impl = cls()
  except ImportError: pass
  else: break
else:
  raise ImportError('no implementation available')

def copy(x):
  '''Pass unicode object in to be copied to clipboard.'''
  if not isinstance(x, unicode): raise TypeError('must be unicode')
  impl.copy(x)

def paste():
  '''Return contents of clipboard; return None if empty.'''
  r = impl.paste()
  if r is None: return None
  if not isinstance(r, unicode):
    raise Exception('got non-unicode %r from implementation' % r)
  return r

if __name__ == '__main__':
  import random
  import string
  def test():
    def randu():
      return u''.join(random.sample(string.printable, 32))
    for _ in xrange(100):
      data = randu()
      impl.copy(data)
      assert data == impl.paste()
  test()
