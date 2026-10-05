import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import processamento
import os

try:
    import pygame
except ImportError:
    pygame = None


class Aplicacao:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("PDI - Processamento Digital de Imagens")
        self.janela.geometry("1250x780")
        self.janela.minsize(1050, 680)
        self.janela.configure(bg="#eef2f7")

        self.imagem_original = None
        self.imagem_resultado = None

        self.camera = None
        self.camera_ativa = False
        self.modo_video = None

        self.musica_tocando = False
        self.musica_carregada = False
        self.aviso_musica = False
        self.caminho_musica = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "sons",
            "musica.mp3"
        )

        self.configurar_estilo()
        self.criar_interface()
        self.atualizar_status()

        self.janela.protocol(
            "WM_DELETE_WINDOW",
            self.fechar_aplicacao
        )

    def configurar_estilo(self):
        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        estilo.configure(
            "Grupo.TLabelframe",
            background="white",
            borderwidth=1
        )

        estilo.configure(
            "Grupo.TLabelframe.Label",
            background="white",
            foreground="#1f2937",
            font=("Segoe UI", 10, "bold")
        )

        estilo.configure(
            "Acao.TButton",
            font=("Segoe UI", 9),
            padding=(7, 7)
        )

        estilo.configure(
            "Destaque.TButton",
            font=("Segoe UI", 9, "bold"),
            padding=(7, 8)
        )

    def criar_interface(self):
        cabecalho = tk.Frame(
            self.janela,
            bg="#1f2937",
            height=88
        )
        cabecalho.pack(fill="x")
        cabecalho.pack_propagate(False)

        tk.Label(
            cabecalho,
            text="Processamento Digital de Imagens",
            bg="#1f2937",
            fg="white",
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w", padx=24, pady=(14, 0))

        tk.Label(
            cabecalho,
            text="Imagem • Vídeo • Rastreamento • Áudio",
            bg="#1f2937",
            fg="#cbd5e1",
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=25)

        principal = tk.Frame(
            self.janela,
            bg="#eef2f7"
        )
        principal.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=14
        )

        principal.grid_columnconfigure(0, minsize=255, weight=0)
        principal.grid_columnconfigure(1, minsize=350, weight=1)
        principal.grid_columnconfigure(2, minsize=350, weight=1)
        principal.grid_rowconfigure(0, weight=1)

        controles = tk.Frame(
            principal,
            bg="#eef2f7"
        )
        controles.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 10)
        )

        self.criar_controles(controles)

        self.label_original = self.criar_card(
            principal,
            1,
            "Imagem Original",
            "Nenhuma imagem carregada"
        )

        self.label_resultado = self.criar_card(
            principal,
            2,
            "Resultado",
            "O resultado aparecerá aqui"
        )

        status = tk.Frame(
            self.janela,
            bg="#e5e7eb",
            height=34
        )
        status.pack(fill="x")
        status.pack_propagate(False)

        self.status_camera = tk.Label(
            status,
            bg="#e5e7eb",
            fg="#374151",
            font=("Segoe UI", 9)
        )
        self.status_camera.pack(side="left", padx=(14, 10))

        self.status_modo = tk.Label(
            status,
            bg="#e5e7eb",
            fg="#374151",
            font=("Segoe UI", 9)
        )
        self.status_modo.pack(side="left", padx=10)

        self.status_musica = tk.Label(
            status,
            bg="#e5e7eb",
            fg="#374151",
            font=("Segoe UI", 9)
        )
        self.status_musica.pack(side="left", padx=10)

    def criar_controles(self, painel):
        self.grupo(
            painel,
            "Aquisição",
            [
                ("Abrir Imagem", self.abrir_imagem, True)
            ]
        )

        self.grupo(
            painel,
            "Conversões - Imagem",
            [
                ("Cinza", self.aplicar_cinza, False),
                ("Negativo", self.aplicar_negativo, False),
                ("Otsu", self.aplicar_otsu, False)
            ]
        )

        self.grupo(
            painel,
            "Filtros e Bordas - Imagem",
            [
                ("Média", self.aplicar_media_botao, False),
                ("Mediana", self.aplicar_mediana_botao, False),
                ("Canny", self.aplicar_canny, False)
            ]
        )

        self.grupo(
            painel,
            "Morfologia - Imagem",
            [
                ("Erosão", self.aplicar_erosao_botao, False),
                ("Dilatação", self.aplicar_dilatacao_botao, False),
                ("Abertura", self.aplicar_abertura, False),
                ("Fechamento", self.aplicar_fechamento, False)
            ]
        )

        self.grupo(
            painel,
            "Análise",
            [
                ("Histograma", self.mostrar_histograma, False),
                ("Componentes", self.detectar_componentes, False)
            ]
        )

        self.grupo(
            painel,
            "Vídeo - Conversões",
            [
                ("Câmera", self.iniciar_camera, False),
                ("Cinza Vídeo", self.video_cinza, False),
                ("Negativo Vídeo", self.video_negativo, False),
                ("Otsu Vídeo", self.video_otsu, False)
            ]
        )

        self.grupo(
            painel,
            "Vídeo - Filtros",
            [
                ("Média Vídeo", self.video_media, False),
                ("Mediana Vídeo", self.video_mediana, False),
                ("Canny Vídeo", self.video_canny, False)
            ]
        )

        self.grupo(
            painel,
            "Vídeo - Morfologia",
            [
                ("Erosão Vídeo", self.video_erosao, False),
                ("Dilatação Vídeo", self.video_dilatacao, False),
                ("Abertura Vídeo", self.video_abertura, False),
                ("Fechamento Vídeo", self.video_fechamento, False)
            ]
        )

        self.grupo(
            painel,
            "Rastreamento e Áudio",
            [
                ("Rastrear + Música", self.rastrear_vermelho, True),
                ("Parar Câmera", self.parar_camera, False)
            ]
        )

        ttk.Button(
            painel,
            text="Limpar Tela",
            command=self.limpar,
            style="Acao.TButton"
        ).pack(fill="x", pady=(0, 4))

    def grupo(self, painel, titulo, botoes):
        frame = ttk.LabelFrame(
            painel,
            text=titulo,
            style="Grupo.TLabelframe"
        )
        frame.pack(fill="x", pady=(0, 8))
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        for i, (texto, comando, destaque) in enumerate(botoes):
            botao = ttk.Button(
                frame,
                text=texto,
                command=comando,
                style=(
                    "Destaque.TButton"
                    if destaque
                    else "Acao.TButton"
                )
            )
            botao.grid(
                row=i // 2,
                column=i % 2,
                sticky="ew",
                padx=4,
                pady=3
            )

            if len(botoes) == 1:
                botao.grid(columnspan=2)

    def criar_card(self, principal, coluna, titulo, texto):
        card = tk.Frame(
            principal,
            bg="white",
            bd=1,
            relief="solid"
        )

        card.grid(
            row=0,
            column=coluna,
            sticky="nsew",
            padx=(4 if coluna == 1 else 5, 5 if coluna == 1 else 0)
        )

        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        tk.Label(
            card,
            text=titulo,
            bg="white",
            fg="#1f2937",
            font=("Segoe UI", 12, "bold"),
            anchor="w"
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=14,
            pady=10
        )

        area = tk.Frame(card, bg="#111827")
        area.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10)
        )
        area.grid_rowconfigure(0, weight=1)
        area.grid_columnconfigure(0, weight=1)

        label = tk.Label(
            area,
            text=texto,
            bg="#111827",
            fg="#9ca3af",
            font=("Segoe UI", 11)
        )
        label.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=5,
            pady=5
        )

        return label

    def abrir_imagem(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar imagem",
            filetypes=[
                ("Imagens", "*.jpg *.jpeg *.png *.bmp"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if not caminho:
            return

        imagem = cv2.imread(caminho)

        if imagem is None:
            messagebox.showerror(
                "Erro",
                "Não foi possível abrir a imagem."
            )
            return

        self.parar_camera()

        self.imagem_original = imagem
        self.imagem_resultado = imagem.copy()

        self.mostrar_imagem(
            imagem,
            self.label_original
        )
        self.mostrar_imagem(
            imagem,
            self.label_resultado
        )

    def mostrar_imagem(self, imagem, label):
        if imagem is None:
            return

        if len(imagem.shape) == 2:
            rgb = cv2.cvtColor(
                imagem,
                cv2.COLOR_GRAY2RGB
            )
        else:
            rgb = cv2.cvtColor(
                imagem,
                cv2.COLOR_BGR2RGB
            )

        pil = Image.fromarray(rgb)

        largura = max(
            label.winfo_width() - 20,
            320
        )
        altura = max(
            label.winfo_height() - 20,
            250
        )

        resampling = getattr(
            Image,
            "Resampling",
            Image
        ).LANCZOS

        pil.thumbnail(
            (largura, altura),
            resampling
        )

        foto = ImageTk.PhotoImage(pil)
        label.configure(
            image=foto,
            text=""
        )
        label.image = foto

    def obter_cinza(self):
        if self.imagem_original is None:
            messagebox.showwarning(
                "Aviso",
                "Abra uma imagem primeiro."
            )
            return None

        return processamento.obter_cinza(self.imagem_original)

    def aplicar_cinza(self):
        imagem = self.obter_cinza()
        if imagem is not None:
            self.imagem_resultado = imagem
            self.mostrar_imagem(
                imagem,
                self.label_resultado
            )

    def aplicar_negativo(self):
        imagem = self.obter_cinza()
        if imagem is not None:
            resultado = 255 - imagem
            self.imagem_resultado = resultado
            self.mostrar_imagem(
                resultado,
                self.label_resultado
            )

    def otsu_manual(self, imagem):
        return processamento.otsu_manual(imagem)

    def aplicar_otsu(self):
        imagem = self.obter_cinza()
        if imagem is not None:
            resultado = self.otsu_manual(imagem)
            self.imagem_resultado = resultado
            self.mostrar_imagem(
                resultado,
                self.label_resultado
            )

    def janelas_3x3(self, imagem):
        return processamento.janelas_3x3(imagem)

    def aplicar_media(self, imagem):
        return processamento.aplicar_media(imagem)

    def aplicar_mediana(self, imagem):
        return processamento.aplicar_mediana(imagem)

    def aplicar_media_botao(self):
        imagem = self.obter_cinza()
        if imagem is not None:
            resultado = self.aplicar_media(imagem)
            self.imagem_resultado = resultado
            self.mostrar_imagem(
                resultado,
                self.label_resultado
            )

    def aplicar_mediana_botao(self):
        imagem = self.obter_cinza()
        if imagem is not None:
            resultado = self.aplicar_mediana(imagem)
            self.imagem_resultado = resultado
            self.mostrar_imagem(
                resultado,
                self.label_resultado
            )

    def canny_manual(self, imagem, limiar_baixo=100, limiar_alto=200):
        return processamento.canny_manual(imagem, limiar_baixo, limiar_alto)

    def aplicar_canny(self):
        imagem = self.obter_cinza()
        if imagem is not None:
            resultado = self.canny_manual(
                imagem,
                100,
                200
            )
            self.imagem_resultado = resultado
            self.mostrar_imagem(
                resultado,
                self.label_resultado
            )

    def aplicar_erosao(self, imagem):
        return processamento.aplicar_erosao(imagem)

    def aplicar_dilatacao(self, imagem):
        return processamento.aplicar_dilatacao(imagem)

    def aplicar_erosao_botao(self):
        imagem = self.obter_cinza()
        if imagem is not None:
            resultado = self.aplicar_erosao(imagem)
            self.imagem_resultado = resultado
            self.mostrar_imagem(
                resultado,
                self.label_resultado
            )

    def aplicar_dilatacao_botao(self):
        imagem = self.obter_cinza()
        if imagem is not None:
            resultado = self.aplicar_dilatacao(imagem)
            self.imagem_resultado = resultado
            self.mostrar_imagem(
                resultado,
                self.label_resultado
            )

    def aplicar_abertura(self):
        imagem = self.obter_cinza()
        if imagem is not None:
            resultado = self.aplicar_dilatacao(
                self.aplicar_erosao(imagem)
            )
            self.imagem_resultado = resultado
            self.mostrar_imagem(
                resultado,
                self.label_resultado
            )

    def aplicar_fechamento(self):
        imagem = self.obter_cinza()
        if imagem is not None:
            resultado = self.aplicar_erosao(
                self.aplicar_dilatacao(imagem)
            )
            self.imagem_resultado = resultado
            self.mostrar_imagem(
                resultado,
                self.label_resultado
            )

    def mostrar_histograma(self):
        imagem = self.obter_cinza()

        if imagem is None:
            return

        hist = processamento.calcular_histograma(imagem)

        janela = tk.Toplevel(self.janela)
        janela.title("Histograma")
        janela.geometry("760x450")
        janela.configure(bg="#eef2f7")

        tk.Label(
            janela,
            text="Histograma da Imagem",
            bg="#eef2f7",
            fg="#1f2937",
            font=("Segoe UI", 15, "bold")
        ).pack(pady=(14, 8))

        canvas = tk.Canvas(
            janela,
            width=720,
            height=360,
            bg="white",
            highlightthickness=1,
            highlightbackground="#d1d5db"
        )
        canvas.pack(
            padx=14,
            pady=8
        )

        maior = max(int(hist.max()), 1)
        passo = 700 / 256

        for i in range(256):
            h = (hist[i] / maior) * 320
            x1 = 10 + i * passo

            canvas.create_rectangle(
                x1,
                345 - h,
                x1 + passo,
                345,
                fill="#374151",
                outline=""
            )

    def detectar_componentes(self):
        imagem = self.obter_cinza()

        if imagem is None:
            return

        componentes = processamento.detectar_componentes(imagem)
        altura, largura = imagem.shape

        imagem_componentes = np.zeros(
            (altura, largura, 3),
            dtype=np.uint8
        )

        for i, componente in enumerate(componentes):
            cor = (
                50 + (i * 70) % 206,
                50 + (i * 130) % 206,
                50 + (i * 190) % 206
            )

            for py, px in componente["pixels"]:
                imagem_componentes[py, px] = cor

        self.imagem_resultado = imagem_componentes

        self.mostrar_imagem(
            imagem_componentes,
            self.label_resultado
        )

        janela = tk.Toplevel(self.janela)
        janela.title("Componentes Detectados")
        janela.geometry("560x520")
        janela.configure(bg="#eef2f7")

        tk.Label(
            janela,
            text=f"{len(componentes)} objeto(s) detectado(s)",
            bg="#eef2f7",
            fg="#1f2937",
            font=("Segoe UI", 15, "bold")
        ).pack(pady=(14, 8))

        tabela = ttk.Treeview(
            janela,
            columns=(
                "objeto",
                "area",
                "perimetro",
                "diametro"
            ),
            show="headings",
            height=16
        )

        colunas = [
            ("objeto", "Objeto", 80),
            ("area", "Área", 100),
            ("perimetro", "Perímetro", 120),
            ("diametro", "Diâmetro", 110)
        ]

        for col, titulo, largura_col in colunas:
            tabela.heading(col, text=titulo)
            tabela.column(
                col,
                width=largura_col,
                anchor="center"
            )

        for i, componente in enumerate(componentes, 1):
            tabela.insert(
                "",
                "end",
                values=(
                    i,
                    componente["area"],
                    componente["perimetro"],
                    f"{componente['diametro']:.2f}"
                )
            )

        tabela.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=10
        )

    def iniciar_camera(self):
        if self.camera_ativa:
            return

        self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():
            messagebox.showerror(
                "Erro",
                "Não foi possível abrir a câmera."
            )
            self.camera.release()
            self.camera = None
            return

        self.camera.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            640
        )
        self.camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            480
        )

        self.camera_ativa = True
        self.modo_video = "normal"
        self.atualizar_status()
        self.atualizar_camera()

    def verificar_camera(self):
        if not self.camera_ativa:
            messagebox.showwarning(
                "Aviso",
                "Abra a câmera primeiro."
            )
            return False
        return True

    def video_cinza(self):
        if self.verificar_camera():
            self.modo_video = "cinza"
            self.atualizar_status()

    def video_negativo(self):
        if self.verificar_camera():
            self.modo_video = "negativo"
            self.atualizar_status()

    def video_otsu(self):
        if self.verificar_camera():
            self.modo_video = "otsu"
            self.atualizar_status()

    def video_media(self):
        if self.verificar_camera():
            self.modo_video = "media"
            self.atualizar_status()

    def video_mediana(self):
        if self.verificar_camera():
            self.modo_video = "mediana"
            self.atualizar_status()

    def video_canny(self):
        if self.verificar_camera():
            self.modo_video = "canny"
            self.atualizar_status()

    def video_erosao(self):
        if self.verificar_camera():
            self.modo_video = "erosao"
            self.atualizar_status()

    def video_dilatacao(self):
        if self.verificar_camera():
            self.modo_video = "dilatacao"
            self.atualizar_status()

    def video_abertura(self):
        if self.verificar_camera():
            self.modo_video = "abertura"
            self.atualizar_status()

    def video_fechamento(self):
        if self.verificar_camera():
            self.modo_video = "fechamento"
            self.atualizar_status()

    def processar_frame_video(self, frame):
        if self.modo_video == "normal":
            return frame

        cinza = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        if self.modo_video == "cinza":
            return cinza

        if self.modo_video == "negativo":
            return 255 - frame

        if self.modo_video == "otsu":
            _, resultado = cv2.threshold(
                cinza,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            return resultado

        if self.modo_video == "media":
            return cv2.blur(
                cinza,
                (3, 3)
            )

        if self.modo_video == "mediana":
            return cv2.medianBlur(
                cinza,
                3
            )

        if self.modo_video == "canny":
            return cv2.Canny(
                cinza,
                100,
                200
            )

        kernel = np.ones(
            (3, 3),
            np.uint8
        )

        if self.modo_video == "erosao":
            return cv2.erode(
                cinza,
                kernel,
                iterations=1
            )

        if self.modo_video == "dilatacao":
            return cv2.dilate(
                cinza,
                kernel,
                iterations=1
            )

        if self.modo_video == "abertura":
            return cv2.morphologyEx(
                cinza,
                cv2.MORPH_OPEN,
                kernel
            )

        if self.modo_video == "fechamento":
            return cv2.morphologyEx(
                cinza,
                cv2.MORPH_CLOSE,
                kernel
            )

        return frame

    def rastrear_vermelho(self):
        if self.verificar_camera():
            self.modo_video = "rastrear"
            self.atualizar_status()

    def preparar_musica(self):
        if (
            pygame is None
            or not os.path.exists(self.caminho_musica)
        ):
            return False

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()

            if not self.musica_carregada:
                pygame.mixer.music.load(
                    self.caminho_musica
                )
                self.musica_carregada = True

            return True

        except Exception:
            self.musica_carregada = False
            return False

    def iniciar_musica(self):
        if not self.preparar_musica():
            if not self.aviso_musica:
                if pygame is None:
                    mensagem = (
                        "O pygame não está instalado.\n\n"
                        "Execute:\n"
                        "pip install pygame"
                    )
                else:
                    mensagem = (
                        "Não foi encontrada a música.\n\n"
                        "Coloque 'musica.mp3' "
                        "dentro da pasta 'sons'."
                    )

                messagebox.showwarning(
                    "Música",
                    mensagem
                )
                self.aviso_musica = True

            return

        try:
            if (
                not self.musica_tocando
                or not pygame.mixer.music.get_busy()
            ):
                pygame.mixer.music.play(loops=-1)
                self.musica_tocando = True
                self.atualizar_status()

        except Exception:
            self.musica_tocando = False

    def parar_musica(self):
        if pygame is not None:
            try:
                if pygame.mixer.get_init() is not None:
                    pygame.mixer.music.stop()
            except Exception:
                pass

        self.musica_tocando = False
        self.atualizar_status()

    def rastrear_objeto_vermelho(self, frame):
        hsv = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2HSV
        )

        baixo1 = np.array([0, 100, 80])
        alto1 = np.array([10, 255, 255])

        baixo2 = np.array([170, 100, 80])
        alto2 = np.array([180, 255, 255])

        mascara1 = cv2.inRange(
            hsv,
            baixo1,
            alto1
        )

        mascara2 = cv2.inRange(
            hsv,
            baixo2,
            alto2
        )

        mascara = cv2.bitwise_or(
            mascara1,
            mascara2
        )

        kernel = np.ones(
            (5, 5),
            np.uint8
        )

        mascara = cv2.morphologyEx(
            mascara,
            cv2.MORPH_OPEN,
            kernel
        )

        mascara = cv2.morphologyEx(
            mascara,
            cv2.MORPH_CLOSE,
            kernel
        )

        contornos, _ = cv2.findContours(
            mascara,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if not contornos:
            self.parar_musica()
            return frame

        maior = max(
            contornos,
            key=cv2.contourArea
        )

        area = cv2.contourArea(maior)

        if area < 500:
            self.parar_musica()
            return frame

        x, y, w, h = cv2.boundingRect(maior)

        cx = x + w // 2
        cy = y + h // 2

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 0, 255),
            2
        )

        cv2.circle(
            frame,
            (cx, cy),
            5,
            (0, 255, 0),
            -1
        )

        cv2.putText(
            frame,
            "OBJETO DETECTADO",
            (x, max(y - 10, 25)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 0, 255),
            2
        )

        cv2.putText(
            frame,
            f"Centro: ({cx}, {cy})",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Area: {int(area)}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "MUSICA TOCANDO",
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

        self.iniciar_musica()

        return frame

    def atualizar_camera(self):
        if (
            not self.camera_ativa
            or self.camera is None
        ):
            return

        ret, frame = self.camera.read()

        if not ret:
            self.parar_camera()
            return

        frame = cv2.resize(
            frame,
            (640, 480)
        )

        if self.modo_video == "rastrear":
            processado = self.rastrear_objeto_vermelho(
                frame
            )
        else:
            processado = self.processar_frame_video(
                frame
            )

        self.mostrar_imagem(
            processado,
            self.label_resultado
        )

        self.atualizar_status()

        self.janela.after(
            30,
            self.atualizar_camera
        )

    def atualizar_status(self):
        self.status_camera.config(
            text=(
                "Câmera: ligada"
                if self.camera_ativa
                else "Câmera: desligada"
            )
        )

        modos = {
            None: "imagem",
            "normal": "normal",
            "cinza": "cinza",
            "negativo": "negativo",
            "otsu": "Otsu",
            "media": "média",
            "mediana": "mediana",
            "canny": "Canny",
            "erosao": "erosão",
            "dilatacao": "dilatação",
            "abertura": "abertura",
            "fechamento": "fechamento",
            "rastrear": "rastreamento vermelho"
        }

        self.status_modo.config(
            text=f"Modo: {modos.get(self.modo_video, 'imagem')}"
        )

        self.status_musica.config(
            text=(
                "Música: tocando"
                if self.musica_tocando
                else "Música: parada"
            )
        )

    def parar_camera(self):
        self.camera_ativa = False
        self.modo_video = None

        if self.camera is not None:
            try:
                self.camera.release()
            except Exception:
                pass

            self.camera = None

        self.parar_musica()
        self.atualizar_status()

    def limpar(self):
        self.parar_camera()

        self.imagem_original = None
        self.imagem_resultado = None

        self.label_original.config(
            image="",
            text="Nenhuma imagem carregada"
        )
        self.label_original.image = None

        self.label_resultado.config(
            image="",
            text="O resultado aparecerá aqui"
        )
        self.label_resultado.image = None

        self.atualizar_status()

    def fechar_aplicacao(self):
        self.camera_ativa = False

        if self.camera is not None:
            try:
                self.camera.release()
            except Exception:
                pass

        if pygame is not None:
            try:
                if pygame.mixer.get_init() is not None:
                    pygame.mixer.music.stop()
                    pygame.mixer.quit()
            except Exception:
                pass

        self.janela.destroy()
