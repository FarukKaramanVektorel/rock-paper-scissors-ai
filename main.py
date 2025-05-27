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

# Ana pencere
root = tk.Tk()
root.title("Taş-Kağıt-Makas AI Launcher")
root.geometry("900x600")
root.resizable(False, False)

# Grid yapılandırması
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)
root.grid_columnconfigure(0, weight=1)

# Ana içerik çerçevesi
main_frame = tk.Frame(root)
main_frame.grid(row=0, column=0, sticky="nsew")

# Sol çerçeve (tanıtım yazısı)
left_frame = tk.Frame(main_frame, width=600, height=600)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH)
left_frame.pack_propagate(False)

intro_text = (
    "Taş-Kağıt-Makas AI Uygulamasına Hoş Geldiniz!\n\n"
    "Bu programda farklı yapay zeka algoritmaları ile taş-kağıt-makas oynayabilirsiniz.\n"
    "- Basit: Rastgele seçim yapan bilgisayar\n"
    "- Markov Model: Kullanıcı alışkanlıklarını tahmin eden bilgisayar\n"
    "- Q-Learning: Öğrenen bilgisayar\n"
    "- Double AI Q-Learning: İki öğrenen bilgisayarın karşılaşması\n"
    "- Nash Q-Learning: Oyun teorisi tabanlı iki bilgisayar\n\n"
    "Sağdaki menüden bir oyun seçerek başlayabilirsiniz."
)
intro_label = tk.Label(left_frame, text=intro_text, font=("Arial", 13), justify=tk.LEFT, wraplength=580)
intro_label.pack(padx=20, pady=40, anchor="n")

# Sağ çerçeve (butonlar)
right_frame = tk.Frame(main_frame, width=300, height=600)
right_frame.pack(side=tk.RIGHT, fill=tk.Y)
right_frame.pack_propagate(False)

label = tk.Label(right_frame, text="Bir oyunu seç ve başlat", font=("Arial", 14))
label.pack(pady=30)

btn_style = {"font": ("Arial", 12), "width": 25, "anchor": "w", "padx": 10, "pady": 5}

for game_name, script_file in games.items():
    btn = tk.Button(right_frame, text=game_name, command=lambda s=script_file: run_script(s), **btn_style)
    btn.pack(pady=5)

# Footer (alt yazı)
footer_label = tk.Label(root, text="Yöneylem Araştırması Bölümü\nFaruk Karaman",
                        font=("Arial", 10), fg="gray")
footer_label.grid(row=1, column=0, pady=10)


root.mainloop()
