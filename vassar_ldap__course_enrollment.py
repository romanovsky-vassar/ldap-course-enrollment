__author__ = 'romanovsky'

import sys
from datetime import datetime
from datetime import timedelta
from time import strftime

from lib.database import Database
from lib.openldap import LDAP
from lib.vassar_email import VassarEmail

fall_term = '201803'
spring_term = '201901'

start_time = (datetime.now() - timedelta(minutes=10)).strftime('%d-%b-%Y %H:%M:%S').upper()

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
    # Course
    dn_course = 'cn='+str(res[0])+',ou=courses,ou=groups,dc=vassar,dc=edu'
    attr_course = 'uniqueMember'
    value_course = 'uid='+res[1]+',ou=people,dc=vassar,dc=edu'

    # Person
    dn_person = 'uid='+res[1]+',ou=people,dc=vassar,dc=edu'
    attr_person1 = 'vassarPersonClasses'
    value_person1 = res[0]
    attr_person2 = 'vassarPersonGroups'
    value_person2 = 'cn='+str(res[0])+',ou=courses,ou=groups,dc=vassar,dc=edu'

    if res[2].strip() in ['add']:
        # Do they already exist as a member of this course:
        res_cn = ldap.search(dn,'(uniqueMember='+value_course+')','cn')
        if res_cn:
            db.crosslistreserve('add', value_course, res[0])
        else:
            ldap.modify(dn_course, attr_course, value_course, 'ADD')
            ldap.modify(dn_person, attr_person1, value_person1, 'ADD')
            ldap.modify(dn_person, attr_person2, value_person2, 'ADD')

    if res[2].strip() in ['drop']:
        # Is this drop in holding:
        res_crosslist = db.crosslistsearch(value_course, res[0])
        print res_crosslist

        if res_crosslist:
            db.crosslistreserve('remove', value_course, res[0])
        else:
            ldap.modify(dn_course, attr_course, value_course, 'DELETE')
            ldap.modify(dn_person, attr_person1, value_person1, 'DELETE')
            ldap.modify(dn_person, attr_person2, value_person2, 'DELETE')


#res_cn = ldap.search('cn=MATH-241-01-2018A,ou=courses,ou=groups,dc=vassar,dc=edu','(uniqueMember=uid=isfurman,ou=people,dc=vassar,dc=edu)','uniqueMember')

ldap.close()
db.close()
