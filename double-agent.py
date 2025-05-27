import tkinter as tk
import random

# --- Q-learning parametreleri ---
alpha = 0.5
epsilon = 0.1
gamma = 0.9

choices = ["Taş", "Kağıt", "Makas"]
idx_to_choice = {0: "Taş", 1: "Kağıt", 2: "Makas"}

# Q-Tablosu için tüm durumlar
states = [None, 0, 1, 2]  # Rakibin son hamlesi

# Her AI için Q tablosu oluştur
def init_q_table():
    q = {}
    for s in states:
        q[s] = [0.0, 0.0, 0.0]
    return q

Q_agent1 = init_q_table()
Q_agent2 = init_q_table()

def choose_action(Q_table, state):
    if random.random() < epsilon:
        return random.randint(0, 2)
    else:
        q_vals = Q_table[state]
        max_q = max(q_vals)
        best_actions = [i for i, q in enumerate(q_vals) if q == max_q]
        return random.choice(best_actions)

def get_result(move1, move2):
    # 0: berabere, 1: move1 kazandı, -1: move2 kazandı
    if move1 == move2:
        return 0
    elif (move1 == 0 and move2 == 2) or (move1 == 1 and move2 == 0) or (move1 == 2 and move2 == 1):
        return 1
    else:
        return -1

# --- Tkinter GUI ---

root = tk.Tk()
root.title("Double AI Taş-Kağıt-Makas (Q-learning)")

user_score = 0
comp_score = 0
draw_score = 0
round_number = 1
max_rounds = 20

last_move_agent1 = None
last_move_agent2 = None

status_label = tk.Label(root, text="Başlıyor...", font=("Arial", 14))
status_label.pack(pady=10)

score_label = tk.Label(root, text="AI 1: 0 | AI 2: 0 | Beraberlik: 0", font=("Arial", 12))
score_label.pack(pady=5)

round_label = tk.Label(root, text=f"Tur: {round_number} / {max_rounds}", font=("Arial", 12))
round_label.pack(pady=5)

history_label = tk.Label(root, text="Oyun Geçmişi", font=("Arial", 12, "bold"))
history_label.pack(pady=10)

history_box = tk.Text(root, height=15, width=50, font=("Arial", 10))
history_box.pack()
history_box.config(state=tk.DISABLED)

def update_history(text):
    history_box.config(state=tk.NORMAL)
    history_box.insert(tk.END, text + "\n")
    history_box.see(tk.END)
    history_box.config(state=tk.DISABLED)

def q_learning_update(Q_table, state, action, reward, next_state):
    old_value = Q_table[state][action]
    next_max = max(Q_table[next_state])
    new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
    Q_table[state][action] = new_value

def play_round():
    global round_number, user_score, comp_score, draw_score
    global last_move_agent1, last_move_agent2

    if round_number > max_rounds:
        return

    state1 = last_move_agent2  # AI1 durumu: rakibin son hamlesi AI2
    state2 = last_move_agent1  # AI2 durumu: rakibin son hamlesi AI1

    move1 = choose_action(Q_agent1, state1)
    move2 = choose_action(Q_agent2, state2)

    result = get_result(move1, move2)

    # AI1 Q güncelle
    reward1 = 1 if result == 1 else 0 if result == 0 else -1
    q_learning_update(Q_agent1, state1, move1, reward1, move2)

    # AI2 Q güncelle
    reward2 = 1 if result == -1 else 0 if result == 0 else -1
    q_learning_update(Q_agent2, state2, move2, reward2, move1)

    # Skor güncelleme
    if result == 1:
        user_score += 1
        round_result = "AI 1 kazandı!"
    elif result == -1:
        comp_score += 1
        round_result = "AI 2 kazandı!"
    else:
        draw_score += 1
        round_result = "Berabere!"

    update_history(f"{round_number}. Tur: AI1={idx_to_choice[move1]} | AI2={idx_to_choice[move2]} -> {round_result}")
    score_label.config(text=f"AI 1: {user_score} | AI 2: {comp_score} | Beraberlik: {draw_score}")

    round_number += 1
    round_label.config(text=f"Tur: {round_number} / {max_rounds}")

    last_move_agent1 = move1
    last_move_agent2 = move2

    if round_number > max_rounds:
        if user_score > comp_score:
            status_label.config(text="AI 1 Oyunu Kazandı!")
        elif user_score < comp_score:
            status_label.config(text="AI 2 Oyunu Kazandı!")
        else:
            status_label.config(text="Oyun Berabere Bitti!")

def reset_game():
    global user_score, comp_score, draw_score, round_number
    global last_move_agent1, last_move_agent2

    user_score = 0
    comp_score = 0
    draw_score = 0
    round_number = 1
    last_move_agent1 = None
    last_move_agent2 = None

    for s in states:
        Q_agent1[s] = [0.0, 0.0, 0.0]
        Q_agent2[s] = [0.0, 0.0, 0.0]

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
