# DMW_project
Energy consumption prediction in Smart cities

#  Energy Consumption Prediction in Smart Cities

This project provides an interactive Streamlit-based dashboard for predicting and analyzing energy consumption in smart cities using machine learning (Random Forest). It integrates a MySQL database, OLAP operations, and real-time user input to generate accurate energy consumption forecasts.

## Project Structure


├── dashboard.py # Streamlit dashboard for prediction and visualization
├── energy_production.py # Model training, evaluation, OLAP operations, and DB insertion
├── Energy_consumption.csv # Dataset with energy metrics and features
└── README.md # Project documentation

## 🧠 Features

- 📊 Real-time energy consumption prediction using Random Forest
- 🗂️ Data stored and retrieved from MySQL database
- 📈 Line charts to visualize energy usage per zone
- 🧮 OLAP operations: Roll-up, Drill-down, Slice, Dice, Pivot
- ✅ Prediction results are stored in `predictions_results` table
- 🔐 Clean user interface built with Streamlit

## ⚙️ Setup Instructions

### 1. Install Required Libraries2. Set Up MySQL Database


pip install -r requirements.txt

Requirements (requirements.txt):

nginx
Copy
Edit
streamlit
pandas
scikit-learn
mysql-connector-python
sqlalchemy


2. Set Up MySQL Database
Create a MySQL database named energy_db

Create the following tables:

Create a MySQL database named energy_db

Create the following tables:

CREATE TABLE energy_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME,
    zone VARCHAR(20),
    predicted_energy FLOAT
);

CREATE TABLE predictions_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zone VARCHAR(20),
    temperature FLOAT,
    humidity FLOAT,
    square_footage FLOAT,
    occupancy INT,
    hvac_usage TINYINT,
    lighting_usage TINYINT,
    renewable_energy FLOAT,
    holiday TINYINT,
    hour INT,
    day INT,
    month INT,
    day_of_week VARCHAR(10),
    predicted_energy FLOAT
);
3. Run the Model and Populate Database
bash
Copy
Edit
python energy_production.py
4. Launch the Dashboard
bash
Copy
Edit
streamlit run dashboard.py
🧪 Machine Learning Model
Model: Random Forest Regressor

Target Variable: EnergyConsumption

Features:

Temperature, Humidity, Square Footage, Occupancy

HVAC Usage, Lighting Usage, Renewable Energy

Holiday, Time features (hour, day, month)

Day of the Week (one-hot encoded)

Evaluation Metric: Mean Absolute Error (MAE)

🔎 OLAP Operations Included
Roll-up: Average energy by month

Drill-down: Daily breakdown for January

Slice: Energy at 9 AM

Dice: January records between 8–10 AM

Pivot Table: Hour vs. Day energy distribution

📸 Dashboard Preview
Add a screenshot here named preview.png for visual reference

🤝 Contributors
Sahil Ashok Thorat
Machine Learning & Web Developer
LinkedIn | GitHub

📌 Future Enhancements
Model persistence using joblib

Multi-zone dataset support

Forecasting via ARIMA or LSTM

Role-based authentication












