# Prediction Changes in Federal Funds Rate Through Multinomial Logistic Regression

This project was built to determine a more feasible method of predicting changes in Federal Funds Rate after each Fed meeting. 

## Get Started 

```bash
    python -m venv venv 
    source venv/Scripts/activate
    pip install -r requirements.txt 
```



## Dataset 
This project contains a custom built dataset that contains every official 
Federal Reserve Meeting from 1969 to 2025. This dataset combines exactly
two different data sources, Romer and Romer's 2004 Monetary Policy Shocks dataset, and 
data from the Federal Reserve Economic Data (FRED). FRED data was obtained through 
its API. 

### Generating the Custom Dataset 
Note that you will have to go onto [FRED](https://www.stlouisfed.org/) and register an account. After you register for an account you will have to request an API key, which you should then create a .env file, and in the .env file you should insert your api key.

```env
    FRED_API_KEY={insert your api key}
```
Then you should run create_dataset.py. 
```bash
    cd dataset 
    python create_dataset.py
```
After this, your dataset will be created BUT, you will need to manually change 8 lines. 

Specifically, you should change the date and adjusted_change_bps below: 

```csv
    date, adjusted_change_bps 
    2008-02-01,-50 
    2008-03-21,0
    2008-05-02,-25
    2008-06-27,0
    2008-08-08,0
    2008-09-19,0
    2008-10-31,0
    2008-12-19,-25 
```
to 
```csv 
    date, adjusted_change_bps 
    2008-02-01,-50 
    2008-03-21,-50
    2008-05-02,-25
    2008-06-27,0
    2008-08-08,0
    2008-09-19,0
    2008-10-31,-50
    2008-12-19,-50 
```
This had to be done because of a dataset limitation between the two data sources. 
To this end, Romer's Data (1969-2007) and FRED's Data (2009-2025) were strung together after identifying all Federal Meeting Dates through the Federal Reserve and isolating those specific dates to create a comprehensive dataset with 510 datapoints. 

[Romer and Romer's 2004 Monetary Policy Shocks dataset](https://www.openicpsr.org/openicpsr/project/135741/version/V1/view?path=/openicpsr/135741/fcr:versions/V1/Monetary_shocks.zip&type=file)

[FRED (obtained through FRED API)](https://fred.stlouisfed.org/)

[All Fed Meeting Dates:](https://fraser.stlouisfed.org/title/federal-open-market-committee-meeting-minutes-transcripts-documents-677?browse=2020s#584519)

## Training and Results 
This can be observed through the file mult_log_regress.ipynb 

## Models 
Two models were created, one for 5 classes ([-50, -25, 0, 25, 25]) and one for 3 ([cut, hold, hike]). The 5 class model had limited datapoints for specific classes, which is why a 3 class model was made. Both demonstrated high accuracy (89% - 5 classes, 99% - 3 classes) after minimal feature engineering.
