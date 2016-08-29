#!/usr/bin/python3

from modules.mail.models.mail import DomainMail
from paramecio.cromosoma.webmodel import WebModel

def post_task(task):
    
    conn=WebModel.connection()
    
    domainmail=DomainMail(conn)
    
    if 'domain_id' in task.extra_data:
        
        domainmail.create_forms()
        
        domainmail.reset_require()
        
        domainmail.set_conditions('where id=%s', [task.extra_data['domain_id']])       
        
        if domainmail.update({'quota': int(task.extra_data['quota'])}):
    
            return True
        else:
            
            task.error_post_task=domainmail.show_errors()
            
            return False

    return False
