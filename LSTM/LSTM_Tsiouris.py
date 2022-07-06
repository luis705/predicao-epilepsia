import getopt
import os
import sys

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import matplotlib.pyplot as plt
import numpy as np
from keras.callbacks import EarlyStopping
from keras.layers import LSTM, Dense
from keras.models import Sequential
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.utils import class_weight
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


optlist, args = getopt.gnu_getopt(sys.argv[1:], "e:")
for (opcao, argumento) in optlist:
    if opcao == "-e":
        seq_dir = argumento


x = []
y = []
print(seq_dir)
for file in tqdm(os.listdir(seq_dir)):
    seq = np.loadtxt(os.path.join(seq_dir, file))
    if np.isnan(seq).any():
        continue
    rotulo = 0
    if "Preictal" in file:
        rotulo = 1
    x.append(seq)
    y.append(rotulo)

x = np.array(x)
y = np.array(y)

formato = x.shape
scaler = MinMaxScaler(feature_range=(-1, 1))
tmp = x.reshape(-1, 1)
scaler.fit(tmp)
x = scaler.transform(tmp).reshape(formato)

# Randomiza entradas e saídas
x_treino, x_teste, y_treino, y_teste = train_test_split(x, y, test_size=0.2)

pesos = dict(
    enumerate(
        class_weight.compute_class_weight(
            "balanced", classes=np.unique(y_treino), y=y_treino
        )
    )
)
print(pesos)

# Cria e treina o modelo
model = Sequential()
model.add(
    LSTM(
        32,
        return_sequences=True,
        batch_input_shape=(1, x.shape[1], x.shape[2]),
    )
)
model.add(Dense(1))
model.compile(loss="mean_squared_error", optimizer="adam", metrics="accuracy")
epocas = 100
early_stopping = EarlyStopping(
    monitor="val_loss",
    patience=10,
    baseline=0.8,
    restore_best_weights=True,
)
resultado()
history = model.fit(
    x_treino,
    y_treino,
    epochs=epocas,
    batch_size=1,
    shuffle=True,
    validation_split=0.2,
    callbacks=[early_stopping],
    class_weight=pesos,
)
resultado()

f, axs = plt.subplots(2, 1)
axs[0].plot(history.history["val_accuracy"], label="Validação")
axs[0].plot(history.history["accuracy"], label="Treino")
axs[0].set_title("Acurácia")
axs[0].legend()

axs[1].plot(history.history["val_loss"], label="Validação")
axs[1].plot(history.history["loss"], label="Treino")
axs[1].set_title("Erro")
axs[1].legend()

plt.show()
