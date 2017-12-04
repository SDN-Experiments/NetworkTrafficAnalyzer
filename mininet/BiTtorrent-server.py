############
# BitTorrent server launch
############
import logging,sys,pdb,time,traceback,os
from thread import get_ident
from operator import mod

#need this prior to BT imports
import gettext
gettext.install('bittorrent', 'locale')
    
from BitTorrent.launchmanycore import LaunchMany
from BitTorrent.defaultargs import get_defaults
from BitTorrent.parseargs import parseargs, printHelp
from BitTorrent import configfile
from BitTorrent import BTFailure
from BitTorrent.bencode import bdecode

from twisted.spread import pb
from twisted.internet import reactor
from twisted.internet import threads


class DataLock:
    def __init__(self):
        if sys.platform == 'win32':
            from qt import QMutex
            self.mutex = QMutex(True)
        elif sys.platform == 'linux2 (*)':
            from Foundation import NSRecursiveLock
            self.mutex = NSRecursiveLock.alloc().init()
    def lock(self): self.mutex.lock()
    def unlock(self): self.mutex.unlock()

def downloadDir():
    ddir=None
    if sys.platform=='win32':
        ddir = os.environ.get('HOMEPATH')
        if ddir and len(ddir)>0:
            ddir = '%s%sMy home%sTorrentServer' % (ddir,os.sep,os.sep)
            if not os.path.isdir(ddir): os.makedirs(ddir)
        else: ddir='.'
    else:
        ddir = os.environ.get('HOME')
        try:
            ddir += '/home/TorrentServer'
            if not os.path.isdir(ddir): os.makedirs(ddir)
        except: ddir = os.environ.get('HOME')
    return ddir
    
    
class TorrentServer(pb.Root):
    
    torrentPort = 11989
    log = None
    tServer = None
    isProcess = True

    def __init__(self, td):
        TorrentServer.tServer = self
        self.launcher = None
        self.torrentDir = td
        self.torrentLock = DataLock()
        self.status = ''
        self.torrents = {}
        self.stoppedTorrents = {}
        self.moduloCount = 0

    def listen(self):
        from twisted.internet import reactor
        TorrentServer.log.debug('init(%s): listening '%get_ident())
        reactor.listenTCP( TorrentServer.torrentPort, pb.PBServerFactory(self))
        reactor.run()

    def remote_UpdateExecutionStatus(self, execStatus):
        self.torrentLock.lock()
        try:
            TorrentServer.log.debug('remote_UpdateExecutionStatus(%s): %s' %\
                                   (get_ident(),execStatus))
            try:
                td = self.torrentDir
                ttdd = execStatus.get('torrent_dir',td)
                self.status = execStatus.get('status','')
                self.torrents = execStatus.get('torrents',{})
                if td and ttdd!=td:
                    self.torrentDir = ttdd
                    self.status = 'restart'
                elif not td: self.torrentDir = ttdd
            except:
                traceback.print_exc()
        finally: self.torrentLock.unlock()

    def remote_ReportProgressStatus(self):
        #TorrentServer.log.debug('remote_ReportProgressStatus: ')
        self.torrentLock.lock()
        try: return {'torrents':self.torrents, 'status': self.status}
        finally: self.torrentLock.unlock()

    def initTorrent(self):
        self.torrentLock.lock()
        self.status=''
        uiname = 'btlaunchmany'
        defaults = get_defaults(uiname)
        try:
            config, args = configfile.parse_configuration_and_args(defaults, uiname, [], 0, 1)
            #config, args = configfile.parse_configuration_and_args(defaults, uiname, sys.argv[1:], 0, 1)
            config['torrent_dir'] = self.torrentDir
            config['parse_dir_interval'] = 20 #make the dir scan happen @20 seconds, not default of 60
            self.config = config
        except BTFailure, e:
            traceback.print_exc()
            TorrentServer.log.error(_("%s\nrun with no args for parameter explanations")) % str(e)
        self.torrentLock.unlock()
        if self.torrentDir: self.runTorrents()

    def runTorrents(self):
        TorrentServer.log.debug('runTorrents(%s): LaunchMany... %s'%\
                               (get_ident(), self.torrentDir))
        self.launcher = LaunchMany(self.config, self, 'btlaunchmany')
        self.launcher.run()
        TorrentServer.log.debug('runTorrents(%s): DONE with torrents...'%get_ident())
        if self.status=='quit':
            if TorrentServer.isProcess:
                reactor.stop()
                #sys.exit()
        else:
            if self.status=='restart':
                log.debug('torrentServer(): Will restart %s '%self.torrentDir)
                self.initTorrent()
            if self.torrentDir: self.runTorrents()
            
    def display(self, data):
        self.torrentLock.lock()
        try:
            if self.status == 'quit': return True
            if self.status=='restart': return True
            while self.status=='paused':
                #TorrentServer.log.debug( 'display(%s): is paused' % (get_ident()))
                self.torrentLock.unlock()
                time.sleep(1.0)
                self.torrentLock.lock()

            self.moduloCount += 1
            modulo = mod(self.moduloCount, 3)

            for xx in data:
                ( name, status, progress, peers, seeds, seedsmsg, dist,
                  uprate, dnrate, upamt, dnamt, size, t, msg ) = xx
                if status is not 'downloading':
                    pass #TorrentServer.log.debug( 'display(%s): %s: %s (%s)' % (get_ident(),status, name, progress))

                stopstatus = self.torrents.get(name)
                if stopstatus and (stopstatus[0]=='cancel' or stopstatus[0]=='stop'):
                    try: os.remove(name)
                    except: traceback.print_exc()
                    del self.torrents[name]
                else:
                    self.torrents[name] = ['progress',progress]
            del data
            return False
        finally: self.torrentLock.unlock()

    def message(self, str):
        TorrentServer.log.debug('FeedbackReporter.message(): %s'%str)

    def exception(self, str):
        TorrentServer.log.warn('FeedbackReporter: exception=%s'%str)

    def didEndTorrentThread(self,foo=None):
        TorrentServer.log.debug('didEndTorrentThread(): %s'%foo)

    def didEndTorrentThreadErr(self,foo=None):
        TorrentServer.log.debug('didEndTorrentThreadErr(): %s'%foo)



def main(args):
    if __debug__:
        level = logging.DEBUG
    else:
        level = logging.WARN

    logging.basicConfig(level=level, format='%(asctime)s %(levelname)s %(message)s')
    handler = logging.StreamHandler()
    TorrentServer.log = logging.getLogger('TorrentServer')
    TorrentServer.log.addHandler(handler)
    TorrentServer.log.propagate = 0

    TorrentServer.log.debug('torrentServer.main(): will load config')
    TorrentServer.tServer = TorrentServer(downloadDir())
    dfr = threads.deferToThread(TorrentServer.tServer.initTorrent)
    dfr.addCallback(TorrentServer.tServer.didEndTorrentThread)
    dfr.addErrback(TorrentServer.tServer.didEndTorrentThreadErr)
    
    TorrentServer.tServer.listen()

if __name__=="__main__":
    main(sys.argv)
