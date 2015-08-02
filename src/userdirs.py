# chris 072315

'''Uesr-specific directory routines; XDG-compatible.'''

import os

# This is really all you ought to be importing from here.
__all__ = 'UserDirs',

def home():
  '''Return user's home directory.'''
  return os.path.expanduser('~')

def join(base,*a):
  '''Join base path with arbitrary additional path components.'''
  return os.path.join(base,*a)

class XdgSpecial(object):
  '''Class to represent one of the three special XDG directories.'''

  localpath = '.local'

  @classmethod
  def defaultroot(cls):
    '''
    By default, where other XDG-style directories should be rooted.  For
    example, var should go in $HOME/.local/var.
    '''
    return join(home(),cls.localpath)

  def __init__(self,name,path):
    '''
    Pass a name and the default path where the XDG-style directory
    should be storedd.  For example, 'config', and ('.config',).
    '''
    self.name,self.path = name,path

  def default(self):
    '''
    Return the full default path where this XDG-style directory should
    be found.
    '''
    return join(home(),*self.path)

class UserDirs(object):
  '''
  Instantiate a UserDirs instance in your project and call methods on it
  to get appropriate user-specific directories to use.  If the client
  system is using any of the XDG_*_HOME environment variables, they will
  be respected.  You may instantiate the UserDirs class in a strict
  mode, in which, if the XDG-style directories are not found, the
  defaults given in the specification will be used.  In non-strict mode,
  if the XDG-style directories are not found, UserDirs will favor
  placing the paths your application requests into the client's home
  directory.
  '''

  # normal path -> xdg special.  Catalog of XDG directories outlined in
  # the spec.
  _special = {
    ('share',):     XdgSpecial('data', ('.local','share')),
    ('etc',):       XdgSpecial('config',('.config',)),
    ('var','cache'):XdgSpecial('cache', ('.cache',)),
  }

  def __init__(self,xdgstrict=False):
    '''
    Pass in whether or not this UserDirs instance ought to be strict
    with respect to its behavior when XDG-style directories are not
    found.  Specifically, this has two uses.

    1. If a directory is requested that maps to an XDG directory, and
       the respective XDG_*_HOME environment variable is not found,
       then in strict mode, the XDG default will be used.

    2. If a directory is requested that does not map to an XDG
       directory, and XDG_DATA_HOME is not found, then in strict mode,
       the XDG "default" of $HOME/.local will be used as the root for
       the requested directory.

    See the dir method description for a more exhaustive description of
    the logic.
    '''
    self.xdgstrict = xdgstrict

  def _env(self,key): return os.environ.get('XDG_%s_HOME' % key.upper())

  def _root(self):
    r = self._env('share')
    if r is None:
      if self.xdgstrict: return XdgSpecial.defaultroot()
      return home()
    r = os.path.normpath(r) # Might have a trailing slash.
    r = os.path.dirname(r)
    return r

  def dir(self,*a):
    '''
    Return properly-rooted path for use by your application.  Meant to
    be used with Unix-style paths, such as dir('var','cache).

    The logic is as follows.

    If the requested path maps to an XDG-style directory, then the
    process environment will be checked to see if the respective XDG
    environment variable is set.  If so, it will be used.  If not, then
    in strict mode, the XDG default will be used.  If strict mode is not
    set, then the below logic applies.

    If the requested path does not map to an XDG-style directory, then
    the path will be joined with the root and returned.  The root is
    determined in the following manner.  If XDG_SHARE_HOME exists, then
    os.path.dirname will be applied to it and that will be the root
    value.  If not, and in strict mode, then $HOME/.local will be used.
    If not, and not in strict mode, then the user's home directory will
    be used.
    '''

    s = self._special.get(a)
    if s is not None:
      e = self._env(s.name)
      if e is not None: return e
      if self.xdgstrict: return s.default()
    return join(self._root(),*a)

  def data(self):
    '''Convenience method for XDG data home.  Uses the path 'share'.'''
    return self.dir('share')

  def config(self):
    '''Convenience method for XDG config home.  Uses the path 'etc'.'''
    return self.dir('etc')

  def cache(self):
    '''
    Convenience method for XDG cache home.  Uses the path 'var/cache'.
    '''
    return self.dir('var','cache')
