from flask import Flask, request, jsonify
import logging
import joblib
import pandas as pd
from tensorflow import keras
import xgboost as xgb

# Load the trained model
model = keras.models.load_model("../models/lstm_model.h5")

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(message)s')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get JSON data from the request
        data = request.get_json(force=True)
        logging.info(f"Incoming request data: {data}")

        # Extract features and ensure they are floats
        features = pd.DataFrame([[
            data['purchase_value'], 
            data['age'], 
            data['hour_of_day']
        ]], columns=['purchase_value', 'age', 'hour_of_day'])

        logging.info(f"Processed features: {features}")

        # Fill NaN values if any
        features = features.fillna(0)

        # Make prediction
        prediction = model.predict(features)
        logging.info(f"Raw Prediction: {prediction}")

        # Extract prediction value
        prediction_value = prediction[0][0]  # Ensure it's a single value
        if pd.isna(prediction_value):  # Check if the prediction is NaN
            raise ValueError("Model returned NaN prediction")

        return jsonify({'prediction': int(prediction_value)})
    
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
