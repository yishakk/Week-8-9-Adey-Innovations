import pandas as pd

def preprocess_data(df):
    if 'datetime_column' in df.columns:
        df['datetime_column'] = pd.to_datetime(df['datetime_column'])
        df['year'] = df['datetime_column'].dt.year
        df['month'] = df['datetime_column'].dt.month
        df['day'] = df['datetime_column'].dt.day
        df['hour'] = df['datetime_column'].dt.hour
        df.drop(columns=['datetime_column'], inplace=True)
    return df