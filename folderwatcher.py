import threading
import time
import os
import Queue        
import md5

class WatchFolder(threading.Thread):
    def __init__(self, homePath, backupPath, backupFileQueue):
        threading.Thread.__init__(self)
        self.fileQueue = backupFileQueue
        self.homePath = homePath
        self.backupPath = backupPath
        self.sleepTime = 5
        self.newCheck = 4*self.sleepTime
        os.chdir(self.homePath)
        self.files = self.getFileList(self.homePath, self.backupPath)
        self.backupFiles = self.getFileList(self.backupPath, self.homePath)
        print 'FolderWatcher watching %s files in %s' %(len(self.files), self.homePath)
        print 'FolderWatcher watching %s files in %s' %(len(self.backupFiles), self.backupPath)
        
    def getFiles(self):
        return self.files
        
    def run(self):
        self.watchFolder()
        
    def watchFolder(self):
        timer = 0
        
        while True:
            self.checkForModifiedFiles(self.files)
            time.sleep(self.sleepTime)
            self.checkForModifiedFiles(self.backupFiles)
            
            timer += self.sleepTime
            if timer == self.newCheck:
                timer = 0
                self.files = self.checkForNewFiles(self.files, self.homePath)
                self.backupFiles = self.checkForNewFiles(self.backupFiles, self.backupPath)
                if len(self.backupFiles) is not len(self.files):
                    for f in self.backupFiles:
                        if not self.files.has_key(f):
                            self.fileQueue.put(self.backupFiles[f])
                    for f in self.files:
                        if not self.backupFiles.has_key(f):
                            self.fileQueue.put(self.files[f])
                else:
                    print 'Files synchronized.'

    def checkForNewFiles(self, files, path):
        if path == self.backupPath:
            newFiles = self.getFileList(path, self.homePath)
        else:
            newFiles = self.getFileList(path, self.backupPath)
            
        for newFile in newFiles:
            if not files.has_key(newFile):
                self.fileQueue.put(newFiles[newFile])
            
        files = newFiles
        print 'FolderWatcher watching %s files in %s' %(len(files), path)
        return files
        
    def checkForModifiedFiles(self, files):
        for f in files:
            fullPath = files[f]['fullpath']
            if files[f]['md5'] is not self.filemd5(fullPath):
                modTime = os.path.getmtime(fullPath)
                if (modTime > files[f]["modtime"]+30):          
                    files[f]["modtime"] = modTime
                    self.fileQueue.put(files[f])
        
    def getFileList(self, path, backupPath):
        files = {}
        for f in os.listdir(path):
            filePath = path+f
            if os.path.isfile(filePath):
                if f[-1] is not '~':
                    if f[0] is not '.':
                        fileHash = self.filemd5(filePath)
                        modtime = os.path.getmtime(filePath)
                        files[f] = {'filename': f, 'modtime':modtime, 'fullpath':filePath, 'backuppath':backupPath, 'md5':fileHash}
            #elif os.path.isfolder(filePath):
            # Add directories to watch list.
        return files

    def filemd5(self, fp, block_size=128):
        has = md5.new()
        with open(fp, 'rb') as f:
            data = f.read(block_size)
            has.update(data)
        return has.hexdigest()

if __name__ == '__main__':
    q = Queue.Queue()
    homePath = '/home/andrew/Documents/'
    backupPath = '/mnt/ExtTV/DesktopBackup/Documents/'
    pictures = WatchFolder(homePath, backupPath, q)
    pictures.start()
    while True:
        # When we get files from the queue, we are getting the differences between the folders.
        if q.not_empty:
            print q.get()
            
