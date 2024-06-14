import sys
import re
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

def extract_datetimes(script_file):
    datetimes = []
    with open(script_file, 'r') as file:
        for line in file:
            match = re.search(r'"(\d{4}-\d{2}-\d{2} \d{2}:\d{2})"', line)
            if match:
                datetimes.append(match.group(1))
    return datetimes

def find_json_files(datetimes):
    json_files = []
    for dt in datetimes:
        dt_str = dt.replace(":", "-")
        json_file = os.path.join("..", "json_data", f"gcs_params{dt_str}.json")
        if os.path.exists(json_file):
            json_files.append(json_file)
    return json_files

def load_json_to_df(json_files):
    data = []
    for json_file in json_files:
        with open(json_file, 'r') as file:
            json_data = json.load(file)
            # Extract datetime from filename
            dt_str = re.search(r'gcs_params(\d{4}-\d{2}-\d{2} \d{2}-\d{2})\.json', json_file).group(1)
            dt = datetime.strptime(dt_str, '%Y-%m-%d %H-%M')
            json_data['datetime'] = dt
            data.append(json_data)
    df = pd.DataFrame(data)
    df.set_index('datetime', inplace=True)
    return df

def perform_linear_fit(df):
    # Convert datetime index to seconds since epoch for fitting
    df['time_seconds'] = (df.index - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
    
    # Perform linear fit
    fit = np.polyfit(df['time_seconds'], df['height'], 1)
    slope = fit[0]
    
    # Convert slope (solar radii per second) to km/s
    solar_radius_km = 696340  # Solar radius in kilometers
    speed_kms = slope * solar_radius_km
    
    return fit, speed_kms

def plot_fit(df, fit):
    plt.figure(figsize=(10, 6))
    plt.scatter(df.index, df['height'], color='blue', label='Data Points')
    
    # Generate fitted line
    fitted_line = np.polyval(fit, df['time_seconds'])
    
    plt.plot(df.index, fitted_line, color='red', label='Linear Fit')
    plt.xlabel('Time')
    plt.ylabel('Height (Solar Radii)')
    plt.title('Time vs Height Linear Fit')
    plt.legend()
    plt.show()

def delete_json_files(folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.json'):
            file_path = os.path.join(folder_path, file_name)
            os.remove(file_path)

def rename_png_files(folder_path, identifier):
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.png') and 'science' not in file_name and 'beacon' not in file_name:
            base_name = file_name.rsplit('.', 1)[0]
            new_file_name = f"{base_name}_{identifier}.png"
            os.rename(
                os.path.join(folder_path, file_name),
                os.path.join(folder_path, new_file_name)
            )

def main():
    if len(sys.argv) != 2:
        print("Usage: python analyse_gcs_results.py <shell_script.sh>")
        sys.exit(1)

    script_file = sys.argv[1]
    identifier = "beacon" if "beacon" in script_file else "science"
    
    datetimes = extract_datetimes(script_file)
    json_files = find_json_files(datetimes)
    
    if not json_files:
        print("No corresponding JSON files found.")
        sys.exit(1)
    
    df = load_json_to_df(json_files)
    print(df)

    # Perform linear fit and calculate speed
    fit, speed_kms = perform_linear_fit(df)
    
    # Print results
    print(f"Linear fit slope: {fit[0]} (solar radii/second)")
    print(f"Speed: {speed_kms:.2f} km/s")
    
    # Plot the fit
    plot_fit(df, fit)

    # Delete JSON files
    delete_json_files(os.path.join("..", "json_data"))

    # Rename PNG files
    rename_png_files(os.path.join("..", "json_data"), identifier)

if __name__ == "__main__":
    main()