import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder         
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from hpelm import ELM
from sklearn.metrics import classification_report
from .preprocessing import preprocessingELM
from ..controller import saveDataToCsv

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

def extremelearningmachine(age, profession, family_size, graduated, ever_married, gender, spending_Score):

    saveDataToCsv()

    # df = pd.read_csv("./customersegment/cobacustomer_segment.csv", sep=",")
    df = pd.read_csv('./dataset/customers_data.csv')
    
    X, y_encoded, preprocessor = preprocessingELM(df=df)

    # Split 70% training, 30% validasi + testing
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y_encoded, test_size=0.3, random_state=42, stratify=y_encoded
    )

    # Split 20% validasi, 10% testing dari sisa 30%
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.3333, random_state=42, stratify=y_temp
    )

    # Terapkan preprocessing pada fitur
    X_train = preprocessor.fit_transform(X_train)
    X_val = preprocessor.transform(X_val)
    X_test = preprocessor.transform(X_test)

    # One-hot encoding untuk target
    onehot_encoder = OneHotEncoder(sparse_output=False)
    y_train_oh = onehot_encoder.fit_transform(y_train.reshape(-1, 1))
    # y_val_oh = onehot_encoder.transform(y_val.reshape(-1, 1))
    # y_test_oh = onehot_encoder.transform(y_test.reshape(-1, 1))

    # Train ELM dengan data training
    elm = ELM(X_train.shape[1], y_train_oh.shape[1], classification="c", accelerator="basic")
    elm.add_neurons(50, "sigm")  # 50 neuron dengan fungsi aktivasi sigmoid
    elm.train(X_train, y_train_oh, "c")

    # Validasi dengan data validasi
    y_val_pred = elm.predict(X_val)
    y_val_pred_labels = y_val_pred.argmax(axis=1)  # Konversi probabilitas menjadi label kelas

    
    
    # Evaluasi validasi
    # print("Classification Report (Validation):\n", classification_report(y_val, y_val_pred_labels))

    # Testing dengan data testing
    y_test_pred = elm.predict(X_test)
    y_test_pred_labels = y_test_pred.argmax(axis=1)  # Konversi probabilitas menjadi label kelas

    # Evaluasi testing
    # print("Classification Report (Test):\n", classification_report(y_test, y_test_pred_labels))
    # Ubah key dari angka jadi huruf kaya di data aslinya pada reportValidasi dan reportTest

    # buat laporan akurasi untuk dikirim lewat json
    reportValidasi = classification_report(y_val, y_val_pred_labels, output_dict=True)
    reportTest = classification_report(y_test, y_test_pred_labels, output_dict=True)

    reportValidasi = ubah_key_laporan(reportValidasi)
    reportTest = ubah_key_laporan(reportTest)
    
    data_baru = pd.DataFrame({
        'age': [age],
        'profession': [profession],
        'family_size': [family_size],
        'gender': [gender],
        'graduated': [graduated],
        'ever_married': [ever_married],
        'spending_score': [spending_Score],
    })
    
    print(X_test)
    
    # lanjut disini untuk data barunya
    prediksi = 'A'

    # Cetak bobot dan bias acak
    # print("Bobot acak (input ke hidden):", elm.nnet.get_W())  # Bobot antara input dan hidden
    # print("Bias acak (hidden layer):", elm.nnet.get_B())     # Bias pada hidden layer
    return {
        "data" : data_baru.to_dict(orient='records'),
        "segmentasi" : prediksi,
        "validasi" : reportValidasi,
        "test" : reportTest
    }