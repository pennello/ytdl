# chris 41815

'''Error class for commands to raise.'''

class Error(Exception):
  '''
  Error class for commands to raise.  The Main instance will catch this
  error, output the message to standard error, and exit the process with
  the specified exit code.
  '''
  def __init__(self,code,msg):
    super(Error,self).__init__(code,msg)
    self.code,self.msg = code,msg
