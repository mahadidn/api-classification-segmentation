import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import GridSearchCV

from ..controller import getAllCustomers
from .preprocessing import preprocessing

# Mapping untuk mengganti key
key_mapping = {
    '0': 'A',
    '1': 'B',
    '2': 'C',
    '3': 'D'
}

def saveData():
    # Ambil data pelanggan dari fungsi getAllCustomers
    data_customers = getAllCustomers()

    # Konversi data ke format list of dictionaries
    data_as_dicts = [customer.dict() for customer in data_customers]

    # Buat DataFrame menggunakan Pandas
    df = pd.DataFrame(data_as_dicts)

    # Simpan ke file CSV
    df.to_csv("./dataset/customers_data.csv", index=False)

    return {"message": "Data saved to customers_data.csv successfully!"}


# Fungsi untuk mengganti key
def ubah_key_laporan(report):
    
    return {
        key_mapping.get(key, key): value for key, value in report.items()
    }

def naivebayes(age, profession, family_size, graduated, ever_married, gender, spending_Score):
    
    saveData()
    
    # get data
    df = pd.read_csv('./dataset/customers_data.csv')
    
    # preprocessing
    df = preprocessing(df=df)
    
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

    # Split data: 70% training, 30% temp (validasi + testing)
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

    # Split temp menjadi 20% validasi dan 10% testing
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.33, random_state=42, stratify=y_temp)

    # untuk hyperparameter tuning
    params = {'var_smoothing' : np.logspace(0, -9, num=100)}
    
    # model
    gnb = GaussianNB()
    
    # gaussian naive bayes di tuning menggunakan grid search
    model = GridSearchCV(estimator=gnb, param_grid=params, cv=10, scoring='accuracy')
    model.fit(X_train, y_train)
    
    # print("Best params: ", model.best_params_)
    # print("Best score: ", model.best_score_)
    
    # Prediksi pada data validasi
    y_val_pred = model.predict(X_val)
    
    akurasiValidasi = accuracy_score(y_val, y_val_pred)
    reportValidasi = classification_report(y_val, y_val_pred, output_dict=True)

    # Evaluasi
    # print("Accuracy pada data validasi:", akurasiValidasi)
    # print("Classification Report (Validasi):\n", reportValidasi)

    # Prediksi pada data testing
    y_test_pred = model.predict(X_test)

    akurasiTest = accuracy_score(y_test, y_test_pred)
    reportTest = classification_report(y_test, y_test_pred, output_dict=True)

    # Evaluasi
    # print("Accuracy pada data testing:", akurasiTest)
    # print("Classification Report (Testing):\n", reportTest)
    
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
    elif(data_baru['profession'][0] == 'Lawyer'):
        data_baru['profession'] = 6
    elif(data_baru['profession'][0] == 'Marketing'):
        data_baru['profession'][0] = 7
    # spending score
    if(data_baru['spending_score'][0] == 'Low'):
        data_baru['spending_score'][0] = 2
    elif(data_baru['spending_score'][0] == 'Average'):
        data_baru['spending_score'][0] = 0
    elif(data_baru['spending_score'][0] == 'High'):
        data_baru['spending_score'][0] = 1
    
    data_baru = data_baru[X_val.columns]

    # print("tabel bawah")
    # print(df)
    # print("tabel atas")
    # print(X_val)
    # print("tabel predik")
    # print(data_baru)

    # Prediksi segmentasi
    prediction = model.predict(data_baru)
    
    prediksi = ''
    
    if(prediction[0] == 0):
        prediksi = 'A'
    elif(prediction[0] == 1):
        prediksi = 'B'
    elif(prediction[0] == 2):
        prediksi = 'C'
    elif(prediction[0] == 3):
        prediksi = 'D'
    
    # print("Predicted Segmentation:", prediksi)
    # print("Report validasi: ")
    # print(reportValidasi)

    data_baru = pd.DataFrame({
        'age': [age],
        'profession': [profession],
        'family_size': [family_size],
        'gender': [gender],
        'graduated': [graduated],
        'ever_married': [ever_married],
        'spending_score': [spending_Score],
    })

    # Ubah key dari angka jadi huruf kaya di data aslinya pada reportValidasi dan reportTest
    reportValidasi = ubah_key_laporan(reportValidasi)
    reportTest = ubah_key_laporan(reportTest)

    return {
        "data" : data_baru.to_dict(orient='records'),
        "segmentasi" : prediksi,
        "akurasi validasi" : akurasiValidasi,
        "validasi" : reportValidasi,
        "akurasi testing" : akurasiTest,
        "test" : reportTest
    }
    