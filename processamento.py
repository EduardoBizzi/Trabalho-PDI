import numpy as np
import math


def obter_cinza(imagem):
    if len(imagem.shape) == 2:
        return imagem.copy()

    if imagem.shape[2] == 1:
        return imagem[:, :, 0].copy()

    b = imagem[:, :, 0].astype(float)
    g = imagem[:, :, 1].astype(float)
    r = imagem[:, :, 2].astype(float)
    return np.clip(
        np.rint(0.299 * r + 0.587 * g + 0.114 * b),
        0,
        255
    ).astype(np.uint8)


def otsu_manual(imagem):
    hist = np.bincount(
        imagem.ravel(),
        minlength=256
    )

    total = imagem.size
    valores = np.arange(256)

    soma_total = np.sum(
        valores * hist
    )

    peso_fundo = np.cumsum(hist)
    soma_fundo = np.cumsum(
        valores * hist
    )

    peso_objeto = total - peso_fundo

    media_fundo = np.divide(
        soma_fundo,
        peso_fundo,
        out=np.zeros(256, float),
        where=peso_fundo != 0
    )

    media_objeto = np.divide(
        soma_total - soma_fundo,
        peso_objeto,
        out=np.zeros(256, float),
        where=peso_objeto != 0
    )

    variancia = (
        peso_fundo *
        peso_objeto *
        (media_fundo - media_objeto) ** 2
    )

    variancia[
        (peso_fundo == 0) |
        (peso_objeto == 0)
    ] = 0

    limiar = int(
        np.argmax(variancia)
    )

    binaria = np.zeros_like(imagem)
    binaria[imagem > limiar] = 255

    return binaria


def janelas_3x3(imagem):
    return np.lib.stride_tricks.sliding_window_view(
        imagem,
        (3, 3)
    )


def aplicar_media(imagem):
    janelas = janelas_3x3(imagem)
    resultado = imagem.copy()
    resultado[1:-1, 1:-1] = np.mean(
        janelas,
        axis=(2, 3)
    ).astype(np.uint8)
    return resultado


def aplicar_mediana(imagem):
    janelas = janelas_3x3(imagem)
    resultado = imagem.copy()
    resultado[1:-1, 1:-1] = np.median(
        janelas,
        axis=(2, 3)
    ).astype(np.uint8)
    return resultado


def canny_manual(imagem, limiar_baixo=100, limiar_alto=200):
    # Suavização gaussiana 3x3, com repetição dos pixels da borda.
    kernel = np.array([
        [1, 2, 1],
        [2, 4, 2],
        [1, 2, 1]
    ], dtype=float) / 16
    janelas = janelas_3x3(
        np.pad(imagem.astype(float), 1, mode="edge")
    )
    suavizada = np.sum(janelas * kernel, axis=(2, 3))

    # Gradientes de Sobel, magnitude e direção em graus.
    sobel_x = np.array([
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
    ])
    janelas = janelas_3x3(
        np.pad(suavizada, 1, mode="edge")
    )
    gx = np.sum(janelas * sobel_x, axis=(2, 3))
    gy = np.sum(janelas * sobel_x.T, axis=(2, 3))
    magnitude = np.hypot(gx, gy)
    direcao = np.degrees(np.arctan2(gy, gx)) % 180

    # Supressão de não máximos nas quatro direções do gradiente.
    suprimida = np.zeros_like(magnitude)
    centro = magnitude[1:-1, 1:-1]
    angulo = direcao[1:-1, 1:-1]
    vizinhos = [
        (((angulo < 22.5) | (angulo >= 157.5)),
         magnitude[1:-1, :-2], magnitude[1:-1, 2:]),
        (((angulo >= 22.5) & (angulo < 67.5)),
         magnitude[:-2, :-2], magnitude[2:, 2:]),
        (((angulo >= 67.5) & (angulo < 112.5)),
         magnitude[:-2, 1:-1], magnitude[2:, 1:-1]),
        (((angulo >= 112.5) & (angulo < 157.5)),
         magnitude[:-2, 2:], magnitude[2:, :-2])
    ]
    for mascara, anterior, seguinte in vizinhos:
        manter = mascara & (centro >= anterior) & (centro >= seguinte)
        suprimida[1:-1, 1:-1][manter] = centro[manter]

    # Limiarização dupla e histerese por conexão de oito vizinhos.
    fortes = (suprimida > 0) & (suprimida >= limiar_alto)
    fracas = (suprimida > 0) & (suprimida >= limiar_baixo) & ~fortes
    resultado = np.zeros(imagem.shape, dtype=np.uint8)
    resultado[fortes] = 255
    pilha = list(zip(*np.nonzero(fortes)))
    altura, largura = imagem.shape
    while pilha:
        y, x = pilha.pop()
        for ny in range(max(0, y - 1), min(altura, y + 2)):
            for nx in range(max(0, x - 1), min(largura, x + 2)):
                if fracas[ny, nx]:
                    fracas[ny, nx] = False
                    resultado[ny, nx] = 255
                    pilha.append((ny, nx))
    return resultado


def aplicar_erosao(imagem):
    janelas = janelas_3x3(imagem)
    resultado = imagem.copy()
    resultado[1:-1, 1:-1] = np.min(
        janelas,
        axis=(2, 3)
    )
    return resultado


def aplicar_dilatacao(imagem):
    janelas = janelas_3x3(imagem)
    resultado = imagem.copy()
    resultado[1:-1, 1:-1] = np.max(
        janelas,
        axis=(2, 3)
    )
    return resultado


def calcular_histograma(imagem):
    return np.bincount(
        imagem.ravel(),
        minlength=256
    )


def detectar_componentes(imagem):
    binaria = otsu_manual(imagem)

    altura, largura = binaria.shape

    visitado = np.zeros(
        (altura, largura),
        dtype=bool
    )

    componentes = []

    for y in range(altura):
        for x in range(largura):

            if (
                binaria[y, x] != 255
                or visitado[y, x]
            ):
                continue

            fila = [(y, x)]
            indice = 0
            visitado[y, x] = True
            pixels = []

            while indice < len(fila):
                cy, cx = fila[indice]
                indice += 1
                pixels.append((cy, cx))

                vizinhos = [
                    (cy - 1, cx),
                    (cy + 1, cx),
                    (cy, cx - 1),
                    (cy, cx + 1)
                ]

                for ny, nx in vizinhos:
                    if (
                        0 <= ny < altura
                        and 0 <= nx < largura
                        and binaria[ny, nx] == 255
                        and not visitado[ny, nx]
                    ):
                        visitado[ny, nx] = True
                        fila.append((ny, nx))

            if len(pixels) < 10:
                continue

            conjunto = set(pixels)
            perimetro = 0

            for py, px in pixels:
                vizinhos = [
                    (py - 1, px),
                    (py + 1, px),
                    (py, px - 1),
                    (py, px + 1)
                ]

                for vizinho in vizinhos:
                    if vizinho not in conjunto:
                        perimetro += 1

            ys = [p[0] for p in pixels]
            xs = [p[1] for p in pixels]

            diametro = math.sqrt(
                (max(ys) - min(ys)) ** 2 +
                (max(xs) - min(xs)) ** 2
            )

            componentes.append({
                "area": len(pixels),
                "perimetro": perimetro,
                "diametro": diametro,
                "pixels": pixels
            })

    return componentes
