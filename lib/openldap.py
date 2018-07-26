__author__ = 'romanovsky'

import sys
import ldap
import ldap.modlist as modlist
import ConfigParser

class LDAP:

    #based on input, create a new connection to that database
    def __init__(self):
        settings = ConfigParser.ConfigParser()
        settings.read('./assets/auth/auth.ini')
        self.ldaphost = settings.get('ldap','host')
        self.ldapbind = settings.get('ldap','User')
        self.ldappw = settings.get('ldap','PW')

        try:
            self.cn = ldap.initialize(self.ldaphost)
            self.cn.simple_bind_s(self.ldapbind, self.ldappw)
        except ldap.INVALID_CREDENTIALS as exc:
            print exc


    def search(self, base_dn, search, returning_attr):
        print self.cn.search_s(base_dn, ldap.SCOPE_SUBTREE, search, ['cn'])

    def add(self, dn, attrs):
        ldif = modlist.addModlist(attrs)
        try:
            self.cn.add_s(dn, ldif)
        except ldap.LDAPError as exc:
            print exc

    #close the database connection
    def close(self):
        self.cn.unbind_ext_s()
