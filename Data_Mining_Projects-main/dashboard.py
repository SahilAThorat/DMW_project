import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# SQLAlchemy connection
engine = create_engine('mysql+mysqlconnector://root:root@localhost/energy_db')

# Load data from MySQL
df = pd.read_sql("SELECT * FROM energy_predictions", con=engine)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Example of handling datetime64 column
# Convert 'timestamp' to days since the earliest timestamp for safe operations
df['timestamp_days'] = (df['timestamp'] - df['timestamp'].min()).dt.days

# UI - Dashboard
st.title("🔌 Energy Consumption Prediction Dashboard")

zone_filter = st.selectbox("Select Zone", df['zone'].unique())
filtered_df = df[df['zone'] == zone_filter]

if filtered_df.empty:
    st.warning("No data available for the selected zone.")
else:
    st.line_chart(filtered_df.set_index('timestamp')['predicted_energy'])
    st.write("📄 Data Preview")
    st.dataframe(filtered_df.sort_values(by='timestamp', ascending=False))

# ========================
# Energy Consumption Prediction
# ========================
st.header("📊 Predict Energy Consumption")

with st.form("prediction_form"):
    temperature = st.number_input("Temperature (°C)", 0.0, 50.0, 25.0)
    humidity = st.number_input("Humidity (%)", 0.0, 100.0, 50.0)
    sqft = st.number_input("Square Footage", 100.0, 10000.0, 1000.0)
    occupancy = st.number_input("Occupancy", 0, 1000, 10)
    hvac = st.selectbox("HVAC Usage", ["On", "Off"])
    lighting = st.selectbox("Lighting Usage", ["On", "Off"])
    renewable = st.number_input("Renewable Energy Generated (kWh)", 0.0, value=5.0)
    holiday = st.selectbox("Holiday", ["Yes", "No"])
    hour = st.slider("Hour of Day", 0, 23, 12)
    day = st.slider("Day", 1, 31, 15)
    month = st.slider("Month", 1, 12, 6)
    dayofweek = st.selectbox("Day of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    submitted = st.form_submit_button("Predict")

if submitted:
    dataset = pd.read_csv("Energy_consumption.csv")
    dataset.columns = dataset.columns.str.strip()
    dataset['Timestamp'] = pd.to_datetime(dataset['Timestamp'])

    # Encode categorical fields
    dataset['HVACUsage'] = dataset['HVACUsage'].map({'On': 1, 'Off': 0})
    dataset['LightingUsage'] = dataset['LightingUsage'].map({'On': 1, 'Off': 0})
    dataset['Holiday'] = dataset['Holiday'].map({'Yes': 1, 'No': 0})
    dataset['hour'] = dataset['Timestamp'].dt.hour
    dataset['day'] = dataset['Timestamp'].dt.day
    dataset['month'] = dataset['Timestamp'].dt.month
    dataset = pd.get_dummies(dataset, columns=['DayOfWeek'])

    # Prepare model
    all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_dummies = [f'DayOfWeek_{d}' for d in all_days if f'DayOfWeek_{d}' in dataset.columns]
    feature_cols = ['Temperature', 'Humidity', 'SquareFootage', 'Occupancy',
                    'HVACUsage', 'LightingUsage', 'RenewableEnergy', 'Holiday',
                    'hour', 'day', 'month'] + day_dummies

    X = dataset[feature_cols]
    y = dataset['EnergyConsumption']

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Prepare input data
    input_data = {
        'Temperature': temperature,
        'Humidity': humidity,
        'SquareFootage': sqft,
        'Occupancy': occupancy,
        'HVACUsage': 1 if hvac == "On" else 0,
        'LightingUsage': 1 if lighting == "On" else 0,
        'RenewableEnergy': renewable,
        'Holiday': 1 if holiday == "Yes" else 0,
        'hour': hour,
        'day': day,
        'month': month,
    }

    for d in all_days:
        col = f'DayOfWeek_{d}'
        input_data[col] = 1 if d == dayofweek else 0

    for col in feature_cols:
        if col not in input_data:
            input_data[col] = 0

    input_df = pd.DataFrame([input_data])[feature_cols]
    prediction = model.predict(input_df)[0]
    st.success(f"✅ Predicted Energy Consumption: **{prediction:.2f} kWh**")

    # Add the predicted result to the filtered dataframe for graphing
    predicted_df = pd.DataFrame({
        'timestamp': [pd.Timestamp.now()],
        'predicted_energy': [prediction]
    })

    # Append predicted result to the existing data and display on line chart
    updated_df = pd.concat([filtered_df, predicted_df], ignore_index=True)
    
    # Plot updated graph including predicted value
    st.line_chart(updated_df.set_index('timestamp')['predicted_energy'])
    
    # Insert result into DB
    prediction_data = {
        'zone': zone_filter,
        'temperature': temperature,
        'humidity': humidity,
        'square_footage': sqft,
        'occupancy': occupancy,
        'hvac_usage': 1 if hvac == "On" else 0,
        'lighting_usage': 1 if lighting == "On" else 0,
        'renewable_energy': renewable,
        'holiday': 1 if holiday == "Yes" else 0,
        'hour': hour,
        'day': day,
        'month': month,
        'day_of_week': dayofweek,
        'predicted_energy': float(prediction)
    }

    try:
        with engine.begin() as connection:  # ensures autocommit
            query = text("""
                INSERT INTO predictions_results (
                    zone, temperature, humidity, square_footage, occupancy,
                    hvac_usage, lighting_usage, renewable_energy, holiday,
                    hour, day, month, day_of_week, predicted_energy
                ) VALUES (
                    :zone, :temperature, :humidity, :square_footage, :occupancy,
                    :hvac_usage, :lighting_usage, :renewable_energy, :holiday,
                    :hour, :day, :month, :day_of_week, :predicted_energy
                )
            """)
            connection.execute(query, prediction_data)
            st.success("📝 Prediction result stored in database successfully!")
    except Exception as e:
        st.error(f"❌ Error inserting into DB: {e}")

# Close connection
engine.dispose()
