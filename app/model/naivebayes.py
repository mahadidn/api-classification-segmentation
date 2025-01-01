import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import GridSearchCV

from ..controller import saveDataToCsv
from .preprocessing import preprocessingNB

# Mapping untuk mengganti key
key_mapping = {
    '0': 'A',
    '1': 'B',
    '2': 'C',
    '3': 'D'
}



# Fungsi untuk mengganti key
def ubah_key_laporan(report):
    
    return {
        key_mapping.get(key, key): value for key, value in report.items()
    }

def naivebayes(age, profession, family_size, graduated, ever_married, gender, spending_Score):
    
    saveDataToCsv()
    
    # get data
    df = pd.read_csv('./dataset/customers_data.csv')
    
    # preprocessing
    X, y = preprocessingNB(df=df)
    
    

    # split data: 70% training, 30% temp (validasi + testing)
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

    # split temp jadi 20% validasi dan 10% testing
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.33, random_state=42, stratify=y_temp)

    # model
    gnb = GaussianNB()
    bestScore = 0
    bestParam = None
    
    # validasi lalu cari parameter terbaik
    for v in np.logspace(0, -9, num=100):
        gnb.set_params(var_smoothing=v)
        gnb.fit(X_train, y_train)
        y_val_pred = gnb.predict(X_val)
        score = accuracy_score(y_val, y_val_pred)
        
        if(score > bestScore):
            bestScore = score
            bestParam = v
            
    # pakai gnb dengan parameter terbaik
    gnb.set_params(var_smoothing=bestParam)
    gnb.fit(X_train, y_train)

    # Prediksi pada data testing
    y_test_pred = gnb.predict(X_test)

    # akurasiTest = accuracy_score(y_test, y_test_pred)
    reportTest = classification_report(y_test, y_test_pred, output_dict=True)

    # klasifikasi data
    # Data baru (tanpa segmentasi)
    data_baru = pd.DataFrame({
        'age': [age],
        'profession': [profession],
        'family_size': [family_size],
        'gender': [gender],
        'graduated': [graduated],
        'ever_married': [ever_married],
        'spending_score': [spending_Score],
    })
    

    # encoder
    # gender
    if(data_baru['gender'][0] == 'Male'):
        data_baru['gender'][0] = 1
    else:
        data_baru['gender'][0] = 0
    # ever married
    if(data_baru['ever_married'][0] == 'Yes'):
        data_baru['ever_married'][0] = 1
    else:
        data_baru['ever_married'][0] = 0
    # graduated
    if(data_baru['graduated'][0] == 'Yes'):
        data_baru['graduated'][0] = 1
    else:
        data_baru['graduated'][0] = 0
    # profession
    if(data_baru['profession'][0] == 'Artist'):
        data_baru['profession'][0] = 0
    elif(data_baru['profession'][0] == 'Doctor'):
        data_baru['profession'][0] = 1
    elif(data_baru['profession'][0] == 'Engineer'):
        data_baru['profession'][0] = 2
    elif(data_baru['profession'][0] == 'Entertainment'):
        data_baru['profession'][0] = 3
    elif(data_baru['profession'][0] == 'Executive'):
        data_baru['profession'][0] = 4
    elif(data_baru['profession'][0] == 'Healthcare'):
        data_baru['profession'][0] = 5
    elif(data_baru['profession'][0] == 'Homemaker'):
        data_baru['profession'] = 6
    elif(data_baru['profession'][0] == 'Lawyer'):
        data_baru['profession'] = 7
    elif(data_baru['profession'][0] == 'Marketing'):
        data_baru['profession'][0] = 8
    # spending score
    if(data_baru['spending_score'][0] == 'Low'):
        data_baru['spending_score'][0] = 2
    elif(data_baru['spending_score'][0] == 'Average'):
        data_baru['spending_score'][0] = 0
    elif(data_baru['spending_score'][0] == 'High'):
        data_baru['spending_score'][0] = 1
    
    data_baru = data_baru[X_val.columns]

    # Prediksi segmentasi
    prediction = gnb.predict(data_baru)
    
    prediksi = ''
    
    if(prediction[0] == 0):
        prediksi = 'A'
    elif(prediction[0] == 1):
        prediksi = 'B'
    elif(prediction[0] == 2):
        prediksi = 'C'
    elif(prediction[0] == 3):
        prediksi = 'D'
    

    data_baru = pd.DataFrame({
        'age': [age],
        'profession': [profession],
        'family_size': [family_size],
        'gender': [gender],
        'graduated': [graduated],
        'ever_married': [ever_married],
        'spending_score': [spending_Score],
    })

    # Ubah key dari angka jadi huruf kaya di data aslinya pada reportTest
    reportTest = ubah_key_laporan(reportTest)

    return {
        "data" : data_baru.to_dict(orient='records'),
        "segmentasi" : prediksi,
        "test" : reportTest
    }
    