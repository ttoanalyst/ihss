import pandas as pd
https://drive.google.com/uc?export=download&id=FILE_ID
file_url = f"https://docs.google.com/uc?export=download&id=1pjaVbBfL4K6rNL9sJqwtH9D_SHTpK_6_"

def prepare_data(level=None):
    woreda = pd.read_excel(file_url, sheet_name="Woreda Activities")
    woreda["Level"] = "Woreda level"
    region = pd.read_excel(file_url, sheet_name="Region Activities")
    region["Level"] = "Regional level"
    national = pd.read_excel(file_url, sheet_name="National Activities")
    national["Level"] = "National level"

    df = pd.DataFrame()
    for d in [woreda, region, national]:
        d.columns = d.columns.str.lower()
        df = pd.concat([d, df], axis=0)

    pmap = {
        'Availability of essential inputs ensured': "PO3-Inputs & HMIS",
        'Improved primary health care governance': "PO1-Governance",
        'Improved efficiencies and resource mobilization for health': "PO2-Financing",
        'Cross cutting': "Cross cutting"
    }
    df["po key"] = df["primary outcome"].map(pmap)
    print(df["level"].unique())
    if level == None:
        return df
    elif level == "Activity":
        filtered_rows = (df["level"] == "Woreda level") | (df["level"] =="Regional level")
        return df.loc[filtered_rows,:]
