from dotenv import load_dotenv
import os 
from fredapi import Fred
import pandas as pd
import numpy as np


# dataset considers both scheduled rate hike's / cuts based on 
# actual meeting dates, and emergency rate hikes or cuts 
# that don't have an actual meeting date 

# note that there are different policies over time resulting in 
# inconsistent decision timies 

# federal funds rate can change without FOMC meeting 
# need to correctly 

# dataset must label policy action vs. natural federal funds rate change 
# Post 2008 has correct fed rate decision 
# outline decisions are categorized as 50, -50 bps 

# confirmed emergency rate cuts or hikes included prior to 2008 

# note that specific dates result in no data due to market being phsyically shut down 
# e.g., 9/11 

# cite romer data set

# pre- 1990s the fed also moved in 12.5 bps and 18.75 bps 62.5 bps
# convert -12.5 - 12.5 to 0 .1875 to 25 , 

# pre 2009 fred saw market outcome from a shift
# the federal rate decision is the mechanical driver, 
# it drives the federal funds rate to change over time

# started official basis point hiks/cuts in 1994 
# converted to next friday

def create_main_data():
    load_dotenv()
    FRED_API_KEY = os.getenv("FRED_API_KEY")


    fred = Fred(api_key=FRED_API_KEY)

    # fedfunds is a temporary placeholder, since it has monthly data, and not daily like 
    # ffr_upper and ffr_lower, which can be configured to the fed meeting date
    # this specific subsection of the change in bps column will be replaced by the 
    # Romer and Romer Dataset with (adjusted) change in bps and modified
    series_ids = {
        "fedfunds": "FEDFUNDS",
        "ffr_upper": "DFEDTARU",
        "ffr_lower": "DFEDTARL",
        "cpi": "CPIAUCSL",
        "core_pce": "PCEPILFE",
        "gdp": "GDPC1",
        "unrate": "UNRATE",
        "sentiment": "UMCSENT",
        "recession": "USREC"
    }

    data = {}
    for name, id in series_ids.items():
        print(f"Fetching {name} ({id})")
        try:
            data[name] = fred.get_series(id)
        except Exception as e:
            print(f"Couldn't find")
            raise

    df = pd.DataFrame(data)

    df.index = pd.to_datetime(df.index)

    df = df.resample("W-FRI").last()
    df = df.ffill()

    # pre-2009 used fed_funds so need to connect both lists 
    df["ffr_mid"] = np.where(df["ffr_upper"].notna(), 
                            (df["ffr_upper"] + df["ffr_lower"]) / 2, 
                            df["fedfunds"])
    df["ffr_change_bps"] = (df["ffr_mid"] - df["ffr_mid"].shift(1)) * 100

    def map_to_class(x):
        if x <= -50: return -50
        elif x < 0:  return -25
        elif x == 0: return 0
        elif x <= 25: return 25
        else: return 50

    # 5 classes, anything greater than 50 bps is categorized as 50 bps, and anything less than -50 bps is categorized at -50 bps
    df["adjusted_change_bps"] = df["ffr_change_bps"].apply(map_to_class)
    
    # --------------------------------------------------------------
    # CPI 
    # cpi as a year over year measure 
    df["cpi_yoy"] = df["cpi"].pct_change(52) * 100
    # cpi as a measure
    df["cpi_12w_change"] = df["cpi_yoy"] - df["cpi_yoy"].shift(12)
    # --------------------------------------------------------------
    # Inflation
    # inflation year over year 
    df["inflation"] = df["core_pce"].pct_change(52) * 100
    # --------------------------------------------------------------
    # GDP 
    # gdp year over year 
    df["gdp_yoy"] = df["gdp"].pct_change(4) * 100
    # year over year gdp compared to 6 months prior old data 
    df["gdp_26w_change"] = df["gdp_yoy"] - df["gdp_yoy"].shift(2)
    # --------------------------------------------------------------
    # Unemployment 
    # umeployment compared to three months ago 
    df["unemployment_rate"] = df["unrate"]
    df["unemployment_rate_12w_change"] = df["unrate"] - df["unrate"].shift(12)
    # --------------------------------------------------------------
    # Consumer Sentiment
    # consumer sentiment compared to three months ago 
    df["consumer_sentiment"] = df["sentiment"]
    df["consumer_sentiment_12w_change"] = df["sentiment"] - df["sentiment"].shift(12)
    # --------------------------------------------------------------
    # Past Performances 
    # determines federal funds rate from three months ago 
    df["ffr_change_12w"] = df["ffr_change_bps"].rolling(12).sum()
    # determines numbers of hikes in the last 3 months 
    df["num_hikes_12w"] = (df["ffr_change_bps"] > 0).rolling(12).sum()
    # determines number of cuts in the last 3 months 
    df["num_cuts_12w"] = (df["ffr_change_bps"] < 0).rolling(12).sum()

    # determines number of weeks since the last hike 
    df["weeks_since_last_hike"] = (
        df["ffr_change_bps"].gt(0).groupby((df["ffr_change_bps"] <= 0).cumsum()).cumcount()
    )
    # determines number of weeks since the last cut
    df["weeks_since_last_cut"] = (
        df["ffr_change_bps"].lt(0).groupby((df["ffr_change_bps"] >= 0).cumsum()).cumcount()
    )
    # --------------------------------------------------------------
    final_columns = [
        "adjusted_change_bps",
        "cpi_yoy", 
        "cpi_12w_change", 
        "inflation",
        "gdp_yoy", 
        "gdp_26w_change",
        "unemployment_rate", 
        "unemployment_rate_12w_change",
        "consumer_sentiment", 
        "consumer_sentiment_12w_change",
        "ffr_mid", 
        "ffr_change_12w",
        "num_hikes_12w", 
        "num_cuts_12w",
        "weeks_since_last_hike", 
        "weeks_since_last_cut",
        "recession"
    ]
    
    data_df = df[final_columns].dropna()
    data_df = data_df.reset_index().rename(columns={"index": "date"})

    # Romer's dataset only has data starting from 1969, need to drop values prior
    data_df = data_df[data_df["date"] >= "1969-01-17"]

    # data_df.to_csv("fred_main_data.csv")

    return data_df