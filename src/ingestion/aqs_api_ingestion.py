import pandas as pd
import requests
from config import settings
from requests.adapters import HTTPAdapter, Retry
import time
import calendar

BASE_URL = settings.base_url
RETRIES = Retry(
    total=5,
    backoff_factor=0.2,
    status_forcelist=[429, 500, 502, 503, 504]
)
request_session = requests.Session()
request_session.mount(BASE_URL, HTTPAdapter(max_retries=RETRIES))

def get_california_pm25_data(year: int):
    """Get California AQS data from the API for a given year. Fetch by month with pauses in between requests so the API does not block our request.
    Fetch requests from the beginning of one month to the beginning of the next. 

    Args:
        year (str): Study year
    """
    PARAMS = {
            "email": settings.epa_user,
            "key": settings.epa_key,
            "param": 88101,
            "state": "06",
        }
    
    format_month = lambda x: "{:02d}".format(x) if x < 10 else x
    df = []
    start = time.time()
    
    print(f"================Started fetch for {year}===========================")
    for month in range(1, 13):
        PARAMS["bdate"] = f"{year}{format_month(month)}01"
        PARAMS['edate'] = f"{year}{format_month(month)}{calendar.monthrange(year, month)[1]}"
        
        print(f"===================MONTH {month} STARTED=========================")
        try:
            api_data = request_session.get(f"{BASE_URL}dailyData/byState", params=PARAMS)
            api_data.raise_for_status()
            aqs_records = api_data.json().get('Data', [])
            
            if not aqs_records:
                raise Exception(f"Failed to get month {month} of {year}")
            
            df.extend(api_data.json().get('Data', []))
        except Exception as e:
            print(f"Error while fetching data for {year}: {e}")
        print(f"==================MONTH {month} DONE============================")
        time.sleep(5)
        
    df = pd.DataFrame(df)
    df.to_csv(f"CA{year}.csv", index=False)
    end = time.time()
    print(f"================Finished fetching data for {year}. Time elapsed: {end - start}s====================")
    
if __name__ == "__main__":
    # for year in range(2018, 2026):
    #     get_california_pm25_data(year)
        
    # November for 2022 raised a max retries error. Retrying for 2022
    
    get_california_pm25_data(2022)
