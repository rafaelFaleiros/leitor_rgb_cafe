import tkinter as tk
from tkinter import messagebox, filedialog
import serial
import serial.tools.list_ports
import time
import csv
from tkinter import ttk

# Função para encontrar portas COM disponíveis
def listar_portas():
    portas = [comport.device for comport in serial.tools.list_ports.comports()]
    return portas

# Função para ler a cor e exibir na interface
def ler_cor():
    try:
        porta_com = porta_com_entry.get()
        if porta_com:
            arduino = serial.Serial(porta_com, 9600, timeout=1)
            time.sleep(2)  # Espera a conexão estabilizar
            arduino.write(b"START")
            time.sleep(1)
            
            # Leitura dos dados de cor RGB
            dados = arduino.readline().decode('utf-8').strip()
            if dados:
                r, g, b = map(int, dados.split(","))
                atualizar_interface(r, g, b)
                salvar_historico(r, g, b)
            else:
                messagebox.showerror("Erro", "Não foi possível ler os dados do sensor.")
            arduino.close()
        else:
            messagebox.showwarning("Aviso", "Por favor, selecione uma porta COM válida.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

# Função para atualizar a interface com os valores RGB e a cor
def atualizar_interface(r, g, b):
    # Atualiza os valores de RGB
    label_rgb.config(text=f"RGB: ({r}, {g}, {b})")
    
    # Atualiza a cor de fundo do label com a cor lida
    color = f"#{r:02x}{g:02x}{b:02x}"
    frame_cor.config(bg=color)
    
    # Exibe o nome da cor (aproximação)
    nome_cor = cor_aproximada(r, g, b)
    label_nome_cor.config(text=f"Cor: {nome_cor}")

# Função para determinar o nome aproximado da cor
def cor_aproximada(r, g, b):
    if r > g and r > b:
        return "Vermelho"
    elif g > r and g > b:
        return "Verde"
    elif b > r and b > g:
        return "Azul"
    else:
        return "Cor indefinida"

# Função para salvar o histórico em um arquivo CSV
def salvar_historico(r, g, b):
    try:
        with open('historico_cores.csv', mode='a', newline='') as arquivo:
            writer = csv.writer(arquivo)
            writer.writerow([r, g, b])
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar o histórico: {e}")

# Função para exibir a tela "Sobre"
def exibir_sobre():
    messagebox.showinfo("Sobre", "Ferramenta para leitura de cores de torras de café.\nAutor: Rafael Amorim Faleiros\nCafé Herdeiros")

# Configuração da janela principal
root = tk.Tk()
root.title("Leitor de Cores - Café Herdeiros")
root.geometry("400x400")
root.configure(bg="#2c1e16")

# Estilos
estilo_titulo = {"font": ("Helvetica", 14, "bold"), "bg": "#2c1e16", "fg": "#d4a373"}
estilo_botao = {"font": ("Helvetica", 12), "bg": "#6e4b3d", "fg": "white", "width": 20}

# Título
titulo_label = tk.Label(root, text="Leitor de Cores", **estilo_titulo)
titulo_label.pack(pady=10)

# Menu de portas COM
porta_com_label = tk.Label(root, text="Selecione a porta COM:", bg="#2c1e16", fg="white")
porta_com_label.pack(pady=5)

# Lista de portas COM
porta_coms = listar_portas()
porta_com_var = tk.StringVar(value=porta_coms[0] if porta_coms else "Nenhuma")
porta_com_menu = ttk.Combobox(root, textvariable=porta_com_var, values=porta_coms, width=20)
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

# Botão "Sobre"
sobre_botao = tk.Button(root, text="Sobre", command=exibir_sobre, **estilo_botao)
sobre_botao.pack(pady=10)

# Iniciar a interface
root.mainloop()
