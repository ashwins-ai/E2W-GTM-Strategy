# City Aggregation Logic

## RTO-to-City Mapping Challenge

VAHAN data reports registrations at the RTO level rather than the city level.

However, RTO naming conventions vary significantly, including:

- multiple RTOs per city  
- directional tags (North, South, Central)  
- administrative prefixes (DTO, ARTO, ADDL RTO)  

Without normalization, this results in fragmented city counts and inaccurate demand representation.

---

## City Normalization Approach

To resolve this, a master RTO reference file was used to map:

- RTO code → city name  
- RTO code → state  

City names were standardized by:

- removing directional qualifiers  
- consolidating multiple RTOs into a single city entity  
- applying consistent capitalization and formatting  

This allowed accurate city-level aggregation.

---

## Aggregation Method

After normalization:

- EV registrations were aggregated by city and state  
- total electric two-wheeler volumes were calculated  
- duplicate RTO entries within the same city were merged  

This produced a single consolidated EV adoption value per city.

---

## Top-City Selection Rationale

Given the long-tail nature of Indian cities, the dataset was trimmed to the top 1,000 cities by electric two-wheeler registrations.

This step ensured:

- focus on cities with meaningful EV activity  
- reduction of noise from extremely low-volume regions  
- computational efficiency  
- relevance to near- and medium-term GTM decisions  

The trimmed dataset captured the vast majority of national E2W EV registrations while preserving geographic diversity.
