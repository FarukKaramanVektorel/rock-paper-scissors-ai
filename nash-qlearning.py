import tkinter as tk
import numpy as np
import random
import nashpy as nash

# Parametreler
alpha = 0.5  # öğrenme hızı
gamma = 0.9  # indirim faktörü
epsilon = 0.1  # keşif oranı (karışık strateji yerine bazen rasgele)

max_rounds = 20
round_number = 1

# Taş=0, Kağıt=1, Makas=2
choices = ["Taş", "Kağıt", "Makas"]

# Q matrisi: 3x3, AI1 satır (AI1 hareketi), AI2 sütun (AI2 hareketi)
Q1 = np.zeros((3, 3))
Q2 = np.zeros((3, 3))

# Oyunun sonuç matrisi (AI1 kazanırsa 1, kaybederse -1, berabere 0)
# satır: AI1 hareketi, sütun: AI2 hareketi
payoff_matrix = np.array([
    [0, -1, 1],   # Taş vs (Taş, Kağıt, Makas)
    [1, 0, -1],   # Kağıt vs (Taş, Kağıt, Makas)
    [-1, 1, 0]    # Makas vs (Taş, Kağıt, Makas)
])

# Nash denge stratejilerini bulma fonksiyonu
def compute_nash_strategy(Q1, Q2):
    game = nash.Game(Q1, Q2)
    equilibria = list(game.support_enumeration())
    if len(equilibria) == 0:
        # Nash yoksa eşit dağılım yapalım
        return np.array([1/3]*3), np.array([1/3]*3)
    # İlk Nash dengesi alıyoruz (çoğunlukla 1 tane olur)
    sigma_r, sigma_c = equilibria[0]
    return sigma_r, sigma_c

def select_action(strategy):
    # Verilen karışık stratejiye göre hamle seç
    return np.random.choice([0,1,2], p=strategy)

def update_Q(Q, action_self, action_opponent, reward):
    old_value = Q[action_self, action_opponent]
    # Basit Q-learning güncelleme
    Q[action_self, action_opponent] = (1 - alpha) * old_value + alpha * (reward + gamma * old_value)

# Tkinter GUI kurulumu
root = tk.Tk()
root.title("Double AI Nash Q-learning Taş-Kağıt-Makas")

status_label = tk.Label(root, text="Başlıyor...", font=("Arial", 14))
status_label.pack(pady=10)

score_label = tk.Label(root, text="AI 1: 0 | AI 2: 0 | Beraberlik: 0", font=("Arial", 12))
score_label.pack(pady=5)

round_label = tk.Label(root, text=f"Tur: {round_number} / {max_rounds}", font=("Arial", 12))
round_label.pack(pady=5)

history_box = tk.Text(root, height=15, width=50, font=("Arial", 10))
history_box.pack()
history_box.config(state=tk.DISABLED)

score_ai1 = 0
score_ai2 = 0
draw_score = 0

def update_history(text):
    history_box.config(state=tk.NORMAL)
    history_box.insert(tk.END, text + "\n")
    history_box.see(tk.END)
    history_box.config(state=tk.DISABLED)

def play_round():
    global round_number, score_ai1, score_ai2, draw_score, Q1, Q2

    if round_number > max_rounds:
        return

    # Nash denge stratejilerini hesapla
    strat1, strat2 = compute_nash_strategy(Q1, Q2)

    # epsilon ile rastgele seçme şansı
    if random.random() < epsilon:
        action1 = random.randint(0,2)
    else:
        action1 = select_action(strat1)

    if random.random() < epsilon:
        action2 = random.randint(0,2)
    else:
        action2 = select_action(strat2)

    # Sonuç
    result = payoff_matrix[action1, action2]

    if result == 1:
        score_ai1 += 1
        result_text = "AI 1 kazandı!"
    elif result == -1:
        score_ai2 += 1
        result_text = "AI 2 kazandı!"
    else:
        draw_score += 1
        result_text = "Berabere!"

    update_history(f"{round_number}. Tur: AI1={choices[action1]} | AI2={choices[action2]} -> {result_text}")
    score_label.config(text=f"AI 1: {score_ai1} | AI 2: {score_ai2} | Beraberlik: {draw_score}")

    # Q tablolarını güncelle
    update_Q(Q1, action1, action2, result)
    update_Q(Q2, action2, action1, -result)

    round_number += 1
    round_label.config(text=f"Tur: {round_number} / {max_rounds}")

    if round_number > max_rounds:
        if score_ai1 > score_ai2:
            status_label.config(text="AI 1 Oyunu Kazandı!")
        elif score_ai1 < score_ai2:
            status_label.config(text="AI 2 Oyunu Kazandı!")
        else:
            status_label.config(text="Oyun Berabere Bitti!")

def reset_game():
    global score_ai1, score_ai2, draw_score, round_number, Q1, Q2
    score_ai1 = 0
    score_ai2 = 0
    draw_score = 0
    round_number = 1
    Q1 = np.zeros((3,3))
    Q2 = np.zeros((3,3))
    status_label.config(text="Başlıyor...")
    score_label.config(text="AI 1: 0 | AI 2: 0 | Beraberlik: 0")
    round_label.config(text=f"Tur: {round_number} / {max_rounds}")
    history_box.config(state=tk.NORMAL)
    history_box.delete(1.0, tk.END)
    history_box.config(state=tk.DISABLED)

button_frame = tk.Frame(root)
button_frame.pack(pady=20)

play_button = tk.Button(button_frame, text="Tur Oyna", font=("Arial", 14), command=play_round)
play_button.grid(row=0, column=0, padx=10)

reset_button = tk.Button(button_frame, text="Yeniden Başlat", font=("Arial", 14), command=reset_game)
reset_button.grid(row=0, column=1, padx=10)
icon = tk.PhotoImage(file="images/hbv.png")
root.iconphoto(False, icon)
root.mainloop()
