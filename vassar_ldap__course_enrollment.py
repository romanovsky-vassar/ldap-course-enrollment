__author__ = 'romanovsky'

import cx_Oracle
import datetime
from time import strftime

from lib.database import Database
from lib.openldap import LDAP

db = Database("oracle")

if hasattr(db, 'cn'):
    print ("connect")
    db.close()

else:
    print ("no connection", db.error)

ldap = LDAP()
 
