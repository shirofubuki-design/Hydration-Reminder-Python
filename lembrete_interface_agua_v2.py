
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from PIL import Image, ImageTk

# Configurações visuais
FUNDO = "#101827"
PAINEL = "#1B2638"
AZUL = "#258CFF"
BRANCO = "#FFFFFF"
CINZA = "#AAB7CC"

PASTA = Path(__file__).parent
CAMINHO_IMAGEM = PASTA / "agua.png"


class LembreteAgua:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Hydration Reminder 2.0")
        self.janela.geometry("430x620")
        self.janela.configure(bg=FUNDO)
        self.janela.resizable(False, False)

        self.copos = 0
        self.ativo = True
        self.intervalo = tk.IntVar(value=60)
        self.agendamento = None
        self.popup = None

        self.criar_interface()
        self.agendar()

    def carregar_imagem(self, tamanho):
        try:
            imagem = Image.open(CAMINHO_IMAGEM)
            imagem = imagem.convert("RGB")
            imagem.thumbnail((tamanho, tamanho))
            return ImageTk.PhotoImage(imagem)
        except Exception as erro:
            print("Erro ao carregar imagem:", erro)
            return None

    def criar_botao(self, pai, texto, comando, cor=AZUL):
        return tk.Button(
            pai,
            text=texto,
            command=comando,
            bg=cor,
            fg=BRANCO,
            activebackground="#176ACC",
            activeforeground=BRANCO,
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            pady=10
        )

    def criar_interface(self):
        tk.Label(
            self.janela,
            text="HYDRATION REMINDER",
            bg=FUNDO,
            fg=AZUL,
            font=("Segoe UI", 19, "bold")
        ).pack(pady=(20, 5))

        tk.Label(
            self.janela,
            text="Cuide de você. Beba água!",
            bg=FUNDO,
            fg=CINZA,
            font=("Segoe UI", 11)
        ).pack()

        self.foto = self.carregar_imagem(255)

        if self.foto:
            tk.Label(
                self.janela,
                image=self.foto,
                bg=FUNDO
            ).pack(pady=15)

        self.contador = tk.Label(
            self.janela,
            text="Copos consumidos: 0",
            bg=FUNDO,
            fg=BRANCO,
            font=("Segoe UI", 15, "bold")
        )
        self.contador.pack(pady=5)

        painel = tk.Frame(self.janela, bg=PAINEL)
        painel.pack(fill="x", padx=25, pady=12)

        tk.Label(
            painel,
            text="Intervalo dos lembretes (minutos)",
            bg=PAINEL,
            fg=BRANCO
        ).pack(pady=(10, 5))

        menu = tk.OptionMenu(
            painel,
            self.intervalo,
            1, 15, 30, 45, 60, 90,
            command=lambda _: self.agendar()
        )
        menu.config(bg=PAINEL, fg=AZUL, width=12)
        menu.pack(pady=(0, 10))

        self.criar_botao(
            self.janela,
            "Já bebi água!",
            self.registrar_agua
        ).pack(fill="x", padx=35, pady=5)

        self.criar_botao(
            self.janela,
            "Testar notificação",
            self.mostrar_notificacao,
            "#34445B"
        ).pack(fill="x", padx=35, pady=5)

        self.botao_pausa = self.criar_botao(
            self.janela,
            "Pausar lembretes",
            self.alternar_pausa,
            "#34445B"
        )
        self.botao_pausa.pack(fill="x", padx=35, pady=5)

    def registrar_agua(self):
        self.copos += 1
        self.contador.config(
            text=f"Copos consumidos: {self.copos}"
        )

        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            self.popup = None

        self.agendar()

    def agendar(self, minutos=None):
        if self.agendamento is not None:
            self.janela.after_cancel(self.agendamento)
            self.agendamento = None

        if not self.ativo:
            return

        if minutos is None:
            minutos = self.intervalo.get()

        self.agendamento = self.janela.after(
            int(minutos * 60 * 1000),
            self.avisar
        )

    def avisar(self):
        self.agendamento = None
        self.mostrar_notificacao()
        self.agendar()

    def alternar_pausa(self):
        self.ativo = not self.ativo

        if self.ativo:
            self.botao_pausa.config(text="Pausar lembretes")
            self.agendar()
        else:
            self.botao_pausa.config(text="Retomar lembretes")
            if self.agendamento is not None:
                self.janela.after_cancel(self.agendamento)
                self.agendamento = None

    def mostrar_notificacao(self):
        if self.popup and self.popup.winfo_exists():
            self.popup.lift()
            return

        self.popup = tk.Toplevel(self.janela)
        self.popup.title("Hora de beber água!")
        self.popup.geometry("330x430")
        self.popup.configure(bg=FUNDO)
        self.popup.resizable(False, False)
        self.popup.attributes("-topmost", True)

        # Posicionar no canto inferior direito
        self.popup.update_idletasks()
        largura = self.popup.winfo_width()
        altura = self.popup.winfo_height()
        x = self.popup.winfo_screenwidth() - largura - 25
        y = self.popup.winfo_screenheight() - altura - 70
        self.popup.geometry(f"+{x}+{y}")

        tk.Label(
            self.popup,
            text="HORA DE BEBER ÁGUA!",
            bg=FUNDO,
            fg=AZUL,
            font=("Segoe UI", 15, "bold")
        ).pack(pady=(18, 10))

        self.foto_popup = self.carregar_imagem(225)

        if self.foto_popup:
            tk.Label(
                self.popup,
                image=self.foto_popup,
                bg=FUNDO
            ).pack()

        tk.Label(
            self.popup,
            text="Uma pausa para se hidratar!",
            bg=FUNDO,
            fg=BRANCO,
            font=("Segoe UI", 11)
        ).pack(pady=12)

        self.criar_botao(
            self.popup,
            "Já bebi água!",
            self.registrar_agua
        ).pack(fill="x", padx=30, pady=5)

        self.criar_botao(
            self.popup,
            "Adiar 10 minutos",
            self.adiar,
            "#34445B"
        ).pack(fill="x", padx=30, pady=5)

    def adiar(self):
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            self.popup = None

        self.agendar(10)


if __name__ == "__main__":
    janela = tk.Tk()
    aplicativo = LembreteAgua(janela)
    janela.mainloop()
