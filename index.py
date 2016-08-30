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
from modules.mail.models.mail import DomainMail
from paramecio.citoplasma.filesize import filesize
from modules.pastafari.libraries.configclass import config_task
#from modules.mail.models.mail import MailServer, MailServerGroup
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

@route('/'+pastafari_folder+'/mail')
def frontend():
    
    return base_admin(admin_groups, env, 'Mail servers')

def admin_groups(connection, t, s):
    
    server=Server(connection)
    data_server=DataServer(connection)
    
    data_server.set_conditions('where dataserver.ip IN (select ip from servergrouptask where name_task="standalone_postfix")', [])
    
    data_server.set_order(['id'], [1])
    
    #data_server.set_limit([1])
    
    arr_servers=data_server.select_to_array()
    #print(data_server.last_query)
    # Horrible hack, need fix to most elegant method for get the query for disk
    
    for k,v in enumerate(arr_servers):
        z=0
        check_disk=[]
        num_disks=0
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
    
    domain_list.fields_showed=['domain']
    
    domain_list.arr_extra_options=[mail_options]

    return t.load_template('mail/domains.phtml', hostname=arr_server['hostname'], domains=domain_list.show(), server_id=arr_server['id'])

@route('/'+pastafari_folder+'/mail/add_domain/<server_id:int>')
def add_domain(server_id):
    
    args={'server_id': server_id}
    
    args['request']='GET'
    
    return base_admin(form_add_domain, env, 'Mail servers - Add domain', **args)

def form_add_domain(connection, t, s, **args):

    server=Server(connection)
    
    domains=DomainMail(connection)
    
    domains.create_forms(['domain', 'group', 'quota'])
    
    domains.valid_fields.append('ip')
    
    domains.valid_fields.append('server')
    
    arr_server=server.select_a_row(args['server_id'], ['id', 'hostname', 'ip', 'os_codename'])
    
    if args['request']=='GET':
        
        forms=show_form({}, domains.forms, t, False, False)
        
        return t.load_template('mail/add_domain.phtml', hostname=arr_server['hostname'], server_id=arr_server['id'], forms=forms)
    
    else:
        
        task=Task(connection)
        logtask=LogTask(connection)
        
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
            
            url=make_url('pastafari/mail/domains/'+str(arr_server['id']))
            
            if domains.insert({'domain': post['domain'], 'group': post['group'], 'quota': post['quota'], 'server': arr_server['id'], 'ip': arr_server['ip']}):
                
                domain_id=domains.insert_id()
                
                # Insert task
                
                commands_to_execute=[]
                                
                commands_to_execute.append(['modules/mail/utilities/'+arr_server['os_codename']+'/add_domain.py', '--domain '+post['domain']+' --group '+post['group']+' --quota '+str(post['quota']), ''])
                
                task.create_forms()
                logtask.create_forms()
                
                if task.insert({'name_task': 'add_domain','description_task': I18n.lang('mail', 'add_domain', 'Adding domain to the server...'), 'url_return': url, 'files':  [], 'commands_to_execute': commands_to_execute, 'delete_files': [], 'delete_directories': [], 'server': arr_server['ip']}):
                    
                    task_id=task.insert_id()
                                                    
                    #try:
                    
                    r=requests.get(server_task+str(task_id))
                    
                    arr_data=r.json()
                    
                    arr_data['task_id']=task_id
                    
                    if not logtask.insert(arr_data):
                        
                        return "Error:Wrong format of json data..."
                    else:
                        
                        redirect(make_url(pastafari_folder+'/showprogress/'+str(task_id)+'/'+arr_server['ip']))
                        
                        #return t_admin.load_template('pastafari/ajax_progress.phtml', title='Adding monitoritation to the server...') #"Load template with ajax..."
                    """
                    except:
                        
                        logtask.conditions=['WHERE id=%s', [task_id]]
                        
                        task.reset_require()
                        
                        task.set_conditions('where id=%s', [task_id])
                        
                        task.update({'status': 1, 'error': 1})
                        
                        # Delete domain
                        
                        domains.set_conditions('where id=%s', [domain_id])
                        
                        domains.delete()
                        
                        return "Error:cannot connect to task server, check the url for it..."
                    """
                else:
                    
                    return "Cannot insert the new domain"
            else:
                 
                 return domains.show_errors()
                  
            
            #redirect(make_url(pastafari_folder+'/mail/add_domain/'+str(arr_server['id'])))
        

@post('/'+pastafari_folder+'/mail/add_domain/<server_id:int>')
def add_domain_db(server_id):
    
    args={'server_id': server_id}
    
    args['request']='POST'
    
    return base_admin(form_add_domain, env, 'Mail servers - Add domain', **args)
    
    pass

@route('/'+pastafari_folder+'/mail/delete_domain/<domain_id:int>')
@route('/'+pastafari_folder+'/mail/delete_domain/<domain_id:int>/<delete:int>')
def delete_domain(domain_id, delete=0):
    
    args={'domain_id': domain_id, 'delete': delete}
    
    if delete==0:
    
        return base_admin(form_delete_domain, env, 'Mail servers - Delete domain', **args)
    else:
        
        conn=WebModel.connection()
        
        server=Server(conn)
    
        domains=DomainMail(conn)
        
        task=Task(conn)
        logtask=LogTask(conn)
        
        domains.set_conditions('where id=%s', [domain_id])
        
        arr_domain=domains.select_a_row(domain_id, ['domain', 'ip'])
        
        server.set_conditions('where ip=%s', [arr_domain['ip']])
        
        arr_server=server.select_a_row_where(['id', 'hostname', 'os_codename'])
        
        commands_to_execute=[]
                                
        commands_to_execute.append(['modules/mail/utilities/'+arr_server['os_codename']+'/remove_domain.py', '--domain '+arr_domain['domain'], ''])
        
        url=make_url('pastafari/mail/domains/'+str(arr_server['id']))
        
        task.create_forms()
        logtask.create_forms()
        
        if task.insert({'name_task': 'add_domain','description_task': I18n.lang('mail', 'delete_domain', 'Deleting domain '+arr_domain['domain']+' to the server...'), 'url_return': url, 'files':  [], 'commands_to_execute': commands_to_execute, 'delete_files': [], 'delete_directories': [], 'server': arr_domain['ip'], 'post_func': 'modules.mail.libraries.func_tasks', 'extra_data': {'domain_id': domain_id} }):
            
            task_id=task.insert_id()
                                            
            #try:
            
            r=requests.get(server_task+str(task_id))
            
            arr_data=r.json()
            
            arr_data['task_id']=task_id
            
            if not logtask.insert(arr_data):
                
                return "Error:Wrong format of json data..."
            else:
                
                redirect(make_url(pastafari_folder+'/showprogress/'+str(task_id)+'/'+arr_domain['ip']))
        else:
            
            return "Cannot insert the task"
        
        return ""
    

def form_delete_domain(connection, t, s, **args):
    
    if args['delete']==0:
    
        return '<form method="get" action="'+make_url(pastafari_folder+'/mail/delete_domain/'+str(args['domain_id'])+'/1')+'"><p><input type="submit" value="Delete domain?"/></p></form>'
    else:
        return "Error: cannot delete the domain"

@route('/'+pastafari_folder+'/mail/change_quota/<domain_id:int>')
@route('/'+pastafari_folder+'/mail/change_quota/<domain_id:int>/<change:int>')
def change_quota(domain_id, change=0):
    
    args={'domain_id': domain_id, 'change': change}
    
    if change==0:
    
        return base_admin(form_change_quota_domain, env, 'Mail servers - Change domain quota', **args)
    else:
        
        conn=WebModel.connection()
        
        server=Server(conn)
    
        domains=DomainMail(conn)
        
        task=Task(conn)
        logtask=LogTask(conn)
        
        domains.set_conditions('where id=%s', [args['domain_id']])
        
        arr_domain=domains.select_a_row(args['domain_id'], ['id', 'domain', 'ip', 'quota', 'group'])
        
        getpostfiles=GetPostFiles()
        
        getpostfiles.obtain_get()
        
        getpostfiles.get['quota']=getpostfiles.get.get('quota', '0')
        
        server.set_conditions('where ip=%s', [arr_domain['ip']])
        
        arr_server=server.select_a_row_where(['id', 'hostname', 'os_codename'])
        
        try:
            
            quota=int(getpostfiles.get['quota'])
        
        except:
            
            quota=arr_domain['quota']
            
        commands_to_execute=[]
                                
        commands_to_execute.append(['modules/mail/utilities/'+arr_server['os_codename']+'/change_quota.py', '--group '+arr_domain['group']+' --quota '+str(quota), ''])
        
        url=make_url('pastafari/mail/domains/'+str(arr_server['id']))
        
        task.create_forms()
        logtask.create_forms()
        
        if task.insert({'name_task': 'add_domain','description_task': I18n.lang('mail', 'change_quota', 'Changing quota of domain '+arr_domain['domain']), 'url_return': url, 'files':  [], 'commands_to_execute': commands_to_execute, 'delete_files': [], 'delete_directories': [], 'server': arr_domain['ip'], 'post_func': 'modules.mail.libraries.change_quota_tasks', 'extra_data': {'domain_id': domain_id, 'quota': quota} }):
            
            task_id=task.insert_id()
                                            
            #try:
            
            r=requests.get(server_task+str(task_id))
            
            arr_data=r.json()
            
            arr_data['task_id']=task_id
            
            if not logtask.insert(arr_data):
                
                return "Error:Wrong format of json data..."
            else:
                
                redirect(make_url(pastafari_folder+'/showprogress/'+str(task_id)+'/'+arr_domain['ip']))
        else:
            
            return "Cannot insert the task"
            
        

def form_change_quota_domain(connection, t, s, **args):
    
    if args['change']==0:
        
        conn=WebModel.connection()
        
        server=Server(conn)
    
        domains=DomainMail(conn)
        
        domains.set_conditions('where id=%s', [args['domain_id']])
        
        arr_domain=domains.select_a_row(args['domain_id'], ['id', 'domain', 'ip', 'quota'])
    
        return t.load_template('mail/change_quota.phtml', quota=arr_domain['quota'], domain_id=arr_domain['id'], domain=arr_domain['domain'])
    
        #'<form method="get" action="'+make_url(pastafari_folder+'/mail/delete_domain/'+str(args['domain_id'])+'/1')+'"><p><input type="submit" value="Delete domain?"/></p></form>'
    else:
        return "Error: cannot change the quota the domain"

def mail_options(url, id, arr_row):
    
    arr_options=[]
    
    arr_options.append('<a href="'+make_url('pastafari/mail/mailboxes/'+str(id))+'">Mailboxes</a>')
    arr_options.append('<a href="'+make_url(pastafari_folder+'/mail/change_quota/'+str(id))+'">Change quota</a>')
    arr_options.append('<a href="'+make_url(pastafari_folder+'/mail/delete_domain/'+str(id))+'">Delete</a>')
    
    return arr_options
