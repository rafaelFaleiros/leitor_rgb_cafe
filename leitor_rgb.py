import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import serial
import serial.tools.list_ports
import time
import json
import os
from tkinter.colorchooser import askcolor

CONFIG_FILE = "config_cores.json"

def carregar_configuracoes():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {}

def salvar_configuracoes(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

def listar_portas():
    return [comport.device for comport in serial.tools.list_ports.comports()]

def ler_cor():
    try:
        porta_com = porta_com_var.get()
        if porta_com:
            arduino = serial.Serial(porta_com, 9600, timeout=1)
            time.sleep(2)
            arduino.write(b"START")
            time.sleep(1)
            dados = arduino.readline().decode("utf-8").strip()
            if dados:
                r, g, b = map(int, dados.split(","))
                atualizar_interface(r, g, b)
            else:
                messagebox.showerror("Erro", "Não foi possível ler os dados do sensor.")
            arduino.close()
        else:
            messagebox.showwarning("Aviso", "Selecione uma porta COM válida.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao ler a cor: {e}")

def atualizar_interface(r, g, b):
    color = f"#{r:02x}{g:02x}{b:02x}"
    frame_cor.config(bg=color)
    label_rgb.config(text=f"RGB: ({r}, {g}, {b})")
    
    nome_cor = cor_mais_proxima(r, g, b)
    label_nome_cor.config(text=f"Cor: {nome_cor}")
    
    atualizar_paleta(r, g, b)

def cor_mais_proxima(r, g, b):
    config = carregar_configuracoes()
    cores_salvas = config.get("cores", [])
    if not cores_salvas:
        return "Nenhuma cor salva"
    melhor_cor = min(cores_salvas, key=lambda cor: (r - cor["r"])**2 + (g - cor["g"])**2 + (b - cor["b"])**2)
    return melhor_cor["nome"]

def atualizar_paleta(r, g, b):
    config = carregar_configuracoes()
    cores_salvas = config.get("cores", [])
    
    for i, cor in enumerate(cores_salvas):
        color = f"#{cor['r']:02x}{cor['g']:02x}{cor['b']:02x}"
        cor_quadros[i].config(bg=color)
        if cor["r"] == r and cor["g"] == g and cor["b"] == b:
            cor_quadros[i].config(borderwidth=3, relief="solid", bg="white")
        else:
            cor_quadros[i].config(borderwidth=0, relief="flat")

def abrir_configuracoes():
    config_window = tk.Toplevel(root)
    config_window.title("Configurações de Cores")
    config_window.geometry("400x300")
    config_window.configure(bg="#2c1e16")
    
    def adicionar_cor():
        cor_rgb, cor_hex = askcolor()
        if cor_rgb:
            nome = simpledialog.askstring("Nome da Cor", "Digite um nome para a cor:")
            if nome:
                config = carregar_configuracoes()
                if "cores" not in config:
                    config["cores"] = []
                config["cores"].append({
                    "nome": nome, 
                    "r": int(cor_rgb[0]), 
                    "g": int(cor_rgb[1]), 
                    "b": int(cor_rgb[2])
                })
                salvar_configuracoes(config)
                atualizar_lista_cores()
                atualizar_paleta_de_cores()
    
    def remover_cor():
        selecionado = lista_cores.selection()
        if selecionado:
            item = lista_cores.item(selecionado)
            nome_cor = item["values"][0]
            config = carregar_configuracoes()
            config["cores"] = [cor for cor in config["cores"] if cor["nome"] != nome_cor]
            salvar_configuracoes(config)
            atualizar_lista_cores()
            atualizar_paleta_de_cores()
    
    frame_lista = tk.Frame(config_window)
    frame_lista.pack(pady=10)
    
    lista_cores = ttk.Treeview(frame_lista, columns=("Nome", "RGB"), show="headings")
    lista_cores.heading("Nome", text="Nome")
    lista_cores.heading("RGB", text="RGB")
    lista_cores.pack()
    
    def atualizar_lista_cores():
        lista_cores.delete(*lista_cores.get_children())
        config = carregar_configuracoes()
        for cor in config.get("cores", []):
            lista_cores.insert("", "end", values=(cor["nome"], f"({cor['r']}, {cor['g']}, {cor['b']})"))
    
    atualizar_lista_cores()
    
    btn_adicionar = tk.Button(config_window, text="Adicionar Cor", command=adicionar_cor, bg="#6e4b3d", fg="white", font=("Helvetica", 12))
    btn_adicionar.pack(pady=5)
    
    btn_remover = tk.Button(config_window, text="Remover Selecionada", command=remover_cor, bg="#6e4b3d", fg="white", font=("Helvetica", 12))
    btn_remover.pack(pady=5)

def exibir_sobre():
    messagebox.showinfo("Sobre", "Ferramenta para leitura de cores de torras de café.\nAutor: Rafael Amorim Faleiros\nCafé Herdeiros")

# Configuração da janela principal
root = tk.Tk()
root.title("Leitor de Cores - Café Herdeiros")
root.geometry("600x500")
root.configure(bg="#2c1e16")

# Estilos
estilo_titulo = {"font": ("Helvetica", 16, "bold"), "bg": "#2c1e16", "fg": "#d4a373"}
estilo_botao = {"font": ("Helvetica", 12), "bg": "#6e4b3d", "fg": "white", "width": 20}

# Título
titulo_label = tk.Label(root, text="Leitor de Cores", **estilo_titulo)
titulo_label.pack(pady=10)

# Menu de portas COM
porta_com_label = tk.Label(root, text="Selecione a porta COM:", bg="#2c1e16", fg="white", font=("Helvetica", 12))
porta_com_label.pack(pady=5)

# Lista de portas COM
porta_com_var = tk.StringVar(value=listar_portas()[0] if listar_portas() else "Nenhuma")
porta_com_menu = ttk.Combobox(root, textvariable=porta_com_var, values=listar_portas(), width=20)
porta_com_menu.pack(pady=10)

# Botão "Ler"
ler_botao = tk.Button(root, text="Ler Cor", command=ler_cor, **estilo_botao)
ler_botao.pack(pady=10)

# Exibição da cor e valores RGB
frame_cor = tk.Frame(root, width=200, height=100, bg="gray")
frame_cor.pack(pady=10)

label_rgb = tk.Label(root, text="RGB: (0, 0, 0)", bg="#2c1e16", fg="white", font=("Helvetica", 12))
label_rgb.pack()

label_nome_cor = tk.Label(root, text="Cor: Indefinida", bg="#2c1e16", fg="white", font=("Helvetica", 12))
label_nome_cor.pack()

# Paleta de Cores
frame_paleta = tk.Frame(root, bg="#2c1e16")
frame_paleta.pack(side="right", padx=10, pady=10)

cor_quadros = []

def atualizar_paleta_de_cores():
    config = carregar_configuracoes()
    cores_salvas = config.get("cores", [])
    
    for widget in frame_paleta.winfo_children():
        widget.destroy()
    
    for cor in cores_salvas:
        cor_hex = f"#{cor['r']:02x}{cor['g']:02x}{cor['b']:02x}"  # Convertendo RGB para Hex
        cor_label = tk.Label(frame_paleta, width=5, height=2, bg=cor_hex)
        cor_label.pack(pady=5, padx=5)
        cor_quadros.append(cor_label)

atualizar_paleta_de_cores()

# Botão "Configurações"
config_botao = tk.Button(root, text="Configurações", command=abrir_configuracoes, **estilo_botao)
config_botao.pack(pady=10)

# Botão "Sobre"
sobre_botao = tk.Button(root, text="Sobre", command=exibir_sobre, **estilo_botao)
sobre_botao.pack(pady=10)

# Iniciar a interface
root.mainloop()
