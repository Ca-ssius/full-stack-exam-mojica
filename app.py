from asyncio.windows_events import NULL
from multiprocessing import connection
from flask import Flask, render_template, request, flash, redirect, url_for, session
from functools import wraps
import sqlite3

app = Flask(__name__)
app.secret_key="123"

def loginRequired(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'loggedIn' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to log in first')
            return redirect(url_for('index'))
    return wrap

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=='POST':
        userName=request.form['userName']
        passWord=request.form['passWord']
        con=sqlite3.connect("regist.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from register where userName=? and passWord=?",(userName,passWord))
        data=cur.fetchone()
        if data:
            session["userName"]=data["userName"]
            session["passWord"]=data["passWord"]
            hold = session["userName"]
            hold2 = session["passWord"]
            session['loggedIn'] = True
            cur.execute("select food from register where userName=?",(hold,))
            food=cur.fetchone()
            cur.execute("select music from register where userName=?",(hold,))
            music=cur.fetchone()
            cur.execute("select truth from register where userName=?",(hold,))
            truth=cur.fetchone()
            cur.close()
            if food[0] == None:
                return redirect('step1')
            elif music[0] == None:
                return redirect('step2')
            elif truth[0] == None:
                return redirect('step3')
            else:
                return redirect(url_for('home'))
        else:
            flash("Username and Password Mismatch","danger")
    return redirect(url_for("index"))


@app.route('/home',methods=["GET","POST"])
@loginRequired
def home():
    data = session["userName"]
    data2 = session["passWord"]
    con = sqlite3.connect('regist.db') 
    cur = con.cursor()
    cur.execute("SELECT * FROM register WHERE userName=? and passWord=?",(data, data2))  
    records = cur.fetchall()  
    return render_template('home.html', records=records)
    
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        try:
            userName=request.form['userName']
            passWord=request.form['passWord']
            con=sqlite3.connect("regist.db")
            cur=con.cursor()
            cur.execute("INSERT INTO register(userName,passWord)values(?,?)",(userName,passWord))
            con.commit()
            flash("Account Created  Successfully","success")
            cur.execute("select * from register where userName=? and passWord=?",(userName,passWord))
            data=cur.fetchone()
        except:
            flash("Try Again","danger")
        else:
            session["userName"] = userName
            session["passWord"] = passWord
            session['loggedIn'] = True
            return redirect(url_for("step1"))
    return render_template('register.html')

@app.route('/step1',methods=["GET","POST"])
@loginRequired
def step1():
    data = session["userName"]
    if request.method=='POST':
        food=request.form['food']
        con=sqlite3.connect("regist.db")
        cur=con.cursor()
        cur.execute("UPDATE register SET food = ? WHERE userName = ?", (food, data))
        con.commit()
        return redirect(url_for("step2"))
    return render_template('step1.html')

@app.route('/step2',methods=["GET","POST"])
@loginRequired
def step2():
    data = session["userName"]
    if request.method=='POST':
        music=request.form['music']
        con=sqlite3.connect("regist.db")
        cur=con.cursor()
        cur.execute("UPDATE register SET music = ? WHERE userName = ?", (music, data))
        con.commit()
        return redirect(url_for("step3"))
    return render_template("step2.html")

@app.route('/step3',methods=["GET","POST"])
def step3():
    data = session["userName"]
    if request.method=='POST':
        truth=request.form['truth']
        con=sqlite3.connect("regist.db")
        cur=con.cursor()
        cur.execute("UPDATE register SET truth = ? WHERE userName = ?", (truth, data))
        con.commit()
        return redirect(url_for("home"))
    return render_template('step3.html')

@app.route('/logout')
def logout():
    session.pop('loggedIn', None)
    session.clear()
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)
