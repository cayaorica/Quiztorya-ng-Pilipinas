import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Import Ttk for advanced styling
import random
import json
import pygame
import os
from PIL import Image, ImageTk  # >>> FIXED MISSING IMPORT <<<

# Initialize pygame mixer for sound effects
pygame.mixer.init()


def load_sound(filename):
    """Load a sound safely. Returns None if file not found."""
    if not pygame.mixer.get_init():
        return None

    if os.path.exists(filename):
        return pygame.mixer.Sound(filename)
    else:
        # print(f"Warning: Sound file '{filename}' not found!")
        return None


# --- NEW FUNCTION FOR MUSIC LOADING ---
def load_music(filename):
    """Load background music safely. Returns True if successful, False otherwise."""
    if not pygame.mixer.get_init():
        return False

    if os.path.exists(filename):
        try:
            # Use pygame.mixer.music module for background tracks
            pygame.mixer.music.load(filename)
            return True
        except pygame.error as e:
            # Handle cases where the file might be corrupt or an unsupported format
            # print(f"Error loading music file {filename}: {e}")
            return False
    else:
        # print(f"Warning: Music file '{filename}' not found!")
        return False


# Load sound effects
correct_sound = load_sound("correct.wav")
incorrect_sound = load_sound("incorrect.wav")
timeup_sound = load_sound("timeup.wav")
finishgame_sound = load_sound("finishgame.wav")

# Load background music (Place your music file, e.g., 'bg_music.mp3', in the same folder)
music_loaded = load_music("dragons.wav")


# You can change "bg_music.mp3" to the name of your actual BGM file.


class QuizGame:
    def __init__(self, master):
        self.master = master
        master.title("Quiztorya ng Pilipinas")

        # Set initial window size (width x height)
        master.geometry("600x450")  # Adjust values as needed

        # Colors
        self.bg_color = "#F5F0E1"
        self.text_color = "#1A150A"
        self.accent_color = "#FFDA63"
        self.border_color = "#CCAC43"
        master.configure(bg=self.bg_color)


        # Intro screen
        self.intro_frame = tk.Frame(master, bg=self.bg_color)
        self.intro_frame.pack(expand=True, fill="both")

        # Logo image
        if os.path.exists("Chick.png"):
            logo_img = Image.open("Chick.png")
            logo_img = logo_img.resize((90, 90), Image.Resampling.LANCZOS)  # Updated for Pillow >=10
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            self.logo_label = tk.Label(self.intro_frame, image=self.logo_photo, bg=self.bg_color)
            self.logo_label.pack(pady=(30, 10))

        #Main Title
        self.title_label = tk.Label(
            self.intro_frame,
            text="QUIZTORYA NG PILIPINAS",
            font=("Garamond", 32, "bold"),
            bg=self.bg_color,
            fg="#8A4B2A"
        )
        self.title_label.pack(pady=(0, 5))


        # Subtitle / description
        self.subtitle_label = tk.Label(
            self.intro_frame,
            text="Test your knowledge about Philippine history!\nAnswer the questions and aim for the high score!",
            font=("Garamond", 16,),
            bg=self.bg_color,
            fg="#8A4B2A",
            justify=tk.CENTER
        )
        self.subtitle_label.pack(pady=(0, 20))  # Space below the subtitle

        self.start_button = tk.Button(
            self.intro_frame,
            text="Start the Quiz",
            font=("Garamond", 15, "bold"),
            bg=self.accent_color,
            fg="black",
            padx=20,
            pady=10,
            command=self.start_quiz
        )

        # --- Ttk Styling Setup ---
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # 1. Base Radiobutton Style
        self.style.configure("Final.TRadiobutton",
                             background=self.bg_color,
                             foreground=self.text_color,
                             font=("Garamond", 13, "bold"),
                             indicatorrelief="flat",
                             borderwidth=0,
                             focusthickness=0,
                             focuscolor=self.bg_color,
                             padding=[0, 0])
        self.style.map("Final.TRadiobutton",
                       background=[('active', self.bg_color)],
                       indicatorforeground=[('selected', '#555555'),
                                            ('!selected', 'white')],
                       indicatorbackground=[('selected', '#555555'),
                                            ('!selected', 'light gray')])

        # 2. Ttk Button Style (Large Buttons)
        self.style.configure("Final.TButton",
                             font=("Garamond", 13, "bold"),
                             foreground="black",
                             background=self.accent_color,
                             padding=(14, 8),
                             width=18)

        self.style.map("Final.TButton",
                       background=[('active', '#EED24E')],
                       foreground=[('disabled', '#AAAAAA')])

        # 3. Ttk Small Menu Button Style
        self.style.configure("Menu.TButton",
                             font=("Garamond", 12, "bold"),
                             foreground="#444444",
                             background="#DDDDDD",
                             padding=(10, 6),
                             width=16,
                             relief="flat")

        self.style.map("Menu.TButton",
                       background=[('active', '#CCCCCC')])
        # -------------------------

        # Variables initialization
        self.music_on = pygame.mixer.music.get_busy() if music_loaded else False
        self.timer_id = None
        self.highscore_file = "highscore.json"
        self.highscore = self.load_highscore()
        self.num_questions_to_ask = 15
        self.questions = self._load_questions_data()  # Load all questions once
        self.all_questions = self.questions.copy()
        self.current_question_index = 0
        self.score = 0
        self.main_frame = None

        # --- NEW FIX: TANGGALIN ANG FOCUS NG MOUSE CLICKS/TAB SA RADIOBUTTONS ---
        master.option_add('*TButton.takeFocus', False)
        master.option_add('*TRadiobutton.takeFocus', False)
        # ----------------------------------------------------------------------

        self.create_intro_screen()  # Start with the Intro Screen

    def _load_questions_data(self):
        # Questions definition (Ito ang orihinal na listahan)
        return [
            {
                "question": "Who is known as the 'Father of the Philippine Revolution'?",
                "options": ["Andres Bonifacio", "Jose Rizal", "Emilio Aguinaldo", "Apolinario Mabini"],
                "answer": "Andres Bonifacio"
            },
            {
                "question": "In what year did the Philippines declare its independence from Spain?",
                "options": ["1896", "1898", "1901", "1946"],
                "answer": "1898"
            },
            {
                "question": "Who was the first president of the Philippines?",
                "options": ["Ramon Magsaysay", "Manuel L. Quezon", "Jose P. Laurel", "Emilio Aguinaldo"],
                "answer": "Emilio Aguinaldo"
            },
            {
                "question": "What was the name of the ship that Jose Rizal sailed on to exile in Dapitan?",
                "options": ["La Solidaridad", "Noli Me Tangere", "El Filibusterismo", "España"],
                "answer": "España"
            },
            {
                "question": "Which battle marked the end of Spanish colonization in the Philippines?",
                "options": ["Battle of Mactan", "Battle of Tirad Pass", "Battle of Manila Bay", "Battle of Leyte Gulf"],
                "answer": "Battle of Manila Bay"
            },
            {
                "question": "Who is considered the national hero of the Philippines?",
                "options": ["Emilio Aguinaldo", "Jose Rizal", "Andres Bonifacio", "Ferdinand Marcos"],
                "answer": "Jose Rizal"
            },
            {
                "question": "Who painted the Spoliarium?",
                "options": ["Juan Luna", "Fernando Amorsolo", "Felix Hidalgo", "Benedicto Cabrera"],
                "answer": "Juan Luna"
            },
            {
                "question": "In what province is the Barasoain Church located?",
                "options": ["Cavite", "Bulacan", "Laguna", "Batangas"],
                "answer": "Bulacan"
            },
            {
                "question": "Which treaty officially ended the Spanish-American War?",
                "options": ["Treaty of Paris", "Treaty of Versailles", "Treaty of Tordesillas", "Treaty of Ghent"],
                "answer": "Treaty of Paris"
            },
            {
                "question": "Who founded the Katipunan?",
                "options": ["Jose Rizal", "Emilio Aguinaldo", "Andres Bonifacio", "Apolinario Mabini"],
                "answer": "Andres Bonifacio"
            },
            {
                "question": "What was the main crop promoted during the American colonial period?",
                "options": ["Coconut", "Rice", "Tobacco", "Sugar"],
                "answer": "Sugar"
            },
            {
                "question": "Who was the 'Brains of the Katipunan'?",
                "options": ["Apolinario Mabini", "Andres Bonifacio", "Emilio Jacinto", "Jose Rizal"],
                "answer": "Emilio Jacinto"
            },
            {
                "question": "Which U.S. President decided to annex the Philippines?",
                "options": ["Warren G. Harding", "Theodore Roosevelt", "Grover Cleveland", "William McKinley"],
                "answer": "William McKinley"
            },
            {
                "question": "What was the name of the revolutionary government established by Emilio Aguinaldo?",
                "options": ["Biak-na-Bato Republic", "Malolos Republic", "First Philippine Republic",
                            "Philippine Commonwealth"],
                "answer": "Biak-na-Bato Republic"
            },
            {
                "question": "Who was the last Spanish Governor-General of the Philippines?",
                "options": ["Basilio Agustin", "Fermin Jaudenes", "Diego de los Rios", "Camilo Polavieja"],
                "answer": "Diego de los Rios"
            },
            {
                "question": "What year did Ferdinand Magellan reach the Philippines?",
                "options": ["1521", "1600", "1492", "1776"],
                "answer": "1521"
            },
            {
                "question": "Who ordered the execution of Jose Rizal?",
                "options": ["Ramon Blanco", "Camilo de Polavieja", "Basilio Augustin", "Fermin Jaudenes"],
                "answer": "Camilo de Polavieja"
            },
            {
                "question": "What was the name of the secret society founded by Jose Rizal?",
                "options": ["Propaganda Movement", "Katipunan", "La Liga Filipina", "Indios Bravos"],
                "answer": "La Liga Filipina"
            },
            {
                "question": "Which province was the site of the Tejeros Convention?",
                "options": ["Cavite", "Laguna", "Batangas", "Bulacan"],
                "answer": "Cavite"
            },
            {
                "question": "Who succeeded Andres Bonifacio as the leader of the Katipunan?",
                "options": ["Emilio Aguinaldo", "Emilio Jacinto", "Mariano Trias", "Pio del Pilar"],
                "answer": "Emilio Aguinaldo"
            },
            {
                "question": "What was the name given to Filipinos of Spanish descent during the colonial era?",
                "options": ["Illustrados", "Peninsulares", "Insulares", "Principalia"],
                "answer": "Insulares"
            },
            {
                "question": "Who was the Filipino priest executed for alleged involvement in the Cavite Mutiny of 1872?",
                "options": ["Jose Burgos", "Mariano Gomez", "Jacinto Zamora", "All of the above"],
                "answer": "All of the above"
            },
            {
                "question": "Which battle saw the death of General Gregorio del Pilar?",
                "options": ["Battle of Tirad Pass", "Battle of Manila Bay", "Battle of Mactan", "Battle of Imus"],
                "answer": "Battle of Tirad Pass"
            },
            {
                "question": "Who was the first Filipino to be appointed Chief Justice of the Supreme Court?",
                "options": ["Jose Abad Santos", "Cayetano Arellano", "Ramon Avanceña", "Manuel Araullo"],
                "answer": "Cayetano Arellano"
            },
            {
                "question": "What was the name of the American policy aimed at 'Americanizing' the Philippines?",
                "options": ["Roosevelt Corollary", "Manifest Destiny", "Open Door Policy", "Benevolent Assimilation"],
                "answer": "Benevolent Assimilation"
            },
            {
                "question": "Who was the leader of the Sakdalista uprising?",
                "options": ["Benigno Ramos", "Pedro Abad Santos", "Crisanto Evangelista", "Jose Maria Sison"],
                "answer": "Benigno Ramos"
            },
            {
                "question": "Which president of the Philippines declared martial law in 1972?",
                "options": ["Ferdinand Marcos", "Diosdado Macapagal", "Carlos P. Garcia", "Corazon Aquino"],
                "answer": "Ferdinand Marcos"
            },
            {
                "question": "Who was the first woman to serve as President of the Philippines?",
                "options": ["Imelda Marcos", "Gloria Macapagal Arroyo", "Corazon Aquino", "Leni Robredo"],
                "answer": "Corazon Aquino"
            },
            {
                "question": "What was the name of the group of Filipino soldiers who resisted Japanese occupation in World War II?",
                "options": ["Hukbalahap", "Katipunan", "Sandatahan", "Kababata"],
                "answer": "Hukbalahap"
            },
            {
                "question": "Who was the Filipino general known for his guerrilla tactics against the Americans?",
                "options": ["Antonio Luna", "Miguel Malvar", "Gregorio del Pilar", "Vicente Lukban"],
                "answer": "Miguel Malvar"
            },
            {
                "question": "What was the name of the economic policy implemented by President Diosdado Macapagal?",
                "options": ["Decontrol Policy", "Import Substitution", "Export-Oriented Industrialization",
                            "Structural Adjustment"],
                "answer": "Decontrol Policy"
            },
            {
                "question": "Who was the longest-serving Chief Justice of the Supreme Court of the Philippines?",
                "options": ["Ramon Avanceña", "Cesar Bengzon", "Roberto Concepcion", "Hilario Davide Jr."],
                "answer": "Cesar Bengzon"
            },
            {
                "question": "Which president of the Philippines is known for his 'Filipino First' policy?",
                "options": ["Elpidio Quirino", "Ramon Magsaysay", "Carlos P. Garcia", "Manuel Roxas"],
                "answer": "Carlos P. Garcia"
            },
            {
                "question": "What was the name of the scandal involving the assassination of Benigno Aquino Jr.?",
                "options": ["Watergate Scandal", "Agrava Commission", "Iran-Contra Affair", "Whitewater Controversy"],
                "answer": "Agrava Commission"
            },
            {
                "question": "Who was the commander of the Japanese forces during the invasion of the Philippines in World War II?",
                "options": ["Tomoyuki Yamashita", "Masaharu Homma", "Isoroku Yamamoto", "Hideki Tojo"],
                "answer": "Masaharu Homma"
            },
            {
                "question": "What was the name of the guerilla resistance movement led by Luis Taruc?",
                "options": ["Sandatahan", "Katipunan", "Hukbalahap", "Kababata"],
                "answer": "Hukbalahap"
            },
            {
                "question": "Which president of the Philippines signed the Comprehensive Agrarian Reform Program (CARP) into law?",
                "options": ["Joseph Estrada", "Ferdinand Marcos", "Fidel V. Ramos", "Corazon Aquino"],
                "answer": "Corazon Aquino"
            },
            {
                "question": "Who was the first Filipino cardinal of the Roman Catholic Church?",
                "options": ["Rufino Santos", "Jaime Sin", "Ricardo Vidal", "Luis Antonio Tagle"],
                "answer": "Rufino Santos"
            },
            {
                "question": "What was the name of the 'People Power' revolution that ousted President Ferdinand Marcos?",
                "options": ["October Revolution", "EDSA Revolution", "Velvet Revolution", "Rose Revolution"],
                "answer": "EDSA Revolution"
            },
            {
                "question": "Who was the Filipino diplomat who served as President of the United Nations General Assembly?",
                "options": ["Narciso G. Reyes", "Salvador P. Lopez", "Carlos P. Romulo", "Letitia Ramos Shahani"],
                "answer": "Carlos P. Romulo"
            },
            {
                "question": "What was the name of the US military base located in Pampanga?",
                "options": ["Subic Naval Base", "Clark Air Base", "Sangley Point", "Camp John Hay"],
                "answer": "Clark Air Base"
            },
            {
                "question": "Who was the first president of the Third Republic of the Philippines?",
                "options": ["Ramon Magsaysay", "Elpidio Quirino", "Manuel Roxas", "Carlos P. Garcia"],
                "answer": "Manuel Roxas"
            },
            {
                "question": "What was the name of the political party founded by Manuel L. Quezon?",
                "options": ["Liberal Party", "Nacionalista Party", "Progressive Party", "People's Reform Party"],
                "answer": "Nacionalista Party"
            },
            {
                "question": "Who was the Filipino general who defended Bataan during World War II?",
                "options": ["Edward P. King", "Jonathan Wainwright", "Douglas MacArthur", "Vicente Lim"],
                "answer": "Vicente Lim"
            }
        ]

    # --- NEW METHOD: Create Intro Screen ---
    def create_intro_screen(self):
        # Stop music if it's playing from a previous session
        self.stop_music()

        # Ensure all existing widgets are cleared before re-creating
        for widget in self.master.winfo_children():
            widget.destroy()

        # Intro screen frame
        self.intro_frame = tk.Frame(self.master, bg=self.bg_color)
        self.intro_frame.pack(expand=True, fill="both")

        # Logo image
        self.logo_photo = None
        if os.path.exists("Chick.png"):
            logo_img = Image.open("Chick.png")
            logo_img = logo_img.resize((90, 90), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            self.logo_label = tk.Label(self.intro_frame, image=self.logo_photo, bg=self.bg_color)
            self.logo_label.pack(pady=(30, 10))

        # Main Title
        tk.Label(
            self.intro_frame,
            text="QUIZTORYA NG PILIPINAS",
            font=("Garamond", 32, "bold"),
            bg=self.bg_color,
            fg="#8A4B2A"
        ).pack(pady=(0, 5))

        # Subtitle / description frame (card-like)
        self.subtitle_frame = tk.Frame(
            self.intro_frame,
            bg="black",
            relief=tk.RAISED,
            borderwidth=3
        )
        self.subtitle_frame.pack(pady=(0, 50), padx=40, fill="x")

        # Subtitle / description
        self.subtitle_text = "Test your knowledge about Philippine history!\nAnswer the questions and aim for the high score!"
        tk.Label(
            self.intro_frame,
            text=self.subtitle_text,
            font=("Garamond", 16,),
            bg=self.bg_color,
            fg="#8A4B2A",
            justify=tk.CENTER
        ).pack(pady=(8, 18))

        # Start Button (Using Ttk Button for consistent style)
        ttk.Button(
            self.intro_frame,
            text="Start the Quiz",
            style="Final.TButton",
            command=self.start_quiz
        ).pack(pady=4)

        # Quit button on Intro screen (Using Ttk Button)
        ttk.Button(
            self.intro_frame,
            text="Quit Game",
            style="Menu.TButton",
            command=self.master.destroy
        ).pack(pady=10)

    # --- END NEW METHOD: Create Intro Screen ---

    # --- MUSIC METHODS ---
    def play_music(self):
        """Starts the background music on an infinite loop."""
        global music_loaded
        if music_loaded:
            self.music_on = True
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)

    def stop_music(self):
        """Stops the background music."""
        global music_loaded
        if music_loaded:
            self.music_on = False
            pygame.mixer.music.stop()

    # Highscore methods
    def load_highscore(self):
        try:
            with open(self.highscore_file, "r") as f:
                return json.load(f)
        except:
            return 0

    def save_highscore(self, score):
        with open(self.highscore_file, "w") as f:
            json.dump(score, f)

    def start_quiz(self):
        self.intro_frame.destroy()

        # Re-sample and shuffle questions for a new game
        self.questions_for_game = random.sample(self.all_questions, self.num_questions_to_ask)
        random.shuffle(self.questions_for_game)
        self.current_question_index = 0
        self.score = 0
        self.highscore = self.load_highscore()

        # Main frame
        self.main_frame = tk.Frame(self.master, bg=self.bg_color)
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Header Frame (Para sa Timer, Scores, at MENU)
        header_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 15))

        # -----------------------------------------------------------------
        # --- MENU BUTTON ---
        self.menu_button = ttk.Button(
            header_frame,
            text="☰ Menu",
            command=self.show_menu,  # Calls the method below
            style="Menu.TButton"
        )
        self.menu_button.pack(side=tk.LEFT, padx=(0, 15))
        # -----------------------------------------------------------------

        # Timer (Pack sa LEFT, after Menu)
        self.time_left = 20
        self.timer_label = tk.Label(
            header_frame,
            text=f"Time Left: {self.time_left}",
            font=("Garamond", 15, "bold"),
            bg=self.bg_color,
            fg="#B22222"
        )
        self.timer_label.pack(side=tk.LEFT, padx=(10, 0))

        # Highscore label (Pack sa RIGHT)
        self.highscore_label = tk.Label(
            header_frame,
            text=f"High Score: {self.highscore}",
            font=("Garamond", 12, "bold"),
            fg=self.text_color,
            bg=self.accent_color,
            padx=6,
            pady=3,
            relief=tk.RAISED,
            borderwidth=2,
            highlightbackground=self.border_color,
            highlightcolor=self.border_color
        )
        self.highscore_label.pack(side=tk.RIGHT, padx=5)

        # Score label (Pack sa RIGHT)
        self.score_label = tk.Label(
            header_frame,
            text=f"Score: {self.score}",
            font=("Garamond", 12, "bold"),
            fg=self.text_color,
            bg=self.accent_color,
            padx=6,
            pady=3,
            relief=tk.RAISED,
            borderwidth=2,
            highlightbackground=self.border_color,
            highlightcolor=self.border_color
        )
        self.score_label.pack(side=tk.RIGHT, padx=5)

        self.timer_id = None
        self.start_timer()

        # Question Frame
        self.question_frame = tk.Frame(self.main_frame, bg=self.bg_color, height=120)
        self.question_frame.pack(fill="x")
        self.question_frame.pack_propagate(False)
        self.question_label = tk.Label(
            self.question_frame,
            text="",
            wraplength=540,
            font=("Garamond", 15, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
            justify="left",
            anchor="w",
            height=4
        )

        self.question_label.pack(side=tk.LEFT, pady=(3, 10), anchor=tk.W)

        # Options frame
        self.options_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.options_frame.pack(fill="x", pady=(0, 5))
        self.options_frame.pack_propagate(False)
        # --- Configure Grid for Two Columns ---
        self.options_frame.grid_columnconfigure(0, weight=1, minsize=280)
        self.options_frame.grid_columnconfigure(1, weight=1, minsize=280)

        # Options (Ttk Radio Buttons)
        self.radio_var = tk.StringVar()
        self.radio_buttons = []
        positions = [(0, 0), (1, 0), (0, 1), (1, 1)]

        for i in range(4):
            option_container = tk.Frame(self.options_frame, bg=self.bg_color)
            row, col = positions[i]
            option_container.grid(row=row, column=col, sticky="w", padx=10, pady=10)

            rb = ttk.Radiobutton(
                option_container,
                variable=self.radio_var,
                value="",
                style="Final.TRadiobutton",
                command=self.check_answer
            )
            rb.pack(side="left")

            label = tk.Label(
                option_container,
                text="",  # Will set text in load_question()
                wraplength=260,
                justify="left",
                bg=self.bg_color,
                font=("Garamond", 13, "bold")
            )
            label.pack(side="left", padx=5)

            # Make the label clickable
            def select_option(event, val=rb):
                self.radio_var.set(val["value"])
                self.check_answer()  # Optional: immediately check answer

            label.bind("<Button-1>", select_option)

            # Keep track of both
            self.radio_buttons.append((rb, label))

        # Next button frame
        self.bottom_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.bottom_frame.pack(pady=4)

        # Next Button (Using Ttk Button)
        self.next_button = ttk.Button(
            self.bottom_frame,
            text="Next Question",
            command=self.next_question,
            state=tk.DISABLED,
            style="Final.TButton"
        )
        self.next_button.pack()

        # 1. Feedback Label Container (Stops horizontal stretching)
        # Create this frame to be the parent of the feedback label.
        self.feedback_container = tk.Frame(self.main_frame, bg=self.bg_color)
        self.feedback_container.pack(pady=4)  # Centered pack for the container

        # Feedback Label
        self.feedback_label = tk.Label(
            self.feedback_container,
            text="",
            font=("Garamond", 12, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            padx=10,
            pady=4,
            relief=tk.RAISED,
            borderwidth=2,
        )
        self.feedback_label.pack()
        self.feedback_label.pack_forget()

        self.load_question()
        self.play_music()

    # -------------------------------------------------------------
    # --- MENU POPUP FUNCTIONS (CORRECTLY INDENTED AS METHODS) ---
    # -------------------------------------------------------------
    def show_menu(self):
        # 1. Cancel Timer and Disable UI while Menu is open
        if self.timer_id:
            self.master.after_cancel(self.timer_id)

        # Temporarily disable controls
        self.menu_button.config(state=tk.DISABLED)
        for rb, label in self.radio_buttons:
            rb.config(state=tk.DISABLED)

        self.next_button.config(state=tk.DISABLED)

        # 2. Create the Toplevel window (The menu popup)
        self.menu_window = tk.Toplevel(self.master)
        self.menu_window.title("Game Menu")
        self.menu_window.configure(bg=self.bg_color)

        # Center the Toplevel window over the main window
        main_x = self.master.winfo_x()
        main_y = self.master.winfo_y()
        main_width = self.master.winfo_width()
        main_height = self.master.winfo_height()

        menu_width = 300
        # Inadjust ang taas dahil tinanggal ang isang button
        menu_height = 160
        center_x = main_x + (main_width // 2) - (menu_width // 2)
        center_y = main_y + (main_height // 2) - (menu_height // 2)

        self.menu_window.geometry(f"{menu_width}x{menu_height}+{center_x}+{center_y}")
        self.menu_window.transient(self.master)
        self.menu_window.grab_set()

        tk.Label(self.menu_window, text="— Game Menu —", font=("Garamond", 18, "bold"), bg=self.bg_color,
                 fg=self.text_color).pack(pady=(15, 10))

        # 3. Music Toggle Button
        self.music_toggle_button = ttk.Button(
            self.menu_window,
            text=f"Music: {'ON' if self.music_on else 'OFF'}",
            command=self.toggle_music,
            style="Menu.TButton"
        )
        self.music_toggle_button.pack(fill="x", padx=30, pady=2)

        # >>> TINANGGAL ANG INSTRUCTIONS BUTTON DITO <<<

        # 4. End Game Button (RETURNS TO INTRO SCREEN)
        ttk.Button(
            self.menu_window,
            text="Back Home",
            command=self.end_quiz_early,
            style="Menu.TButton"
        ).pack(fill="x", padx=30, pady=8)



        self.menu_window.protocol("WM_DELETE_WINDOW", self.close_menu)

    def toggle_music(self):
        if self.music_on:
            self.stop_music()
            self.music_toggle_button.config(text="Music: OFF")
        else:
            self.play_music()
            self.music_toggle_button.config(text="Music: ON")

    def show_instructions_popup(self):
        messagebox.showinfo("Instructions", self.subtitle_text.replace('\n', ' '))

    def close_menu(self):
        self.menu_window.grab_release()
        self.menu_window.destroy()

        # 8. Resume Timer and Enable UI controls
        self.menu_button.config(state=tk.NORMAL)
        # Resume timer/game state if the question hasn't been answered
        if not self.radio_var.get():
            self.start_timer()
            for rb, label in self.radio_buttons:
                rb.config(state=tk.NORMAL)

        else:
            # If question was answered, just enable the Next button
            self.next_button.config(state=tk.NORMAL)

    def end_quiz_early(self):
        confirm = messagebox.askyesno("Confirm End Game",
                                      "Are you sure you want to end the current game and return to the start screen? Your current score will not be saved.")
        if confirm:
            self.close_menu()
            self.stop_music()

            if self.timer_id:
                self.master.after_cancel(self.timer_id)

            # Destroy the quiz screen (self.main_frame)
            if self.main_frame:
                self.main_frame.destroy()

            # Recreate the Intro Screen
            self.create_intro_screen()

    # -------------------------------------------------------------
    # --- END MENU POPUP FUNCTIONS ---
    # -------------------------------------------------------------

        # Timer functions
    def start_timer(self):
            if self.timer_id:
                self.master.after_cancel(self.timer_id)
            self.time_left = 20
            self.timer_label.config(text=f"Time Left: {self.time_left}")
            self.timer_id = self.master.after(1000, self.update_timer)

    def update_timer(self):
            # 🚨 Safety Check: Check if the master window (root) still exists
            if not self.master.winfo_exists():
                return

            if self.time_left > 0:
                self.time_left -= 1
                # I-check kung buhay pa ang timer label
                if self.timer_label.winfo_exists():
                    self.timer_label.config(text=f"Time Left: {self.time_left}")
                    self.timer_id = self.master.after(1000, self.update_timer)
            else:
                self.time_up()

    def time_up(self):
            # 🚨 Safety Check: Check if the master window (root) still exists
            if not self.master.winfo_exists():
                return

            self.answered = True

            if timeup_sound and pygame.mixer.get_init(): timeup_sound.play()
            correct = self.questions_for_game[self.current_question_index]["answer"]

            # Check if labels/buttons exist before configuring
            if self.feedback_label.winfo_exists():
                self.feedback_label.config(text=f"Time's up! Correct: {correct}", fg="red")
                self.feedback_label.pack(pady=5)

            for rb, label in self.radio_buttons:
                rb.config(state=tk.DISABLED)
                label.config(fg="gray")

            self.next_button.config(state=tk.NORMAL)
            self.menu_button.config(state=tk.NORMAL)  # Re-enable menu

            # Prevent further clicks
            self.answered = True
    def load_question(self):
        if not self.master.winfo_exists():
            return

        self.feedback_label.pack_forget()
        self.answered = False  # Reset for new question

        if self.current_question_index < len(self.questions_for_game):
            q = self.questions_for_game[self.current_question_index]
            self.question_label.config(text=f"{self.current_question_index + 1}. {q['question']}")

            for i in range(4):
                rb, label = self.radio_buttons[i]
                rb.config(value=q["options"][i], state=tk.NORMAL)
                label.config(text=q["options"][i], fg=self.text_color)

                # Update label click to respect answered status
                def select_option(event, val=rb):
                    if self.answered:  # <-- Prevent clicks after answer/time up
                        return
                    self.radio_var.set(val["value"])
                    self.check_answer()

                label.bind("<Button-1>", select_option)

            self.radio_var.set("")
            self.next_button.config(state=tk.DISABLED)
            self.menu_button.config(state=tk.NORMAL)

            if self.current_question_index == len(self.questions_for_game) - 1:
                self.next_button.config(text="Show Result")
            else:
                self.next_button.config(text="Next Question")

            self.start_timer()
        else:
            self.show_result()

    def check_answer(self):
        # 🚨 Safety Check: Tiyakin na buhay pa ang master
        if not self.master.winfo_exists():
            return


        self.answered = True  # Mark current question as answered

        # 1. Stop the timer immediately
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
            self.timer_id = None

        # 2. Get current question and user selection
        current_q = self.questions_for_game[self.current_question_index]
        user_answer = self.radio_var.get()
        correct_answer = current_q["answer"]

        # 3. Disable all radio buttons to prevent further changes
        for rb, label in self.radio_buttons:
            rb.config(state=tk.DISABLED)
            label.config(fg="gray")  # <-- Makes the text appear faded

        # 4. Check Answer, Update Score, Play Sound
        is_correct = (user_answer == correct_answer)
        if is_correct:
            if correct_sound and pygame.mixer.get_init(): correct_sound.play()
            self.score += 1
            feedback_text = "Correct!"
            feedback_color = "#38761D"
        else:
            if incorrect_sound and pygame.mixer.get_init(): incorrect_sound.play()
            feedback_text = f"Incorrect. The correct answer is: {correct_answer}"
            feedback_color = "red"

        # Update score
        self.score_label.config(text=f"Score: {self.score}")

        # Show feedback
        if self.feedback_label.winfo_exists():
            self.feedback_label.config(text=feedback_text, fg=feedback_color, bg=self.accent_color)
            self.feedback_label.pack(pady=6)

        # Enable Next button
        self.next_button.config(state=tk.NORMAL)
        self.menu_button.config(state=tk.NORMAL)

    def next_question(self):
        # 🚨 Safety Check: Tiyakin na buhay pa ang master
        if not self.master.winfo_exists():
            return

        self.current_question_index += 1

        if self.current_question_index < len(self.questions_for_game):
            # Load the next question and restart the timer
            self.load_question()
            self.start_timer()
        else:
            # End of quiz
            self.show_result()

    def show_result(self):
        # 🚨 Safety Check: Tiyakin na buhay pa ang master
        if not self.master.winfo_exists():
            return

        if finishgame_sound and pygame.mixer.get_init(): finishgame_sound.play()
        self.stop_music()  # Stop background music

        # 1. Update High Score if necessary
        new_highscore = False
        if self.score > self.highscore:
            self.save_highscore(self.score)
            self.highscore = self.score
            new_highscore = True

        # 2. Destroy the main quiz frame
        if self.main_frame:
            self.main_frame.destroy()

        # 3. Create Result Screen Frame
        result_frame = tk.Frame(self.master, bg=self.bg_color)
        result_frame.pack(expand=True, fill="both")

        # Title
        tk.Label(result_frame, text="QUIZ RESULTS", font=("Garamond", 30, "bold"), bg=self.bg_color,
                 fg="#8A4B2A").pack(pady=(50, 20))

        # Score Summary
        summary = f"Your Final Score: {self.score} points"
        if new_highscore:
            summary += "\n🎉 NEW HIGH SCORE! 🎉"

        tk.Label(result_frame, text=summary, font=("Garamond", 18, "bold"), bg=self.bg_color,
                 fg=self.text_color).pack(pady=10)

        # High Score Label
        tk.Label(result_frame, text=f"Current High Score: {self.highscore}", font=("Garamond", 15), bg=self.bg_color,
                 fg="#B22222").pack(pady=5)

        # Button to return to the start screen
        ttk.Button(
            result_frame,
            text="Back Home",
            style="Final.TButton",
            command=self.create_intro_screen
        ).pack(pady=30)

        # Quit Button
        ttk.Button(
            result_frame,
            text="Quit Game",
            style="Menu.TButton",
            command=self.master.destroy
        ).pack(pady=5)
# Run the application
root = tk.Tk()
quiz_game = QuizGame(root)
root.mainloop()