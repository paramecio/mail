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

def remove_user():

    parser=argparse.ArgumentParser(prog='remove_user.py', description='A tool for remove users to /etc/postfix/virtual_mailbox and the system')

    parser.add_argument('--mailbox', help='Mailbox to remove', required=True)
    
    args=parser.parse_args()

    json_return={'error':0, 'status': 0, 'progress': 0, 'no_progress':0, 'message': ''}

    check_lock('virtual_domains')

    user, domain=args.mailbox.split("@")

    mailbox_user=args.mailbox.replace("@", "_")

    domain_check=re.compile('^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|([a-zA-Z0-9][a-zA-Z0-9-_]{1,61}[a-zA-Z0-9]))\.([a-zA-Z]{2,6}|[a-zA-Z0-9-]{2,30}\.[a-zA-Z]{2,3})$')

    user_check=re.compile('^[a-zA-Z0-9-_|\.]+$')
    
    user_mailbox_check=re.compile(r'.* '+mailbox_user.replace('.', '\.')+'.*$')

    if not domain_check.match(domain) or not user_check.match(user):
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
        user_pwd=pwd.getpwnam(user+'_'+domain)        

        line_domain=args.mailbox+' '+mailbox_user
        final_domains=[]

        if call("sudo userdel -r %s" % mailbox_user,  shell=True, stdout=DEVNULL, stderr=DEVNULL) > 0:

            json_return['error']=1
            json_return['status']=1
            json_return['progress']=100
            json_return['message']='Error: cannot delete the user'

            print(json.dumps(json_return))
            unlock_file('virtual_domains')
            exit(1)
        else:
            
            with open('/etc/postfix/virtual_mailbox') as f:
                for domain in f:
                    
                    if domain.strip()!=line_domain and not user_mailbox_check.match(domain):
                        
                        final_domains.append(domain.strip())        
            
            #final_domains.append("\n")

            final_domains_file=""

            if len(final_domains)>0:
                final_domains_file="\n".join(final_domains)+"\n"
            

            with open('/etc/postfix/virtual_mailbox', 'w') as f:
                if f.write(final_domains_file) or final_domains_file=="":
                    json_return['progress']=75
                    json_return['message']='Deleted user from mailboxes'

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
            json_return['message']='Mailbox deleted successfully'

            print(json.dumps(json_return))
            unlock_file('virtual_domains')
            exit(0)


    except KeyError:
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: user no exists'

        print(json.dumps(json_return))
        unlock_file('virtual_domains')
        sys.exit(1)

    
if __name__=='__main__':
    remove_user()

