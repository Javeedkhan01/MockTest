import tkinter as tk
from tkinter import messagebox, ttk
import random
import html
import requests

class MockTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Mock Test Application")
        self.root.geometry("600x400")
        self.setup_ui()
        self.score = 0
        self.question_index = 0
        self.questions = []
        self.correct_answers = []
        self.selected_answers = []
        self.time_per_question = 60  # Time per question in seconds
        self.timer_label = None
        self.timer_id = None
        self.time_left = 0  # Total time left for all questions
        self.total_questions = 0

    def setup_ui(self):
        # Topic Entry
        topic_frame = tk.Frame(self.root)
        topic_frame.pack(pady=10)
        topic_label = tk.Label(topic_frame, text="Select Subject:")
        topic_label.pack(side=tk.LEFT)
        self.topic_choice = ttk.Combobox(topic_frame, values=["SELECT", "JEE", "NEET", "CIVIL SERVICES"])
        self.topic_choice.pack(side=tk.LEFT)
        self.topic_choice.current(0)

        # Number of Questions Entry
        num_questions_frame = tk.Frame(self.root)
        num_questions_frame.pack(pady=10)
        num_questions_label = tk.Label(num_questions_frame, text="Number of Questions:")
        num_questions_label.pack(side=tk.LEFT)
        self.num_questions_entry = ttk.Entry(num_questions_frame, width=5)
        self.num_questions_entry.pack(side=tk.LEFT)
        self.num_questions_entry.insert(0, "5")

        # Start Button
        self.start_button = ttk.Button(self.root, text="Start Mock Test", command=self.start_mock_test)
        self.start_button.pack(pady=10)

        # Question Label
        self.question_label = tk.Label(self.root, text="", wraplength=800, justify=tk.LEFT, font=("", 20))
        self.question_label.pack(pady=10)

        # Options Frame
        self.options_frame = tk.Frame(self.root)
        self.options_frame.pack(pady=10)

        # Navigation Buttons
        self.nav_buttons_frame = tk.Frame(self.root)
        self.nav_buttons_frame.pack(pady=10)
        self.previous_button = ttk.Button(self.nav_buttons_frame, text="Previous", command=self.previous_question)
        self.next_button = ttk.Button(self.nav_buttons_frame, text="Next", command=self.next_question)
        self.submit_button = ttk.Button(self.nav_buttons_frame, text="Submit", command=self.submit_test)

        self.previous_button.pack(side=tk.LEFT)
        self.next_button.pack(side=tk.RIGHT)
        self.submit_button.pack(side=tk.LEFT)

        self.previous_button.pack_forget()
        self.next_button.pack_forget()
        self.submit_button.pack_forget()

    def start_mock_test(self):
        topic = self.topic_choice.get().lower()
        if topic == "select":
            messagebox.showwarning("Input Error", "Please select a topic.")
            return
        
        num_questions = self.num_questions_entry.get()

        if not num_questions.isdigit() or int(num_questions) <= 0:
            messagebox.showwarning("Input Error", "Please enter a valid number of questions.")
            return

        self.fetch_questions(topic, int(num_questions))
        self.previous_button.pack(side=tk.LEFT)
        self.next_button.pack(side=tk.RIGHT)
        self.submit_button.pack_forget()

    def fetch_questions(self, topic, num_questions):
        # Map topics to Open Trivia Database categories (you may need to adjust these mappings)
        topic_mapping = {
            "jee": 17,  # Science & Nature
            "neet": 17,  # Science & Nature
            "civil services": 23  # History
        }

        if topic not in topic_mapping:
            messagebox.showwarning("Input Error", "Invalid topic.")
            return

        category = topic_mapping[topic]

        url = f"https://opentdb.com/api.php?amount={num_questions}&category={category}&type=multiple"
        response = requests.get(url)
        if response.status_code != 200:
            messagebox.showerror("Error", "Failed to fetch questions from the internet.")
            return

        data = response.json()
        if data['response_code'] != 0:
            messagebox.showerror("Error", "No questions available for the selected topic.")
            return

        self.questions = data['results']
        self.total_questions = len(self.questions)
        # Adding a random year to each question for the sake of the example
        for question in self.questions:
            question['year'] = random.randint(2000, 2023)
        self.correct_answers = [html.unescape(q['correct_answer']) for q in self.questions]
        self.display_question()

    def display_question(self):
        if self.question_index < len(self.questions):
            question_data = self.questions[self.question_index]
            question_number = self.question_index + 1
            self.question_label.config(text=f"Q{question_number}: ({question_data['year']}) {html.unescape(question_data['question'])}")

            for widget in self.options_frame.winfo_children():
                widget.destroy()

            correct_answer = html.unescape(question_data['correct_answer'])
            options = [html.unescape(opt) for opt in question_data['incorrect_answers']] + [correct_answer]
            random.shuffle(options)

            self.var_selected_option = tk.StringVar()

            for option in options:
                checkbox = ttk.Radiobutton(self.options_frame, text=option, variable=self.var_selected_option, value=option)
                checkbox.pack(anchor="w")

            self.update_navigation_buttons()

            # Start the timer only when the first question is displayed
            if self.question_index == 0:
                self.time_left = self.total_questions * self.time_per_question
                self.display_timer()

        else:
            self.show_result_window()

    def display_timer(self):
        if self.timer_label:
            self.timer_label.destroy()

        self.timer_label = tk.Label(self.root, text=f"Time Left: {self.format_time(self.time_left)}", font=("", 12))
        self.timer_label.pack(pady=10)

        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        
        self.timer_id = self.root.after(1000, self.update_timer)

    def update_timer(self):
        self.time_left -= 1
        self.timer_label.config(text=f"Time Left: {self.format_time(self.time_left)}")

        if self.time_left <= 0:
            self.save_selected_answer()
            self.submit_test()
        elif self.time_left <= 10:  # Change to red when 10 seconds or less are remaining
            self.timer_label.config(fg="red")
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.timer_id = self.root.after(1000, self.update_timer)

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def update_navigation_buttons(self):
        self.previous_button.config(state=tk.NORMAL if self.question_index > 0 else tk.DISABLED)
        if self.question_index < len(self.questions) - 1:
            self.next_button.pack(side=tk.RIGHT)
            self.submit_button.pack_forget()
        else:
            self.next_button.pack_forget()
            self.submit_button.pack(side=tk.RIGHT)

    def previous_question(self):
        if self.question_index > 0:
            self.question_index -= 1
            self.display_question()

    def next_question(self):
        self.save_selected_answer()
        if self.question_index < len(self.questions) - 1:
            self.question_index += 1
            self.display_question()

    def save_selected_answer(self):
        selected_option = self.var_selected_option.get()
        if len(self.selected_answers) <= self.question_index:
            self.selected_answers.append(selected_option)
        else:
            self.selected_answers[self.question_index] = selected_option

        if selected_option == self.correct_answers[self.question_index]:
            self.score += 1
        else:
            self.score = max(0, self.score)

    def submit_test(self):
        self.save_selected_answer()
        self.show_result_window()

    def show_result_window(self):
        result_window = tk.Toplevel(self.root)
        result_window.title("Test Results")
        result_window.geometry("600x400")

        result_frame = tk.Frame(result_window)
        result_frame.pack(pady=10, fill="both", expand=True)

        canvas = tk.Canvas(result_frame)
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        result_text = f"Your Score: {self.score}/{len(self.questions)}\n\n"
        result_label = tk.Label(scrollable_frame, text=result_text, wraplength=400,font=("", 10), justify=tk.CENTER)
        result_label.pack()

        correct_answers_text = "Correct Answers:\n\n"
        correct_answers_label = tk.Label(scrollable_frame, text=correct_answers_text, wraplength=400,font=("", 10), justify=tk.CENTER)
        correct_answers_label.pack()

        for idx, question in enumerate(self.questions):
            question_text = f"Q{idx + 1}: ({question['year']}) {html.unescape(question['question'])}\n"
            answer_text = f"A: {html.unescape(self.correct_answers[idx])}\n\n"
            question_label = tk.Label(scrollable_frame, text=question_text, wraplength=400,font=("", 10), justify=tk.CENTER)
            answer_label = tk.Label(scrollable_frame, text=answer_text, wraplength=400,font=("", 10), justify=tk.CENTER)

            if idx < len(self.selected_answers):
                if self.correct_answers[idx] == self.selected_answers[idx]:
                    answer_label.config(fg="green")
                else:
                    answer_label.config(fg="red")
            else:
                answer_label.config(fg="black")

            question_label.pack()
            answer_label.pack()

        suggestion_text = f"Suggestion: {self.get_suggestion()}"
        suggestion_label = tk.Label(scrollable_frame, text=suggestion_text, wraplength=400,font=("", 10), justify=tk.CENTER)
        suggestion_label.pack()

        self.reset_mock_test()

    def get_suggestion(self):
        if self.score > 7:
            return "Excellent!"
        elif self.score > 4:
            return "Good job! Keep practicing."
        else:
            return "You need more practice."

    def reset_mock_test(self):
        self.score = 0
        self.question_index = 0
        self.questions = []
        self.correct_answers = []
        self.selected_answers = []
        self.topic_choice.current(0)
        self.num_questions_entry.delete(0, tk.END)
        self.num_questions_entry.insert(0, "5")
        self.question_label.config(text="")
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        self.start_button.config(text="Start Mock Test", command=self.start_mock_test)
        self.previous_button.pack_forget()
        self.next_button.pack_forget()
        self.submit_button.pack_forget()

root = tk.Tk()
image_path = tk.PhotoImage(file=r"C:\Users\Dell\Desktop\TRANSFORMERS\image.png")
bg_image = tk.Label(root, image=image_path)
bg_image.place(x=0, y=0)
app = MockTestApp(root)
root.mainloop()

