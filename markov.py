import tkinter as tk
import random
from tkinter import PhotoImage
import pygame

# Ses sistemi başlat
pygame.mixer.init()
click_sound = pygame.mixer.Sound("sounds/click.wav")

root = tk.Tk()
root.title("Taş Kağıt Makas")
root.geometry("1000x600")

choices = ["Taş", "Kağıt", "Makas"]
user_score = 0
comp_score = 0
draw_score = 0
round_number = 1
max_rounds = 20
history = []

status_label = tk.Label(root, text="Seçimini yap!", font=("Arial", 14))
status_label.pack(pady=10)

score_label = tk.Label(root, text="Sen: 0 | Bilgisayar: 0 | Beraberlik: 0", font=("Arial", 12))
score_label.pack(pady=5)

round_label = tk.Label(root, text="Tur: 1 / 9", font=("Arial", 12))
round_label.pack(pady=5)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=5)

history_label = tk.Label(root, text="Oyun Geçmişi", font=("Arial", 12, "bold"))
history_label.pack(pady=(10, 0))

history_box = tk.Text(root, height=10, width=50, font=("Arial", 10))
history_box.pack(pady=5)
history_box.config(state=tk.DISABLED)

tas_img = PhotoImage(file="images/rock.png").subsample(3, 3)
kagit_img = PhotoImage(file="images/paper.png").subsample(3, 3)
makas_img = PhotoImage(file="images/scissors.png").subsample(3, 3)
images = {"Taş": tas_img, "Kağıt": kagit_img, "Makas": makas_img}

# --- MARKOV MODEL VERİLERİ ---
user_history = []  # Kullanıcının hamleleri
transition_counts = {
    "Taş": {"Taş": 0, "Kağıt": 0, "Makas": 0},
    "Kağıt": {"Taş": 0, "Kağıt": 0, "Makas": 0},
    "Makas": {"Taş": 0, "Kağıt": 0, "Makas": 0},
}

def update_transition(prev_move, current_move):
    if prev_move is not None:
        transition_counts[prev_move][current_move] += 1

def predict_next_move():
    if not user_history:
        return random.choice(choices)
    last_move = user_history[-1]
    next_moves = transition_counts[last_move]
    max_count = max(next_moves.values())
    if max_count == 0:
        return random.choice(choices)
    likely_moves = [move for move, count in next_moves.items() if count == max_count]
    return random.choice(likely_moves)

def counter_move(move):
    if move == "Taş":
        return "Kağıt"
    elif move == "Kağıt":
        return "Makas"
    else:  # Makas
        return "Taş"

def play(user_choice):
    global user_score, comp_score, draw_score, round_number

    if round_number > max_rounds:
        return

    click_sound.play()

    # Bilgisayarın tahmini ve karşı hamlesi
    predicted_user_move = predict_next_move()
    comp_choice = counter_move(predicted_user_move)

    # Geçiş tablosunu güncelle
    prev_move = user_history[-1] if user_history else None
    update_transition(prev_move, user_choice)

    user_history.append(user_choice)

    # Sonucu hesapla
    result = ""
    if user_choice == comp_choice:
        draw_score += 1
        result = f"Berabere! Bilgisayar da {comp_choice} seçti."
    elif (user_choice == "Taş" and comp_choice == "Makas") or \
         (user_choice == "Kağıt" and comp_choice == "Taş") or \
         (user_choice == "Makas" and comp_choice == "Kağıt"):
        user_score += 1
        result = f"Kazandın! Bilgisayar {comp_choice} seçti."
    else:
        comp_score += 1
        result = f"Kaybettin! Bilgisayar {comp_choice} seçti."

    score_label.config(text=f"Sen: {user_score} | Bilgisayar: {comp_score} | Beraberlik: {draw_score}")
    result_label.config(text=result)

    history_entry = f"{round_number}. Tur - Sen: {user_choice} | Bilgisayar: {comp_choice}\n"
    history.append(history_entry)
    update_history_box()

    if round_number == max_rounds:
        if user_score > comp_score:
            final = "🎉 Oyunu Sen Kazandın!"
        elif user_score < comp_score:
            final = "💻 Bilgisayar Kazandı!"
        else:
            final = "🤝 Oyun Berabere!"
        status_label.config(text=final)
        for button in buttons:
            button.config(state=tk.DISABLED)
    else:
        round_number += 1
        round_label.config(text=f"Tur: {round_number} / {max_rounds}")

def update_history_box():
    history_box.config(state=tk.NORMAL)
    history_box.delete(1.0, tk.END)
    for entry in history:
        history_box.insert(tk.END, entry)
    history_box.config(state=tk.DISABLED)

def reset_game():
    global user_score, comp_score, draw_score, round_number, history, user_history, transition_counts
    user_score = 0
    comp_score = 0
    draw_score = 0
    round_number = 1
    history = []
    user_history = []
    # Geçiş sayacını sıfırla
    transition_counts = {
        "Taş": {"Taş": 0, "Kağıt": 0, "Makas": 0},
        "Kağıt": {"Taş": 0, "Kağıt": 0, "Makas": 0},
        "Makas": {"Taş": 0, "Kağıt": 0, "Makas": 0},
    }
    score_label.config(text="Sen: 0 | Bilgisayar: 0 | Beraberlik: 0")
    round_label.config(text=f"Tur: {round_number} / {max_rounds}")
    status_label.config(text="Seçimini yap!")
    result_label.config(text="")
    update_history_box()
    for button in buttons:
        button.config(state=tk.NORMAL)

button_frame = tk.Frame(root)
button_frame.pack(pady=20)

buttons = []
for idx, choice in enumerate(choices):
    btn = tk.Button(button_frame, image=images[choice], command=lambda c=choice: play(c), width=100, height=100)
    btn.grid(row=0, column=idx, padx=20)
    buttons.append(btn)

refresh_img = PhotoImage(file="images/refresh.png").subsample(1, 1)
reset_button = tk.Button(root, image=refresh_img, command=reset_game)
reset_button.pack(pady=10)
icon = tk.PhotoImage(file="images/hbv.png")
root.iconphoto(False, icon)
root.mainloop()
