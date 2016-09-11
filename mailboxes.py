#!/usr/bin/python3

from bottle import get, route, post
from settings import config, config_admin
from paramecio.citoplasma.mtemplates import env_theme, PTemplate
from paramecio.citoplasma.i18n import load_lang, I18n
from paramecio.citoplasma.urls import redirect, make_url
from paramecio.citoplasma.sessions import get_session
from paramecio.citoplasma.adminutils import check_login, get_menu, get_language
from paramecio.citoplasma.base_admin import base_admin
from paramecio.citoplasma.lists import SimpleList
from paramecio.citoplasma.httputils import GetPostFiles
from paramecio.cromosoma.webmodel import WebModel
from paramecio.cromosoma import coreforms
from paramecio.cromosoma.formsutils import show_form, CheckForm
from modules.pastafari.models.servers import Server, ServerGroup, ServerGroupTask, StatusDisk, DataServer
from modules.pastafari.models.tasks import Task, LogTask
from modules.mail.models.mail import DomainMail, MailBox
from paramecio.citoplasma.filesize import filesize
from modules.pastafari.libraries.configclass import config_task
from collections import OrderedDict
import copy
import requests

server_task=config_task.server_task

server_task=server_task+'/exec/'+config_task.api_key+'/'

pastafari_folder='pastafari'

if hasattr(config, 'pastafari_folder'):
    pastafari_folder=config.pastafari_folder

load_lang(['paramecio', 'admin'], ['paramecio', 'common'])

env=env_theme(__file__)

@route('/'+pastafari_folder+'/mail/mailboxes')
@route('/'+pastafari_folder+'/mail/mailboxes/<domain_id:int>')
def mailboxes(domain_id=0):
    
    args={'domain_id': domain_id}
    
    return base_admin(admin_mailboxes, env, 'Mailboxes', **args)

def admin_mailboxes(connection, t, s, **args):
    
    conn=WebModel.connection()
    
    domain=DomainMail(conn)
    
    domainmail=MailBox(conn)
    
    select_form_group=coreforms.SelectModelForm('group_id', args['domain_id'], domain, 'domain', 'id')
        
    select_form_group.name_field_id='change_domain_id_form'
    
    mailbox_list=SimpleList(domainmail, '', t)
    
    mailbox_list.fields_showed=['mailbox', 'domain_id']
    
    mailbox_list.raw_query=False
    
    mailbox_list.search_fields=['mailbox']
    
    return t.load_template('mail/mailboxes.phtml', select_form=select_form_group.form(), mailbox_list=mailbox_list, domain_id=args['domain_id'])

@route('/'+pastafari_folder+'/mail/mailboxes/add/<domain_id:int>')
@get('/'+pastafari_folder+'/mail/mailboxes/add/<domain_id:int>/add:int>')
def add_form_mailbox(domain_id, add=0):
    
    args={'domain_id': domain_id}
    
    conn=WebModel.connection()
    
    domain=DomainMail(conn)
    
    arr_domain=domain.select_a_row(domain_id, ['domain'])
    
    if arr_domain:
    
        mailbox=MailBox(conn)
        
        args['domain_id']=domain_id
        
        args['mailbox']=mailbox
        
        args['domain']=arr_domain['domain']
        
        args['post']={}
        
        args['yes_error']=False
        
        args['pass_values']=False
        
        return base_admin(form_admin_mailbox, env, 'Add Mailbox - '+arr_domain['domain'], **args)
        
    else:
        
        return ""

def form_admin_mailbox(connection, t, s, **args):
    
    args['mailbox'].fields['mailbox'].name_form=coreforms.SimpleTextForm
    
    args['mailbox'].create_forms(['mailbox'])
    
    args['mailbox'].forms['mailbox'].after_text='@'+args['domain']
    
    form=show_form(args['post'], args['mailbox'].forms, t, args['yes_error'], args['pass_values'])
    
    return t.load_template('mail/add_mailbox.phtml', forms=form, url_post=make_url(pastafari_folder+'/mail/mailboxes/addmailbox/'+str(args['domain_id'])))
    

@post('/'+pastafari_folder+'/mail/mailboxes/addmailbox/<domain_id:int>')
def add_mailbox(domain_id):
    
    args={'domain_id': domain_id}
    
    conn=WebModel.connection()
    
    domain=DomainMail(conn)
    
    arr_domain=domain.select_a_row(domain_id, ['domain'])
    
    if arr_domain:
        
        args['arr_domain']=arr_domain
        
        args['domain']=domain
        
        return base_admin(save_admin_mailbox, env, 'Save Mailbox - '+arr_domain['domain'], **args)
        
    else:
        
        return ""


def save_admin_mailbox(connection, t, s, **args):
    
    getpost=GetPostFiles()
    
    getpost.obtain_post()
    
    mboxmodel=MailBox(connection)
        
    args['mailbox']=mboxmodel
    
    args['domain']=args['arr_domain']['domain']
    
    args['post']=getpost.post
    
    args['yes_error']=True
    
    args['pass_values']=True
    
    if 'mailbox' in getpost.post:
        
        mailbox=getpost.post['mailbox']+'@'+args['arr_domain']['domain']
        
        mailbox=mboxmodel.fields['mailbox'].check(mailbox)
        
        if mboxmodel.fields['mailbox'].error==False:
            
            # Check if in database
            
            c=mboxmodel.set_conditions('WHERE mailbox=%s', [mailbox]).select_count()
            
            if c>0:
                
                mboxmodel.fields['mailbox'].error=True
                mboxmodel.fields['mailbox'].txt_error=I18n.lang('mail', 'mailbox_exists', 'Mailbox exists in the server')

                return form_admin_mailbox(connection, t, s, **args)
            else:
                
                # insert mailbox
                
                mboxmodel.create_forms()
                
                if mboxmodel.insert({'mailbox': mailbox, 'domain_id': args['domain_id']}):
                
                    #Insert task with extra_data with mailbox created
                    
                    pass
                else:
                    
                    return 'Cannot insert the mailbox: '+mboxmodel.show_errors()
                    
        else:
            
            return mboxmodel.fields['mailbox'].txt_error
            
    
    return ""


