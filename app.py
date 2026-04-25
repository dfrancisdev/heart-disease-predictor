body {
  font-family: Arial, sans-serif;
  margin: 0;
  background: #f4f8fb;
}

/* NAVBAR */
nav {
  display: flex;
  justify-content: space-between;
  padding: 15px 30px;
  background: white;
  position: fixed;
  width: 100%;
  top: 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

nav a {
  margin-left: 20px;
  text-decoration: none;
  color: #333;
}

/* HOME */
.home {
  text-align: center;
  padding: 120px 20px;
}

.home button {
  padding: 12px 25px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

/* FORM */
.form-section {
  padding: 80px 20px;
  text-align: center;
}

form {
  background: white;
  padding: 30px;
  border-radius: 10px;
  max-width: 400px;
  margin: auto;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

label {
  display: block;
  margin-top: 15px;
}

input,
select {
  width: 100%;
  padding: 10px;
  margin-top: 5px;
}

button {
  margin-top: 20px;
  padding: 12px;
  width: 100%;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
}

/* RESULT */
#result {
  margin-top: 20px;
  font-size: 20px;
  font-weight: bold;
}
/* HERO SECTION UPGRADE */
.home {
  text-align: center;
  padding: 140px 20px 80px;
  background: linear-gradient(to right, #007bff, #00c6ff);
  color: white;
}

.home h1 {
  font-size: 40px;
  margin-bottom: 10px;
}

.home p {
  font-size: 18px;
  margin-bottom: 20px;
}

.home button {
  background: white;
  color: #007bff;
  font-weight: bold;
}

/* 🔵 RISK GAUGE */
.gauge-container {
  width: 100%;
  max-width: 400px;
  height: 20px;
  background: #e0e0e0;
  border-radius: 10px;
  margin: 10px auto;
  overflow: hidden;
}

.gauge-fill {
  height: 100%;
  transition: width from flask import Flask, request, redirect, render_template, session, flash
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
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        age INTEGER,
        prediction TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    
    return render_template("home.html", username=session['user'])


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
            return render_template("register.html", error="User already exists")

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
           flash("Login successful!")
           return redirect('/')
        else:
           return render_template("login.html", error="Invalid username or password")

    return render_template('login.html')

#🚪 STEP 4: Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out")
    return redirect('/login')


# 📜 History Page
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # ⚠️ We will create this table later
    c.execute("SELECT * FROM history WHERE username=?", (session['user'],))
    records = c.fetchall()

    conn.close()

    return render_template("history.html", records=records)


# ℹ️ About Page
@app.route('/about')
def about():
    if 'user' not in session:
        return redirect('/login')

    return render_template("about.html")

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
        probability = model.predict_proba(data)
        result = str(prediction[0])
        risk_score = round(probability[0][1] * 100, 2)
        # 🔍 DEBUG TIP (ADD HERE)
        print("Risk Score:", risk_score)

        # 🧠 Generate explanation (AI-style reasoning)
        explanation = ""

        if result == "1":
           explanation = "Your risk is high due to "

           reasons = []
   
           if age > 50:
              reasons.append("your age")

           if bp == 1:
              reasons.append("high blood pressure")

           if chol_simple == 1:
              reasons.append("high cholesterol")

           if fbs == 1:
              reasons.append("high blood sugar")

           if exang == 1:
              reasons.append("exercise-related chest pain")

           if reasons:
              explanation += ", ".join(reasons)
           else:
              explanation += "a combination of health indicators"

           explanation += ". Consider lifestyle changes and consulting a doctor."

        elif result == "0":
           explanation = "Your risk appears low based on your current health indicators. Maintain a healthy lifestyle to keep your heart strong."

           # 📊 Feature contribution (simple scoring system)
           contributions = {
               "Age": age / 100,
               "Blood Pressure": bp * 1.0,
               "Cholesterol": chol_simple * 1.0,
               "Blood Sugar": fbs * 1.0,
               "Chest Pain": exang * 1.0
            }

        # 💾 Save to history
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute(
            "INSERT INTO history (username, age, prediction) VALUES (?, ?, ?)",
            (session['user'], age, result)
        )

        conn.commit()
        conn.close()

        return render_template(
            "home.html",
            prediction=result,
            explanation=explanation,
            risk_score=risk_score,
            username=session['user']
)
    except Exception as e:
        print("ERROR:", e)
        return render_template(
            "home.html",
            prediction="error",
            explanation="Something went wrong. Please try again.",
            risk_score=0,
            contributions=contributions,
            username=session['user']
)


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)0.5s ease-in-out;
}
