__author__ = 'romanovsky'

import sys
import cx_Oracle
import ConfigParser
import logging
from datetime import datetime

from lib.vassar_email import VassarEmail

logging.basicConfig(filename='/home/romanovsky/devel/python-project/ldap_student_course/log/course-enrollment-sync.log',level=logging.DEBUG)

class Database:
    valid_database = {"oracle" : "oracle",
                      "mysql" : "mysql"}

    #based on input, create a new connection to that database
    def __init__(self, database_platform):
        try:
            db = self.valid_database[database_platform]
        except KeyError:
            self.error = "invalid database"
        else:
            settings = ConfigParser.ConfigParser()
            settings.read('/home/romanovsky/devel/python-project/ldap_student_course/assets/auth/auth.ini')
            self.dbuser = settings.get(db,'User')
            self.dbpw = settings.get(db, 'PW')
            self.dbhost = settings.get(db, 'host')
            self.dbport = settings.get(db,'port')
            self.servicename = settings.get(db,'service_name')

        try:
            self.cn = cx_Oracle.connect('%s/%s@%s:%s/%s' % (self.dbuser, self.dbpw, \
            self.dbhost, self.dbport, self.servicename ))

        except cx_Oracle.DatabaseError as exc:
            error, = exc.args
            self.error = error.message
            logging.debug('No Oracle database connection: '+str(datetime.now()) )



    def course(self, term, status, start_time):
        if status == 'new':
            self.c1 = self.cn.cursor()
            self.course_collection = self.cn.cursor()
            try:
                self.c1.callproc("VASSAR_IAM.get_new_courses", [start_time,self.course_collection])
                self.c1.close()
            except cx_Oracle.DatabaseError as exc:
                error, = exc.args
                self.error = error.message
                logging.debug('Call Oracle Procedure Fail - VASSAR_IAM.get_new_courses - '+str(datetime.now()) )
                VassarEmail.send('LDAPError - Course Enrollment Sync', self.error)
        else:
            return null
        return self.course_collection



    def faculty(self, course_label):
        self.c1 = self.cn.cursor()
        self.course_faculty = self.cn.cursor()
        try:
            self.c1.callproc("VASSAR_IAM.get_course_faculty", [course_label, self.course_faculty])
            self.c1.close()
        except cx_Oracle.DatabaseError as exc:
            error, = exc.args
            self.error = error.message
            logging.debug('Call Oracle Procedure Fail - VASSAR_IAM.get_course_faculty - '+str(datetime.now()) )
            VassarEmail.send('LDAPError - Course Enrollment Sync', self.error)

        return self.course_faculty



    def enrollment(self, term, start_time):
        self.c1 = self.cn.cursor()
        self.course_enrollments = self.cn.cursor()

        try:
            self.c1.callproc("VASSAR_IAM.get_course_enroll_changes", [start_time,self.course_enrollments])
            self.c1.close()
        except cx_Oracle.DatabaseError as exc:
            error, = exc.args
            self.error = error.message
            logging.debug('Call Oracle Procedure Fail - VASSAR_IAM.get_course_enroll_changes - '+str(datetime.now()) )
            VassarEmail.send('LDAPError - Course Enrollment Sync', self.error)
            return null

        return self.course_enrollments

    def crosslistreserve(self, action, uid, course_label):
        self.c1 = self.cn.cursor()


        if action == 'add':
            param = {"1" : uid, "2" : course_label, "3" : str(datetime.now()) }
            try:
                self.c1.execute("INSERT INTO LDAPDATA.ADD_DROP_XLIST(UUID, COURSE_LABEL, ACT_DATE) values (:1, :2, :3)", param)
                self.cn.commit()
            except cx_Oracle.DatabaseError as exc:
                error, = exc.args
                self.error = error.message
                logging.debug('INSERT Error - LDAPDATA.ADD_DROP_XLIST - '+str(datetime.now()) )
                VassarEmail.send('LDAPError - Course Enrollment Sync', self.error)

        if action == 'remove':
            param = {"1" : uid, "2" : course_label}
            self.c1.execute("DELETE FROM LDAPDATA.ADD_DROP_XLIST WHERE UUID = :1 and COURSE_LABEL = :2", param)
            self.cn.commit()

        self.c1.close()


    def crosslistsearch(self, uid, course_label):
        self.c1 = self.cn.cursor()
        param = {"1" : uid, "2" : course_label}

        self.c1.execute("SELECT UUID FROM LDAPDATA.ADD_DROP_XLIST WHERE UUID = :1 and COURSE_LABEL = :2", param)
        res = self.c1.fetchone()

        return res

    #close the database connection
    def close(self):
        self.cn.close()
