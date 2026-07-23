import os
import urllib.request
import json
from datetime import datetime, timedelta

# Target events and their windows (Target Date, Start, End)
events = [
    ("2010-08-31", "2010-08-29", "2010-09-03"),
    ("2010-10-20", "2010-10-18", "2010-10-23"),
    ("2010-11-02", "2010-10-31", "2010-11-05"),
    ("2010-11-11", "2010-11-09", "2010-11-14"),
    ("2011-01-21", "2011-01-19", "2011-01-24")
]

def download_via_api():
    base_dir = "STEREO_A_Events"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        
    for target, start_str, end_str in events:
        print(f"\nProcessing Event: {target} (Window: {start_str} to {end_str})")
        
        event_dir = os.path.join(base_dir, f"Event_{target}")
        if not os.path.exists(event_dir):
            os.makedirs(event_dir)
            
        start_date = start_str.replace("-", "") + "T000000Z"
        end_date = end_str.replace("-", "") + "T235959Z"
        
        # Note: NASA groups this entire dataset by YEAR in single large files per year!
        # sta_l2_magplasma_1m_20100101_v07.cdf contains the whole 2010 year.
        # So we just request the original files overlapping our time range.
        url = f"https://cdaweb.gsfc.nasa.gov/WS/cdasr/1/dataviews/sp_phys/datasets/STA_L2_MAGPLASMA_1M/orig_data/{start_date},{end_date}"
        print(f"Requesting API data for {target}...")
        
        try:
            req = urllib.request.Request(url, headers={'Accept': 'application/json'})
            html = urllib.request.urlopen(req).read().decode('utf-8')
            data = json.loads(html)
            
            if 'FileDescription' in data:
                for file_info in data['FileDescription']:
                    file_url = file_info.get('Name')
                    if file_url:
                        filename = file_url.split('/')[-1]
                        save_path = os.path.join(event_dir, filename)
                        
                        if not os.path.exists(save_path):
                            print(f"  Downloading {filename}... (this may take a minute, it's a yearly file)")
                            urllib.request.urlretrieve(file_url, save_path)
                            print(f"  Saved {filename}")
                        else:
                            print(f"  Already have {filename}")
            else:
                print("  No files found in response.")
                
        except Exception as e:
            print(f"  Error for {target}: {e}")

if __name__ == "__main__":
    download_via_api()
