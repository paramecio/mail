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
from modules.pastafari.models.servers import Server, ServerGroup, ServerGroupTask, StatusDisk, DataServer
from paramecio.citoplasma.filesize import filesize
#from modules.mail.models.mail import MailServer, MailServerGroup
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
    
    server=Server(connection)
    data_server=DataServer(connection)
    
    data_server.set_conditions('where dataserver.ip IN (select ip from servergrouptask where name_task="standalone_postfix")', [])
    
    data_server.set_order(['id'], [1])
    
    data_server.set_limit([1])
    
    arr_servers=data_server.select_to_array()
    
    # Horrible hack, need fix to most elegant method for get the query for disk
    
    z=0
    check_disk=[]
    num_disks=0
    for k,v in enumerate(arr_servers):
        for z in range(0, 6):
            if not arr_servers[k]['disk'+str(z)+'_id'] in check_disk:
                check_disk.append(arr_servers[k]['disk'+str(z)+'_id'])
                arr_servers[k]['disk'+str(z)+'_id_free']=str(filesize(arr_servers[k]['disk'+str(z)+'_id_free']))+' free'
                num_disks+=1
            else:
                
                del arr_servers[k]['disk'+str(z)+'_id']
                del arr_servers[k]['disk'+str(z)+'_id_free']
                del arr_servers[k]['disk'+str(z)+'_id_used']
                del arr_servers[k]['disk'+str(z)+'_id_size']
                del arr_servers[k]['disk'+str(z)+'_id_percent']
    
    return t.load_template('mail/admin.phtml', servers=arr_servers, num_disks=num_disks)
    
    """
    data_server.set_order(['free'], [1])
    
    arr_disk=disk_server.select_to_array()
    
    arr_servers=OrderedDict()
    
    for disk in arr_disk:
        
        if disk['server_id'] in arr_servers:
            
            arr_servers[disk['server_id']].append(disk)
        
        else:
            arr_servers[disk['server_id']]=[disk]
    
    return t.load_template('mail/admin.phtml', servers=arr_servers)
    """
    
    """
    #server.fields['server_date'].label='Status'
    
    server.set_conditions('where ip IN (select ip from servergrouptask where name_task="standalone_postfix")', [])
    
    groups_list=SimpleList(disks_server, '', t)
    
    groups_list.raw_query=False
    
    #groups_list.fields_showed=['hostname', 'ip', 'actual_idle', 'date']
    
    groups_list.yes_search=False
    
    return t.load_template('mail/admin.phtml', groups_list=groups_list.show())
    """
"""
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
    
"""
