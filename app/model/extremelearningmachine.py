import pandas as pd
from sklearn.preprocessing import OneHotEncoder    
import pandas as pd
from sklearn.model_selection import train_test_split
from hpelm import ELM
from sklearn.metrics import classification_report, accuracy_score
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


    data_baru = pd.DataFrame({
        'age': [int(age)],
        'profession': [profession],
        'family_size': [int(family_size)],
        'gender': [gender],
        'graduated': [graduated],
        'ever_married': [ever_married],
        'spending_score': [spending_Score],
    })
    
    df = pd.concat([df, data_baru], ignore_index=True)
    
    X, y_encoded, data_baru_encode = preprocessingELM(df=df)

    # Split 70% training, 30% validasi + testing
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y_encoded, test_size=0.3, random_state=42, stratify=y_encoded
    )

    # Split 20% validasi, 10% testing dari sisa 30%
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.3333, random_state=42, stratify=y_temp
    )

    # One-hot encoding untuk target
    onehot_encoder = OneHotEncoder(sparse_output=False)
    y_train_oh = onehot_encoder.fit_transform(y_train.reshape(-1, 1))

    bestValScore = 0
    usedNeuron = 0
    bestFunction = ""
    
    fungsiAktivasi = {
        "fungsi" : ["sigm", "tanh", "rbf_l2"]
    }
    
    for neurons in range(10, 100):
        
        for aktivasi in fungsiAktivasi['fungsi']:
            
            # Train ELM dengan data training
            elm = ELM(X_train.shape[1], y_train_oh.shape[1], classification="c", accelerator="basic")
            elm.add_neurons(neurons, aktivasi)  
            elm.train(X_train, y_train_oh, "c")

            # Validasi dengan data validasi
            y_val_pred = elm.predict(X_val)
            y_val_pred_labels = y_val_pred.argmax(axis=1)  
            valScore = accuracy_score(y_val, y_val_pred_labels)
            
            if valScore > bestValScore:
                bestValScore = valScore
                bestModel = elm
                usedNeuron = neurons
                bestFunction = aktivasi
    
    
    # Testing dengan data testing
    y_test_pred = bestModel.predict(X_test)
    y_test_pred_labels = y_test_pred.argmax(axis=1)  

    # Evaluasi testing
    # print("Classification Report (Test):\n", classification_report(y_test, y_test_pred_labels))
    
    # buat laporan akurasi untuk dikirim lewat json
    reportTest = classification_report(y_test, y_test_pred_labels, output_dict=True)

    reportTest = ubah_key_laporan(reportTest)
    
    y_baru = bestModel.predict(data_baru_encode)
    y_baru_label = y_baru.argmax(axis=1)
    prediksi = ''
    
    if(y_baru_label[0] == 0):
        prediksi = 'A'
    elif(y_baru_label[0] == 1):
        prediksi = 'B'
    elif(y_baru_label[0] == 2):
        prediksi = 'C'
    elif(y_baru_label[0] == 3):
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
    
    # Cetak bobot dan bias acak
    # print("Bobot acak (input ke hidden):", elm.nnet.get_W())  # Bobot antara input dan hidden
    # print("Bias acak (hidden layer):", elm.nnet.get_B())     # Bias pada hidden layer
    return {
        "data" : data_baru.to_dict(orient='records'),
        "segmentasi" : prediksi,
        "test" : reportTest,
        "jumlahNeuron" : usedNeuron,
        "fungsiAktivasi" : bestFunction,
    }