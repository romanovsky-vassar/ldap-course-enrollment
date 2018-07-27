__author__ = 'romanovsky'

import sys
from datetime import datetime

from time import strftime

from lib.database import Database
from lib.openldap import LDAP
from lib.vassar_email import VassarEmail

fall_term = '201803'
spring_term = '201901'

start_time = '27-JUL-2018 20:00:00'

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
if ldap.valid_connection:
    print ("ldap connect")
else:
    print ("no ldap connection")
    VassarEmail.send('ERROR: LDAP/Course Sync', 'no ldap connection')
    sys.exit()


##
## Enrollment::Courses
##
new_courses = db.course(fall_term, 'new', start_time)

for res in new_courses:
    dn = 'cn='+str(res[0])+',ou=courses,ou=groups,dc=vassar,dc=edu'

    attrs = {}
    attrs['objectclass'] = ['top','groupOfUniqueNames']
    attrs['cn'] = str(res[0])
    attrs['description'] = str(res[0])+' classroom group'
    attrs['uniqueMember'] = 'uid=placeholder,ou=people,dc=vassar,dc=edu'

    ldap.add(dn, attrs)

    ##
    ## Enrollment::Course::Faculty
    ##
    course_faculty = db.faculty(str(res[0]) ) # Find the faculty for the course provided
    res = course_faculty.fetchone()
    attr = 'owner'
    value = 'uid='+res[0]+',ou=people,dc=vassar,dc=edu'
    ldap.modify(dn, attr, value, 'ADD') # Modify this DN for faculy member as owner


##
## Enrollment::AddDrop
##
course_enrollments = db.enrollment(fall_term, start_time)
for res in course_enrollments:
    dn = 'cn='+str(res[0])+',ou=courses,ou=groups,dc=vassar,dc=edu'
    attr = 'uniqueMember'
    value = 'uid='+res[1]+',ou=people,dc=vassar,dc=edu'

    if res[2].strip() in ['add']:
        ldap.modify(dn, attr, value, 'ADD')
    if res[2].strip() in ['drop']:
        ldap.modify(dn, attr, value, 'DELETE')

ldap.close()
db.close()



#ldap.search('ou=people,dc=vassar,dc=edu','(uid=romanovsky)','cn')
