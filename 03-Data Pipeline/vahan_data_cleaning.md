# VAHAN Data Cleaning Methodology

## Data Source

Vehicle registration data was sourced from the Ministry of Road Transport & Highways (MoRTH) VAHAN dashboard, covering national vehicle registrations between 2020 and 2025.

The dataset contained approximately 24 million rows and included information across fuel types, vehicle classes, manufacturers, and regional transport offices (RTOs).

---

## Data Challenges

The raw dataset presented multiple structural issues:

- inconsistent column structures across files  
- malformed CSV rows with additional delimiters  
- inconsistent encoding and special characters  
- non-standard city and RTO naming conventions  
- mixed aggregation levels (vehicle-level vs count-level data)  

As a result, direct city-level analysis was not feasible without extensive preprocessing.

---

## Processing Approach

To handle dataset scale and quality constraints, the following approach was adopted:

- chunk-based reading to manage memory usage  
- strict column selection to reduce processing overhead  
- tolerant parsing with malformed rows skipped  
- encoding error handling to avoid read failures  

This ensured stable processing across the full dataset without data loss from file-level corruption.

---

## Filtering Logic

To isolate the relevant market segment, records were filtered using the following criteria:

### Fuel Type
Only electric vehicles were retained, including:

- `ELECTRIC(BOV)`  
- `PURE EV`  

All hybrid, CNG, petrol, and diesel records were excluded.

---

### Vehicle Category
Only two-wheeler formats were considered:

- Motorcycles / scooters  
- Mopeds  

Three-wheelers, passenger vehicles, and commercial classes were removed.

---

### Registration Metric

Where vehicle-level entries were unavailable, the dataset’s `vehicleCount` field was used as the unit of measurement.

All non-numeric or malformed values were coerced and excluded to preserve aggregation accuracy.

---

## Output of Cleaning Stage

The output of this step was a clean dataset containing:

- electric two-wheeler registrations only  
- valid registration counts  
- standardised RTO identifiers  

This dataset served as the foundation for city-level aggregation and directional adoption analysis.
