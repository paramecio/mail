#!/usr/bin/python3

from bottle import get, route, post
from settings import config, config_admin
from paramecio.citoplasma.mtemplates import env_theme, PTemplate
from paramecio.citoplasma.i18n import load_lang, I18n
from paramecio.citoplasma.urls import redirect, make_url
from paramecio.citoplasma.sessions import get_session
from paramecio.citoplasma.adminutils import check_login, get_menu, get_language, base_admin
from paramecio.citoplasma.lists import SimpleList
from paramecio.citoplasma.httputils import GetPostFiles
from paramecio.cromosoma.webmodel import WebModel
from paramecio.cromosoma import coreforms
from paramecio.cromosoma.formsutils import show_form, CheckForm
from modules.pastafari.models.servers import Server, ServerGroup, ServerGroupTask, StatusDisk, DataServer
from modules.mail.models.mail import DomainMail
from paramecio.citoplasma.filesize import filesize
#from modules.mail.models.mail import MailServer, MailServerGroup
from collections import OrderedDict
import copy


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
        arr_servers[k]['memory_id_free']=filesize(arr_servers[k]['memory_id_free'])+' free'
        arr_servers[k]['memory_id_cached']=filesize(arr_servers[k]['memory_id_cached'])+' cached'
        arr_servers[k]['memory_id_used']=filesize(arr_servers[k]['memory_id_used'])+' used'
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

@route('/'+pastafari_folder+'/mail/domains/<server_id:int>')
def domains(server_id):
    
    args={'server_id': server_id}
    
    return base_admin(admin_domains, env, 'Mail servers - Domains', **args)

def admin_domains(connection, t, s, **args):

    server=Server(connection)
    
    domains=DomainMail(connection)
    
    arr_server=server.select_a_row(args['server_id'], ['id', 'hostname'])
    
    domain_list=SimpleList(domains, '', t)
    
    domain_list.fields_showed=['domain', 'server']

    return t.load_template('mail/domains.phtml', hostname=arr_server['hostname'], domains=domain_list.show(), server_id=arr_server['id'])

@route('/'+pastafari_folder+'/mail/add_domain/<server_id:int>')
def add_domain(server_id):
    
    args={'server_id': server_id}
    
    args['request']='GET'
    
    return base_admin(form_add_domain, env, 'Mail servers - Add domain', **args)

def form_add_domain(connection, t, s, **args):

    server=Server(connection)
    
    domains=DomainMail(connection)
    
    domains.create_forms(['domain'])
    
    arr_server=server.select_a_row(args['server_id'], ['id', 'hostname', 'ip'])
    
    if args['request']=='GET':
        
        forms=show_form({}, domains.forms, t, False, False)
        
        return t.load_template('mail/add_domain.phtml', hostname=arr_server['hostname'], server_id=arr_server['id'], forms=forms)
    
    else:
        
        getpost=GetPostFiles()
    
        getpost.obtain_post()
        
        check_form=CheckForm()
        
        arr_post=copy.deepcopy(getpost.post)
        
        post, arr_form=check_form.check(arr_post, domains.forms)
        
        if check_form.error>0:
            
            #getpost.obtain_post()
            
            forms=show_form(getpost.post, arr_form, t, True, True)
        
            return t.load_template('mail/add_domain.phtml', hostname=arr_server['hostname'], server_id=arr_server['id'], forms=forms)
            
        else:
            return "Vamos palla"
            
            #redirect(make_url(pastafari_folder+'/mail/add_domain/'+str(arr_server['id'])))
        

@post('/'+pastafari_folder+'/mail/add_domain/<server_id:int>')
def add_domain_db(server_id):
    
    args={'server_id': server_id}
    
    args['request']='POST'
    
    return base_admin(form_add_domain, env, 'Mail servers - Add domain', **args)
    
    pass

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
