import time
import sys
import os
from threading import Thread
import getpass
import paramiko



'''
This is the Machine Class
'''
class Machine:


    '''
    This is the constructor (called something else in python?) it takes as
    input and ip address and sets/creates an instance variable for the ip along
    with the creation of a hostname instance variable and lists for rawConfig,
    cleanedConfig, and ip_route.
    '''
    def __init__(self, ip, username, password):
        self.ip = ip
        self.hostname = "S1"
        self.username = username
        self.password = password
        self.rawConfig = []
        self.cleanedConfig = []
        self.ip_route = []


    '''
    This function is used for gathering the config files of the
    machines and the routing table information. The function takes as
    input an object that it is called upon...
    '''
    def gatherConfigs(self):

        ssh = paramiko.SSHClient()
        #In case the machine is not a known host. What if the fingerprint
        #changed though? Mitm....?
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.ip, port=22, username=self.username, password=self.password, allow_agent=False, look_for_keys=False)
            stdin, stdout, stderr = ssh.exec_command('show run')
            self.rawConfig = stdout.readlines()

            ssh.close()

        except:
            print(sys.exc_info()[0])

        self.cleanConfigss()


    '''
    Method to strip out unecessary question marks from cisco configs
    '''
    def cleanConfigss(self):
        count = 0
        last = ""

        for line in self.rawConfig:
            if count > 2:
                if self.rawConfig[count] != last: #Might be expensive. There are other ways...
                    self.cleanedConfig.append(self.rawConfig[count])
                    last = self.rawConfig[count]
            count += 1

        self.cleanedConfig[-1] = 'end' # NOT GOOD
        print(self.cleanedConfig[-1])
        print(self.cleanedConfig)
        self.write_cleaned()

    def write_cleaned(self):
        f = open('config' + str(time.time()),'w')
        for i in self.cleanedConfig:
            f.write(i)
        


def populateMachineList(list_name, machines, username, password):

    with open(list_name, 'r') as ip_list:
        for ip in ip_list:
            #Create and put the machine objects in a list.
            machines.append(Machine(ip, username, password))

def startThreads(machines, threads):
    for i in machines:
        t1 = Thread(target=i.gatherConfigs, args=())
        t1.start()
        threads.append(t1)
    for t1 in threads:
        t1.join()


def get_credentials():
    username = input('Username: ')
    password = getpass.getpass('Password: ')

    return username, password


def Main():
    username, password = get_credentials()
        
    machines = []
    threads = []
    populateMachineList('ips.txt', machines, username, password)
    os.mkdir('Cleaned_Configs')
    os.chdir('Cleaned_Configs')
    startThreads(machines, threads)
    os.chdir('..')


if __name__ == '__main__':
    Main()
