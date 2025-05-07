import os
import pandas as pd
import mysql.connector
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# ========= Step 1: Load the dataset =========

csv_path = 'Energy_consumption.csv'
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"❌ File '{csv_path}' not found. Please check the path.")

df = pd.read_csv(csv_path)

# ========= Step 2: Clean and format =========

df.columns = df.columns.str.strip()
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Map categorical values
df['HVACUsage'] = df['HVACUsage'].map({'On': 1, 'Off': 0})
df['LightingUsage'] = df['LightingUsage'].map({'On': 1, 'Off': 0})
df['Holiday'] = df['Holiday'].map({'Yes': 1, 'No': 0})

# One-hot encoding for DayOfWeek
df = pd.get_dummies(df, columns=['DayOfWeek'], drop_first=True)

# Time-based features
df['hour'] = df['Timestamp'].dt.hour
df['day'] = df['Timestamp'].dt.day
df['month'] = df['Timestamp'].dt.month

# ========= Step 3: Prepare features and target =========

feature_cols = ['Temperature', 'Humidity', 'SquareFootage', 'Occupancy',
                'HVACUsage', 'LightingUsage', 'RenewableEnergy', 'Holiday',
                'hour', 'day', 'month'] + [col for col in df.columns if col.startswith('DayOfWeek_')]

X = df[feature_cols]
y = df['EnergyConsumption']

# ========= Step 4: Model Training =========

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ========= Step 5: Predictions & Evaluation =========

df['predicted_energy'] = model.predict(X)
mae = mean_absolute_error(y_test, model.predict(X_test))
print(f"✅ Mean Absolute Error: {round(mae, 2)}")

# ========= Step 6: Insert predictions into MySQL =========

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='energy_db'
    )
    cursor = conn.cursor()
    cursor.execute("DELETE FROM energy_predictions")

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO energy_predictions (timestamp, zone, predicted_energy)
            VALUES (%s, %s, %s)
        """, (row['Timestamp'].to_pydatetime(), 'ZoneA', float(row['predicted_energy'])))

    conn.commit()
    print("📦 Predictions successfully inserted into MySQL database.")

except mysql.connector.Error as err:
    print(f"❌ MySQL Error: {err}")

finally:
    if 'cursor' in locals(): cursor.close()
    if 'conn' in locals(): conn.close()

# ========= Step 7: OLAP Operations =========

print("\n--- OLAP Operations ---")

# Roll-up: Monthly average
monthly = df.groupby('month')['predicted_energy'].mean()
print("\n📈 Roll-up (Monthly average):\n", monthly)

# Drill-down: Daily for January
january = df[df['month'] == 1].groupby('day')['predicted_energy'].mean()
print("\n🔍 Drill-down (January daily average):\n", january)

# Slice: 9 AM records
slice_9am = df[df['hour'] == 9][['Timestamp', 'predicted_energy']]
print("\n⏰ Slice (9 AM):\n", slice_9am)

# Dice: Month = 1 and Hour 8–10
dice = df[(df['month'] == 1) & (df['hour'].between(8, 10))][['Timestamp', 'predicted_energy']]
print("\n🎲 Dice (Jan, 8–10 AM):\n", dice)

# Pivot table: Hour vs Day
pivot = pd.pivot_table(df, values='predicted_energy', index='hour', columns='day', aggfunc='mean')
print("\n📊 Pivot (Hour vs Day):\n", pivot)
