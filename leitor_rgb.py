import serial
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
import serial.tools.list_ports

# Função para listar as portas seriais disponíveis no PC
def listar_portas():
    portas = [comport.device for comport in serial.tools.list_ports.comports()]
    return portas

# Função que será executada quando o botão "Ler" for pressionado
def ler_dados():
    porta_serial = combo_porta.get()  # Obtém a porta serial selecionada
    try:
        # Configura a conexão serial
        ser = serial.Serial(porta_serial, 9600)
        time.sleep(2)  # Espera a conexão estabilizar

        # Lê os dados e exibe na interface
        dados = ser.readline().decode('utf-8').strip()
        valores = dados.split(';')

        if len(valores) == 3:  # Verifica se os dados estão no formato RGB
            r, g, b = map(int, valores)  # Converte os valores para inteiros
            resultado_label.config(text=f"R: {r} | G: {g} | B: {b}")
            # Atualiza a cor de fundo com o valor RGB
            cor_canvas.config(bg=f'#{r:02x}{g:02x}{b:02x}')
        else:
            messagebox.showerror("Erro", "Dados no formato incorreto.")
        
        ser.close()  # Fecha a conexão serial

    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível se conectar à porta: {e}")

# Função para iniciar a leitura em uma thread separada
def iniciar_leitura():
    # Desabilita o botão enquanto o processo está em andamento
    ler_button.config(state=tk.DISABLED)
    # Cria uma thread para evitar que a interface congele
    threading.Thread(target=ler_dados).start()
    # Reabilita o botão após 3 segundos
    time.sleep(3)
    ler_button.config(state=tk.NORMAL)

# Configuração da janela principal do Tkinter
root = tk.Tk()
root.title("Leitor RGB para Torras de Café")
root.geometry("450x500")
root.configure(bg="#2c1e16")  # Fundo com cor de café escuro

# Estilo da interface
estilo_padrao = {"font": ("Helvetica", 12), "bg": "#2c1e16", "fg": "#f3e5ab"}
estilo_titulo = {"font": ("Helvetica", 14, "bold"), "bg": "#2c1e16", "fg": "#d4a373"}

# Título do aplicativo
titulo_label = tk.Label(root, text="Leitor RGB para Torras de Café", **estilo_titulo)
titulo_label.pack(pady=10)

# Nome da fazenda
fazenda_label = tk.Label(root, text="Fazenda: Café Herdeiros", font=("Helvetica", 12, "italic"), bg="#2c1e16", fg="#f3e5ab")
fazenda_label.pack(pady=5)

# Texto de instrução
instrucoes_label = tk.Label(root, text="Selecione a porta serial e clique em 'Ler'.", **estilo_padrao)
instrucoes_label.pack(pady=5)

# ComboBox para selecionar a porta serial
combo_porta = ttk.Combobox(root, values=listar_portas(), width=30)
combo_porta.set("Selecione a porta...")
combo_porta.pack(pady=10)

# Botão para iniciar a leitura
ler_button = tk.Button(
    root,
    text="Ler",
    width=20,
    height=2,
    bg="#d4a373",
    fg="#2c1e16",
    font=("Helvetica", 12, "bold"),
    relief="raised",
    bd=3,
    command=iniciar_leitura
)
ler_button.pack(pady=10)

# Label para exibir os resultados RGB
resultado_label = tk.Label(root, text="Os valores RGB aparecerão aqui.", **estilo_padrao)
resultado_label.pack(pady=10)

# Moldura para exibir a cor (branca)
frame_cor = tk.Frame(root, bg="#ffffff", width=200, height=100, relief="raised", bd=2)
frame_cor.pack(pady=20)

# Canvas para exibir a cor RGB dentro da moldura
cor_canvas = tk.Canvas(frame_cor, width=190, height=90, bg="#000000", highlightthickness=0)
cor_canvas.pack(padx=5, pady=5)

# Rótulo com o nome do autor
autor_label = tk.Label(root, text="Autor: Rafael Amorim Faleiros", font=("Helvetica", 8), bg="#2c1e16", fg="#a67c52")
autor_label.pack(side=tk.BOTTOM, pady=5)

# Inicia a interface gráfica
root.mainloop()
