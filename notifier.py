#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import gobject
gtk.gdk.threads_init()
import appindicator
import time
import pynotify
import subprocess
import sys
import os
import os.path
import Queue
import threading
import random
import md5er

class AppIndicatorExample:
    def __init__(self):
        self.programmingFolder = '/home/andrew/programming/'
        self.picturesFolder = '/home/andrew/Pictures/'
        self.backupDirectory = '/mnt/ExtTV/DesktopBackup/'
        self.base = '/home/andrew/' #base is used to determine where we are from 
        self.initPyNotify()
        self.initTray()
        self.watchFolderThread(self.picturesFolder)
        self.watchFolderThread(self.programmingFolder)

    def initTray(self):
        self.ind = appindicator.Indicator ("example-simple-client", "indicator-messages", appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_attention_icon ("indicator-messages-new")
        self.ind.set_icon("/usr/share/icons/Humanity/apps/64/internet-feed-reader.svg")

        self.menu = gtk.Menu()
        
        item = gtk.MenuItem("Sync Programming Folder")
        item.connect('activate', self.syncProgramming)
        item.show()
        self.menu.append(item)
        item = gtk.MenuItem("Sync Photos")
        item.connect('activate', self.syncPhotos)
        item.show()
        self.menu.append(item)

        image = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        image.connect("activate", self.quit)
        image.show()
        self.menu.append(image)
        
        self.menu.show()
        self.ind.set_menu(self.menu)
    
    def initPyNotify(self):
        pynotify.init("Timekpr notification")
        
    def watchFolderThread(self, path):
        threading.Thread(target=self.watchFolder, args=(path,)).start()
        
    def watchFolder(self, path='./'):
        sleepTime = 5
        newCheck = 120
        timer = 0
        if path == './':
            #print 'path is ', path
            path = os.getcwd()
        #print 'Source Path: ', path

        files = self.getFileList(path)
        #print 'Source Files: ', files
        relativeBackup = self.backupDirectory + path.split(self.base)[1]
        #print 'Backup Path: ',relativeBackup
        backupList = self.getFileList(relativeBackup)
        #print 'Backup Files: ', backupList
        self.backupDifference(files, backupList)
        print 'Watching %s files in %s' %(len(files), path)
        while True:
            time.sleep(sleepTime)
            timer += sleepTime
            if timer == newCheck:
                timer = 0
                print '\nGetting new file list to see if any new files changed...'
                files = self.getFileList(path)
                backupList = self.getFileList(relativeBackup)
                self.backupDifference(files, backupList)
            
            for f in files:
                fullPath = files[f]['fullpath']
                modTime = os.path.getmtime(fullPath)
                if (modTime > files[f]["modtime"]) and (modTime > backupList[f]['modtime']): 
                    if files[f]['md5'] is not md5er.filemd5(fullPath):
                        # store new time and...
                        files[f]["modtime"] = os.path.getmtime(fullPath)
                        print 'Syncing', f, 'to', relativeBackup
                        self.genericSyncer(fullPath, mode='run')
                                    
    def getFileList(self, path):
        #print 'File list path: ', path
        files = {}
        for f in os.listdir(path):
            fullPath = path+f
            if os.path.isfile(fullPath):
                if f[-1] is not '~':
                    modtime = os.path.getmtime(fullPath)
                    has = md5er.filemd5(fullPath)
                    files[f] = {'modtime':modtime, 'md5':has, 'fullpath':fullPath}
        return files

    def backupDifference(self, files, backupFiles):
        numFiles = 0
        relPath = ''
        for f in files:
            relPath = files[f]['fullpath'].split(self.base)
            relPath = relPath[1].split('/')[0]
            if not backupFiles.has_key(f):
                numFiles += 1
                path = files[f]['fullpath']
                self.genericSyncer(path, mode='run')
        if numFiles > 0:
            print "Backed up %s files that weren't in %s" %(numFiles, self.backupDirectory+relPath)
        else:
            print 'No new files.'    
    def rsyncData(self, path, mode='test'):
        backupDir = self.backupDirectory + path.split(self.base)[1]
        if mode == 'test':
            command = 'rsync --dry-run -rzvv %s %s' %(path, backupDir)
            
        elif mode == 'run':
            command = 'rsync -rzvv %s %s' %(path, backupDir)
        else:
            return 0
        #print command
        try:
            output = subprocess.check_output(command.split(' '))
        except:
            raise
            print 'Error rsyncing data...'

        output = output.split('\n')
        last = output[-2]
        size = last.split(' ')[3]
        size = int(size)/(1024*1024.)
        return size
        
    def notify(self, notificationTitle, notificationBody, status='NORMAL'):
        n = pynotify.Notification(notificationTitle, notificationBody)
        if status == 'normal':
            n.set_urgency(pynotify.URGENCY_NORMAL)
        elif status == 'critical':
            n.set_urgency(pynotify.URGENCY_CRITICAL)
        elif status == 'low':
            n.set_urgency(pynotify.URGENCY_LOW)
        helper = gtk.Button()
        icon = helper.render_icon(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_DIALOG)
        n.set_icon_from_pixbuf(icon)
        n.show()
        if not n.show():
            print "Failed to send notification"
            sys.exit(1)

    def genericSyncer(self, path, mode='test'):
        self.ind.set_status(appindicator.STATUS_ATTENTION)
        size = self.rsyncData(path, mode='test')
        notificationTitle = "Syncing %s" %path.split('/')[-1]
        notificationBody = "Syncing %.3f Mbytes." %(size)
        print notificationTitle, notificationBody
        self.notify(notificationTitle, notificationBody)
        a = time.time()
        size = self.rsyncData(path, mode)
        notificationTitle = "Finished Syncing %s" %path.split('/')[-1]
        notificationBody = "Synced %3f Mbytes in %.2f seconds." %(size, time.time()-a)
        print notificationTitle, notificationBody
        self.notify(notificationTitle, notificationBody, 'critical')
        self.ind.set_status (appindicator.STATUS_ACTIVE)
        
    def syncPhotos(self, widget, data=None):
        print 'syncing photos...'
        self.genericSyncer(path=self.picturesFolder)
               
    def syncProgramming(self, widget, data=None):
        print 'syncing programming...'
        self.genericSyncer(path=self.programmingFolder)
        
    def switchIcon(self, widget, data=None):
    	self.ind.set_status (appindicator.STATUS_ATTENTION)
    
    def quit(self, widget, data=None):
        gtk.main_quit()

def main():
    gtk.main()
    return 0

if __name__ == '__main__':
    indicator = AppIndicatorExample()
    main()
