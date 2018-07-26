__author__ = 'romanovsky'

import sys
import datetime
from time import strftime

from lib.database import Database
from lib.openldap import LDAP
from lib.vassar_email import VassarEmail

fall_term = '201803'
spring_term = '201901'
m = VassarEmail()

#Banner Oracle Database
db = Database("oracle")
if hasattr(db, 'cn'):
    print ("database connect")
else:
    print ("no database connection", db.error)
    m.send('no oracle connection')
    sys.exit()

#ldap.vassar.edu
ldap = LDAP()
#print(ldap.__dict__)
if hasattr(ldap,'cn'):
    print ("ldap connect")
else:
    print ("no ldap connection")
    sys.exit()


#Enrollment::Courses
new_courses = db.course(fall_term, 'new')

for res in new_courses:
    attrs = {}
    attrs['objectclass'] = ['top','groupOfUniqueNames']
    attrs['cn'] = str(res[0])
    attrs['description'] = str(res[0])+' classroom group'
    attrs['uniqueMember'] = 'uid=placeholder,ou=people,dc=vassar,dc=edu'
    dn = 'cn='+str(res[0])+',ou=courses,ou=groups,dc=vassar,dc=edu'

    ldap.add(dn, attrs)

ldap.close()
db.close()

#ldap.search('ou=people,dc=vassar,dc=edu','(uid=romanovsky)','cn')
#ldap.close()
