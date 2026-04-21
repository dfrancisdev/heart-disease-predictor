from flask import Flask, request, render_template
import joblib
import numpy as np

app = Flask(__name__)

# Load trained model
model = joblib.load("heart_model.pkl")

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form values
        age = int(request.form['age'])
        sex = int(request.form['sex'])
        cp = int(request.form['cp'])
        
        bp = int(request.form['bp'])
         if bp = 1:
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
