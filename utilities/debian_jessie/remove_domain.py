#!/usr/bin/python3 -u

import os
import re
import argparse
import json
import pwd
import sys
from subprocess import call, DEVNULL

def remove_user():

    parser=argparse.ArgumentParser(prog='remove_domain.py', description='A tool for remove all users from a domain in all places in server')

    parser.add_argument('--domain', help='Domain to remove', required=True)
    
    args=parser.parse_args()

    json_return={'error':0, 'status': 0, 'progress': 0, 'no_progress':0, 'message': ''}

    domain_check=re.compile('^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|([a-zA-Z0-9][a-zA-Z0-9-_]{1,61}[a-zA-Z0-9]))\.([a-zA-Z]{2,6}|[a-zA-Z0-9-]{2,30}\.[a-zA-Z]{2,3})$')

    if not domain_check.match(args.domain):
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: domain or user is not valid'
        
        print(json.dumps(json_return))

        exit(1)

    json_return['progress']=25
    json_return['message']='Is a valid domain and user'

    print(json.dumps(json_return))

    domain_search=re.compile('^.*@'+args.domain)

    try:

        stat_group=os.stat('/home/%s' % args.domain)

        uid=stat_group.st_uid

        user_domain=pwd.getpwuid(uid)[0]
        
    except:
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: cannot delete the user'

        print(json.dumps(json_return))
        exit(1)

    final_domains=[]

    with open('/etc/postfix/virtual_mailbox') as f:
        for domain in f:
            if domain_search.match(domain):
                #print(" ".split(domain.strip()))
                user_mail, user=domain.strip().split(" ")
                # delete user

                if not domain_search.match(user):

                    try:
                        user_pwd=pwd.getpwnam(user)

                        if call("sudo userdel -r %s" % user,  shell=True, stdout=DEVNULL, stderr=DEVNULL) > 0:

                            json_return['error']=1
                            json_return['status']=1
                            json_return['progress']=100
                            json_return['message']='Error: cannot delete the user'

                            print(json.dumps(json_return))
                            exit(1)

                    except KeyError:
                        json_return['error']=1
                        json_return['status']=1
                        json_return['progress']=100
                        json_return['message']='Error: user no exists'

                        print(json.dumps(json_return))
                        sys.exit(1)
		    


            else:
                final_domains.append(domain.strip())

        final_domains_file=""

        if len(final_domains)>0:
            final_domains_file="\n".join(final_domains)

        with open('/etc/postfix/virtual_mailbox', 'w') as f:
            if f.write(final_domains_file) or final_domains_file=="":
                json_return['progress']=50
                json_return['message']='Deleted users from mailboxes'

                print(json.dumps(json_return))

            else:
                json_return['error']=1
                json_return['status']=1
                json_return['progress']=100
                json_return['message']='Error: cannot update mailboxes'

                print(json.dumps(json_return))

                sys.exit(1)

        #Delete account
        # Delete user
        
        if call("sudo userdel -r %s" % user_domain,  shell=True, stdout=DEVNULL, stderr=DEVNULL) > 0:

            json_return['error']=1
            json_return['status']=1
            json_return['progress']=100
            json_return['message']='Error: cannot delete the user'

            print(json.dumps(json_return))
            exit(1)
        else:
            json_return['progress']=75
            json_return['message']='Deleted domain user from system'

            print(json.dumps(json_return))

        # Delete from virtual_domain

        line_domain=args.domain+' '+args.domain
        final_domains=[]
        with open('/etc/postfix/virtual_domains') as f:
            for domain in f:
                if domain.strip()!=line_domain:
                    final_domains.append(domain.strip())
                    
        final_domains_file=""

        if len(final_domains)>0:
            final_domains_file="\n".join(final_domains) 

        with open('/etc/postfix/virtual_domains', 'w') as f:
            if f.write(final_domains_file) or final_domains_file=="":
                json_return['progress']=85
                json_return['message']='Deleted domain from virtual domains file'

                print(json.dumps(json_return))
            else:
                json_return['error']=1
                json_return['status']=1
                json_return['progress']=100
                json_return['message']='Error: cannot update virtual domains file'

                print(json.dumps(json_return))

                sys.exit(1)

        # Refresh virtual_mailbox and virtual_domains
        
        
        if call("postmap hash:/etc/postfix/virtual_mailbox",  shell=True, stdout=DEVNULL) > 0:

            json_return['error']=1
            json_return['status']=1
            json_return['progress']=100
            json_return['message']='Error: cannot refresh the mailbox mapper'

            print(json.dumps(json_return))

            exit(1)
    
        if call("postmap hash:/etc/postfix/virtual_domains",  shell=True, stdout=DEVNULL) > 0:

            json_return['error']=1
            json_return['status']=1
            json_return['progress']=100
            json_return['message']='Error: cannot refresh the mailbox mapper'

            print(json.dumps(json_return))

            exit(1)

        json_return['progress']=100
        json_return['status']=1
        json_return['message']='Domain and related accounts deleted successfully'

        print(json.dumps(json_return))

    """

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
    """

if __name__=='__main__':
    remove_user()

