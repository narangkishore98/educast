from flask import *
from flask_mail import *
from werkzeug import *
import os
import json
import random
import pymysql
import datetime
import time
app=Flask(__name__)
app.secret_key='edupass'

db=pymysql.connect("127.0.0.1","root","","educast")
#mail connection
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']='projecteducast@gmail.com'
app.config['MAIL_PASSWORD']='hypersecurity'
app.config['MAIL_USE_SSL']=True
app.config['MAIL_USE_TLS']=False
app.config['MAX_CONTENT_PATH']=1024*2048
mail=Mail(app)

#state getter
def stateGen():
    cursor=db.cursor()
    cursor.execute("SELECT * FROM STATES ORDER BY STATENAME")
    state=cursor.fetchall()
    cursor.close()
    return state
#password generator function
def passGen(l=8):
    r="".join(random.sample("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",l))
    return r
#homepage routing
@app.route("/")
def index():
    return render_template("index.html")

#homepage contactus handler
@app.route("/submit",methods=["POST"])
def takeQuery():
    if request.method == "POST" :
        name=request.form['name']
        email=request.form['email']
        phone=request.form['phone']
        query=request.form['query']
        cursor.execute("INSERT INTO QUERY (NAME, EMAIL, PHONE, QUERY) VALUES ('%s','%s','%s','%s')" %(name,email,phone,query))
        db.commit()
        return render_template("submit.html") 

############################################################
#school login page
@app.route("/school-login")
def s_login():
    if 'setuser' in session:
        return redirect(url_for('setuser'))
    if 'updocs' in session:
        return redirect(url_for('updocs'))
    if 'applicationid' in session:
        if 'username' in session:
            return redirect(url_for('school_dashboard',name=session['username']))
    return render_template("school/school-login.html")
#school loggin authentication
@app.route("/school-login/authenticate",methods=["POST"])
def s_login_authenticate():
    if request.method=="POST":
        db=pymysql.connect("127.0.0.1","root","","educast")
        cursor=db.cursor()
        username=request.form['username']
        password=request.form['password']
        result=cursor.execute("SELECT  A1.APPLICATIONID, A1.PASSWORD, A2.USERNAME,A1.STATUS FROM SCHOOLAPPLY AS A1 LEFT OUTER JOIN SCHOOLPROCEED AS A2  ON A1.APPLICATIONID=A2.APPLICATIONID WHERE (A1.APPLICATIONID='%s' OR A2.USERNAME='%s' ) AND (A1.PASSWORD='%s' OR A2.PASSWORD='%s')"%(username,username,password,password))
        if result>0:
            row=cursor.fetchone()
            cursor.close()
            db.close()
            session['applicationid']=row[0]
            print(row)
            print(row)
            if row[1] != None and row[3] == 0 or row[3]==1:
                session['updocs']='True'
                return redirect(url_for('updocs'))
            elif row[1]!=None and row[1]!="" and row[3] ==2 :
                session['setuser']='True'
                return redirect(url_for('setuser'))
            elif  row[3] ==3:
                session['deactivated']='True'
                return render_template('school/deactivated.html')
            else:
                session['username']=row[2]
                return redirect(url_for('school_dashboard',name=session['username']))
        else:
            return redirect(url_for('s_login',login=False))
#school logout
@app.route("/school-login/unauthenticate")
def s_login_unauthenticate():
    session.clear()
    return redirect(url_for('s_login'))

#upload docs
@app.route('/updocs')
def updocs():
    if 'applicationid' not in session or 'updocs' not in session:
        return redirect(url_for('s_login'))
    cursor=db.cursor()
    result=cursor.execute("SELECT FIRSTNAME,STATUS FROM SCHOOLAPPLY WHERE APPLICATIONID = '%s' "%session['applicationid'])
    row=cursor.fetchone()
    name=row[0]
    status=row[1]
    cursor.close()
    return render_template('school/updocs.html',name=name,status=status)
#upload backend uploader
@app.route('/uploader',methods=["POST"])
def uploader():
    if request.method=="POST":
        app.config['UPLOAD_FOLDER']="static/school/data"
        file1=request.files['file1']
        file1name=str(session['applicationid'])+"rc.pdf"
        file2=request.files['file2']
        file2name=str(session['applicationid'])+"id.pdf"
        file3=request.files['file3']
        file3name=str(session['applicationid'])+"ad.pdf"
        file4=request.files['file4']
        file4name=str(session['applicationid'])+"gst.pdf"
        file1.save(os.path.join(app.config['UPLOAD_FOLDER'],file1name))
        file2.save(os.path.join(app.config['UPLOAD_FOLDER'],file2name))
        file3.save(os.path.join(app.config['UPLOAD_FOLDER'],file3name))
        file4.save(os.path.join(app.config['UPLOAD_FOLDER'],file4name))
        cursor=db.cursor()
        cursor.execute("UPDATE SCHOOLAPPLY SET STATUS=1 WHERE APPLICATIONID='%s'"%session['applicationid'])
        db.commit()
        return redirect(url_for('updocs'))


#school dashboard
@app.route("/school/<name>") 
def school_dashboard(name):
    if 'updocs' in session:
        return redirect(url_for('updocs'))
    db=pymysql.connect("127.0.0.1","root","","educast")
    cursor=db.cursor()
    if 'applicationid' not in session:
        return redirect(url_for('s_login'))
    if 'setuser' in session:
        return redirect(url_for('setuser'))
    result = cursor.execute("SELECT * FROM SCHOOLAPPLY AS A1 ,SCHOOLPROCEED AS A2 WHERE  A1.APPLICATIONID=A2.APPLICATIONID AND A2.USERNAME='%s' AND A1.APPLICATIONID='%s'"%(name,session['applicationid']))
    if result > 0:
        row=cursor.fetchone()
        cursor.close()
        db.close()
        return render_template('school/dashboard.html',row=row)
    else:
        return render_template('school/unauthorized-access.html')

#school employee ##### EMPLOYEE SECTION STARTS.......................................................
@app.route('/school/<name>/faculty')
def school_faculty(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('s_login'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    cursor=db.cursor()
    result=cursor.execute("SELECT * FROM SCHOOLAPPLY AS A1, SCHOOLPROCEED AS A2  WHERE A1.APPLICATIONID=A2.APPLICATIONID AND A1.APPLICATIONID='%s'"%session['applicationid'])
    row=cursor.fetchone()  
    cursor.close()  
    return render_template('school/faculty.html',data=row)

#school employee add
@app.route('/school/<name>/faculty/add')
def school_faculty_add(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    states=stateGen()
    return render_template('school/faculty-add.html',states=states)

#school employee add handler
@app.route('/school/<name>/faculty/add/handler',methods=["POST"])
def school_faculty_add_handler(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    if request.method=="POST":
        name=request.form['facultyname']
        mobile=request.form['facultymobile']
        email=request.form['facultyemail']
        dob=request.form['facultydob']
        qualification=request.form['facultyqualification']
        address=request.form['facultyaddress1']
        city=request.form['facultycity']
        state=request.form['facultystate']
        salary=request.form['facultysalary']
        applicationid=session['applicationid']
        joindate=str(datetime.datetime.now().date())
        cursor=db.cursor()
        cursor.execute("INSERT INTO FACULTY (APPLICATIONID, FACULTYNAME, FACULTYEMAIL, FACULTYMOBILE,\
         FACULTYDOB,FACULTYQUALIFICATION,FACULTYADDRESS,FACULTYCITY,FACULTYSTATE,FACULTYSALARY,FACULTYJOIN,PASSWORD)\
         VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')\
         "%(applicationid, name, email, mobile, dob, qualification, address, city, state, salary,joindate,passGen()))
        db.commit()
        cursor.close()
        return redirect(url_for('school_faculty_add',faculty='added',name=session['username']))

#employee view 
@app.route("/school/<name>/faculty/view")
def school_faculty_view(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    cursor=db.cursor()
    cursor.execute("SELECT * FROM FACULTY WHERE  FACULTYFIRE IS NULL AND APPLICATIONID= '%s'"%session['applicationid'])
    row=cursor.fetchall()
    l=len(row)
    return render_template('school/faculty-view.html',data=row, l=l)

#employee view with full details -- view more
@app.route('/school/<name>/faculty/viewmore',methods=["GET"])
def school_faculty_view_more(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    if request.method=="GET":
        cursor=db.cursor()
        fid=request.args.get('fid')
        row  = cursor.execute("SELECT * FROM  FACULTY LEFT OUTER JOIN CLASSES ON CLASSCOORDINATOR = FACULTYID WHERE FACULTYID='%s' AND FACULTY.APPLICATIONID='%s'"%(fid, session['applicationid']))
        row = cursor.fetchone()
        if len(row)==0:
            return render_template('school/unauthorized-access.html')
        cursor.execute("SELECT * FROM STATES WHERE STATEID = '%s'"%row[9])
        stateid=cursor.fetchone()
        return render_template('school/faculty-viewmore.html',data = row, l=len(row),state=stateid[1])

@app.route('/school/<name>/faculty/edit',methods=["GET"])
def school_faculty_edit(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    if request.method=="GET":
        cursor=db.cursor()
        fid=request.args.get('id')
        row  = cursor.execute("SELECT * FROM  FACULTY  WHERE FACULTYID='%s' AND FACULTY.APPLICATIONID='%s'"%(fid, session['applicationid']))
        row = cursor.fetchone()
        if len(row)==0:
            return render_template('school/unauthorized-access.html')
        cursor.execute("SELECT * FROM STATES")
        states=cursor.fetchone()
        return render_template('school/faculty-edit.html',data = row, l=len(row),states=states)
    
#send password to the email id 
@app.route("/school/<name>/faculty/sendpasswordmail")
def school_faculty_send_password(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    if request.method=="GET":
        cursor=db.cursor()
        fid=request.args.get('fid')
        row  = cursor.execute("SELECT * FROM FACULTY WHERE FACULTYID='%s' AND APPLICATIONID='%s'"%(fid, session['applicationid']))
        row = cursor.fetchone()
        email = row[3]
        password = row[13]
        template = open('templates/school/passwordmail.html','r')
        text = template.read().format(email,password)
        msg=Message("Confidential: Password Inside",recipients=[email], sender='projecteducast@gmail.com',html=text)
        mail.send(msg)
        return redirect(url_for('school_faculty_view_more',name = name, fid = fid))

#faculty fire
@app.route("/school/<name>/faculty/fire", methods=["GET"])
def school_faculty_fire(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    if request.method=="GET":
        cursor=db.cursor()
        fid=request.args.get("fid")
        currdate=str(datetime.datetime.now().date())
        cursor.execute("UPDATE FACULTY SET FACULTYFIRE = '%s' WHERE FACULTYID='%s' AND APPLICATIONID = '%s' "%(currdate,fid,session['applicationid']))
        db.commit()
        return redirect(url_for('school_faculty_view',name=session['username']))

#faculty raise
@app.route("/school/<name>/faculty/raise",methods=["POST"])
def school_faculty_raise(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    if request.method=="POST":
        value=request.form['value']
        radio=request.form['radio']
        fid=request.form['fid']
        sql=""
        if radio == "percent":
            sql="UPDATE FACULTY SET FACULTYSALARY = FACULTYSALARY + ((FACULTYSALARY*%s)/100) WHERE FACULTYID = '%s' AND APPLICATIONID='%s'"%(value,fid,session['applicationid'])
        elif radio == "amount":
            sql =  "UPDATE FACULTY SET FACULTYSALARY  = FACULTYSALARY + %s WHERE FACULTYID = '%s' AND APPLICATIONID = '%s'"%(value,fid,session['applicationid'])
        cursor=db.cursor()
        cursor.execute(sql)
        db.commit()
        cursor.close()
        return redirect(url_for('school_faculty_view_more',name=session['username'],fid=fid))    

#faculty manage more settings
@app.route('/school/<name>/faculty/manage')
def school_faculty_manage(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    return render_template('school/faculty-manage.html')  

#view fired faculties in manage settings
@app.route('/school/<name>/faculty/view_fired')
def school_faculty_view_fired(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    cursor=db.cursor()
    cursor.execute("SELECT * FROM FACULTY WHERE  FACULTYFIRE IS NOT NULL AND APPLICATIONID= '%s'"%session['applicationid'])
    row=cursor.fetchall()
    l=len(row)
    return render_template('school/faculty-view-fired.html',data=row, l=l)

#readd the faculty
@app.route('/school/<name>/faculty/readd')
def school_faculty_readd(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    cursor = db.cursor()
    cursor.execute("UPDATE  FACULTY SET FACULTYFIRE = NULL WHERE FACULTYID = %s AND APPLICATIONID = %s"%(request.args.get('fid'),session['applicationid']))
    return redirect(url_for('school_faculty_view_more', name = name, fid = request.args.get('fid')))

#assigning the duties
@app.route('/school/<name>/faculty/assign_class')
def school_faculty_assign_class(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM CLASSES LEFT OUTER JOIN FACULTY ON CLASSCOORDINATOR = FACULTYID WHERE CLASSES.APPLICATIONID = '%s'"%session['applicationid'])
    classes = cursor.fetchall()
    return render_template("school/assign-class.html",classes = classes)

@app.route('/school/<name>/faculty/assignhandler')
def school_faculty_assignhandler(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    classid = request.args.get("classid")
    cursor = db.cursor()
    result = cursor.execute("SELECT * FROM CLASSES WHERE APPLICATIONID = '%s' AND CLASSID = '%s'"%(session['applicationid'],classid))
    if not (result > 0):
        return redirect(url_for('school_faculty_assign_class',name = name))
    classe = cursor.fetchone()
    cursor.execute("SELECT* FROM FACULTY WHERE APPLICATIONID = '%s'"%session['applicationid'])
    faculties = cursor.fetchall()
    cursor.execute("SELECT * FROM FACULTY,CLASSES WHERE CLASSCOORDINATOR=FACULTYID AND CLASSID='%s'"%classid)
    mix = cursor.fetchone()
    cursor.close()
    return render_template('school/assign-handler.html',classe = classe,faculties = faculties, mix = mix)

@app.route("/school/<name>/faculty/assignhandlersubmit", methods = ["POST"])
def school_faculty_assignhandler_submit(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    if request.method == "POST":
        classid = request.form['id']
        facultyid = request.form['facultyid']
        cursor = db.cursor()
        cursor.execute("UPDATE CLASSES SET CLASSCOORDINATOR = '%s' WHERE CLASSID = '%s'"%(facultyid,classid))
        db.commit()
        cursor.close()
        return redirect(url_for('school_faculty_assign_class',name=name))
    
@app.route("/school/<name>/maketimetable/")
def school_maketimetable(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM CLASSES WHERE APPLICATIONID = '%s' ORDER BY CLASSTYPE, CLASSNAME"%session['applicationid'])
    classes = cursor.fetchall()
    cursor.execute("SELECT * FROM FACULTY WHERE APPLICATIONID = '%s'"%session['applicationid'])
    faculty = cursor.fetchall()
    classtype = ('Class','Hall','Lab','Office')
    cursor.close()
    return render_template('school/maketimetable.html',classes= classes, faculty=faculty, ct = classtype, name = name)

@app.route("/school/<name>/addsubjects/")
def school_addsubjects(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM CLASSES WHERE APPLICATIONID = '%s'"%session['applicationid'])
    classes = cursor.fetchall()
    cursor.close()
    return render_template("school/add-subjects.html",classes = classes)

###### student sections #######
#student homepage
@app.route('/school/<name>/student')
def school_student(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    cursor=db.cursor()
    result=cursor.execute("SELECT * FROM SCHOOLAPPLY AS A1, SCHOOLPROCEED AS A2  WHERE A1.APPLICATIONID=A2.APPLICATIONID AND A1.APPLICATIONID='%s'"%session['applicationid'])
    row=cursor.fetchone()  
    cursor.close()  
    return render_template('school/student.html',data=row) 

#school student add
@app.route('/school/<name>/student/getstudentinfo')
def school_student_newadd_studentinfo(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    states=stateGen()
    return render_template('school/get-student-info.html',states=states)
@app.route('/school/<name>/student/getparentinfo',methods=["POST"])
def school_student_newadd_parentinfo(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    if request.method=="POST":
        studentname = request.form['studentname']
        studentdob = request.form['studentdob']
        studentclass=request.form['studentclass']
        studentuid=request.form['studentuid']
        studentaddress1=request.form['studentaddress1']
        studentcity=request.form['studentcity']
        studentstate=request.form['studentstate']
        parentid = request.form['parentid']
        print(parentid)
        cursor=db.cursor()
        admitdate  =  str(datetime.datetime.now()).split()[0]
        session['studentuid']=studentuid
        cursor.execute("INSERT INTO STUDENT (APPLICATIONID,STUDENTNAME, STUDENTDOB, STUDENTCLASS, STUDENTUID, STUDENTADMITDATE,\
        STUDENTADDRESS, STUDENTCITY, STUDENTSTATE,STUDENTSTATUS) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','0') "%(session['applicationid'],studentname,studentdob,studentclass,\
        studentuid,admitdate,studentaddress1, studentcity, studentstate))
        
        if parentid == "":
            cursor.close()
            return render_template('school/get-parent-info-new.html',studentname=studentname) 
        else:
            result = cursor.execute("SELECT * FROM PARENT WHERE PARENTID = '%s'"%parentid)
            if result == 0:
                cursor.close()
                return redirect(url_for('school_student_newadd_studentinfo',name=session['username'],parentid='not-available'))
            row = cursor.fetchone()
            cursor.close()
            return render_template('school/get-parent-info-parent-id.html',data=row)
#admit student --> commit changes in database for studentinfo and parent info
@app.route('/school/<name>/student/finalize',methods=["POST"])
def school_student_newadd_finalize(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    if request.method=="POST":
        fname = request.form['fname']
        mname = request.form['mname']
        contact = request.form['contact']
        email = request.form['email']
        occupation = request.form['occupation']
        salary = request.form['salary']
        cursor = db.cursor() 
        cursor.execute("INSERT INTO PARENT (PARENTFNAME, PARENTMNAME, PARENTMOBILE,PARENTEMAIL, PARENTOCCUPATION\
        , PARENTANNUALSALARY) VALUES('%s','%s','%s','%s','%s','%s')"%(fname, mname, contact, email , occupation, salary))
        row = cursor.execute("SELECT * FROM PARENT ORDER BY PARENTID DESC")
        parentid = cursor.fetchone()[0]
        cursor.execute("UPDATE STUDENT SET PARENTID = '%s' WHERE APPLICATIONID = '%s' AND STUDENTUID = '%s'"%(parentid, session['applicationid'], session['studentuid']))
        cursor.execute("SELECT * FROM STUDENT, PARENT,STATES WHERE PARENT.PARENTID = STUDENT.PARENTID AND STUDENT.STATEID = STATES.STATEID  AND STUDENT.APPLICATIONID = '%s'"%session['applicationid'])
        row = cursor.fetchone()
        cursor.close()
        db.commit()
        session['temp']=row
        return redirect(url_for('school_student_newadd_done',name=session['username']))

# show the confirmation and print confirmation -- >
@app.route('/school/<name>/student/confirmation')
def school_student_newadd_done(name):
    if 'username' not in session or 'updocs' in session:
        return redirect(url_for('school_name'))
    if session['username']!=name:
        return render_template('school/unauthorized-access.html')
    data =session['temp']
    #del(session['temp'])
    print(data)
    return render_template('school/finalize-admission.html',data=data)
    
#school apply for membership:
@app.route("/school/apply")
def apply():
    return render_template("school/apply.html")
 
#submit application
@app.route("/school/apply/submit",methods=["POST"])
def applysubmit():
    if request.method=="POST":
        db=pymysql.connect("127.0.0.1","root","","educast")
        cursor=db.cursor()
        print("Hello")
        fname=request.form['firstname']
        lname=request.form['lastname']
        school=request.form['schoolname']
        email=request.form['email']
        mobile=request.form['mobile']
        city=request.form['city']
        pasword=passGen()
        try:
            cursor.execute("INSERT INTO SCHOOLAPPLY (FIRSTNAME,LASTNAME,SCHOOLNAME,EMAIL,MOBILE,CITY,PASSWORD) VALUES ('%s','%s','%s','%s','%s','%s','%s')" %(fname,lname,school,email,mobile,city,pasword))
            db.commit()
            session['applymail']=email
            sendApplicationMail(email)
        except pymysql.IntegrityError:
            return redirect(url_for('apply',apply=False))
        finally:
            cursor.close()
            db.close()
        return redirect(url_for('apply',apply=True))

#send application successful mail
def sendApplicationMail(email):
    print(email)
    db=pymysql.connect("127.0.0.1","root","","educast")
    cursor=db.cursor()
    cursor.execute("SELECT APPLICATIONID,PASSWORD,FIRSTNAME FROM SCHOOLAPPLY WHERE EMAIL='%s'"%(email))
    result=cursor.fetchone()
    appid=result[0]
    passs=result[1]
    fname=result[2]
    mailfile=open("templates/mail.html","r")
    mailmessage=mailfile.read()%(fname,appid,passs)
    msg=Message("Your Application Has Received",recipients=[email], sender='projecteducast@gmail.com',html=mailmessage)
    mail.send(msg)
#check username if exists or not working with ajax
@app.route("/school/checkusername",methods=["POST","GET"])
def check_username():
    db=pymysql.connect("127.0.0.1","root","","educast")
    cursor=db.cursor()
    username=request.args.get('username')
    cursor.execute("SELECT USERNAME FROM SCHOOLPROCEED WHERE USERNAME='%s'"%(username))
    row=(cursor.fetchall())
    cursor.close()
    db.close()
    if len(row)>0:
        return json.dumps({"status":"OK","user":"exist"})
    return json.dumps({"status":"OK","user":"noexist"})

#insert username and password
@app.route("/school/setusername",methods=["POST"])
def set_username():
    db=pymysql.connect("127.0.0.1","root","","educast")
    cursor=db.cursor()
    if request.method == "POST":
        password=request.form['pass']
        confirmpassword=request.form['cpass']
        username=request.form['username']
        if password != confirmpassword:
            return render_template('oops.html')
        try:
            applicationid=session['applicationid']
            session['username']=username
            cursor.execute("INSERT INTO SCHOOLPROCEED (APPLICATIONID,USERNAME,PASSWORD) VALUES ('%s','%s','%s')"%(applicationid,username,confirmpassword))
            cursor.execute("UPDATE SCHOOLAPPLY SET PASSWORD=NULL WHERE APPLICATIONID='%s'"%applicationid)
            db.commit()
            cursor.close()
            db.close()
            session.pop('setuser')
            return redirect(url_for('school_dashboard',name=session['username']))
        except pymysql.err.IntegrityError:
            return render_template('school/oops.html')

# first login
@app.route("/school/setuser")
def setuser():
    if 'setuser' not in session:
        return redirect(url_for('s_login'))
    db=pymysql.connect("127.0.0.1","root","","educast")
    cursor=db.cursor()
    applicationid=session['applicationid']
    result=cursor.execute("SELECT firstname FROM SCHOOLAPPLY WHERE APPLICATIONID= '%s'"%applicationid)
    print(applicationid)
    row=cursor.fetchone()
    name=row[0]
    return render_template("school/first-login.html",name=name)





## ajax requests calls ##
##
##
@app.route("/school/<name>/getfacultyfortimetable",methods=["POST"])
def getfacultyfortimetable(name):
    if request.method == "POST":
        schoolid = request.form["id"]
        cursor = db.cursor()
        sql = "SELECT * FROM SCHOOLAPPLY,SCHOOLPROCEED, FACULTY WHERE SCHOOLAPPLY.APPLICATIONID = SCHOOLPROCEED.APPLICATIONID AND SCHOOLPROCEED.APPLICATIONID = FACULTY.APPLICATIONID AND (SCHOOLAPPLY.APPLICATIONID = '%s' OR SCHOOLPROCEED.USERNAME = '%s')"%(schoolid,schoolid)
        cursor.execute(sql)
        row =cursor.fetchall()
        data = {
            "facultyname" : [
               x[14] for x in row
            ],
            "facultyid":[
                x[13] for x in row
            ]
        }
        jsondata = json.dumps(data)
        return jsondata

    
@app.route("/school/<name>/gettimefortimetable",methods=["POST"])
def gettimefortimetable(name):
    if request.method == "POST":
        schoolid = request.form["id"]
        classid = request.form["classid"]
        return "ALLOKAY"
##
## ajax requests calls end ##



############################d###################

#parent login
@app.route("/parent-login")
def p_login():
    return render_template("parent/parent-login.html")

############################################

#admin homepage
@app.route("/admin")
def admin():
    if 'adminmail' not in session:
        return render_template("admin/index.html")
    else:
        return redirect(url_for('dashboard'))
#admin - logout
@app.route('/admin/unauthenticate')
def admin_logout():
    session.clear()
    return redirect(url_for('admin'))

#admin  login
@app.route("/admin/authenticate",methods=["POST"])
def admin_login():
    if request.method=="POST":
        if request.form['username'] == 'admin' and request.form['password'] == 'mypass':
            session['adminmail']='True'
            return redirect(url_for("dashboard"))
        else:
            return redirect(url_for("admin",login=False))

#admin dashboard
@app.route("/admin/dashboard")
def dashboard():
    if 'adminmail' in session:
        return render_template("admin/dashboard.html")
    else:
        return redirect(url_for('admin'))

@app.route("/admin/pending/<pageno>")
def admin_pending_applications(pageno):
    if 'adminmail' not in session:
        return redirect(url_for('admin'))
    cursor = db.cursor()
    result = cursor.execute("SELECT * FROM SCHOOLAPPLY WHERE STATUS = 0 OR STATUS = 1 ORDER BY STATUS DESC")
    row = cursor.fetchall()
    #print(row)
    return render_template('admin/pending.html',data = row,pageno = pageno,int = int, len=len,str = str)

@app.route("/admin/pending-more",methods = ["GET"])
def admin_pending_applications_more():
    if 'adminmail' not in session:
        return redirect(url_for('admin'))
    applicationid = request.args.get("id")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM SCHOOLAPPLY WHERE  APPLICATIONID = %s AND (STATUS = 0 OR STATUS = 1)"%applicationid)
    row = cursor.fetchone()
    print(applicationid)
    print(row)
    cursor.close()
    return render_template("admin/pending-more.html",data= row, str=str)

@app.route("/admin/verifyschool",methods=["GET"])
def admin_verify_school():
    if 'adminmail' not in session:
        return redirect(url_for('admin'))
    applicationid = request.args.get("id")
    cursor = db.cursor()
    cursor.execute("UPDATE SCHOOLAPPLY SET STATUS = 2 WHERE APPLICATIONID = %s"%applicationid)
    db.commit()
    cursor.execute("SELECT * FROM SCHOOLAPPLY WHERE APPLICATIONID = %s"%applicationid)
    row = cursor.fetchone()
    school_name = row[3]
    first_name = row[1]
    email = row[4]
    mailfile = open("templates/admin/verify-school-mail.html","r").read().format(first_name,school_name)
    msg = Message("Your Account Has Been Successfully Verified - Educast",recipients=[email], html = mailfile, sender="projecteducast@gmail.com")
    mail.send(msg)
    cursor.close()
    return redirect(url_for('admin_registered_more',id=applicationid,verify="true"))

@app.route("/admin/registered/<pageno>")
def admin_registered_school(pageno):
    if 'adminmail' not in session:
        return redirect(url_for('admin'))
    cursor = db.cursor()
    cursor.execute("SELECT * FROM SCHOOLAPPLY AS A1 LEFT  JOIN SCHOOLPROCEED AS A2 ON A1.APPLICATIONID  = A2.APPLICATIONID WHERE A1.STATUS = 2 OR A1.STATUS = 3")
    row = cursor.fetchall()
    cursor.close()
    print(row)
    return render_template("admin/view-school.html",data=row,int = int, str = str,pageno = pageno,len = len)   

@app.route("/admin/registered-more",methods=["GET"])
def admin_registered_more():
    if 'adminmail' not in session:
        return redirect(url_for('admin'))
    cursor = db.cursor()
    result = cursor.execute("SELECT * FROM SCHOOLAPPLY AS A1 LEFT JOIN SCHOOLPROCEED AS A2 ON A1.APPLICATIONID = A2.APPLICATIONID WHERE (A1.STATUS = 2 OR A1.STATUS = 3 )AND A1.APPLICATIONID = %s "%request.args.get("id"))
    if result == 0:
       return render_template("school/oops.html")
    row = cursor.fetchone()
    cursor.execute("SELECT * FROM CLASSES WHERE APPLICATIONID = %s"%request.args.get("id"))
    classes = cursor.fetchall()
    print(row)
    x = (request.args.get("verify"),)
    return render_template("admin/view-school-more.html",data = row+x, classes = classes, str = str,len=len, classtype = ["","Class","Hall","Lab","Office"])

@app.route("/admin/addclass",methods=["POST"])
def admin_add_class():
    if 'adminmail' not in session:
        return redirect(url_for('admin'))
    if request.method == "POST":

        classname = request.form['classname']
        classfloor = request.form['floornumber']
        sectioncount = request.form["sectioncount"]
        classtype = request.form['classtype']
        applicationid = request.form['id']
        cursor  = db.cursor()
        cursor.execute("INSERT INTO CLASSES (APPLICATIONID,CLASSNAME,CLASSFLOOR,CLASSTYPE,CLASSSECTIONS) VALUES ('%s','%s','%s','%s','%s')"%(applicationid,classname,classfloor,classtype,sectioncount))
        db.commit()
        cursor.close()
        return redirect(url_for('admin_registered_more',id=applicationid))
    return render_template("oops.html")

@app.route("/admin/registerededit",methods = ["POST"])
def admin_registered_edit():
    if request.method == "POST":
        ndata = request.form['xid']
        pdata = request.form['previousdata']
        x = request.form['rowid']
        cursor = db.cursor()
        sql  = ""
        if pdata =="1":
            sql = "UPDATE SCHOOLAPPLY SET SCHOOLNAME = '%s' WHERE APPLICATIONID = '%s'"%(ndata,x)
        elif pdata == "2":
            fullname = ndata.split(" ")
            sql = "UPDATE SCHOOLAPPLY SET FIRSTNAME = '%s', LASTNAME = '%s' WHERE APPLICATIONID = '%s'"%(fullname[0],fullname[1],x)
        elif pdata=='3':
            sql = "UPDATE SCHOOLAPPLY SET EMAIL = '%s' WHERE APPLICATIONID = '%s'"%(ndata,x)
        elif pdata == '4':
            sql = "UPDATE SCHOOLAPPLY SET MOBILE = '%s' WHERE APPLICATIONID = '%s'"%(ndata,x)
        elif pdata =="5":
            sql = "UPDATE SCHOOLAPPLY SET CITY = '%s' WHERE APPLICATIONID = '%s'"%(ndata,x)
        elif pdata=="6":
            sql = "UPDATE SCHOOLAPPLY SET STATUS = '%s' WHERE APPLICATIONID = '%s'"%(ndata,x)
        cursor.execute(sql)
        db.commit()
        cursor.close()
    return redirect(url_for('admin_registered_more',id = x))

@app.route("/admin/sendpasswordmail/",methods=["GET","POST"])
def admin_sendpasswordmail():
    if 'adminmail' not in session:
        return redirect(url_for('admin'))
    applicationid = request.args.get("aid")
    cursor = db.cursor()
    cursor.execute("SELECT SA.PASSWORD, SP.PASSWORD , SP.USERNAME, SA.EMAIL FROM SCHOOLAPPLY AS SA , SCHOOLPROCEED AS SP WHERE SA.APPLICATIONID = SP.APPLICATIONID AND SA.APPLICATIONID = '%s'"%applicationid)
    row = cursor.fetchone()
    password = "Don't Know"
    if row[0] == "" or row[0] == None:
        password = row[1]
    else:
        password= row[0]
    template = open("templates/admin/passwordmail.html","r")
    template = template.read().format(row[2],password)
    msg = Message("Confidential: Password Inside", recipients = [row[3]], sender = "projecteducast@gmail.com" , html = template)
    mail.send(msg)
    return redirect(url_for('admin_registered_more',id = applicationid))




###############################
if __name__ == '__main__':
    app.jinja_env.auto_reload=True
    app.run(debug=True)


################################
### school status codes
# 0 for fresh account creation
# 1 for docs uploaded
# 2 for docs verified/activated
# 3 for account deactivated temporarily


### student status codes
# 0 for new admission
# 1 for transfer student
# 2 for alumni

## class type status 

#  1 for room
# 2 for hall
# 3 for lab 
# 4 for office