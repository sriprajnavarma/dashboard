from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import plotly.express as px
import os

app = Flask(__name__)

# Define the path to the CSV file
CSV_FILE_PATH = 'patient_data.csv'

# Define column headers for the DataFrame
COLUMN_HEADERS = ['appointment_date', 'patient_id', 'age_group', 'gender', 'diagnosis']

# Function to read patient data from CSV
def read_patient_data():
    if os.path.exists(CSV_FILE_PATH):
        # If the CSV file exists, read it into a DataFrame
        df = pd.read_csv(CSV_FILE_PATH)
    else:
        # If the CSV file doesn't exist, create an empty DataFrame with defined column headers
        df = pd.DataFrame(columns=COLUMN_HEADERS)
    
    return df

# Function to write patient data to CSV
def write_patient_data(data):
    data.to_csv(CSV_FILE_PATH, index=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_patient', methods=['POST'])
def add_patient():
    appointment_date = request.form['appointment_date']
    patient_id = request.form['patient_id']
    age = request.form['age']
    gender = request.form['gender']
    diagnosis = request.form['diagnosis']
    
    # Read existing data
    df = read_patient_data()
    
    # Append new patient data
    new_data = {
        'appointment_date': appointment_date,
        'patient_id': patient_id,
        'age_group': age,
        'gender': gender,
        'diagnosis': diagnosis
    }
    df = df.append(new_data, ignore_index=True)
    
    # Write updated data back to CSV
    write_patient_data(df)
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    # Read patient data from CSV
    df = read_patient_data()
    
    # Get selected age group and gender from query parameters
    age_group = request.args.get('age_group', default='all')
    gender = request.args.get('gender', default='all')

    # Filter data based on selected age group and gender
    if age_group != 'all':
        df = df[df['age_group'] == age_group]
    if gender != 'all':
        df = df[df['gender'] == gender]

    if df.empty:
        fig = px.bar()
    else:
        diagnosis_counts = df['diagnosis'].value_counts().reset_index()
        diagnosis_counts.columns = ['diagnosis', 'count']
        fig = px.bar(diagnosis_counts, x='diagnosis', y='count', title=f'Number of Patients Admitted for Each Diagnosis (Age Group: {age_group}, Gender: {gender})')

    graph_html = fig.to_html(full_html=False)
    return render_template('dashboard.html', graph_html=graph_html)

if __name__ == '__main__':
    app.run(debug=True)
