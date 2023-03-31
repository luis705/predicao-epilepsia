import getopt
import os
import sys

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from keras.callbacks import EarlyStopping
from keras.layers import LSTM, Dense
from keras.models import Sequential
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.utils import class_weight
from tqdm import tqdm

matplotlib.use('Agg')

class CustomStopper(EarlyStopping):
    def __init__(
        self,
        monitor="val_loss",
        min_delta=0,
        patience=0,
        verbose=0,
        mode="auto",
        start_epoch=100,
        baseline=0.8,
        restore_best_weights=True,
    ):  # add argument for starting epoch
        super(CustomStopper, self).__init__()
        self.start_epoch = start_epoch

    def on_epoch_end(self, epoch, logs=None):
        if epoch > self.start_epoch:
            super().on_epoch_end(epoch, logs)


def resultado(caminho):
    # Teste do modelo
    rotsPreditos = model.predict(x_teste, batch_size=1)[:, -1, 0]
    contaAcertos = 0
    verdadeirosPositivos = 0
    verdadeirosNegativos = 0
    falsosPositivos = 0
    falsosNegativos = 0

    # Printa resultado
    (
        verdadeirosPositivos,
        verdadeirosNegativos,
        falsosPositivos,
        falsosNegativos,
    ) = metricas(y_teste, rotsPreditos, 0.5)

    with open(caminho, mode="w") as f:
        f.write(f"TP: {verdadeirosPositivos}\n")
        f.write(f"FP: {falsosPositivos}\n")
        f.write(f"TN: {verdadeirosNegativos}\n")
        f.write(f"FN: {falsosNegativos}\n")

    novo_caminho = caminho[:-4] + " valores.txt"
    with open(novo_caminho, mode="w") as f:
        f.writelines(
            [
                f"Predição: {predito}, Correto: {esperado}\n"
                for predito, esperado in zip(rotsPreditos, y_teste)
            ]
        )


def metricas(y_teste, y_pred, thresh):
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    for pred, teste in zip(y_pred, y_teste):
        if pred >= thresh and teste == 1:
            tp += 1
        elif pred >= thresh and teste == 0:
            fp += 1
        elif pred < thresh and teste == 1:
            fn += 1
        elif pred < thresh and teste == 0:
            tn += 1
    return tp, tn, fp, fn


optlist, args = getopt.gnu_getopt(sys.argv[1:], "e:")
for (opcao, argumento) in optlist:
    if opcao == "-e":
        seq_dir = argumento


x = []
y = []
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

# Cria e treina o modelo
model = Sequential()
model.add(
    LSTM(
        32,
        return_sequences=True,
        batch_input_shape=(1, x.shape[1], x.shape[2]),
        activation="tanh",
    )
)
model.add(Dense(1, activation="sigmoid"))
model.compile(loss="mean_squared_error", optimizer="adam", metrics="accuracy")
epocas = 100
early_stopping = CustomStopper(
    monitor="val_loss",
    patience=10,
    baseline=0.8,
    restore_best_weights=True,
    start_epoch=30,
)
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

pastas = seq_dir.split("/")
pasta_resultado = os.path.join(
    "..",
    "Resultados",
    pastas[3],  # antigo ou novo
    pastas[2],  # paciente
    pastas[5],  # tipo de vetor
)

if not os.path.exists(pasta_resultado):
    os.makedirs(pasta_resultado)
resultado(
    os.path.join(
        pasta_resultado, f"Tsiouris - {int(pastas[4])} janelas por sequência.txt"
    )
)

print('Iniciando gráfico')
f, axs = plt.subplots(2, 1, figsize=(8, 6))
axs[0].plot(history.history["val_accuracy"], label="Validação")
axs[0].plot(history.history["accuracy"], label="Treino")
axs[0].set_title("Acurácia")
axs[0].legend()

print('Fim do primeiro plot')
axs[1].plot(history.history["val_loss"], label="Validação")
axs[1].plot(history.history["loss"], label="Treino")
axs[1].set_title("Erro")
axs[1].legend()
print('Fim do segundo plot')

pasta_graficos = os.path.join(
    "..",
    "Gráficos",
    pastas[3],  # antigo ou novo
    pastas[2],  # paciente
    pastas[5],  # tipo de vetor
)

if not os.path.exists(pasta_graficos):
    os.makedirs(pasta_graficos)
print('Salvando gráfico')
plt.savefig(
    os.path.join(
        pasta_graficos, f"Tsiouris - {int(pastas[4])} janelas por sequência.png"
    )
)
"""
rotsPreditos = model.predict(x_teste, batch_size=1)[:, -1, 0]

plt.figure()
tpr = []
fpr = []
for thresh in [i * .05 for i in range(20)] :
    tp, tn, fp, fn = metricas(y_teste, rotsPreditos, thresh)
    tpr.append(tp / (tp + fn))
    fpr.append(1 - (tn / (tn + fp)))
print(tpr, fpr)
plt.plot(fpr, tpr, label=f"AUC={metrics.auc(tpr, fpr)}")
plt.legend()
plt.savefig(
    os.path.join(
        pasta_graficos,
        f"Tsiouris - {int(pastas[4])} janelas por sequência - Curva ROC.png",
    )
)


metrics.RocCurveDisplay.from_predictions(y_true=y_teste, y_pred=rotsPreditos, name='Curva ROC')
plt.savefig(
    os.path.join(
        pasta_graficos,
        f"Tsiouris - {int(pastas[4])} janelas por sequência - Curva ROC.png",
    )
)


fpr, tpr, threshold = metrics.roc_curve(y_teste, rotsPreditos)
roc_auc = metrics.auc(fpr, tpr)
print(threshold)

plt.plot(fpr, tpr, 'b', label = 'AUC = %0.2f' % roc_auc)
plt.legend(loc = 'lower right')
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0, 1])
plt.ylim([0, 1])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.savefig(
    os.path.join(
        pasta_graficos,
        f"Tsiouris - {int(pastas[4])} janelas por sequência - Curva ROC.png",
    )
)
"""
