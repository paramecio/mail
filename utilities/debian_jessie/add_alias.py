#!/usr/bin/python3 -u

import time
import os
import re
import argparse
import json
import pwd
import sys
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

def add_alias():

    parser=argparse.ArgumentParser(prog='add_alias.py', description='A tool for add alias to mail')

    parser.add_argument('--mailbox', help='Mailbox to add alias', required=True)
    
    parser.add_argument('--alias', help='Alias for add to mailbox', required=True)
    
    args=parser.parse_args()

    json_return={'error':0, 'status': 0, 'progress': 0, 'no_progress':0, 'message': ''}

    json_return['progress']=5
    json_return['message']='Waiting unlock...'

    print(json.dumps(json_return))
    
    check_lock('virtual_domains')

    try:

        user, domain=args.mailbox.split("@")
        
        user_alias, domain_alias=args.alias.split("@")
        
    except:
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: domain or user is not valid'
        
        print(json.dumps(json_return))

        unlock_file('virtual_domains')

        exit(1) 
        

    mailbox_user=args.mailbox.replace("@", "_")

    domain_check=re.compile('^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|([a-zA-Z0-9][a-zA-Z0-9-_]{1,61}[a-zA-Z0-9]))\.([a-zA-Z]{2,6}|[a-zA-Z0-9-]{2,30}\.[a-zA-Z]{2,3})$')

    user_check=re.compile('^[a-zA-Z0-9-_|\.]+$')
    
    alias_check=re.compile('^'+args.alias+' .*$')
    
    if not domain_check.match(domain) or not user_check.match(user) or not domain_check.match(domain_alias) or not user_check.match(user_alias) or domain_alias!=domain:
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: domain or user is not valid'
        
        print(json.dumps(json_return))

        unlock_file('virtual_domains')

        exit(1)

    json_return['progress']=25
    json_return['message']='Is a valid domain and user'

    print(json.dumps(json_return))
    
    time.sleep(1)
    
    try:
        
        user_pwd=pwd.getpwnam(mailbox_user) 
        
    except KeyError:
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: user no exists'

        print(json.dumps(json_return))

        unlock_file('virtual_domains')

        sys.exit(1)
    
    # Add user to virtual_mailbox

    #mailbox=args.user+'@'+args.domain
    #mailbox_user=args.user+'_'+args.domain
    
    # Check that alias doesnt exists
    
    with open('/etc/postfix/virtual_mailbox') as f:
        
        
        #print(all_mailboxes)
        
        for line in f:
            if alias_check.match(line):
                json_return['error']=1
                json_return['status']=1
                json_return['progress']=100
                json_return['message']='Error: alias exists'

                print(json.dumps(json_return))

                unlock_file('virtual_domains')

                sys.exit(1)
    
    #Add alias

    with open('/etc/postfix/virtual_mailbox', 'a') as f:
        if f.write(args.alias+' '+mailbox_user+"\n"):
            json_return['progress']=50
            json_return['message']='Alias added'

            print(json.dumps(json_return))
            
            time.sleep(1)
            
        else:
            json_return['error']=1
            json_return['status']=1
            json_return['progress']=100
            json_return['message']='Error: cannot add the new mailbox to file'

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
    
    json_return['progress']=100
    json_return['status']=1
    json_return['message']='Alias added sucessfully'
    print(json.dumps(json_return))
    
    unlock_file('virtual_domains')
    
    exit(0)
    
if __name__=='__main__':
    add_alias()

