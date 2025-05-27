import tkinter as tk
import random
import pygame

# --- Tooltip sınıfı ---
class CreateToolTip(object):
    """
    Tooltip için basit sınıf
    """
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # pencere süsü yok
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# --- Oyun ayarları ---
root = tk.Tk()
root.title("Taş Kağıt Makas - Q-Learning")
root.geometry("1000x650")

pygame.mixer.init()
click_sound = pygame.mixer.Sound("sounds/click.wav")

choices = ["Taş", "Kağıt", "Makas"]
choice_to_idx = {"Taş":0, "Kağıt":1, "Makas":2}
idx_to_choice = {0:"Taş",1:"Kağıt",2:"Makas"}

user_score = 0
comp_score = 0
draw_score = 0
round_number = 1
max_rounds = 20
history = []

# Q-learning parametreleri
alpha = 0.5      # Öğrenme hızı
epsilon = 0.1    # Keşif oranı
gamma = 0.9      # Gelecek ödül indirim faktörü

# Q-Tablosu: durum (kullanıcının son hamlesi 0,1,2 veya None) x aksiyon (bilgisayarın hamlesi 0,1,2)
Q = {}
states = [None, 0, 1, 2]  # None: oyun başı durum
for s in states:
    Q[s] = [0.0, 0.0, 0.0]

last_user_move = None
last_comp_move = None

# --- Arayüz bileşenleri ---

status_label = tk.Label(root, text="Seçimini yap!", font=("Arial", 14))
status_label.pack(pady=10)

score_label = tk.Label(root, text="Sen: 0 | Bilgisayar: 0 | Beraberlik: 0", font=("Arial", 12))
score_label.pack(pady=5)

round_label = tk.Label(root, text=f"Tur: {round_number} / {max_rounds}", font=("Arial", 12))
round_label.pack(pady=5)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=5)

history_label = tk.Label(root, text="Oyun Geçmişi", font=("Arial", 12, "bold"))
history_label.pack(pady=(10,0))

history_box = tk.Text(root, height=10, width=50, font=("Arial", 10))
history_box.pack(pady=5)
history_box.config(state=tk.DISABLED)

# Sliderlar ve tooltip'ler için çerçeve
slider_frame = tk.Frame(root)
slider_frame.pack(pady=10)

alpha_label = tk.Label(slider_frame, text=f"Öğrenme Hızı (alpha): {alpha:.2f}")
alpha_label.grid(row=0, column=0, padx=20)
epsilon_label = tk.Label(slider_frame, text=f"Keşif Oranı (epsilon): {epsilon:.2f}")
epsilon_label.grid(row=0, column=1, padx=20)

def on_alpha_change(val):
    global alpha
    alpha = float(val)

def on_epsilon_change(val):
    global epsilon
    epsilon = float(val)

alpha_slider = tk.Scale(slider_frame, from_=0.0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=lambda v: (on_alpha_change(v), alpha_label.config(text=f"Öğrenme Hızı (alpha): {float(v):.2f}")))
alpha_slider.set(alpha)
alpha_slider.grid(row=1, column=0)
CreateToolTip(alpha_slider, "Öğrenme hızı (alpha): Yeni bilgilerin eski Q değerini ne kadar değiştireceğini belirler. 0-1 arası değer alır.")

epsilon_slider = tk.Scale(slider_frame, from_=0.0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=lambda v: (on_epsilon_change(v), epsilon_label.config(text=f"Keşif Oranı (epsilon): {float(v):.2f}")))
epsilon_slider.set(epsilon)
epsilon_slider.grid(row=1, column=1)
CreateToolTip(epsilon_slider, "Keşif oranı (epsilon): Rastgele hareket yapma olasılığı. 0-1 arası değer alır.")

# Butonlar ve görseller
tas_img = tk.PhotoImage(file="images/rock.png").subsample(3,3)
kagit_img = tk.PhotoImage(file="images/paper.png").subsample(3,3)
makas_img = tk.PhotoImage(file="images/scissors.png").subsample(3,3)
images = {"Taş": tas_img, "Kağıt": kagit_img, "Makas": makas_img}

button_frame = tk.Frame(root)
button_frame.pack(pady=20)

buttons = []
for idx, choice in enumerate(choices):
    btn = tk.Button(button_frame, image=images[choice], width=100, height=100,
                    command=lambda c=choice: play(c))
    btn.grid(row=0, column=idx, padx=20)
    buttons.append(btn)

refresh_img = tk.PhotoImage(file="images/refresh.png").subsample(2,2)
reset_button = tk.Button(root, image=refresh_img, command=lambda: reset_game())
reset_button.pack(pady=10)

# --- Oyun fonksiyonları ---

def choose_action(state):
    # Epsilon-greedy seçimi
    if random.random() < epsilon:
        return random.randint(0,2)  # rastgele
    else:
        q_vals = Q[state]
        max_q = max(q_vals)
        # En yüksek Q değerli hareketleri bul (birden fazla olabilir)
        best_actions = [i for i, q in enumerate(q_vals) if q == max_q]
        return random.choice(best_actions)

def get_result(user_move, comp_move):
    # 0: berabere, 1: kullanıcı kazandı, -1: bilgisayar kazandı
    if user_move == comp_move:
        return 0
    elif (user_move == 0 and comp_move == 2) or (user_move == 1 and comp_move == 0) or (user_move == 2 and comp_move == 1):
        return 1
    else:
        return -1

def play(user_choice):
    global user_score, comp_score, draw_score, round_number, last_user_move, last_comp_move

    click_sound.play()

    if round_number > max_rounds:
        return

    user_move = choice_to_idx[user_choice]
    state = last_user_move

    comp_move = choose_action(state)

    # Sonuç ve ödül
    result = get_result(user_move, comp_move)

    # Q-learning güncellemesi
    old_value = Q[state][comp_move]
    next_max = max(Q[user_move])  # bir sonraki durum için en yüksek Q değeri
    reward = 0
    if result == -1:   # bilgisayar kazandı
        reward = 1
    elif result == 0:  # berabere
        reward = 0
    else:              # kullanıcı kazandı
        reward = -1

    new_value = (1 - alpha)*old_value + alpha*(reward + gamma*next_max)
    Q[state][comp_move] = new_value

    # Skor güncelle
    if result == 0:
        draw_score += 1
        result_text = f"Berabere! Bilgisayar da {idx_to_choice[comp_move]} seçti."
    elif result == 1:
        user_score += 1
        result_text = f"Kazandın! Bilgisayar {idx_to_choice[comp_move]} seçti."
    else:
        comp_score += 1
        result_text = f"Kaybettin! Bilgisayar {idx_to_choice[comp_move]} seçti."

    score_label.config(text=f"Sen: {user_score} | Bilgisayar: {comp_score} | Beraberlik: {draw_score}")
    result_label.config(text=result_text)

    # Oyun geçmişi
    history_entry = f"{round_number}. Tur - Sen: {user_choice} | Bilgisayar: {idx_to_choice[comp_move]}\n"
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

    last_user_move = user_move
    last_comp_move = comp_move

def update_history_box():
    history_box.config(state=tk.NORMAL)
    history_box.delete(1.0, tk.END)
    for entry in history:
        history_box.insert(tk.END, entry)
    history_box.config(state=tk.DISABLED)

def reset_game():
    global user_score, comp_score, draw_score, round_number, history, last_user_move, last_comp_move
    user_score = 0
    comp_score = 0
    draw_score = 0
    round_number = 1
    history = []
    last_user_move = None
    last_comp_move = None

    for button in buttons:
        button.config(state=tk.NORMAL)
    score_label.config(text="Sen: 0 | Bilgisayar: 0 | Beraberlik: 0")
    round_label.config(text=f"Tur: {round_number} / {max_rounds}")
    result_label.config(text="")
    status_label.config(text="Seçimini yap!")
    update_history_box()
icon = tk.PhotoImage(file="images/hbv.png")
root.iconphoto(False, icon)

root.mainloop()
