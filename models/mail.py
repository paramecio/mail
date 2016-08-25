from paramecio.cromosoma.webmodel import WebModel
from paramecio.cromosoma import corefields
from paramecio.cromosoma.extrafields.ipfield import IpField
from paramecio.cromosoma.extrafields.urlfield import DomainField
from modules.pastafari.models.servers import Server, ServerGroup

class MailServer(WebModel):
    
    def __init__(self, connection):
        
        super().__init__(connection)
        
        self.register(corefields.ForeignKeyField('server', Server(connection), size=11, required=True, identifier_field='id', named_field="hostname", select_fields=[]))
        

class MailServerGroup(WebModel):
    
    def __init__(self, connection):
        
        super().__init__(connection)
        
        self.register(corefields.ForeignKeyField('group', ServerGroup(connection), size=11, required=True, identifier_field='id', named_field="name", select_fields=[]))
        

class DomainMail(WebModel):
    
    def __init__(self, connection):
        
        super().__init__(connection)
        
        self.register(DomainField('domain'), True)
        self.register(IpField('ip'), True)
        self.register(corefields.ForeignKeyField('server', Server(connection), size=11, required=True, identifier_field='id', named_field="hostname", select_fields=['ip']))
        self.register(corefields.CharField('group'), True)
        self.register(corefields.IntegerField('quota'))
