import Queue
import threading
import subprocess
import shutil
import os

class FileSyncer(threading.Thread):
    def __init__(self, fileQueue):
        threading.Thread.__init__(self)
        self.fileQueue = fileQueue
        print 'FileSyncer ready to rock.'
        
    def run(self):
        self.daemonBackup()
        
    def daemonBackup(self):
        '''
        This function watches the file queue, gets the backupPath and the filePath,
        and sends them to the backupFile function.
        '''
        while True:
            if self.fileQueue.not_empty:
                f = self.fileQueue.get()
                print 'Fullpath :', f['fullpath']
                backupPath = f['backuppath']
                print 'Backupath:', backupPath
                self.backupFile(f['fullpath'], backupPath)
            
    def backupFile(self, filePath, backupPath):
        '''
        This function takes in a source file and a backup destination (fullpath)
        It tries to copy with shutil.copy2, if it fails it tries rsync.
        '''
        print 'FileSyncer backing up %s to %s' %(filePath, backupPath)
        try:
            shutil.copy2(filePath, backupPath)
            if os.path.isfile(backupPath): 'Success!'
        except:
            print backupPath
            backupDir = "/".join(backupPath.split('/')[:-1]) + '/'
            print backupDir
            print 'Backing file up to', backupDir, 'with rsync.'
            command = 'rsync -rupt  %s %s' %(filePath, backupDir)
            #print 'COMMAND: ', command
            output = subprocess.check_output(command.split(' '))
            #print output
            
if __name__ == '__main__':
    f = {'modtime': 1339564955.1287122, 'fullpath': '/home/andrew/programming/folderwatcher.py', 'basepath': '/home/andrew/programming/', 'filename': 'folderwatcher.py'}

    q = Queue.Queue()
    backupDir = '/mnt/ExtTV/DesktopBackup/'

    a = FileSyncer(q, backupDir)
    a.start()

    q.put(f)

