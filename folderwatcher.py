import threading
import time
import os
import Queue

class WatchFolder(threading.Thread):
    def __init__(self, path, backupFileQueue):
        threading.Thread.__init__(self)
        self.fileQueue = backupFileQueue
        self.path = path
        self.sleepTime = 5
        self.newCheck = 20*self.sleepTime
    
    def run(self):
        self.watchFolder()
        
    def watchFolder(self):
        timer = 0
        
        self.files = self.getFileList(self.path)
        
        print 'FolderWatcher watching %s files in %s' %(len(self.files), self.path)
        while True:
            time.sleep(self.sleepTime)
            timer += self.sleepTime
            if timer == self.newCheck:
                timer = 0
                newFiles = self.getFileList(self.path)
                for newFile in newFiles:
                    if not self.files.has_key(newFile):
                        self.fileQueue.put(newFile)

            for f in self.files:
                fullPath = self.files[f]['fullpath']
                modTime = os.path.getmtime(fullPath)
                if (modTime > self.files[f]["modtime"]): 
                    #if files[f]['md5'] is not md5er.filemd5(fullPath):
                    self.files[f]["modtime"] = os.path.getmtime(fullPath)
                    self.fileQueue.put(self.files[f])
                    
    def getFileList(self, path):
        files = {}
        for f in os.listdir(path):
            if os.path.isfile(f):
                if f[-1] is not '~':
                    modtime = os.path.getmtime(f)
                    fullPath = path+f
                    files[f] = {'filename': f, 'modtime':modtime, 'fullpath':fullPath,\
                                'basepath':fullPath.split(f)[0]}
        return files
        
if __name__ == '__main__':
    q = Queue.Queue()
    pictures = WatchFolder('/home/andrew/Pictures/', q)
    pictures.start()
    programming = WatchFolder('/home/andrew/programming/', q)
    programming.start()
    while True:
        if q.not_empty:
            print q.get()
            
