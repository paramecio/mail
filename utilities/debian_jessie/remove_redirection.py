#!/usr/bin/python3 -u

import time
import os
import re
import argparse
import json
import pwd
import sys
import socket
from subprocess import call, DEVNULL

def lock_file(file_lock):
    with open('/tmp/lock_'+file_lock, 'w') as f:
        f.write('lock')
    return True
        
def unlock_file(file_lock):
    os.remove('/tmp/lock_'+file_lock)
    
def check_lock(file_lock):
    while os.path.isfile('/tmp/lock_'+file_lock)==True:
        time.sleep(1)
    
    lock_file(file_lock)
    
    return True

def remove_redirection():

    parser=argparse.ArgumentParser(prog='remove_redirection.py', description='A tool for remove redirections')

    parser.add_argument('--mailbox', help='Mailbox to remove redirection', required=True)
    
    parser.add_argument('--redirection', help='Redirection to delete', required=False)
    
    args=parser.parse_args()

    json_return={'error':0, 'status': 0, 'progress': 0, 'no_progress':0, 'message': ''}
    
    check_lock('virtual_domains')

    try:

        user, domain=args.mailbox.split("@")
        
        user_redirection, domain_redirection=args.redirection.split("@")
    
    except ValueError:
        try:
            
            user_redirection, domain_redirection, tld=args.redirection.split("@")
            #Check if domain is the host domain
            hostname='autoreply.'+socket.getfqdn()
            
            if tld!=hostname:
                json_return['error']=1
                json_return['status']=1
                json_return['progress']=100
                json_return['message']='Error: not valid hostname for the service'
                
                print(json.dumps(json_return))
                unlock_file('virtual_domains')
                exit(1)
                
            
        except ValueError:
            
            json_return['error']=1
            json_return['status']=1
            json_return['progress']=100
            json_return['message']='Error: domain or user is not valid'
            
            print(json.dumps(json_return))
            unlock_file('virtual_domains')
            exit(1) 
        
    
    #mailbox_user=args.mailbox.replace("@", "_")

    domain_check=re.compile('^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|([a-zA-Z0-9][a-zA-Z0-9-_]{1,61}[a-zA-Z0-9]))\.([a-zA-Z]{2,6}|[a-zA-Z0-9-]{2,30}\.[a-zA-Z]{2,3})$')

    user_check=re.compile('^[a-zA-Z0-9-_|\.]+$')
    
    mailbox_check=re.compile('^'+args.mailbox+' .*$')
    
    if args.redirection!=None:
        if not domain_check.match(domain_redirection) or not user_check.match(user_redirection):
            json_return['error']=1
            json_return['status']=1
            json_return['progress']=100
            json_return['message']='Error: domain or user is not valid'
            
            print(json.dumps(json_return))
            unlock_file('virtual_domains')
            exit(1)
    
    if not domain_check.match(domain) or not user_check.match(user):
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: domain or user is not valid'
        
        print(json.dumps(json_return))
        unlock_file('virtual_domains')
        exit(1)

    json_return['progress']=25
    json_return['message']='Is a valid mailbox and redirection'

    print(json.dumps(json_return))
    time.sleep(1)
    # If args == None find the line and delete the element
    
    arr_mailbox=[]
    
    yes_mailbox=False
    
    if args.redirection==None:
        with open('/etc/postfix/virtual_mailbox') as f:
            for l in f:
                l=l.strip()
                if not mailbox_check.match(l):
                    arr_mailbox.append(l)
                else:
                    yes_mailbox=True
    else:
        
        with open('/etc/postfix/virtual_mailbox') as f:
            for l in f:
                l=l.strip()
                if mailbox_check.match(l):
                    yes_mailbox=True
                    ls=l.split(' ')
                    redirections=ls[1].split(',')
                    try:
                        redirections.remove(args.redirection)
                    except:
                        json_return['error']=1
                        json_return['status']=1
                        json_return['progress']=100
                        json_return['message']='Error: no exists redirected mailbox'

                        print(json.dumps(json_return))
                        unlock_file('virtual_domains')
                        exit(1)
                        
                    if len(redirections)>0:
                        l=ls[0]+' '+','.join(redirections)
                        arr_mailbox.append(l)
                    
                else:
                    arr_mailbox.append(l)
    
    if yes_mailbox==True:
    
        with open('/etc/postfix/virtual_mailbox', 'w') as f:
            if f.write("\n".join(arr_mailbox)+"\n"):
                json_return['progress']=50
                json_return['message']='Redirection deleted'
                
                print(json.dumps(json_return))
                time.sleep(1)
            else:
                json_return['error']=1
                json_return['status']=1
                json_return['progress']=100
                json_return['message']='Error: cannot delete the redirection'
                    
                print(json.dumps(json_return))
                unlock_file('virtual_domains')
                exit(1)
                    
        if call("postmap hash:/etc/postfix/virtual_mailbox",  shell=True, stdout=DEVNULL) > 0:

            json_return['error']=1
            json_return['status']=1
            json_return['progress']=100
            json_return['message']='Error: cannot refresh the domain mapper'

            print(json.dumps(json_return))
            unlock_file('virtual_domains')
            exit(1)
        else:
            json_return['progress']=75
            json_return['message']='Domain mapper refreshed'

            print(json.dumps(json_return))
            time.sleep(1)
            
        json_return['progress']=100
        json_return['status']=1
        json_return['message']='Redirection deleted sucessfully'

        print(json.dumps(json_return))
        unlock_file('virtual_domains')
        exit(0) 
    else:
        
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: no exists redirected mailbox'
        
        print(json.dumps(json_return))
    #print(arr_mailbox)
    
    unlock_file('virtual_domains')
    
if __name__=='__main__':
    remove_redirection()

