#!/usr/bin/python3

from modules.mail.models.mail import DomainMail
from paramecio.cromosoma.webmodel import WebModel

def post_task(task):
    
    conn=WebModel.connection()
    
    domainmail=DomainMail(conn)
    
    if 'domain_id' in task.extra_data:
        
        domainmail.set_conditions('where id=%s', [task.extra_data['domain_id']])
        
        domainmail.delete()
    
    return True
