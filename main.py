import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd


# ==========================================
# LOGIC LAYER: Object-Oriented Structure
# ==========================================
class GradeEngine:
    # Target totals for each grade (out of 100)
    TARGETS = {
        "O (Outstanding)": 90,
        "A+ (Excellent)": 80,
        "A (Very Good)": 70,
        "B+ (Good)": 60,
        "B (Average)": 50,
        "C+ (Fair)": 45,
        "C (Pass)": 40,
        "F (Fail)": 0
    }

    @staticmethod
    def get_grade_from_score(total):
        if total >= 90:
            return "O"
        elif total >= 80:
            return "A+"
        elif total >= 70:
            return "A"
        elif total >= 60:
            return "B+"
        elif total >= 50:
            return "B"
        elif total >= 45:
            return "C+"
        elif total >= 40:
            return "C"
        else:
            return "F"


# ==========================================
# UI LAYER: Tkinter Dashboard
# ==========================================
class ExamReadyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ExamReady Pro | Goal-Based Analyzer")
        self.root.geometry("950x750")
        self.root.configure(bg="#f1f3f6")

        # Pandas DataFrame
        self.df = pd.DataFrame(columns=['Subject', 'Secured', 'Credits', 'Goal'])

        self.create_header()
        self.create_main_layout()

    def create_header(self):
        header = tk.Frame(self.root, bg="#2d3436", height=100)
        header.pack(fill="x")
        tk.Label(header, text="EXAMREADY: GOAL-BASED PERFORMANCE ANALYZER",
                 fg="#00cec9", bg="#2d3436", font=("Segoe UI", 18, "bold")).pack(pady=25)

    def create_main_layout(self):
        content = tk.Frame(self.root, bg="#f1f3f6")
        content.pack(pady=10, padx=20, fill="both", expand=True)

        # --- LEFT: INPUT PANEL ---
        input_frame = tk.LabelFrame(content, text=" Subject Setup ", font=("Arial", 10, "bold"), bg="white", padx=15,
                                    pady=10)
        input_frame.grid(row=0, column=0, sticky="nsew", padx=10)

        # Fields
        tk.Label(input_frame, text="Subject Name:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_name = tk.Entry(input_frame, width=25)
        self.ent_name.grid(row=0, column=1, pady=5)

        tk.Label(input_frame, text="Midterm (20%):", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_mid = tk.Entry(input_frame, width=25)
        self.ent_mid.grid(row=1, column=1, pady=5)

        tk.Label(input_frame, text="Internals (50%):", bg="white").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_int = tk.Entry(input_frame, width=25)
        self.ent_int.grid(row=2, column=1, pady=5)

        tk.Label(input_frame, text="Credits:", bg="white").grid(row=3, column=0, sticky="w", pady=5)
        self.ent_cred = tk.Entry(input_frame, width=25)
        self.ent_cred.grid(row=3, column=1, pady=5)

        # GOAL SELECTOR
        tk.Label(input_frame, text="Select Your Goal Grade:", bg="white", font=("Arial", 10, "bold"),
                 fg="#e67e22").grid(row=4, column=0, sticky="w", pady=10)
        self.goal_var = tk.StringVar(value="A (Very Good)")
        self.goal_menu = ttk.Combobox(input_frame, textvariable=self.goal_var, state="readonly", width=22)
        self.goal_menu['values'] = list(GradeEngine.TARGETS.keys())
        self.goal_menu.grid(row=4, column=1, pady=10)

        tk.Button(input_frame, text="Add Subject & Goal", command=self.add_data,
                  bg="#0984e3", fg="white", font=("Arial", 10, "bold"), width=25).grid(row=5, column=0, columnspan=2,
                                                                                       pady=15)

        # --- RIGHT: ANALYTICS ---
        self.stats_frame = tk.LabelFrame(content, text=" Quick Stats ", font=("Arial", 10, "bold"), bg="white")
        self.stats_frame.grid(row=0, column=1, sticky="nsew", padx=10)

        self.cgpa_display = tk.Label(self.stats_frame, text="0.00", font=("Arial", 45, "bold"), fg="#6c5ce7",
                                     bg="white")
        self.cgpa_display.pack(pady=20)
        tk.Label(self.stats_frame, text="Estimated SGPA based on Goals", bg="white").pack()

        # --- BOTTOM: TABLE ---
        self.tree = ttk.Treeview(content, columns=("Name", "Secured", "Goal", "Status"), show='headings', height=10)
        self.tree.heading("Name", text="Subject")
        self.tree.heading("Secured", text="Secured (Out of 70)")
        self.tree.heading("Goal", text="Target Grade")
        self.tree.heading("Status", text="Action Status")
        self.tree.grid(row=1, column=0, columnspan=2, pady=20, sticky="nsew")

        # --- FOOTER ---
        tk.Button(self.root, text="GENERATE TARGET-BASED STUDY STRATEGY", command=self.show_strategy,
                  bg="#d63031", fg="white", font=("Arial", 12, "bold"), height=2).pack(fill="x", padx=40, pady=10)

    def add_data(self):
        try:
            name = self.ent_name.get()
            m = float(self.ent_mid.get())
            i = float(self.ent_int.get())
            c = int(self.ent_cred.get())
            goal = self.goal_var.get()

            # Weightage Math: 20% + 50% = 70%
            secured = (m * 0.20) + (i * 0.50)

            # Store in Pandas
            new_entry = {'Subject': name, 'Secured': secured, 'Credits': c, 'Goal': goal}
            self.df = pd.concat([self.df, pd.DataFrame([new_entry])], ignore_index=True)

            # Update Table
            status = "Analysis Pending"
            self.tree.insert("", "end", values=(name, f"{secured:.1f}", goal, status))
            self.update_sgpa()
            self.clear_fields()
        except:
            messagebox.showerror("Error", "Check your inputs (Use numbers for marks/credits)")

    def update_sgpa(self):
        if self.df.empty: return
        # Mock calculation: Average of target grades
        avg_score = self.df['Secured'].mean()
        self.cgpa_display.config(text=f"{(avg_score / 70) * 10:.2f}")

    def show_strategy(self):
        if self.df.empty: return

        report = "STUDY TARGETS: MARKS NEEDED IN END-SEM (OUT OF 100)\n"
        report += "=" * 60 + "\n\n"

        for _, row in self.df.iterrows():
            target_total = GradeEngine.TARGETS[row['Goal']]
            # Formula: (Target - Secured) / 0.30
            needed = (target_total - row['Secured']) / 0.30

            report += f"Subject: {row['Subject']}\n"
            report += f"  - Your Goal: {row['Goal']}\n"

            if needed > 100:
                result = f"CRITICAL: Needs {needed:.1f}/100. Goal too high for current internals."
            elif needed <= 0:
                result = "ACHIEVED: You have already secured this grade!"
            else:
                result = f"TARGET: Score at least {needed:.1f} / 100 in End-Sem."

            report += f"  - {result}\n"
            report += "-" * 40 + "\n"

        # Show in popup
        strategy_win = tk.Toplevel(self.root)
        strategy_win.title("Your Exam Strategy")
        txt = tk.Text(strategy_win, font=("Courier", 10), padx=10, pady=10)
        txt.insert("1.0", report)
        txt.pack(fill="both", expand=True)

    def clear_fields(self):
        self.ent_name.delete(0, tk.END);
        self.ent_mid.delete(0, tk.END)
        self.ent_int.delete(0, tk.END);
        self.ent_cred.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ExamReadyApp(root)
    root.mainloop()
