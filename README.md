# Processamento Digital de Imagens

Aplicativo desktop em Python com interface Tkinter para aplicar filtros e transformações em imagens e na webcam. Inclui escala de cinza, negativo, limiarização Otsu, filtros de média e mediana, detecção de bordas, operações morfológicas, histograma e detecção de objetos. Também permite rastrear objetos vermelhos pela câmera e reproduzir áudio.

## Windows

Instale o Python 3 com suporte ao Tcl/Tk. No PowerShell, dentro da pasta do projeto, execute:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install numpy opencv-python Pillow pygame
.\.venv\Scripts\python.exe main.py
```

## Linux

Instale o Python 3, o suporte a ambientes virtuais e o Tkinter. No Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-tk
```

Em outras distribuições, instale os pacotes equivalentes. Depois, dentro da pasta do projeto:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install numpy opencv-python Pillow pygame
.venv/bin/python main.py
```

## Como usar

Clique em **Abrir Imagem** e escolha uma operação no painel lateral. Para os recursos de vídeo e rastreamento, conecte uma webcam e inicie a câmera pela interface. O áudio utiliza o arquivo `sons/musica.mp3`; o `pygame` é opcional se você não usar esse recurso.
