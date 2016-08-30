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
    
    mailbox_list.yes_search=False
    
    return t.load_template('mail/mailboxes.phtml', select_form=select_form_group.form(), mailbox_list=mailbox_list, domain_id=args['domain_id'])

