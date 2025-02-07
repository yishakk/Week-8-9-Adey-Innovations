import pandas as pd

def load_data(file_path):
    return pd.read_csv(file_path)

def load_data_with_parse(file_path, parse_dates=None):
    return pd.read_csv(file_path, parse_dates=None)

def load_data_excel(file_path):
    return pd.read_excel(file_path)