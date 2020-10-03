#WEB APP SCRIPT 
#DATED:270920

from flask import *
import sqlite3
import base64

#SQL DATABASE INIT BEGIN
conn = sqlite3.connect('iot.db')
print("Opened database successfully")

#conn.execute('CREATE TABLE user (name TEXT NOT NULL,email TEXT NOT NULL, userid TEXT PRIMARY KEY NOT NULL, password TEXT NOT NULL)')
#conn.execute('CREATE TABLE devices (devname TEXT NOT NULL,devid TEXT NOT NULL PRIMARY KEY NOT NULL, userid TEXT, status INT NOT NULL, opt INT NOT NULL)')
print("Table created successfully")
conn.close()
#SQL DATABASE INIT END

#ENCODING PROCEDURES
def B64encode(text):
    d1=text.encode('ascii')
    d2=base64.urlsafe_b64encode(d1)
    return d2.decode('ascii')
    
def B64decode(text):
    d1=text.encode('ascii')
    d2=base64.urlsafe_b64decode(d1)
    return d2.decode('ascii')

#MAIN APPLICATION

app = Flask(__name__)

err_msg="H"

@app.route("/")
@app.route("/login/<err_msg>")
def home(err_msg="H"):
    return render_template('login.html',err=err_msg)
    
@app.route("/register",methods=['GET', 'POST'])
def register():
   if request.method == 'POST':
      try:
         name = request.form['name']
         mail = request.form['mail']
         username = request.form['username']
         password = request.form['password']
         
         conn = sqlite3.connect('iot.db')   
         conn.execute("INSERT INTO user (name,email,userid,password) VALUES (?,?,?,?)",(name,mail,username,password))
         conn.commit()
         msg = "SUCCESS"
      except:
         conn.rollback()
         msg = "FAIL"
      
      finally:
         return redirect(url_for("home",err_msg=msg))
         conn.close()         

@app.route("/validate",methods=['GET', 'POST'])
def validate():
    if request.method == 'POST':
      try:
         username = request.form['username']
         password = request.form['password']
         conn = sqlite3.connect('iot.db')  
         cur = conn.cursor()
         cur.execute("SELECT * FROM user WHERE userid = ?",(username,))
         pwd = cur.fetchone()
         if pwd[3]==password:
            cur.execute("UPDATE devices SET status=0 WHERE userid = ?",(pwd[2],))
            conn.commit()
            conn.close()
            UserId=B64encode(pwd[2])
            return redirect(url_for("dash",UserID=UserId,msg="H"))
            #return UserID
         else:
            conn.close()
            return redirect(url_for("home",err_msg="WRONG"))
      except:
           conn.close()
           return redirect(url_for("home",err_msg="UNREGISTERED"))
      finally:
         conn.close() 

@app.route("/dashboard/<UserID>/<msg>")
def dash(UserID=None,msg=None):
    username=B64decode(UserID)
    conn = sqlite3.connect('iot.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE userid = ?",(username,))
    user_row=cur.fetchone()
    cur.execute("SELECT * FROM devices WHERE userid = ?",(username,))
    dev_row=cur.fetchall()
    conn.close()
    return render_template('dash.html',name=user_row[0],dev_data=dev_row,msg=msg,user=user_row[2])      

@app.route("/devadd",methods=['GET', 'POST'])
def ADDdevice():
   if request.method == 'POST':
      try:
         dev_name = request.form['dev_name']
         dev_id = request.form['dev_id']
         password = request.form['password']
         userid = request.form['userid']
         conn = sqlite3.connect('iot.db')   
         cur = conn.cursor()
         cur.execute("SELECT * FROM user WHERE userid = ?",(userid,))
         pwd = cur.fetchone()
         if pwd[3]==password:
            try:
                cur.execute("INSERT INTO devices (devname,devid,userid,status,opt) VALUES (?,?,?,?,?)",(dev_name,dev_id,userid,0,0))
                conn.commit()
                msg = "SUCCESS"
            except:
                cur.rollback()
                msg="FAIL"
         else:
            cur.close()
            msg="WRONG"
            
      except:
         msg="DBFAIL"
      finally:
         conn.close()  
         return redirect(url_for("dash",UserID=B64decode(userid),msg=msg))
                

@app.route("/logout",methods=['GET', 'POST'])
def logout():
    return redirect(url_for("home",err_msg="LOGOUT"))
    
@app.route("/control",methods=['GET', 'POST'])
def control():
    if request.method == "POST":
        try:
            dev_id=request.form['dev_id']
            conn = sqlite3.connect('iot.db')   
            cur = conn.cursor()
            cur.execute("SELECT * FROM devices WHERE devid = ?",(dev_id,))
            dev_row=cur.fetchone()
            if dev_row[4]==0:
                cur.execute("UPDATE devices SET opt=1 WHERE devid = ?",(dev_id,))
                conn.commit()
            else:
                cur.execute("UPDATE devices SET opt=0 WHERE devid = ?",(dev_id,))
                conn.commit()
            msg=" "
        except:
            msg="DBFAIL"
        finally:
            conn.close()
            return redirect(url_for("dash",UserID=B64encode(dev_row[2]),msg=msg))
            
@app.route("/view")
def view():
    con = sqlite3.connect("iot.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from user")
   
    rows = cur.fetchall();
    return render_template("view.html",rows = rows)
         
    
@app.route("/devclient/<dev_id>")
def devclient(dev_id=None):
    con = sqlite3.connect("iot.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM devices WHERE devid = ?",(dev_id,))
    dev_row=cur.fetchone()
   
    status=dev_row[3]
    if status==0:
        cur.execute("UPDATE devices SET status=1 WHERE devid = ?",(dev_id,))
        con.commit()
    operation=dev_row[4]
    con.close()
    return str(operation)

    
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
