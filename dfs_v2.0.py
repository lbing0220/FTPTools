#!/usr/bin/python2
from ftplib import FTP
import os
import socket
import re

###########################################################################################
# You may only need to modify below config, then can use this script on your ftp server,  #
# Other issue you may need check the code or contact me through e-mail: lbing0220@126.com #
# Author: Albin Liang                                                                     #
# Update Date: 2020-07-13                                                                 #
# Add Line 159-165, Use mv command to rename one file while name has space                #
# Usage: mv "file name" will change file name to "file_name"                              #
########################################################################################### 
dfshost = 'localhost'
dfsport = 21
dfsuser = 'albin'
dfspass = 'ls930105'

default_ftp_path = '/home/albin/ftp'
default_local_path = '/home/albin/test'
if not os.path.exists(default_local_path):
    os.mkdir(default_local_path)


class FTPTools(object):
    def __init__(self, host=dfshost, port=dfsport, timeout=3000, username=dfsuser, password=dfspass):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.username = username
        self.password = password
        self.conn = FTP()
        self.conn.encoding = 'utf-8'

    def connect(self):
        if self.conn.connect(self.host, self.port, self.timeout) and self.conn.login(self.username, self.password):
            return True
        else:
            return False

    def ftpdircheck(self, path):
        path = path.rstrip('/')  # Remove the last '/'
        dirFlag = False
        current_dir = self.conn.pwd()
        try:
            self.conn.cwd(path)
            dirFlag = True
        except:
            dirFlag = False
        finally:
            self.conn.cwd(current_dir)
        return dirFlag

    def dfsmkdir(self, path):  # Create one directory
        self.conn.mkd(path)

    def dfschdir(self, path):  # Change current directory
        self.conn.cwd(path)

    def dfsrmfile(self, filename):  # remove one file
        self.conn.delete(filename)

    def dfsrmdir(self, dirname):  # Remove directory
        self.conn.rmd(dirname)

    def print_usage(self):
        print ''' ******This script is only used for HKC-H4 AC Systems******
It will help you to deal with ftp files as you in local environment
Support Commands:
            ls
            cd
            mv
            rm
            pwd
            rmdir
            mkdir
            ...

In local status: rcp local_file will upload local file to current ftp path
                rcp local_file remote_file will upload local file to specified folder
                
In ftp status: rcp remote_file will download remote file to current local path
            rcp remote_file local_file will download remote file to specified folder
            add "rmdir" command to delete directory
            
####### Warning: when use rcp command, it will override the file which has the same name
################ Please backup your file first before you use this command ################           
Directory upload/download is still be not supported... No plan to do this...
Only support standard unix commands, didn't support alias command such as : "ll, la, cdpro..."
**********************************Thanks for Use**********************************'''

    def file_download(self, remote_filename, local_filename='.'):
        if os.path.isdir(local_filename) or os.path.isdir(os.path.curdir + os.sep + local_filename):
            file_handle = open(local_filename + os.sep + remote_filename, 'wb')
            self.conn.retrbinary("RETR " + remote_filename, file_handle.write, 1024)
            file_handle.close()
        else:
            file_handle = open(remote_filename, 'wb')
            self.conn.retrbinary('RETR ' + remote_filename, file_handle.write, 1024)
            os.rename(remote_filename, local_filename)
            file_handle.close()

    def file_upload(self, local_filename, remote_filename='.'):
        if self.ftpdircheck(remote_filename) or self.ftpdircheck(self.conn.pwd() + os.sep + remote_filename):
            file_handle = open(local_filename, 'rb')
            self.conn.storbinary('STOR ' + remote_filename + os.sep + local_filename, file_handle, 1024)
            file_handle.close()
        else:
            file_handle = open(local_filename, 'rb')
            self.conn.storbinary('STOR ' + remote_filename, file_handle, 1024)
            self.conn.rename(local_filename, remote_filename)
            file_handle.close()

    def dir_download(self, remote_path, local_path='.'):
        print('Directory download is in developing...')
        print("you can try compress them on windows and use 'rcp filename' to download it ")

    def dir_upload(self, local_path, remote_path='.'):
        print('Directory upload is in developing...')
        print("you can try compress them on sunpc and use 'rcp filename' to upload it")

    def ftp_operation(self, cmdstring):
        print(self.conn.pwd())
        args = cmdstring.split(' ')
        if args[0] == 'ls' or args[0] == 'll' or args[0] == 'la':
            self.conn.dir()
        elif len(args) == 2 and args[0] == 'cd':
            self.conn.cwd(args[1])
            print(self.conn.dir())
        elif args[0] == 'rcp':
            if len(args) == 2:
                if self.ftpdircheck(args[1]):
                    self.dir_download(args[1])
                else:
                    self.file_download(args[1])
            elif len(args) == 3:
                if self.ftpdircheck(args[1]):
                    self.dir_download(args[1], args[2])
                else:
                    self.file_download(args[1], args[2])
        elif args[0] == 'rm' and len(args) == 2:
            if self.ftpdircheck(args[1]):
                print("Please use 'rmdir' command to delete directory...(only can be used in ftp status)")
            else:
                self.dfsrmfile(args[1])
        elif args[0] == 'rmdir':
            self.dfsrmdir(args[1])
        elif args[0] == 'mkdir':
            self.dfsmkdir(args[1])
        elif args[0] == 'cp':
            print("cp functions(copy ftp file from ftp dir to ftp dir) is still in developing...  ")
            # download it to local path
            # local used copy command to create dump file
            # upload dump file to ftp path
            # didn't develop...
        elif args[0] == 'pwd':
            print("current dir is: " + self.conn.pwd())
        elif args[0] == 'mv':
            if re.search(r'".*"', cmdstring)!= None:
                name = re.search(r'".*"', cmdstring).group().replace('"', '')
                #self.conn.rename(name, name.replace(" ", "_"))
            elif re.search(r"'.*'", cmdstring) != None:
                name = re.search(r"'.*'", cmdstring).group().replace("'", "")
                #self.conn.rename(name, name.replace(" ", "_"))
            else:
                if len(args) == 3:
                    if self.ftpdircheck(args[2]):
                        self.conn.rename(args[1], args[2] + os.sep + args[1])
                    else:
                        self.conn.rename(args[1], args[2])
                elif len(args) > 3 and self.ftpdircheck(args[-1]):
                    for each in args[1:-1]:
                        self.conn.rename(each, args[-1] + os.sep + each)
                else:
                    print('The number of parm is wrong...')
        else:
            print(args[0] + " still couldn't be execute, Please input 'help' to get usage manual...")

    def local_operation(self, cmdstring):
        args = cmdstring.split(' ')
        if args[0] == 'cd':
            if len(args) == 1:
                os.chdir(default_local_path)
            elif len(args) == 2 and \
                    (os.path.isdir(args[1]) or os.path.isdir(os.curdir + os.path.sep + args[1])):
                os.chdir(args[1])
        elif args[0] == 'rcp':
            if len(args) == 2:
                if os.path.isdir(args[1]) or os.path.isdir(os.curdir + os.sep + args[1]):
                    self.dir_upload(args[1])
                else:
                    self.file_upload(args[1])
            elif len(args) == 3:
                if os.path.isdir(args[1]) or os.path.isdir(os.curdir + os.sep + args[1]):
                    self.dir_upload(args[1])
                else:
                    self.file_upload(args[1], args[2])
        elif args[0] == 'rmdir' and len(args) == 2:
            # print("Please use 'rm -rf dirname' to delete directory")
            os.system('rm -rf ' + args[1])
        else:
            if os.system(cmdstring) != 0:
                print('############################')
                print(cmdstring, "execute failed...,Please input 'help' to get usage manual...")
                # print(os.path.abspath(os.path.curdir))

    def quit(self):
        self.conn.quit()
        print('Bye-Bye')


if __name__ == "__main__":
    remoteflag = 1
    prefix = "orbo@" + socket.gethostname() + "#ftp:"
    ftp = FTPTools()
    if ftp.connect():
        print('Success')
        ftp.dfschdir(default_ftp_path)
        os.chdir(default_local_path)
        while True:
            print prefix,
            cmd = raw_input()
            args = cmd.split(' ')
            if cmd.find('quit') == 0 or cmd.find('bye') == 0 or cmd.find('exit') == 0:
                break
            elif cmd.find("cdftp") == 0:
                remoteflag = 1
                prefix = prefix.replace('local', 'ftp')
                # ftp.dfschdir(default_ftp_path)
            elif cmd.find('cdlocal') == 0:
                remoteflag = 0
                prefix = prefix.replace('ftp', 'local')
                # os.chdir(default_local_path)
            elif cmd.find('help') == 0:
                ftp.print_usage()
            else:
                if remoteflag == 1:
                    ftp.ftp_operation(cmd)
                elif remoteflag == 0:
                    ftp.local_operation(cmd)
        ftp.quit()
