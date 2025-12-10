import pandas as pd

# takes existing data from 1969-2007 through Romer's Dataset
# https://www.openicpsr.org/openicpsr/project/135741/version/V1/view?path=/openicpsr/135741/fcr:versions/V1/Monetary_shocks.zip&type=file
def modify_romer_dataset():
    romer_dataset = "RRimport.xlsx"

    df = pd.read_excel(romer_dataset)


    # getting date into FRED date format
    # convert MMDDYY number into YYYY-MM-DD
    s_date = df["MTGDATE"].astype(int).astype(str)
    s_date = s_date.str.zfill(6) 

    year = s_date.str[4:6].astype(int)
    month = s_date.str[:2].astype(int)
    day = s_date.str[2:4].astype(int)

    year_converted = year.where(year >= 50, year + 100) + 1900
    df["date"] = pd.to_datetime(dict(year=year_converted,month=month,day=day))
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    # convert date to next friday in accordance to FRED style
    df["date"] = pd.to_datetime(df["date"])
    # f_date refers to the adjusted friday date
    df["f_date"] = df["date"] + pd.to_timedelta((4 - df["date"].dt.weekday) % 7, unit="D")
    df["f_date"] = df["f_date"].dt.strftime("%Y-%m-%d")

    # getting basis point convertion 
    # points are rounded to nearest -50, -25, 0, 25, 50
    df["change_bps"] = round((df["DTARG"] * 100) / 25) * 25
    df["change_bps"] = df["change_bps"].clip(lower=-50, upper=50)
    df["change_bps"] = df["change_bps"].replace(-0, 0)

    date_bps_df = df[["date","f_date", "change_bps"]].copy() 

    #necessary_data = "data_1969_2007.csv"
    #date_bps_df.to_csv(necessary_data, index=False)

    return date_bps_df