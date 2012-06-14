import Queue
import threading
import subprocess
import shutil
import os

class FileSyncer(threading.Thread):
    def __init__(self, fileQueue):
        '''
        The FileSyncer will backup the files you place in the file queue.
        What you put in the queue must be a file with a 'fullpath' key, 
        which is the file's full path, a backup path, which is the directory
        where the file is going
        '''
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
                print f
                backupPath = f['backuppath']
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
            print 'Backing file up to', backupDir, 'with rsync.'
            command = 'rsync -ru  %s %s' %(filePath, backupDir)
            #print 'COMMAND: ', command
            output = subprocess.check_output(command.split(' '))
            #print output
            
if __name__ == '__main__':
    
    f = {'modtime': 1339663784.8836668, 'fullpath': \
        '/home/andrew/Documents/TestFile',\
         'md5': 'd41d8cd98f00b204e9800998ecf8427e', \
         'backuppath': '/mnt/ExtTV/DesktopBackup/Documents/',\
         'filename': 'TestFile'}

    # Make a queue to put files in
    q = Queue.Queue()
    
    # Start the file syncer
    a = FileSyncer(q)
    a.start()

    # Put a file in the queue.
    q.put(f)

