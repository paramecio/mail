#!/usr/bin/python3

from bottle import get, route, post
from settings import config, config_admin
from paramecio.citoplasma.mtemplates import env_theme, PTemplate
from paramecio.citoplasma.i18n import load_lang, I18n
from paramecio.citoplasma.sessions import get_session
from paramecio.citoplasma.adminutils import check_login, get_menu, get_language, base_admin
from paramecio.citoplasma.lists import SimpleList
from paramecio.citoplasma.httputils import GetPostFiles
from paramecio.cromosoma.webmodel import WebModel
from paramecio.cromosoma import coreforms
from paramecio.cromosoma.formsutils import show_form
from modules.pastafari.models.servers import Server, ServerGroup
from modules.mail.models.mail import MailServer, MailServerGroup
from collections import OrderedDict


pastafari_folder='pastafari'

if hasattr(config, 'pastafari_folder'):
    pastafari_folder=config.pastafari_folder

load_lang(['paramecio', 'admin'], ['paramecio', 'common'])

env=env_theme(__file__)

@route('/'+pastafari_folder+'/mail')
def frontend():
    
    return base_admin(admin_groups, env, 'Mail servers')

def admin_groups(connection, t, s):
    
    groups_list=SimpleList(MailServerGroup(connection), '', t)
        
    groups_list.yes_search=False
    
    return t.load_template('mail/admin.phtml', groups_list=groups_list.show())

@route('/'+pastafari_folder+'/mail/addgroup')
def viewform():
    
    return base_admin(admin_form_groups, env, 'Add new mail server')
    
def admin_form_groups(connection, t, s):
    
    return group_form(t, connection)

def group_form(t, connection, yes_error=False, pass_values=False, **args):
    
    arr_form=OrderedDict()
        
    arr_form['group_id']=coreforms. SelectModelForm('group_id', '', ServerGroup(connection), 'name', 'id')
    
    arr_form['group_id'].required=True
    
    arr_form['group_id'].label='Choose server group. If the group was added, simply add the new servers in the group.'

    forms=show_form(args, arr_form, t, yes_error, pass_values)

    return t.load_template('mail/addform.phtml', forms=forms)

@post('/'+pastafari_folder+'/mail/addservers')
def addservers():
    return ""
    
