import getopt
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from keras.layers import LSTM, Dense
from keras.losses import BinaryFocalCrossentropy, BinaryCrossentropy
from keras.models import Sequential
from keras.optimizers import Adam
from keras.utils import set_random_seed
from sklearn.metrics import auc, roc_curve
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.utils import shuffle
from tqdm import tqdm
from tensorflow import keras


def cria_dataset(caminho):
    x_treino = []
    x_teste = []
    y_treino = []
    y_teste = []

    for arquivo in tqdm(os.listdir(caminho)):
        seq = pd.read_parquet(caminho / arquivo)

        rotulo = [1, 0]
        if 'preictal' in arquivo:
            rotulo = [0, 1]
        if 'treino' in arquivo:
            x_treino.append(seq)
            y_treino.append(rotulo)
        else:
            x_teste.append(seq)
            y_teste.append(rotulo)

    return list(
        map(
            lambda lista: np.array(lista),
            [x_treino, x_teste, y_treino, y_teste],
        )
    )


def normaliza(x_treino, x_teste):
    normalizador = MinMaxScaler(feature_range=(-1, 1))
    normalizador.fit(x_treino.reshape(-1, 1))
    x_treino = normalizador.transform(x_treino.reshape(-1, 1)).reshape(
        x_treino.shape
    )
    x_teste = normalizador.transform(x_teste.reshape(-1, 1)).reshape(
        x_teste.shape
    )
    return x_treino, x_teste


def metricas(y_teste, y_pred):
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    preditos = y_pred.argmax(axis=1)
    reais = y_teste.argmax(axis=1)
    for predito, teste in zip(preditos, reais):
        if predito == 1 and teste == 1:
            tp += 1
        elif predito == 1 and teste == 0:
            fp += 1
        elif predito == 0 and teste == 0:
            tn += 1
        elif predito == 0 and teste == 1:
            fn += 1
    return tp, fp, tn, fn


def resultado(caminho, modelo, x_teste, y_teste):
    preditos = modelo.predict(x_teste)

    tp, fp, tn, fn = metricas(y_teste, preditos)
    with open(caminho, mode='w', encoding='utf-8') as arquivo:
        arquivo.write(f'TP: {tp}\n')
        arquivo.write(f'FP: {fp}\n')
        arquivo.write(f'TN: {tn}\n')
        arquivo.write(f'FN: {fn}\n')

    novo_caminho = caminho.parents[0] / Path(caminho.stem + ' valores.txt')
    with open(novo_caminho, mode='w', encoding='utf-8') as f:
        f.writelines(
            [
                f'Predição: {predito}, Correto: {esperado}\n'
                for predito, esperado in zip(preditos, y_teste)
            ]
        )


def graficos(modelo, historico, seq_dir, tsiouris):
    fig, axs = plt.subplots(2, 1, figsize=(8, 6))
    axs[0].plot(historico.history['val_accuracy'], label='Validação')
    axs[0].plot(historico.history['accuracy'], label='Treino')
    axs[0].set_title('Acurácia')
    axs[0].legend()

    axs[1].plot(historico.history['val_loss'], label='Validação')
    axs[1].plot(historico.history['loss'], label='Treino')
    axs[1].set_title('Erro')
    axs[1].legend()

    pasta_graficos = Path(
        '..',
        'Gráficos',
        seq_dir.parents[1].stem,
        seq_dir.stem,
    )

    if tsiouris:
        plt.savefig(
            pasta_graficos
            / f'Tsiouris - {int(seq_dir.parents[0].stem)} janelas por sequência - Acurária e erro'
        )
    else:
        plt.savefig(
            pasta_graficos
            / f'Recomendado - {int(seq_dir.parents[0].stem)} janelas por sequência - Acurária e erro'
        )

    rotulos_preditos = modelo.predict(x_teste, batch_size=1).argmax(axis=1)
    fpr, tpr, threshold = roc_curve(y_teste.argmax(axis=1), rotulos_preditos)
    roc_auc = auc(fpr, tpr)

    plt.figure()
    plt.title('Curva ROC')
    plt.plot(fpr, tpr, 'b', label='AUC = %0.2f' % roc_auc)
    plt.legend(loc='lower right')
    plt.plot([0, 1], [0, 1], 'r--')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.ylabel('True Positive Rate')
    plt.xlabel('False Positive Rate')
    if tsiouris:
        plt.savefig(
            pasta_graficos
            / f'Tsiouris - {int(seq_dir.parents[0].stem)} janelas por sequência - Curva ROC.png'
        )
    else:
        plt.savefig(
            pasta_graficos
            / f'Recomendado - {int(seq_dir.parents[0].stem)} janelas por sequência - Curva ROC.png'
        )

    positivos = historico.history['tp'][0] + historico.history['fn'][0]
    fig, axs = plt.subplots(2, 1, figsize=(12, 8))
    plt.title('Evolução de acertos por época')
    axs[0].plot(np.array(historico.history['tp']) / positivos, label='Verdadeiros positivos')
    axs[0].plot(np.array(historico.history['fn']) / positivos, label='Falsos negativos')
    axs[0].set_title(r'$\dfrac{TP}{TP + FN}$ e $\dfrac{FN}{TP + FN}$')
    axs[0].set_ylim(0, 1)
    axs[0].legend()

    negativos = historico.history['fp'][0] + historico.history['tn'][0]
    axs[1].plot(np.array(historico.history['tn']) / negativos, label='Verdadeiros negativos')
    axs[1].plot(np.array(historico.history['fp']) / negativos, label='Falsos positivos')
    axs[1].set_title(r'$\dfrac{TN}{TN + FP}$ e $\dfrac{FP}{TN + FP}$')
    axs[1].set_ylim(0, 1)
    axs[1].legend()

    if tsiouris:
        plt.savefig(
            pasta_graficos
            / f'Tsiouris - {int(seq_dir.parents[0].stem)} janelas por sequência - Acertos.png'
        )
    else:
        plt.savefig(
            pasta_graficos
            / f'Recomendado - {int(seq_dir.parents[0].stem)} janelas por sequência - Acertos.png'
        )

    positivos = historico.history['val_tp'][0] + historico.history['val_fn'][0]
    fig, axs = plt.subplots(2, 1, figsize=(12, 8))
    plt.title('Evolução de acertos por época')
    axs[0].plot(np.array(historico.history['val_tp']) / positivos, label='Verdadeiros positivos')
    axs[0].plot(np.array(historico.history['val_fn']) / positivos, label='Falsos negativos')
    axs[0].set_title(r'$\dfrac{TP}{TP + FN}$ e $\dfrac{FN}{TP + FN}$')
    axs[0].set_ylim(0, 1)
    axs[0].legend()

    negativos = historico.history['val_fp'][0] + historico.history['val_tn'][0]
    axs[1].plot(np.array(historico.history['val_tn']) / negativos, label='Verdadeiros negativos')
    axs[1].plot(np.array(historico.history['val_fp']) / negativos, label='Falsos positivos')
    axs[1].set_title(r'$\dfrac{TN}{TN + FP}$ e $\dfrac{FP}{TN + FP}$')
    axs[1].set_ylim(0, 1)
    axs[1].legend()

    if tsiouris:
        plt.savefig(
            pasta_graficos
            / f'Tsiouris - {int(seq_dir.parents[0].stem)} janelas por sequência - Acertos validação.png'
        )
    else:
        plt.savefig(
            pasta_graficos
            / f'Recomendado - {int(seq_dir.parents[0].stem)} janelas por sequência - Acertos validação.png'
        )


def gera_modelo():
    modelo = Sequential()
    modelo.add(
        LSTM(
            8, input_shape=(vet_por_seq, n_parametros), return_sequences=False
        )
    )
    modelo.add(Dense(8, activation='relu'))
    modelo.add(Dense(2, activation='softmax'))

    optim = Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, decay=0)
    observado = [
        keras.metrics.BinaryAccuracy(name='accuracy'),
        keras.metrics.TruePositives(name='tp'),
        keras.metrics.FalsePositives(name='fp'),
        keras.metrics.TrueNegatives(name='tn'),
        keras.metrics.FalseNegatives(name='fn'),
        # keras.metrics.Precision(name='precision'),
        # keras.metrics.Recall(name='recall'),
        # keras.metrics.AUC(name='auc'),
        # keras.metrics.AUC(name='prc', curve='PR'),  # precision-recall curve
        # keras.metrics.F1Score(name='f1')
    ]

    modelo.compile(
        loss=BinaryFocalCrossentropy(from_logits=False),
        optimizer=optim,
        metrics=observado
    )
    return modelo


if __name__ == '__main__':
    seed = 123456
    set_random_seed(seed)
    optlist, args = getopt.gnu_getopt(sys.argv[1:], 'e:t')
    tsiouris = False
    for (opcao, argumento) in optlist:
        if opcao == '-e':
            seq_dir = Path(argumento)
        if opcao == '-t':
            tsiouris = True

    x_treino, x_teste, y_treino, y_teste = cria_dataset(seq_dir)
    if tsiouris:
        x = np.append(x_treino, x_teste, axis=0)
        y = np.append(y_treino, y_teste, axis=0)
        x_treino, x_teste, y_treino, y_teste = train_test_split(
            x, y, test_size=0.2, random_state=seed
        )
    else:
        x_treino, y_treino = shuffle(x_treino, y_treino, random_state=seed)
    x_treino, x_teste = normaliza(x_treino, x_teste)
    n_sequencias, vet_por_seq, n_parametros = x_treino.shape

    modelo = gera_modelo()

    # Calcula os pesos das classes
    pre = int((y_treino == [0, 1]).sum() / 2)
    inter = int((y_treino == [1, 0]).astype(int).sum() / 2)
    peso_inter = pre / y_treino.shape[0]
    peso_pre = inter / y_treino.shape[0]
    dict_pesos = {0: peso_inter, 1: peso_pre}
    history = modelo.fit(
        x_treino,
        y_treino,
        epochs=25,
        batch_size=10,
        shuffle=True,
        # validation_split=0.1,
        validation_data=(x_teste, y_teste),
        class_weight=dict_pesos
    )
    if tsiouris:
        caminho_resultados = Path(
            '..',
            'Resultados',
            seq_dir.parents[1].stem,
            seq_dir.stem,
            f'Tsiouris - {int(seq_dir.parents[0].stem)} janelas por sequência.txt',
        )

    else:
        caminho_resultados = Path(
            '..',
            'Resultados',
            seq_dir.parents[1].stem,
            seq_dir.stem,
            f'Recomendado - {int(seq_dir.parents[0].stem)} janelas por sequência.txt',
        )

    resultado(caminho_resultados, modelo, x_teste, y_teste)

    graficos(modelo, history, seq_dir, tsiouris)
