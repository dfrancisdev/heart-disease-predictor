from flask import Flask, request, redirect, render_template, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import numpy as np
import sqlite3

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.debug = True

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
    return render_template(
        "home.html",
        prediction=None,
        explanation=None,
        risk_score=None,   
        username=session.get('user')
    ) 


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
            trestbps = 150
        else:
            trestbps = 120
        chol_simple = int(request.form['chol'])
        if chol_simple == 1:
            chol = 260
        else:
            chol = 200
        fbs = 1 if int(request.form['fbs']) == 1 else 0
        restecg = 1
       
        hr = int(request.form['hr'])
        if hr == 1:
            thalach = 100
        else:
            thalach = 150
        
        exang = int(request.form['exang'])
        
        oldpeak = 1.0
        slope = 1
        ca = 0
        thal = 2

        print("DEBUG INPUTS:")
        print("Age:", age)
        print("Sex:", sex)
        print("Chest Pain (cp):", cp)
        print("Blood Pressure (bp):", bp, "| trestbps:", trestbps)
        print("Chol (raw):", chol_simple, "| chol:", chol)
        print("FBS:", fbs)
        print("Heart Rate input:", hr, "| thalach:", thalach)
        print("Exang:", exang)


        

        # Arrange data EXACTLY as in training
        data = np.array([[age, sex, cp, trestbps, chol, fbs, restecg,
                          thalach, exang, oldpeak, slope, ca, thal]])

        # Make prediction
        print("MODEL INPUT:", data)
        prediction = model.predict(data)
        probability = model.predict_proba(data)
        result = str(prediction[0])
        risk_score = float(round(probability[0][1] * 100, 2))
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
            username=session.get('user')
)
    except Exception as e:
        print("FULL ERROR:", e)
        raise e 
           


import os

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

