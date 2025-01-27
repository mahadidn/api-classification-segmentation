from pandas import DataFrame
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
import pandas as pd


def preprocessingNB(df: DataFrame) -> DataFrame:
    
    # drop column yang tidak diperlukan
    df = df.drop(['id'], axis=1)
    
    # drop data yang null
    df = df.dropna()
    
    # drop data yang duplikat
    df = df.drop_duplicates()
    
    # Encode fitur kategorikal
    label_encoders = {}
    categorical_columns = ['gender', 'ever_married', 'graduated', 'profession', 'spending_score', 'segmentation']

    for col in categorical_columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le
    
    # Pisahkan fitur dan target
    X = df.drop('segmentation', axis=1)
    y = df['segmentation']
    
    return X, y

def preprocessingELM(df: DataFrame):
    
    df = df.drop(['id'], axis=1)
    
    # Pisahkan fitur dan target
    X = df.drop(columns=["segmentation"])  
    y = df["segmentation"]

    # Identifikasi kolom numerik dan kategorikal
    numerical_features = X.select_dtypes(include=["int64", "float64"]).columns
    categorical_features = X.select_dtypes(include=["object"]).columns

    # Preprocessing untuk kolom numerik dan kategorikal
    numerical_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown="ignore")

    # Gabungkan preprocessing dalam satu pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numerical_transformer, numerical_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )
    
    # Encode target label (y) menjadi numerik
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    # hilangkan data baru pada y yang sudah i encode
    y_encoded = y_encoded[:-1]
    
    X = preprocessor.fit_transform(X)
    
    # sebelumnya data barunya ikut di transform agar data baru bisa dilakukan prediksi
    data_baru_encode = X[-1].reshape(1, -1)
    # hilangkan data baru pada matrix X
    X = X[:-1]
    
    return X, y_encoded, data_baru_encode
