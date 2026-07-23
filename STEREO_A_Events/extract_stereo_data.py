import os
import cdflib
import pandas as pd
from datetime import datetime

# Define our specific event windows (Start, End)
events = [
    {"target": "2010-11-11", "start": "2010-11-09", "end": "2010-11-14"},
    {"target": "2011-01-21", "start": "2011-01-19", "end": "2011-01-24"}
]

base_dir = "STEREO_B_Events"

def process_event_data():
    for event in events:
        target = event["target"]
        start_date = pd.to_datetime(event["start"])
        # Set end date to the very end of the day
        end_date = pd.to_datetime(event["end"]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        
        event_dir = os.path.join(base_dir, f"Event_{target}")
        
        # Find the .cdf file in this event's directory
        cdf_file = None
        if os.path.exists(event_dir):
            for file in os.listdir(event_dir):
                if file.endswith(".cdf"):
                    cdf_file = os.path.join(event_dir, file)
                    break
                
        if not cdf_file:
            print(f"No CDF file found in {event_dir}")
            continue
            
        print(f"\nProcessing {target} (Extracting {start_date} to {end_date})...")
        
        try:
            # Open the CDF file
            cdf = cdflib.CDF(cdf_file)
            
            # The time variable is typically "Epoch" in NASA CDF files
            # Let's get the time and convert to datetime objects
            try:
                epoch_data = cdf.varget("Epoch")
                times = cdflib.cdfepoch.to_datetime(epoch_data)
            except ValueError:
                # Some files use different time variable names like 'time_tags'
                print("Could not find 'Epoch', skipping...")
                continue
            
            # Create a base dataframe with just time
            df = pd.DataFrame({'Time': times})
            
            # Variables of interest for Magnetic Field and Plasma
            # From NASA dataset description:
            variables = [
                'BField',          # Magnetic Field Vector (RTN)
                'BTotal',          # Total Magnetic Field
                'Np',              # Solar Wind Proton Number Density
                'Vp',              # Proton Bulk Speed
                'Tp',              # Proton Temperature
                'Beta',            # Beta
                'Entropy',         # Entropy
                'Total_Pressure'   # Total Pressure
            ]
            
            for var in variables:
                try:
                    data = cdf.varget(var)
                    
                    # If it's a vector (like BField RTN), split it into components
                    if len(data.shape) > 1 and data.shape[1] == 3:
                        df[f'{var}_R'] = data[:, 0]
                        df[f'{var}_T'] = data[:, 1]
                        df[f'{var}_N'] = data[:, 2]
                    else:
                        df[var] = data
                except Exception as e:
                    # Not all variables might exist, skip if missing
                    pass
            
            # Filter the dataframe to only include our 5-day window
            mask = (df['Time'] >= start_date) & (df['Time'] <= end_date)
            window_df = df.loc[mask].copy()
            
            # Replace common NASA fill values (like -1.0E31) with NaN
            import numpy as np
            # Generally values < -1e30 are fill values in NASA CDFs
            numeric_cols = window_df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                window_df.loc[window_df[col] < -1e30, col] = np.nan
            
            # Save to CSV
            csv_path = os.path.join(event_dir, f"STEREO_B_Event_{target}.csv")
            window_df.to_csv(csv_path, index=False)
            
            print(f"  Extracted {len(window_df)} rows.")
            print(f"  Saved precise data window to: {csv_path}")
            
        except Exception as e:
            print(f"Error processing {cdf_file}: {e}")

if __name__ == "__main__":
    process_event_data()