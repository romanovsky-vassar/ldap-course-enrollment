__author__ = 'romanovsky'

import sys
import ldap
import ldap.modlist as modlist
import ConfigParser
import logging
from datetime import datetime

from lib.vassar_email import VassarEmail

logging.basicConfig(filename='./log/course-enrollment-sync.log',level=logging.DEBUG)

class LDAP:

    #based on input, create a new connection to that database
    def __init__(self):
        settings = ConfigParser.ConfigParser()
        self.valid_connection = True
        settings.read('./assets/auth/auth.ini')
        self.ldaphost = settings.get('ldap','host')
        self.ldapbind = settings.get('ldap','User')
        self.ldappw = settings.get('ldap','PW')

        try:
            self.cn = ldap.initialize(self.ldaphost)
            self.cn.simple_bind_s(self.ldapbind, self.ldappw)
        except ldap.INVALID_CREDENTIALS as exc:
            self.valid_connection = False
            print exc


    def search(self, base_dn, search, returning_attr):
        print self.cn.search_s(base_dn, ldap.SCOPE_SUBTREE, search, ['cn'])

    def add(self, dn, attrs):
        ldif = modlist.addModlist(attrs)
        logging.info('adding: '+dn+' '+str(datetime.now()) )
        try:
            self.cn.add_s(dn, ldif)
        except ldap.LDAPError as exc:
            print exc
            logging.debug('LDAPError - Add: '+dn+' '+str(exc)+' '+str(datetime.now()))
            VassarEmail.send('LDAPError - Course Enrollment Sync', dn+ ' ' + str(exc))


    def modify(self, dn, attr, value, type):
        switcher = {
        'ADD' : ldap.MOD_ADD,
        'DELETE' : ldap.MOD_DELETE
        }
        logging.info('modifying: '+type+' : '+dn+' '+str(datetime.now()) )
        try:
            self.cn.modify_s(dn, [(switcher.get(type),attr,value)] )
        except ldap.LDAPError as exc:
            print exc
            logging.debug('LDAPError - Modify: '+dn+' '+str(exc)+' '+str(datetime.now()))
            VassarEmail.send('LDAPError - Course Enrollment Sync', dn+ ' ' + str(exc))

    #close the database connection
    def close(self):
        self.cn.unbind_ext_s()
