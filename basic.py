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
max_rounds = 9
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

def play(user_choice):
    click_sound.play()  # Ses efekti burada çalıyor

    global user_score, comp_score, draw_score, round_number

    if round_number > max_rounds:
        return

    comp_choice = random.choice(choices)

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
    global user_score, comp_score, draw_score, round_number, history
    user_score = 0
    comp_score = 0
    draw_score = 0
    round_number = 1
    history = []
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
