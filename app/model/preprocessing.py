from pandas import DataFrame

def preprocessing(df: DataFrame) -> DataFrame:
    
    # drop column yang tidak diperlukan
    df = df.drop(['id'], axis=1)
    
    # drop data yang null
    df = df.dropna()
    
    # drop data yang duplikat
    df = df.drop_duplicates()
    
    return df