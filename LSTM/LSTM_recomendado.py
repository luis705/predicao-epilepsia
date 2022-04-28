import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import numpy as np
from keras.callbacks import EarlyStopping
from keras.layers import LSTM, Dense
from keras.models import Sequential
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm


def resultado():
    # Teste do modelo
    rotsPreditos = model.predict(x_teste, batch_size=1)
    contaAcertos = 0
    verdadeirosPositivos = 0
    verdadeirosNegativos = 0
    falsosPositivos = 0
    falsosNegativos = 0

    # Printa resultado
    for ind in range(y_teste.shape[0]):
        if y_teste[ind] > 0.5 and rotsPreditos[ind, 0] > 0.5:
            contaAcertos += 1
            verdadeirosPositivos += 1
        elif y_teste[ind] <= 0.5 and rotsPreditos[ind, 0] <= 0.5:
            contaAcertos += 1
            verdadeirosNegativos += 1
        elif y_teste[ind] <= 0.5 and rotsPreditos[ind, 0] > 0.5:
            falsosPositivos += 1
        elif y_teste[ind] > 0.5 and rotsPreditos[ind, 0] <= 0.5:
            falsosNegativos += 1
    print(f"TP: {verdadeirosPositivos}")
    print(f"FP: {falsosPositivos}")
    print(f"TN: {verdadeirosNegativos}")
    print(f"FN: {falsosNegativos}")
    print(f"\nacurácia: {contaAcertos / y_teste.shape[0] * 100 :.2f}%")
    print(
        f"sensibilidade: {verdadeirosPositivos / ( verdadeirosPositivos + falsosNegativos ) * 100 :.2f}%"
    )
    print(
        f"especificidade: {verdadeirosNegativos / ( verdadeirosNegativos + falsosPositivos ) * 100 :.2f}%"
    )


seq_dir = os.path.join("..", "sequencias", "CHB01", "Correlacao")
x_treino = []
y_treino = []
x_teste = []
y_teste = []

for file in tqdm(os.listdir(seq_dir)):
    seq = np.loadtxt(os.path.join(seq_dir, file))
    if np.isnan(seq).any():
        continue
    rotulo = 0
    if "Preictal" in file:
        rotulo = 1
    if "Treino" in file:
        x_treino.append(seq)
        y_treino.append(rotulo)
    else:
        x_teste.append(seq)
        y_teste.append(rotulo)

x_treino = np.array(x_treino)
x_teste = np.array(x_teste)
y_treino = np.array(y_treino)
y_teste = np.array(y_teste)

formato = x_treino.shape
scaler = MinMaxScaler(feature_range=(-1, 1))
tmp = x_treino.reshape(-1, 1)
scaler.fit(tmp)
x_treino = scaler.transform(tmp).reshape(formato)
x_teste = scaler.transform(x_teste.reshape(-1, 1)).reshape(x_teste.shape)

print(x_treino.shape)
print(y_treino.shape)
print(x_teste.shape)
print(y_teste.shape)
# Cria e treina o modelo
model = Sequential()
model.add(
    LSTM(
        128,
        return_sequences=True,
        batch_input_shape=(1, x_treino.shape[1], x_treino.shape[2]),
    )
)
model.add(LSTM(128, stateful=False))
model.add(Dense(1))
model.compile(loss="mean_squared_error", optimizer="adam", metrics="accuracy")
epocas = 1000
early_stopping = EarlyStopping(
    monitor="val_loss",
    patience=10,
    baseline=0.8,
    restore_best_weights=True,
)
resultado()
print(y_treino)
print(y_teste)
model.fit(
    x_treino,
    y_treino,
    epochs=epocas,
    batch_size=1,
    shuffle=True,
    validation_split=0.2,
    callbacks=[early_stopping],
)
resultado()
