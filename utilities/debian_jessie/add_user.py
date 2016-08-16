#!/usr/bin/python3 -u

import os
import re
import argparse
import json
import pwd
import sys
from subprocess import call, DEVNULL

def add_user():

    parser=argparse.ArgumentParser(prog='add_user.py', description='A tool for add users to /etc/postfix/virtual_mailbox')

    parser.add_argument('--domain', help='The domain of this user', required=True)

    parser.add_argument('--user', help='User mailbox', required=True)

    parser.add_argument('--quota', help='Quota of this user', required=True)
    
    args=parser.parse_args()

    json_return={'error':0, 'status': 0, 'progress': 0, 'no_progress':0, 'message': ''}

    domain_check=re.compile('^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|([a-zA-Z0-9][a-zA-Z0-9-_]{1,61}[a-zA-Z0-9]))\.([a-zA-Z]{2,6}|[a-zA-Z0-9-]{2,30}\.[a-zA-Z]{2,3})$')

    user_check=re.compile('^[a-zA-Z0-9-_]+$')

    if not domain_check.match(args.domain) or not user_check.match(args.user):
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: domain or user is not valid'
        
        print(json.dumps(json_return))

        exit(1)

    json_return['progress']=25
    json_return['message']='Is a valid domain and user'

    print(json.dumps(json_return))

    yes_domain=0

    #Check if domain exists
    line_domain=args.domain+' '+args.domain
    final_domains=[]
    with open('/etc/postfix/virtual_domains') as f:
        for domain in f:
            if domain.strip()==line_domain:
                yes_domain=1

    if yes_domain==1:
        # check if user exits

        try:
            user_pwd=pwd.getpwnam(args.user+'_'+args.domain)
            json_return['error']=1
            json_return['status']=1
            json_return['progress']=100
            json_return['message']='Error: user exists'

            print(json.dumps(json_return))
            
            sys.exit(1)

        except KeyError:
     
            # add user
           
            stat_group=os.stat('/home/%s' % args.domain)

            gid=stat_group.st_gid

            if call("sudo useradd -m -s /usr/sbin/nologin -g %i -d /home/%s/%s@%s %s_%s" % (gid, args.domain, args.user, args.domain, args.user, args.domain),  shell=True, stdout=DEVNULL) > 0:
                json_return['error']=1
                json_return['status']=1
                json_return['progress']=100
                json_return['message']='Error: cannot create a new user'

                print(json.dumps(json_return))

                exit(1)
    
            json_return['progress']=40
            json_return['message']='User added'

            print(json.dumps(json_return))

            # Add user to virtual_mailbox

            mailbox=args.user+'@'+args.domain
            mailbox_user=args.user+'_'+args.domain

            with open('/etc/postfix/virtual_mailbox', 'a') as f:
                if f.write(mailbox+' '+mailbox_user+"\n"):
                    json_return['progress']=80
                    json_return['message']='Mailbox added'

                    print(json.dumps(json_return))
                else:
                   json_return['error']=1
                   json_return['status']=1
                   json_return['progress']=100
                   json_return['message']='Error: cannot add the new mailbox to file'

                   print(json.dumps(json_return))

                   exit(1)          
            

            if call("postmap hash:/etc/postfix/virtual_mailbox",  shell=True, stdout=DEVNULL) > 0:

                json_return['error']=1
                json_return['status']=1
                json_return['progress']=100
                json_return['message']='Error: cannot refresh the domain mapper'

                print(json.dumps(json_return))

                exit(1)
           
            # add quota

            try:

                args.quota=int(args.quota)

            except:

                args.quota=0

            if args.quota>0:
                num_m=args.quota*1024
                num_mhard=(num_m*0.10)+num_m
            if call("sudo setquota -u %s -a %d %d 0 0" % (mailbox_user, num_m, num_mhard),  shell=True, stdout=DEVNULL) > 0:
                json_return['error']=1
                json_return['status']=1
                json_return['progress']=100
                json_return['message']='Error: cannot add quota to this user group'

                print(json.dumps(json_return))

                exit(1)
            else:
                json_return['progress']=90
                json_return['message']='Quota added sucessfully'
                print(json.dumps(json_return))

            json_return['progress']=100
            json_return['status']=1
            json_return['message']='New mailbox account added sucessfully'

            print(json.dumps(json_return))
            

if __name__=='__main__':
    add_user()

