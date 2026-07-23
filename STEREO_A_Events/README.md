# STEREO-A & STEREO-B Solar Wind & Magnetic Field Events

This repository contains cleaned and extracted solar wind and magnetic field data from the **STEREO Ahead** and **STEREO Behind** spacecraft, focused specifically on 5-day windows surrounding five key event dates in 2010 and 2011.

## Events Extracted
The data has been extracted from 2 days prior to 3 days after the following target dates:

**STEREO Ahead:**
1. **Aug 31, 2010** (Window: 2010-08-29 to 2010-09-03)
2. **Oct 20, 2010** (Window: 2010-10-18 to 2010-10-23)
3. **Nov 02, 2010** (Window: 2010-10-31 to 2010-11-05)

**STEREO Behind:**
4. **Nov 11, 2010** (Window: 2010-11-09 to 2010-11-14)
5. **Jan 21, 2011** (Window: 2011-01-19 to 2011-01-24)

## Data Source
The data originates from the `STA_L2_MAGPLASMA_1M` and `STB_L2_MAGPLASMA_1M` datasets (STEREO IMPACT/MAG Magnetic Field and PLASTIC Solar Wind Plasma Data), downloaded directly via the NASA CDAWeb API. 

Because NASA provides this dataset in massive, full-calendar-year `.cdf` files, the data here has been pre-processed and parsed down to exact 1-minute resolution `.csv` files covering only the windows of interest.

## Variables Included
Each CSV file contains 8,640 rows (1-minute resolution over exactly 6 full days) with the following features:
- `Time`: Datetime (UTC)
- `BField_R`, `BField_T`, `BField_N`: Magnetic field vector in RTN coordinates
- `BTotal`: Total magnetic field
- `Np`: Solar wind proton number density
- `Vp`: Proton bulk speed
- `Tp`: Proton temperature
- `Beta`: Plasma Beta
- `Entropy`: Entropy
- `Total_Pressure`: Total magnetic and plasma pressure

*(NASA Fill values like `-1.0E31` have been replaced with standard `NaN`)*

## Repository Structure
The repository is organized by satellite and event date. Each folder contains the exact `.csv` extraction for the event window.

```
├── Event_2010-08-31/
│   └── STEREO_A_Event_2010-08-31.csv
...
├── STEREO_B_Events/
│   ├── Event_2010-11-11/
│   │   └── STEREO_B_Event_2010-11-11.csv
...
```

*Note: The raw yearly NASA `.cdf` files are ignored by git due to their large size; you can regenerate them using the Python scripts provided in the root directory.*