import pandas as pd
from config import RAW_DIR, EONET_FILENAME, NOAA_FILENAME

def check_noaa():
    """Check eonet info, shape and null"""
    data_check(RAW_DIR/NOAA_FILENAME)

def check_eonet():
    """Check eonet info, shape and null"""
    data_check(RAW_DIR/EONET_FILENAME)


def data_check(path):
    eonet_data = pd.read_json(path)
    print("Data information for {path}.")
    eonet_data.info()
    print(eonet_data.isnull().sum())
    print(eonet_data.shape)

if __name__ == "__main__":
    check_noaa()
    check_eonet()