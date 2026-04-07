from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import mysql.connector
import traceback
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import numpy as np
from dotenv import load_dotenv
import os

# ---------------------- Environment and App Initialization ----------------------

load_dotenv()

app = Flask(__name__)
app.secret_key = "RUL"

# ---------------------- Database Configuration ----------------------

mydb = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME')
)
mycursor = mydb.cursor()

# ---------------------- Database Utility Functions ----------------------

def executionquery(query, values):
    mycursor.execute(query, values)
    mydb.commit()

def retrivequery1(query, values):
    mycursor.execute(query, values)
    return mycursor.fetchall()

def retrivequery2(query):
    mycursor.execute(query)
    return mycursor.fetchall()

# ---------------------- Basic Routes ----------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# ---------------------- User Registration ----------------------

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            name = request.form['name']
            email = request.form['email'].strip().lower()
            phone = request.form['phone']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if password != confirm_password:
                return jsonify({"success": False, "message": "Passwords do not match"})

            mycursor.execute("SELECT email FROM users WHERE email = %s", (email,))
            if mycursor.fetchone():
                return jsonify({"success": False, "message": "Email already exists"})

            query = "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)"
            executionquery(query, (name, email, phone, password))

            return jsonify({"success": True, "message": "Registration successful!"})

        except Exception as e:
            traceback.print_exc()
            return jsonify({"success": False, "message": "Server Error: " + str(e)})

    return render_template("register.html")

# ---------------------- User Login ----------------------

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        query = "SELECT email FROM users"
        emails = [i[0].lower() for i in retrivequery2(query)]

        if email.lower() in emails:
            query = "SELECT name, password FROM users WHERE email = %s"
            retrieved_pass = retrivequery1(query, (email,))
            name, user_password = retrieved_pass[0]

            if user_password and password == user_password:
                session['user_name'] = name
                session['user_email'] = email
                return redirect(url_for('user_home'))

            return render_template('login.html', message="Invalid Password")

        return render_template('login.html', message="Email ID maybe unregistered or incorrect")

    return render_template("login.html")

# ---------------------- User Dashboard ----------------------

@app.route('/user_home')
def user_home():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template("user_home.html", name=session['user_name'])

# ---------------------- Data Loading and Preprocessing ----------------------

df = pd.read_csv("Battery_RUL.csv")

# Standardize column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Outlier removal using IQR method
Q1 = df.quantile(0.25)
Q3 = df.quantile(0.75)
IQR = Q3 - Q1
df_clean = df[~((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).any(axis=1)]

# Feature and target separation
X = df_clean.drop("rul", axis=1)
y = df_clean["rul"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ---------------------- Model Training ----------------------

rf = RandomForestRegressor(n_estimators=150, random_state=42)
rf.fit(X_train, y_train)

# ---------------------- Prediction Route ----------------------

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if request.method == 'POST':
        try:
            cycle_index = float(request.form.get('cycle_index'))
            discharge_time = float(request.form.get('discharge_time'))
            decrement_36_34 = float(request.form.get('decrement_36_34'))
            max_voltage_discharge = float(request.form.get('max_voltage_discharge'))
            min_voltage_charge = float(request.form.get('min_voltage_charge'))
            time_415 = float(request.form.get('time_415'))
            time_constant_current = float(request.form.get('time_constant_current'))
            charging_time = float(request.form.get('charging_time'))
        except (TypeError, ValueError):
            return redirect(url_for('prediction'))

        # Prepare input as DataFrame to match training format
        input_data = np.array([
                cycle_index, discharge_time, decrement_36_34,
                max_voltage_discharge, min_voltage_charge,
                time_415, time_constant_current, charging_time
            ]).reshape(1, -1)

        predicted_rul = rf.predict(input_data)[0]
        prediction_result = int(predicted_rul)

        return redirect(url_for('fair_price', predicted_RUL=prediction_result))

    return render_template('prediction.html')

# ---------------------- Fair Price Calculation ----------------------

@app.route('/fair_price', methods=['GET', 'POST'])
def fair_price():
    fair_price_value = None
    predicted_RUL = request.args.get('predicted_RUL')

    if request.method == 'POST':
        RUL = int(request.form.get('predicted_RUL'))
        battery_lifetime = int(request.form.get('battery_lifetime'))
        price = float(request.form.get('price'))

        fair_price_value = round((RUL / battery_lifetime) * price, 2)
        predicted_RUL = None

    return render_template(
        'fair_price.html',
        fair_price=fair_price_value,
        predicted_RUL=predicted_RUL
    )

# ---------------------- Logout ----------------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ---------------------- Application Entry Point ----------------------

if __name__ == "__main__":
    app.run(debug=True)
