import logging
import pandas as pd
from .mat_trans import mt


def process_csv(file):

    # Define column names for the CSV
    column_names = ['id', 'date', 'rating']

    # Read the CSV file, specifying column names explicitly
    # Note: Use 'file' directly since it's a file-like object
    df = pd.read_csv(file, names=column_names)

    # Process the data using the mt function
    sol = mt({
        'id': df['id'].tolist(),
        'rating': df['rating'].tolist(),
        'date': df['date'].tolist()
    })

    # Convert DataFrame to a dictionary for JSON serialization, if needed
    return sol.to_dict(orient='records')
