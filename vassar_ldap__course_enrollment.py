__author__ = 'romanovsky'

import sys
from datetime import datetime
import logging

from time import strftime

from lib.database import Database
from lib.openldap import LDAP
from lib.vassar_email import VassarEmail

fall_term = '201803'
spring_term = '201901'
logging.basicConfig(filename='./log/course-enrollment-sync.log',level=logging.DEBUG)

VassarEmail.send('Starting LDAP/Course Sync', '')

#Banner Oracle Database
db = Database("oracle")
if hasattr(db, 'cn'):
    print ("database connect")
else:
    print ("no database connection", db.error)
    VassarEmail.send('ERROR: LDAP/Course Sync', 'no oracle connection')
    sys.exit()

#ldap.vassar.edu
ldap = LDAP()
#print(ldap.__dict__)

#if hasattr(ldap,'cn'):
if ldap.valid_connection:
    print ("ldap connect")
else:
    print ("no ldap connection")
    logging.debug('no ldap connection: '+str(datetime.now()) )
    sys.exit()


##
## Enrollment::Courses
##
new_courses = db.course(fall_term, 'new')

for res in new_courses:
    attrs = {}
    attrs['objectclass'] = ['top','groupOfUniqueNames']
    attrs['cn'] = str(res[0])
    attrs['description'] = str(res[0])+' classroom group'
    attrs['uniqueMember'] = 'uid=placeholder,ou=people,dc=vassar,dc=edu'
    dn = 'cn='+str(res[0])+',ou=courses,ou=groups,dc=vassar,dc=edu'

    ldap.add(dn, attrs)

    ## Enrollment::Course::Faculty
    

ldap.close()
db.close()

#ldap.search('ou=people,dc=vassar,dc=edu','(uid=romanovsky)','cn')
#ldap.close()
