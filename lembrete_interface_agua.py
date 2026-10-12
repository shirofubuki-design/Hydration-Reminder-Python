"""Hydration Reminder 3.1 - inicialização opcional oculta na bandeja."""
import json
import os
import sys
import queue
import threading
from datetime import date
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk, ImageDraw
import pystray

# Recursos do executável ficam no diretório temporário do PyInstaller.
PASTA = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
IMAGEM = PASTA / "agua.png"
PASTA_DADOS = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "HydrationReminder"
PASTA_DADOS.mkdir(parents=True, exist_ok=True)
DADOS = PASTA_DADOS / "hidratacao.json"
FUNDO = "#101827"
PAINEL = "#1B2638"
AZUL = "#258CFF"
BRANCO = "#FFFFFF"
CINZA = "#AAB7CC"


class HydrationReminder:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Hydration Reminder 3.1")
        self.janela.geometry("510x750")
        self.janela.minsize(450, 600)
        self.janela.configure(bg=FUNDO)
        self.janela.protocol("WM_DELETE_WINDOW", self.ocultar)

        self.eventos = queue.Queue()
        self.icone_tray = None
        self.popup = None
        self.temporizador = None
        self.ativo = True
        self.encerrando = False
        self.intervalo = tk.IntVar(value=60)
        self.dados = self.ler_dados()
        self.copos = self.dados["copos"]
        self.intervalo.set(self.dados["intervalo"])

        self.criar_interface()
        self.iniciar_tray()
        self.janela.after(200, self.processar_eventos)
        self.janela.after(60000, self.verificar_dia)
        self.agendar()

    def ler_dados(self):
        padrao = {"data": date.today().isoformat(), "copos": 0, "intervalo": 60}
        try:
            dados = json.loads(DADOS.read_text(encoding="utf-8"))
            if not isinstance(dados, dict):
                return padrao
            if dados.get("data") == padrao["data"]:
                copos = dados.get("copos", 0)
                if type(copos) is int and copos >= 0:
                    padrao["copos"] = copos
            intervalo = dados.get("intervalo", 60)
            if type(intervalo) is int and intervalo in (1, 15, 30, 45, 60, 90):
                padrao["intervalo"] = intervalo
        except (OSError, ValueError, TypeError):
            pass
        return padrao

    def salvar(self):
        dados = {"data": date.today().isoformat(),
                 "copos": self.copos, "intervalo": self.intervalo.get()}
        temporario = DADOS.with_suffix(".tmp")
        try:
            temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2),
                                  encoding="utf-8")
            temporario.replace(DADOS)
        except OSError as erro:
            messagebox.showwarning("Erro ao salvar", str(erro))

    def imagem_pil(self):
        try:
            with Image.open(IMAGEM) as arquivo:
                return arquivo.convert("RGBA")
        except (OSError, ValueError):
            imagem = Image.new("RGBA", (256, 256), AZUL)
            desenho = ImageDraw.Draw(imagem)
            desenho.text((90, 115), "H2O", fill="white")
            return imagem

    def foto(self, largura, altura):
        from PIL import ImageOps
        imagem = ImageOps.contain(self.imagem_pil(), (largura, altura))
        return ImageTk.PhotoImage(imagem)

    def botao(self, pai, texto, comando, fundo=AZUL):
        return tk.Button(pai, text=texto, command=comando, bg=fundo, fg=BRANCO,
                         activebackground="#176ACC", activeforeground=BRANCO,
                         font=("Segoe UI", 10, "bold"), relief="flat", pady=9,
                         cursor="hand2")

    def criar_interface(self):
        # Área rolável: todos os controles continuam acessíveis em telas menores.
        canvas = tk.Canvas(self.janela, bg=FUNDO, highlightthickness=0)
        barra = tk.Scrollbar(self.janela, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        conteudo = tk.Frame(canvas, bg=FUNDO)
        janela_canvas = canvas.create_window((0, 0), window=conteudo, anchor="nw")
        conteudo.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(janela_canvas, width=e.width))

        tk.Label(conteudo, text="HYDRATION REMINDER", bg=FUNDO, fg=AZUL,
                 font=("Segoe UI", 20, "bold")).pack(pady=(24, 5))
        tk.Label(conteudo, text="Cuide de você. Beba água!", bg=FUNDO,
                 fg=CINZA, font=("Segoe UI", 11)).pack()
        self.foto_principal = self.foto(260, 260)
        tk.Label(conteudo, image=self.foto_principal, bg=FUNDO).pack(pady=14)
        self.rotulo_copos = tk.Label(conteudo, bg=FUNDO, fg=BRANCO,
                                    font=("Segoe UI", 15, "bold"))
        self.rotulo_copos.pack(pady=(0, 12))
        self.atualizar_contador()

        painel = tk.Frame(conteudo, bg=PAINEL)
        painel.pack(fill="x", padx=35, pady=(0, 12))
        tk.Label(painel, text="Intervalo entre lembretes (minutos)",
                 bg=PAINEL, fg=BRANCO).pack(pady=(12, 4))
        seletor = tk.OptionMenu(painel, self.intervalo, 1, 15, 30, 45, 60, 90,
                               command=lambda _: self.alterar_intervalo())
        seletor.config(bg=PAINEL, fg=AZUL, width=12, highlightthickness=0)
        seletor.pack(pady=(0, 12))

        self.botao(conteudo, "Já bebi água!", self.registrar).pack(fill="x", padx=45, pady=5)
        self.botao(conteudo, "Testar notificação", self.mostrar_popup, PAINEL).pack(
            fill="x", padx=45, pady=5)
        self.botao_pausar = self.botao(conteudo, "Pausar lembretes", self.alternar, PAINEL)
        self.botao_pausar.pack(fill="x", padx=45, pady=5)
        tk.Label(conteudo, text="Fechar a janela minimiza para a bandeja do Windows.",
                 bg=FUNDO, fg=CINZA, font=("Segoe UI", 9)).pack(pady=(12, 20))

    def atualizar_contador(self):
        self.rotulo_copos.config(text=f"Copos consumidos hoje: {self.copos}")

    def verificar_dia(self):
        if self.encerrando:
            return
        if self.dados.get("data") != date.today().isoformat():
            self.copos = 0
            self.dados["data"] = date.today().isoformat()
            self.atualizar_contador()
            self.salvar()
        self.janela.after(60000, self.verificar_dia)

    def registrar(self):
        self.verificar_data_agora()
        self.copos += 1
        self.atualizar_contador()
        self.salvar()
        self.fechar_popup()
        self.agendar()

    def verificar_data_agora(self):
        if self.dados.get("data") != date.today().isoformat():
            self.copos = 0
            self.dados["data"] = date.today().isoformat()

    def alterar_intervalo(self):
        self.salvar()
        self.agendar()

    def agendar(self, minutos=None):
        if self.temporizador is not None:
            self.janela.after_cancel(self.temporizador)
            self.temporizador = None
        if self.ativo and not self.encerrando:
            tempo = self.intervalo.get() if minutos is None else minutos
            self.temporizador = self.janela.after(int(tempo * 60 * 1000), self.avisar)

    def avisar(self):
        self.temporizador = None
        self.mostrar_popup()
        self.agendar()

    def alternar(self):
        self.ativo = not self.ativo
        self.botao_pausar.config(text="Pausar lembretes" if self.ativo
                                else "Retomar lembretes")
        self.agendar()

    def fechar_popup(self):
        if self.popup is not None:
            try:
                if self.popup.winfo_exists():
                    self.popup.destroy()
            except tk.TclError:
                pass
            self.popup = None

    def mostrar_popup(self):
        if self.popup is not None and self.popup.winfo_exists():
            self.popup.deiconify()
            self.popup.lift()
            return
        popup = tk.Toplevel(self.janela)
        self.popup = popup
        popup.title("Hora de beber água!")
        popup.geometry("365x490")
        popup.configure(bg=FUNDO)
        popup.resizable(False, False)
        popup.attributes("-topmost", True)
        popup.protocol("WM_DELETE_WINDOW", self.fechar_popup)
        popup.update_idletasks()
        x = max(0, popup.winfo_screenwidth() - 385)
        y = max(0, popup.winfo_screenheight() - 550)
        popup.geometry(f"365x490+{x}+{y}")
        tk.Label(popup, text="HORA DE BEBER ÁGUA!", bg=FUNDO, fg=AZUL,
                 font=("Segoe UI", 16, "bold")).pack(pady=(17, 10))
        popup.foto = self.foto(230, 230)
        tk.Label(popup, image=popup.foto, bg=FUNDO).pack()
        tk.Label(popup, text="Que tal uma pausa para se hidratar?",
                 bg=FUNDO, fg=BRANCO).pack(pady=12)
        self.botao(popup, "Já bebi água!", self.registrar).pack(fill="x", padx=32, pady=5)
        self.botao(popup, "Adiar 10 minutos", self.adiar, PAINEL).pack(
            fill="x", padx=32, pady=5)

    def adiar(self):
        self.fechar_popup()
        self.agendar(10)

    def iniciar_tray(self):
        imagem = self.imagem_pil().copy()
        imagem.thumbnail((64, 64))
        menu = pystray.Menu(
            pystray.MenuItem("Abrir Hydration Reminder", lambda icon, item: self.eventos.put("abrir"), default=True),
            pystray.MenuItem("Testar lembrete", lambda icon, item: self.eventos.put("testar")),
            pystray.MenuItem("Sair do aplicativo", lambda icon, item: self.eventos.put("sair")),
        )
        self.icone_tray = pystray.Icon("hydration_reminder", imagem,
                                       "Hydration Reminder 3.1", menu)
        # pystray usa seu próprio loop; callbacks comunicam-se com Tk via Queue.
        threading.Thread(target=self.executar_tray, daemon=True).start()

    def executar_tray(self):
        try:
            self.icone_tray.run()
        except Exception as erro:
            print("Não foi possível iniciar o ícone da bandeja:", erro)
            self.eventos.put("tray_erro")

    def processar_eventos(self):
        if self.encerrando:
            return
        try:
            while True:
                evento = self.eventos.get_nowait()
                if evento == "abrir":
                    self.janela.deiconify()
                    self.janela.lift()
                    self.janela.focus_force()
                elif evento == "testar":
                    self.mostrar_popup()
                elif evento == "sair":
                    self.sair()
                    return
                elif evento == "tray_erro":
                    self.icone_tray = None
                    self.janela.deiconify()
                    messagebox.showwarning("Bandeja indisponível",
                                           "O ícone da bandeja não iniciou. A janela não será ocultada.")
        except queue.Empty:
            pass
        self.janela.after(200, self.processar_eventos)

    def ocultar(self):
        if self.icone_tray is None:
            messagebox.showinfo("Bandeja indisponível", "Use a janela principal até corrigir a bandeja.")
            return
        self.janela.withdraw()

    def sair(self):
        self.encerrando = True
        self.salvar()
        if self.temporizador is not None:
            self.janela.after_cancel(self.temporizador)
        self.fechar_popup()
        if self.icone_tray is not None:
            self.icone_tray.stop()
        self.janela.destroy()


if __name__ == "__main__":
    raiz = tk.Tk()
    # A opção --minimized será usada somente pelo atalho de inicialização.
    # Ocultamos antes de construir a interface, evitando mostrar a janela.
    if "--minimized" in sys.argv:
        raiz.withdraw()
    app = HydrationReminder(raiz)
    raiz.mainloop()