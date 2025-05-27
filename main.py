import tkinter as tk
import subprocess
import sys
import os

# Çalıştırılacak dosyaların isimleri ve buton etiketleri
games = {
    "Basit Taş-Kağıt-Makas": "basic.py",
    "Markov Model AI": "markov.py",
    "Q-Learning AI": "qlearning.py",
    "Double AI Q-Learning": "double-agent.py",
    "Double AI Nash Q-Learning": "nash-qlearning.py",
}

def run_script(script_name):
    python = sys.executable
    if os.name == "nt":  # Windows
        subprocess.Popen([python, script_name], creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        subprocess.Popen([python, script_name])

root = tk.Tk()
root.title("Taş-Kağıt-Makas AI Launcher")
root.geometry("500x500")
icon = tk.PhotoImage(file="images/hbv.png")
root.iconphoto(False, icon)

label = tk.Label(root, text="Bir oyunu seç ve başlat", font=("Arial", 14))
label.pack(pady=20)

for game_name, script_file in games.items():
    btn = tk.Button(root, text=game_name, font=("Arial", 12),
                    command=lambda s=script_file: run_script(s))
    btn.pack(pady=5, fill=tk.X, padx=20)

# Butonların altına eklenen metin
footer_label = tk.Label(root, text="Yöneylem Araştırması Bölümü\nFaruk Karaman", 
                        font=("Arial", 10), fg="gray")
footer_label.pack(side=tk.BOTTOM, pady=15)

root.mainloop()
