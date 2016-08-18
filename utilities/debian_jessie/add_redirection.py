#!/usr/bin/python3 -u

import os
import re
import argparse
import json
import pwd
import sys
from subprocess import call, DEVNULL

def add_redirection():

    parser=argparse.ArgumentParser(prog='add_redirection.py', description='A tool for add redirections')

    parser.add_argument('--mailbox', help='Mailbox to add redirection', required=True)
    
    parser.add_argument('--redirection', help='Mailbox to redirect the mail', required=True)
    
    args=parser.parse_args()

    json_return={'error':0, 'status': 0, 'progress': 0, 'no_progress':0, 'message': ''}

    try:

        user, domain=args.mailbox.split("@")
        
        user_redirection, domain_redirection=args.redirection.split("@")
        
    except:
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: domain or user is not valid'
        
        print(json.dumps(json_return))

        exit(1) 
        

    #mailbox_user=args.mailbox.replace("@", "_")

    domain_check=re.compile('^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|([a-zA-Z0-9][a-zA-Z0-9-_]{1,61}[a-zA-Z0-9]))\.([a-zA-Z]{2,6}|[a-zA-Z0-9-]{2,30}\.[a-zA-Z]{2,3})$')

    user_check=re.compile('^[a-zA-Z0-9-_|\.]+$')
    
    redirection_check=re.compile('^'+args.mailbox+' .*$')
    
    if not domain_check.match(domain) or not user_check.match(user) or not domain_check.match(domain_redirection) or not user_check.match(user_redirection):
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: domain or user is not valid'
        
        print(json.dumps(json_return))

        exit(1)

    json_return['progress']=25
    json_return['message']='Is a valid mailbox and redirection'

    print(json.dumps(json_return))
    """
    try:
        
        user_pwd=pwd.getpwnam(mailbox_user) 
        
    except KeyError:
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: user no exists'

        print(json.dumps(json_return))

        sys.exit(1)
    """
    
    # Add user to virtual_mailbox

    #mailbox=args.user+'@'+args.domain
    #mailbox_user=args.user+'_'+args.domain
    
    # You can add many redirections
    
    #Check that if domain exists
    
    domain_line=domain+' '+domain
    
    redirection_line=args.mailbox+' '+args.redirection
    
    yes_domain=0
    
    with open('/etc/postfix/virtual_domains') as f:
        for l in f:
            l=l.strip()
            if l==domain_line:
                yes_domain=1
                break
    
    no_same_redirection=1
    
    arr_line=[redirection_line]
    
    with open('/etc/postfix/virtual_mailbox') as f:
        for l in f:
            l=l.strip()
            if redirection_check.match(l):
                ls=l.split(' ')
                redirections=ls[1].split(',')
                #print(redirections)
                if args.redirection in redirections:
                    no_same_redirection=0
                else:
                    redirections.append(args.redirection)
                    redirection_line=args.mailbox+' '+','.join(redirections)
                    arr_line.append(redirection_line)
                    del arr_line[0]
            else:
                arr_line.append(l)
           
            
    if yes_domain==1 and no_same_redirection==1:
    
        #Add redirection

        with open('/etc/postfix/virtual_mailbox', 'w') as f:
            if f.write("\n".join(arr_line)+"\n"):
                json_return['progress']=50
                json_return['message']='Redirection added'

                print(json.dumps(json_return))
            else:
                json_return['error']=1
                json_return['status']=1
                json_return['progress']=100
                json_return['message']='Error: cannot add the new redirection to file'

                print(json.dumps(json_return))

                exit(1)          
                

        if call("postmap hash:/etc/postfix/virtual_mailbox",  shell=True, stdout=DEVNULL) > 0:

            json_return['error']=1
            json_return['status']=1
            json_return['progress']=100
            json_return['message']='Error: cannot refresh the domain mapper'

            print(json.dumps(json_return))

            exit(1)
        
        json_return['progress']=100
        json_return['status']=1
        json_return['message']='Redirection added sucessfully'

        print(json.dumps(json_return))
    else:
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: domain doesn\'t exists or same redirection exists'

        print(json.dumps(json_return))

        exit(1)
    
if __name__=='__main__':
    add_redirection()
