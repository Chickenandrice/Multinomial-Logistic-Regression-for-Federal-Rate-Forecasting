from main_data import create_main_data
from modify_romer import modify_romer_dataset
from meeting_dates_1969_2025 import find_all_meeting_dates


import pandas as pd 

# note that all meeting dates are adjusted to the closest next friday 
# to reflect the data obtained from FRED API

# the specific time range of this dataset is from 1969-01-17 to 2025-12-05

if __name__ == "__main__":

    # includes all data from 1969 to 2025 as a data frame
    # however, this doesn't include accurate federal fund rate changes 
    # after fed reserve meetings. 
    main_data = create_main_data()

    # includes modified bps data from 1969 to 2007 as a data frame
    # note that prior to 1990s, there wasn't an offical bps move (e.g., 12.5, 18.75, -62.5)
    # this has been adjusted to reflect (-50, -25, 0, 25, 50), where values 
    # less than -50 are categorized at -50 and values more than 50 are categorized as 50
    # Dataset Obtained From 
    # C. D. Romer and D. H. Romer, "A New Measure of Monetary Shocks: Derivation
    # and Implications," American Economic Review, vol. 94, no. 4, pp. 1055–1084, 2004.
    # doi: 10.1257/0002828042002651
    bps_data_from_1969_2007 = modify_romer_dataset()

    # includes all official meeting dates from 1960 to 2025 as a data frame
    # this is used to pull all the dates of meetings, and determine which 
    # datapoints from main are viable 
    meeting_dates = find_all_meeting_dates()

    meeting_date_only_data = main_data[main_data["date"].isin(meeting_dates["f_date"])].copy()

    map_bps = bps_data_from_1969_2007.set_index("date")["change_bps"]
    
    meeting_date_only_data["adjusted_change_bps"] = meeting_date_only_data["date"].map(map_bps).fillna(meeting_date_only_data["adjusted_change_bps"])

    meeting_date_only_data["adjusted_change_bps"] = meeting_date_only_data["adjusted_change_bps"].astype(int)

    final_dataset = "fred_romer_change_bps_dataset_1969_2025.csv" 

    # NOTE that there is a gap in data in 2008 because 
    # existing data only goes from 1969 - 2007 (Romer and Romer's Dataset)
    # and 2008-12-16 - 2025 (FRED introduces target range)
    # The data points from 2008-02-01 to 2008-12-19 were MANUALLY MODIFIED TO REFLECT THE MEETING CHANGES
    # specifically, 
    # 2008-02-01, -50 
    # 2008-03-21, -50
    # 2008-05-02, -25
    # 2008-06-27,  0
    # 2008-08-08,  0 
    # 2008-09-19,  0
    # 2008-10-31, -50
    # 2008-12-19, -50 
    
    # also NOTE THAT NOT ALL EMERGENCY MEETINGS ARE ACCOUNTED FOR 
    meeting_date_only_data.to_csv(final_dataset, index=False)
