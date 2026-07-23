import os
import cdflib
import pandas as pd
from datetime import datetime

# Define our specific event windows (Start, End)
events = [
    {"target": "2010-08-31", "start": "2010-08-29", "end": "2010-09-03"},
    {"target": "2010-10-20", "start": "2010-10-18", "end": "2010-10-23"},
    {"target": "2010-11-02", "start": "2010-10-31", "end": "2010-11-05"},
    {"target": "2010-11-11", "start": "2010-11-09", "end": "2010-11-14"},
    {"target": "2011-01-21", "start": "2011-01-19", "end": "2011-01-24"}
]

base_dir = "STEREO_A_Events"

def process_event_data():
    for event in events:
        target = event["target"]
        start_date = pd.to_datetime(event["start"])
        # Set end date to the very end of the day
        end_date = pd.to_datetime(event["end"]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        
        event_dir = os.path.join(base_dir, f"Event_{target}")
        
        if not os.path.exists(event_dir):
            print(f"Skipping {target}: Directory {event_dir} does not exist.")
            continue
            
        # Find the .cdf file in this event's directory
        cdf_file = None
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
                'BFIELDRTN',          # Magnetic Field Vector (RTN)
                'BTOTAL',             # Total Magnetic Field
                'HAE',                # Spacecraft position in HAE coordinates
                'HEE',                # Spacecraft position in HEE coordinates
                'HEEQ',               # Spacecraft position in HEEQ coordinates
                'CARR',               # Spacecraft position in Carrington Heliographic coordinates
                'HCI',                # Spacecraft position in Heliocentric Inertial
                'R',                  # Distance of STEREO from the Sun
                'Np',                 # Solar wind proton number density
                'Vp',                 # Proton Bulk Speed
                'Tp',                 # Proton Temperature
                'Vth',                # Proton Thermal Speed
                'Vr_Over_V_RTN',      # Direction cosine of radial velocity
                'Vt_Over_V_RTN',      # Direction cosine of tangential velocity
                'Vn_Over_V_RTN',      # Direction cosine of normal velocity
                'Vp_RTN',             # Solar Wind Proton Speed
                'Entropy',            # Entropy
                'Beta',               # Beta
                'Total_Pressure',     # Total Pressure
                'Cone_Angle',         # Cone Angle of magnetic field
                'Clock_Angle',        # Clock Angle of B-field
                'Magnetic_Pressure',  # Magnetic Pressure
                'Dynamic_Pressure'    # Dynamic Pressure
            ]
            
            for var in variables:
                try:
                    data = cdf.varget(var)
                    
                    # If it's a vector (like BField RTN), split it into components
                    if len(data.shape) > 1 and data.shape[1] == 3:
                        if var == 'BFIELDRTN':
                            df['BField_R'] = data[:, 0]
                            df['BField_T'] = data[:, 1]
                            df['BField_N'] = data[:, 2]
                        elif var == 'Vp_RTN':
                            df['Vp_R'] = data[:, 0]
                            df['Vp_T'] = data[:, 1]
                            df['Vp_N'] = data[:, 2]
                        elif var == 'HAE':
                            df['HAE_X'] = data[:, 0]
                            df['HAE_Y'] = data[:, 1]
                            df['HAE_Z'] = data[:, 2]
                        elif var == 'HEE':
                            df['HEE_X'] = data[:, 0]
                            df['HEE_Y'] = data[:, 1]
                            df['HEE_Z'] = data[:, 2]
                        elif var == 'HEEQ':
                            df['HEEQ_X'] = data[:, 0]
                            df['HEEQ_Y'] = data[:, 1]
                            df['HEEQ_Z'] = data[:, 2]
                        elif var == 'CARR':
                            df['CARR_X'] = data[:, 0]
                            df['CARR_Y'] = data[:, 1]
                            df['CARR_Z'] = data[:, 2]
                        elif var == 'HCI':
                            df['HCI_X'] = data[:, 0]
                            df['HCI_Y'] = data[:, 1]
                            df['HCI_Z'] = data[:, 2]
                        else:
                            df[f'{var}_X'] = data[:, 0]
                            df[f'{var}_Y'] = data[:, 1]
                            df[f'{var}_Z'] = data[:, 2]
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
            csv_path = os.path.join(event_dir, f"STEREO_A_Event_{target}.csv")
            window_df.to_csv(csv_path, index=False)
            
            print(f"  Extracted {len(window_df)} rows.")
            print(f"  Saved precise data window to: {csv_path}")
            
            # Clean up the CDF reader
            try:
                cdf.close()
            except AttributeError:
                pass
            
        except Exception as e:
            print(f"Error processing {cdf_file}: {e}")

if __name__ == "__main__":
    process_event_data()