import tkinter as tk
from interface import Aplicacao


if __name__ == "__main__":
    janela = tk.Tk()
    app = Aplicacao(janela)
    janela.mainloop()
