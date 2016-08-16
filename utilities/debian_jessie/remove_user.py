#!/usr/bin/python3 -u

import os
import re
import argparse
import json
import pwd
import sys
from subprocess import call, DEVNULL

def remove_user():

    parser=argparse.ArgumentParser(prog='remove_user.py', description='A tool for remove users to /etc/postfix/virtual_mailbox and the system')

    parser.add_argument('--mailbox', help='Mailbox to remove', required=True)
    
    args=parser.parse_args()

    json_return={'error':0, 'status': 0, 'progress': 0, 'no_progress':0, 'message': ''}

    user, domain=args.mailbox.split("@")

    mailbox_user=args.mailbox.replace("@", "_")

    domain_check=re.compile('^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|([a-zA-Z0-9][a-zA-Z0-9-_]{1,61}[a-zA-Z0-9]))\.([a-zA-Z]{2,6}|[a-zA-Z0-9-]{2,30}\.[a-zA-Z]{2,3})$')

    user_check=re.compile('^[a-zA-Z0-9-_]+$')

    if not domain_check.match(domain) or not user_check.match(user):
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: domain or user is not valid'
        
        print(json.dumps(json_return))

        exit(1)

    json_return['progress']=25
    json_return['message']='Is a valid domain and user'

    print(json.dumps(json_return))

    try:
        user_pwd=pwd.getpwnam(user+'_'+domain)        

        if call("sudo userdel -r %s" % mailbox_user,  shell=True, stdout=DEVNULL, stderr=DEVNULL) > 0:

            json_return['error']=1
            json_return['status']=1
            json_return['progress']=100
            json_return['message']='Error: cannot delete the user'

            print(json.dumps(json_return))
            exit(1)
        else:
            line_domain=args.mailbox+' '+mailbox_user
            final_domains=[]
            with open('/etc/postfix/virtual_mailbox') as f:
                for domain in f:
                    if domain.strip()!=line_domain:
                        final_domains.append(domain.strip())        

            #final_domains.append("\n")

            final_domains_file=""

            if len(final_domains)>0:
                final_domains_file="\n".join(final_domains)
            

            with open('/etc/postfix/virtual_mailbox', 'w') as f:
                if f.write(final_domains_file) or final_domains_file=="":
                    json_return['progress']=75
                    json_return['message']='Deleted user from mailboxes'

                    print(json.dumps(json_return))
                else:
                    json_return['error']=1
                    json_return['status']=1
                    json_return['progress']=100
                    json_return['message']='Error: cannot update mailboxes'

                    print(json.dumps(json_return))

                    sys.exit(1)
                

            if call("postmap hash:/etc/postfix/virtual_mailbox",  shell=True, stdout=DEVNULL) > 0:

                json_return['error']=1
                json_return['status']=1
                json_return['progress']=100
                json_return['message']='Error: cannot refresh the domain mapper'

                print(json.dumps(json_return))

                exit(1)

            json_return['progress']=100
            json_return['status']=1
            json_return['message']='Mailbox deleted successfully'

            print(json.dumps(json_return))


    except KeyError:
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: user no exists'

        print(json.dumps(json_return))

        sys.exit(1)


if __name__=='__main__':
    remove_user()

