# chris 030415 Cross-platform pasteboard access.

# TODO Windows support.

__all__ = 'copy', 'paste'

class Impl(object):
  def copy(x): raise NotImplementedError()
  def paste(): raise NotImplementedError()
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

for cls in clss:
  try: impl = cls()
  except ImportError: pass
  else: break
else:
  raise ImportError('no implementation available')

def copy(x):
  if not isinstance(x, unicode): raise TypeError('must be unicode')
  impl.copy(x)

def paste():
  r = impl.paste()
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
