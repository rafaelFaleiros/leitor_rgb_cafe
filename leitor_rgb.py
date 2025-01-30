import serial
import tkinter as tk
from tkinter import messagebox, ttk, colorchooser
import threading
import time
import serial.tools.list_ports
from tkinter.simpledialog import askstring
import json

# Nome do arquivo JSON para salvar as cores
ARQUIVO_CORES = "cores_salvas.json"

# Função para listar as portas seriais disponíveis no PC
def listar_portas():
    return [comport.device for comport in serial.tools.list_ports.comports()]

# Função para calcular a distância euclidiana entre duas cores RGB
def calcular_distancia(cor1, cor2):
    return sum((c1 - c2) ** 2 for c1, c2 in zip(cor1, cor2)) ** 0.5

# Função para ler os dados da porta serial
def ler_dados():
    porta_serial = combo_porta.get()
    try:
        ser = serial.Serial(porta_serial, 9600)
        time.sleep(2)
        dados = ser.readline().decode('utf-8').strip()
        ser.close()

        valores = dados.split(';')
        if len(valores) == 3:
            r, g, b = map(int, valores)
            resultado_label.config(text=f"R: {r} | G: {g} | B: {b}")
            cor_canvas.config(bg=f'#{r:02x}{g:02x}{b:02x}')
            cor_mais_proxima = encontrar_cor_mais_proxima((r, g, b))
            if cor_mais_proxima:
                nome_cor.set(f"Cor mais próxima: {cor_mais_proxima[1]}")
        else:
            messagebox.showerror("Erro", "Dados no formato incorreto.")
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível se conectar à porta: {e}")

# Função para iniciar a leitura em uma thread separada
def iniciar_leitura():
    ler_button.config(state=tk.DISABLED)
    threading.Thread(target=ler_dados).start()
    root.after(3000, lambda: ler_button.config(state=tk.NORMAL))

# Função para adicionar uma nova cor
def adicionar_cor():
    cor_selecionada = colorchooser.askcolor(title="Selecione a Cor")[0]
    if cor_selecionada:
        r, g, b = map(int, cor_selecionada)
        nome = askstring("Nome da Cor", "Digite um nome para esta cor:")
        if nome:
            cores_salvas.append(((r, g, b), nome))
            salvar_cores()
            atualizar_cores_display()

# Função para salvar as cores no arquivo JSON
def salvar_cores():
    with open(ARQUIVO_CORES, "w") as file:
        json.dump(cores_salvas, file)

# Função para carregar as cores salvas do arquivo JSON
def carregar_cores():
    try:
        with open(ARQUIVO_CORES, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Função para excluir uma cor salva
def excluir_cor(cor):
    cores_salvas.remove(cor)
    salvar_cores()
    atualizar_cores_display()

# Função para atualizar a exibição das cores salvas
def atualizar_cores_display():
    for widget in cores_frame.winfo_children():
        widget.destroy()
    
    for cor, nome in cores_salvas:
        cor_hex = f'#{cor[0]:02x}{cor[1]:02x}{cor[2]:02x}'
        frame = tk.Frame(cores_frame, bg="#2c1e16")
        frame.pack(pady=2, fill=tk.X)
        
        cor_display = tk.Label(frame, width=4, height=2, bg=cor_hex, relief="solid")
        cor_display.pack(side=tk.LEFT, padx=5)
        
        label_nome = tk.Label(frame, text=f"{nome} ({cor[0]},{cor[1]},{cor[2]})", fg="white", bg="#2c1e16")
        label_nome.pack(side=tk.LEFT)
        
        btn_excluir = tk.Button(frame, text="X", fg="red", bg="#2c1e16", command=lambda c=cor: excluir_cor((c, nome)))
        btn_excluir.pack(side=tk.RIGHT, padx=5)

# Função para encontrar a cor mais próxima
def encontrar_cor_mais_proxima(cor_lida):
    return min(cores_salvas, key=lambda cor: calcular_distancia(cor[0], cor_lida), default=None)

# Inicializa a lista de cores salvas
cores_salvas = carregar_cores()

# Configuração da janela principal do Tkinter
root = tk.Tk()
root.title("Leitor RGB para Torras de Café")
root.geometry("600x500")
root.configure(bg="#2c1e16")

# Interface gráfica
titulo_label = tk.Label(root, text="Leitor RGB para Torras de Café", font=("Helvetica", 14, "bold"), bg="#2c1e16", fg="#d4a373")
titulo_label.pack(pady=10)

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

cores_frame = tk.Frame(root, bg="#2c1e16")
cores_frame.pack(side=tk.RIGHT, padx=10)

config_button = tk.Button(root, text="Configurações", width=12, height=2, bg="#d4a373", fg="#2c1e16", font=("Helvetica", 10), command=adicionar_cor)
config_button.place(x=490, y=10)

atualizar_cores_display()

root.mainloop()