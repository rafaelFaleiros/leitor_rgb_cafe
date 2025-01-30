import serial
import tkinter as tk
from tkinter import messagebox, ttk, colorchooser, Canvas, Scrollbar, Frame
import threading
import time
import serial.tools.list_ports
from tkinter.simpledialog import askstring
import json

ARQUIVO_CORES = "cores_salvas.json"

# Função para listar portas disponíveis
def listar_portas():
    return [comport.device for comport in serial.tools.list_ports.comports()]

# Função para calcular a distância entre cores
def calcular_distancia(cor1, cor2):
    return sum((c1 - c2) ** 2 for c1, c2 in zip(cor1, cor2)) ** 0.5

# Função para mostrar mensagens de erro
def mostrar_erro(mensagem):
    messagebox.showerror("Erro", mensagem)

# Função para ler os dados da porta serial
def ler_dados():
    porta_serial = combo_porta.get()
    try:
        with serial.Serial(porta_serial, 9600, timeout=2) as ser:
            time.sleep(2)
            dados = ser.readline().decode('utf-8').strip()

        valores = dados.split(';')
        if len(valores) == 3:
            r, g, b = map(int, valores)
            root.after(0, atualizar_interface, r, g, b)
        else:
            mostrar_erro("Dados no formato incorreto.")
    except Exception as e:
        mostrar_erro(f"Não foi possível se conectar à porta: {e}")

# Função para atualizar a interface com os valores lidos
def atualizar_interface(r, g, b):
    resultado_label.config(text=f"R: {r} | G: {g} | B: {b}")
    cor_canvas.config(bg=f'#{r:02x}{g:02x}{b:02x}')
    cor_mais_proxima = encontrar_cor_mais_proxima((r, g, b))
    if cor_mais_proxima:
        nome_cor.set(f"Cor mais próxima: {cor_mais_proxima[1]}")

# Iniciar leitura com thread para não travar a interface
def iniciar_leitura():
    ler_button.config(state=tk.DISABLED)
    threading.Thread(target=ler_dados).start()
    root.after(3000, lambda: ler_button.config(state=tk.NORMAL))

# Adicionar uma nova cor salva
def adicionar_cor():
    cor_selecionada = colorchooser.askcolor(title="Selecione a Cor")[0]
    if cor_selecionada:
        r, g, b = map(int, cor_selecionada)
        nome = askstring("Nome da Cor", "Digite um nome para esta cor:")
        if nome:
            cores_salvas.append(((r, g, b), nome))
            salvar_cores()
            atualizar_cores_display()

# Salvar cores no JSON
def salvar_cores():
    with open(ARQUIVO_CORES, "w") as file:
        json.dump(cores_salvas, file)

# Carregar cores salvas do JSON
def carregar_cores():
    try:
        with open(ARQUIVO_CORES, "r") as file:
            return [(tuple(cor), nome) for cor, nome in json.load(file)]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Excluir uma cor salva
def excluir_cor(cor, nome):
    for item in cores_salvas:
        if item[0] == cor and item[1] == nome:
            cores_salvas.remove(item)
            break
    salvar_cores()
    atualizar_cores_display()

# Atualizar a lista de cores salvas na interface
def atualizar_cores_display():
    for widget in cores_canvas.winfo_children():
        widget.destroy()

    for cor, nome in cores_salvas:
        cor_hex = f'#{cor[0]:02x}{cor[1]:02x}{cor[2]:02x}'
        frame = tk.Frame(cores_canvas, bg="#2c1e16")
        frame.pack(pady=2, fill=tk.X)

        cor_display = tk.Label(frame, width=4, height=2, bg=cor_hex, relief="solid")
        cor_display.pack(side=tk.LEFT, padx=5)

        label_nome = tk.Label(frame, text=f"{nome} ({cor[0]},{cor[1]},{cor[2]})", fg="white", bg="#2c1e16")
        label_nome.pack(side=tk.LEFT)

        btn_excluir = tk.Button(frame, text="X", fg="red", bg="#2c1e16",
                                command=lambda c=cor, n=nome: excluir_cor(c, n))
        btn_excluir.pack(side=tk.RIGHT, padx=5)

# Encontrar cor mais próxima
def encontrar_cor_mais_proxima(cor_lida):
    if not cores_salvas:
        return None
    return min(cores_salvas, key=lambda cor: calcular_distancia(cor[0], cor_lida))

# Mostrar informações do autor
def mostrar_sobre():
    messagebox.showinfo("Sobre", "Autor: Rafael Amorim Faleiros")

# Inicializar cores salvas
cores_salvas = carregar_cores()

# Configuração da janela principal
root = tk.Tk()
root.title("Leitor RGB para Torras de Café")
root.geometry("600x500")
root.configure(bg="#2c1e16")

titulo_label = tk.Label(root, text="Café Herdeiros", font=("Helvetica", 16, "bold"), bg="#2c1e16", fg="#d4a373")
titulo_label.pack(pady=5)

combo_porta = ttk.Combobox(root, values=listar_portas(), width=30)
combo_porta.set("Selecione a porta...")
combo_porta.pack(pady=10)

ler_button = tk.Button(root, text="Ler", width=20, height=2, bg="#d4a373", fg="#2c1e16", font=("Helvetica", 12, "bold"), command=iniciar_leitura)
ler_button.pack(pady=10)

resultado_label = tk.Label(root, text="Os valores RGB aparecerão aqui.", font=("Helvetica", 12), bg="#2c1e16", fg="#f3e5ab")
resultado_label.pack(pady=10)

frame_cor = tk.Frame(root, bg="#ffffff", width=200, height=100, relief="raised", bd=2)
frame_cor.pack(pady=20)
cor_canvas = tk.Canvas(frame_cor, width=190, height=90, bg="#000000", highlightthickness=0)
cor_canvas.pack(padx=5, pady=5)

nome_cor = tk.StringVar()
cor_mais_proxima_label = tk.Label(root, textvariable=nome_cor, font=("Helvetica", 12), bg="#2c1e16", fg="#f3e5ab")
cor_mais_proxima_label.pack(pady=5)

# Área de cores salvas rolável
scrollbar = Scrollbar(root)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

cores_canvas = Canvas(root, bg="#2c1e16", yscrollcommand=scrollbar.set)
cores_canvas.pack(side=tk.RIGHT, padx=10, fill=tk.Y)

scrollbar.config(command=cores_canvas.yview)

# Botões
frame_botoes = tk.Frame(root, bg="#2c1e16")
frame_botoes.pack(side=tk.TOP, fill=tk.X, pady=10)

tk.Button(frame_botoes, text="+Cor", width=12, height=2, bg="#d4a373", fg="#2c1e16", font=("Helvetica", 10), command=adicionar_cor).pack(side=tk.RIGHT, padx=10)
tk.Button(frame_botoes, text="Sobre", width=12, height=2, bg="#d4a373", fg="#2c1e16", font=("Helvetica", 10), command=mostrar_sobre).pack(side=tk.RIGHT, padx=10)

atualizar_cores_display()
root.mainloop()
