# Processamento Digital de Imagens

Aplicativo desktop em Python com interface Tkinter para aplicar filtros e transformações em imagens e na webcam. Inclui escala de cinza, negativo, limiarização Otsu, filtros de média e mediana, detecção de bordas, operações morfológicas, histograma e detecção de objetos. Também permite rastrear objetos vermelhos pela câmera e reproduzir áudio.

## Windows

Instale o Python 3.12 ou superior com suporte ao Tcl/Tk. No PowerShell, dentro da pasta do projeto, execute:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

## Linux

Use Python 3.12 ou superior, com suporte a ambientes virtuais e Tkinter. No Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-tk
```

No Fedora:

```bash
sudo dnf install python3 python3-pip python3-tkinter
```

Em outras distribuições, instale os pacotes equivalentes. O Tkinter é instalado pelo sistema, não pelo `pip`. Depois, dentro da pasta do projeto:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

## Como usar

Clique em **Abrir Imagem** e escolha uma operação no painel lateral. Para os recursos de vídeo e rastreamento, conecte uma webcam e inicie a câmera pela interface. O áudio utiliza o arquivo `sons/musica.mp3`; o `pygame` é opcional se você não usar esse recurso.

## Tracking YOLO + Música

1. Clique em **Câmera** e depois em **Tracking YOLO + Música**.
2. O YOLO11n pré-treinado (`yolo11n.pt`) detecta objetos, e o ByteTrack pronto
   associa os frames usando `persist=True`. As caixas mostram a classe e o ID.
3. Uma **pessoa** (`person`) presente faz tocar `sons/musica.mp3`.
   Sem pessoa trackeada no frame, a música para.
4. Mova-se na câmera para demonstrar que o ID acompanha o objeto.
   O ID não identifica uma pessoa: pode mudar após perda do objeto ou nova sessão.
5. Use **Parar Câmera** para liberar a câmera e interromper a música.

O modelo só é carregado ao ativar o tracking. Na primeira utilização, o Ultralytics
pode baixar o arquivo automaticamente; prepare esse download com internet antes
da apresentação. Não há treinamento nem dataset adicional. A inferência é
síncrona, com `imgsz=320` para reduzir o processamento.

## Menu Extras

- **Detecção por Cor**: abre o modo antigo de detecção vermelha na câmera,
  preservando seu comportamento e música. É um extra, sem IDs de tracking.
- **Rotacionar 90°**: gira a imagem original no sentido horário com NumPy.
- **Espelhar Horizontalmente**: espelha a imagem original com slicing NumPy.
- **Ajustar Brilho**: aplica de -100 a +100 à imagem original, sem overflow.
- **Salvar Resultado**: salva o resultado exibido (imagem ou frame) em PNG/JPG.
- **Configurar Canny**: muda os dois limiares usados no Canny manual de imagem
  e no Canny de vídeo. Exige `0 <= baixo < alto <= 255`; padrão: 100 e 200.
- **Confiança YOLO**: muda a confiança de 0.1 a 0.9; padrão: 0.40.
  Durante o tracking, o valor novo é usado no próximo frame.

As operações de imagem mostram o resultado no painel existente. Após configurar
o Canny, clique em **Canny** para aplicar os novos valores à imagem; no vídeo,
eles já são usados no próximo frame.
