__author__ = 'romanovsky'

l = ldap.initialize("ldap://ldap03.vassar.edu")

__author__ = 'romanovsky'

import ldap
import ConfigParser

class LDAP:

    #based on input, create a new connection to that database
    def __init__(self):
        settings = ConfigParser.ConfigParser()
        settings.read('./assets/auth/auth.ini')
        self.dbuser = settings.get(ldap,'User')

        try:
            self.cn = ldap.initialize()
        except ldap.CONNECT_ERROR as exc:
            #self.error = "no database connection"
            #self.error = e.message
	    error, = exc.args
            self.error = error.desc

    #close the database connection
    def close(self):
        self.cn.close
