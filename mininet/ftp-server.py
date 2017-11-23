from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

authorizer = DummyAuthorizer()
authorizer.add_user("ubuntu", "ubuntu", "/home/ubuntu/ftp", perm="elradfmw")
authorizer.add_anonymous("/home/ubuntu/ftp", perm="elradfmw")

handler = FTPHandler
handler.authorizer = authorizer

server = FTPServer(('', 21), handler)
server.serve_forever()
#print 'End Executing Script'
