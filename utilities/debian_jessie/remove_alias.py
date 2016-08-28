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

def remove_alias():

    parser=argparse.ArgumentParser(prog='remove_user.py', description='A tool for remove users to /etc/postfix/virtual_mailbox and the system')

    parser.add_argument('--alias', help='Alias to remove', required=True)
    
    args=parser.parse_args()

    json_return={'error':0, 'status': 0, 'progress': 0, 'no_progress':0, 'message': ''}

    check_lock('virtual_domains')

    user, domain=args.alias.split("@")

    mailbox_user=args.alias.replace("@", "_")

    domain_check=re.compile('^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|([a-zA-Z0-9][a-zA-Z0-9-_]{1,61}[a-zA-Z0-9]))\.([a-zA-Z]{2,6}|[a-zA-Z0-9-]{2,30}\.[a-zA-Z]{2,3})$')

    user_check=re.compile('^[a-zA-Z0-9-_|\.]+$')

    if not domain_check.match(domain) or not user_check.match(user):
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: domain or user is not valid'
        
        print(json.dumps(json_return))
        
        unlock_file('virtual_domains')

        exit(1)
    
    alias_check=re.compile('^'+args.alias+' .*$')

    json_return['progress']=50
    json_return['message']='Is a valid domain and user'

    print(json.dumps(json_return))
    time.sleep(1)

    try:
        user_pwd=pwd.getpwnam(user+'_'+domain)        

        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: exists an user with it mail address'

        print(json.dumps(json_return))
        unlock_file('virtual_domains')
        exit(1)

    except KeyError:
        
        final_domains=[]
        with open('/etc/postfix/virtual_mailbox') as f:
            for line in f:
                if not alias_check.match(line):
                    final_domains.append(line.strip())        
        
            #final_domains.append("\n")

        final_domains_file=""

        if len(final_domains)>0:
            final_domains_file="\n".join(final_domains)+"\n"
        
        with open('/etc/postfix/virtual_mailbox', 'w') as f:
            if f.write(final_domains_file) or final_domains_file=="":
                json_return['progress']=75
                json_return['message']='Deleted alias from mailboxes'

                print(json.dumps(json_return))
                time.sleep(1)
            else:
                json_return['error']=1
                json_return['status']=1
                json_return['progress']=100
                json_return['message']='Error: cannot update mailboxes'

                print(json.dumps(json_return))
                unlock_file('virtual_domains')
                sys.exit(1)
                

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
            json_return['message']='Alias deleted successfully'

            print(json.dumps(json_return))
               
    unlock_file('virtual_domains')
    
if __name__=='__main__':
    remove_alias()

