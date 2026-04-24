from flask import request, redirect, render_template
from flask import session
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import numpy as np
import sqlite3

app = Flask(__name__)

app.secret_key = "df_heartcare_ai_2026_secure"
# Load trained model
model = joblib.load("heart_model.pkl")


def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    
    return render_template("index.html")


#🔑 STEP 2: Register (Create Account)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'] 
        password = generate_password_hash(request.form['password'])
        

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except:
            return "User already exists"

        conn.close()
        return redirect('/login')

    return render_template('register.html')   

#🔓 STEP 3: Login


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):

           session['user'] = username
           return redirect('/')
        else:
            return "Invalid credentials"

    return render_template('login.html')

#🚪 STEP 4: Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        return redirect('/login')
    try:
        # Get form values
        age = int(request.form['age'])
        sex = int(request.form['sex'])
        cp = int(request.form['cp'])
        bp = int(request.form['bp'])
        if bp == 1:
            trestbps = 140
        else:
            trestbps = 120
        chol_simple = int(request.form['chol'])
        if chol_simple == 1:
            chol = 240
        else:
            chol = 200
        fbs = int(request.form['fbs'])
       
        hr = int(request.form['hr'])
        if hr == 1:
            thalch = 150
        else:
            thalch = 100
        
        exang = int(request.form['exang'])
        restecg = 1
        oldpeak = 1.0
        slope = 1
        ca = 0
        thal = 2

        # Arrange data EXACTLY as in training
        data = np.array([[age, sex, cp, trestbps, chol, fbs, restecg,
                          thalch, exang, oldpeak, slope, ca, thal]])

        # Make prediction
        prediction = model.predict(data)

        return render_template("result.html", prediction=prediction[0])

    except Exception as e:
        print("ERROR:", e)
        return render_template("result.html", prediction="error")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
