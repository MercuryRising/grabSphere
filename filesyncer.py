import Queue
import threading
import subprocess
import shutil
import os

class FileSyncer(threading.Thread):
    def __init__(self, fileQueue, backupDirectory):
        threading.Thread.__init__(self)
        self.fileQueue = fileQueue
        self.backupDirectory = backupDirectory
        
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
                backupPathEnding = f['fullpath'].split('/', 3)[-1]
                backupPath =  self.backupDirectory+backupPathEnding
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
            backupDir = "/".join(backupPath.split('/')[:-1]) + '/'
            #print 'Backing file up to', backupDir, 'with rsync.'
            command = 'rsync --dry-run -rzvv %s %s' %(filePath, backupDir)
            output = subprocess.check_output(command.split(' '))
            #print output
            
if __name__ == '__main__':
    f = {'fullpath': '/home/andrew/programming/folderwatcher.py', 'basepath': '/home/andrew/programming/', 'filename': 'folderwatcher.py'}
    
    # add your own file, f must be a dictionary with the key f['fullpath']
    backupDir = 'Directory to back up to'
    
    q = Queue.Queue()

    a = FileSyncer(q, backupDir)
    a.start()

    q.put(f)

