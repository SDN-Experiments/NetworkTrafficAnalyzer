from ftplib import FTP

ftp = FTP()
ftp.connect('10.0.0.50','21')
ftp.login('ubuntu','ubuntu')
#ftp.cwd('/home/ubuntu/ftp') #replace with your directory
ftp.retrlines('LIST')

def uploadFile():
 filename = 'testfile.txt' #replace with your file in your home folder
 ftp.storbinary('STOR '+filename, open(filename, 'rb'))
 ftp.quit()

def downloadFile():
 filename = 'temp.ftp' #replace with your file in the directory ('directory_name')
 localfile = open(filename, 'wb')
 ftp.retrbinary('RETR %s' % filename, localfile.write)
 ftp.quit()
 localfile.close()

#uploadFile()
downloadFile()
