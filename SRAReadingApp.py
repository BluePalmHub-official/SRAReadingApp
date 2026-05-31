import json
import os
import tkinter as tk
from collections import defaultdict
from datetime import datetime, date
from tkinter import ttk, messagebox

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SRAReadingTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("SRA Reading Laboratory - Student Progress Tracker")
        self.root.geometry("1200x800")

        # SRA Reading levels mapping
        self.sra_levels = {
            'Purple': {'lexile': 'N/A', 'grade': 'Pre-Primary', 'reading_age': 'Pre-Primary'},
            'Tan': {'lexile': 'N/A', 'grade': 'Primary', 'reading_age': 'Primary'},
            'Pink': {'lexile': '200-300', 'grade': '2.2', 'reading_age': '6.4'},
            'Red 1A': {'lexile': '300-350', 'grade': '2.4', 'reading_age': '6.6'},
            'Orange 1B': {'lexile': '350-400', 'grade': '2.6', 'reading_age': '6.9'},
            'Gold 2A': {'lexile': '400-450', 'grade': '2.9', 'reading_age': '7.0'},
            'Brown 2B': {'lexile': '450-500', 'grade': '3.2', 'reading_age': '7.2'},
            'Tan 2C': {'lexile': '500-550', 'grade': '3.4', 'reading_age': '7.4'},
            'Lime 2D': {'lexile': '550-600', 'grade': '3.6', 'reading_age': '7.6'},
            'Green 2E': {'lexile': '600-650', 'grade': '3.8', 'reading_age': '7.8'},
            'Olive 2F': {'lexile': '650-700', 'grade': '4.0', 'reading_age': '8.0'},
            'Aqua 2G': {'lexile': '700-750', 'grade': '4.2', 'reading_age': '8.5'},
            'Blue 2H': {'lexile': '750-800', 'grade': '4.4', 'reading_age': '8.6'},
            'Purple 2I': {'lexile': '800-850', 'grade': '4.6', 'reading_age': '9.5'},
            'Violet 2J': {'lexile': '850-900', 'grade': '4.8', 'reading_age': '10.5'},
            'Rose 3A': {'lexile': '900-950', 'grade': '5.0', 'reading_age': '10.5'},
            'Red 3B': {'lexile': '950-1000', 'grade': '5.5', 'reading_age': '11.5'}
        }

        self.students = {}
        self.load_data()

        self.create_widgets()

    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Student Management Tab
        self.student_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.student_frame, text="Student Management")
        self.create_student_tab()

        # Progress Tracking Tab
        self.progress_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.progress_frame, text="Progress Tracking")
        self.create_progress_tab()

        # Analytics Tab
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="Analytics & Reports")
        self.create_analytics_tab()

    def create_student_tab(self):
        # Student form frame
        form_frame = ttk.LabelFrame(self.student_frame, text="Student Information", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)

        # Form fields
        ttk.Label(form_frame, text="First Name:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.first_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.first_name_var, width=20).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(form_frame, text="Last Name:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.last_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.last_name_var, width=20).grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(form_frame, text="Date of Birth (YYYY-MM-DD):").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.dob_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.dob_var, width=20).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(form_frame, text="Grade Level:").grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.grade_var = tk.StringVar()
        grade_combo = ttk.Combobox(form_frame, textvariable=self.grade_var, width=17)
        grade_combo['values'] = ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
        grade_combo.grid(row=1, column=3, padx=5, pady=2)

        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)

        ttk.Button(button_frame, text="Add Student", command=self.add_student).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Student", command=self.update_student).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Student", command=self.delete_student).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side='left', padx=5)

        # Student list
        list_frame = ttk.LabelFrame(self.student_frame, text="Students List", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Treeview for student list
        columns = ('ID', 'First Name', 'Last Name', 'DOB', 'Grade', 'Age', 'Current Level')
        self.student_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=scrollbar.set)

        self.student_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.student_tree.bind('<<TreeviewSelect>>', self.on_student_select)

        self.refresh_student_list()

    def create_progress_tab(self):
        # Student selection
        select_frame = ttk.LabelFrame(self.progress_frame, text="Select Student", padding=10)
        select_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(select_frame, text="Student:").pack(side='left', padx=5)
        self.selected_student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(select_frame, textvariable=self.selected_student_var, width=30)
        self.student_combo.pack(side='left', padx=5)
        self.student_combo.bind('<<ComboboxSelected>>', self.on_student_change)

        # Progress entry frame
        entry_frame = ttk.LabelFrame(self.progress_frame, text="Add Progress Entry", padding=10)
        entry_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(entry_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.progress_date_var = tk.StringVar(value=str(date.today()))
        ttk.Entry(entry_frame, textvariable=self.progress_date_var, width=15).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(entry_frame, text="SRA Level:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.sra_level_var = tk.StringVar()
        sra_combo = ttk.Combobox(entry_frame, textvariable=self.sra_level_var, width=15)
        sra_combo['values'] = list(self.sra_levels.keys())
        sra_combo.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(entry_frame, text="Comprehension Score (%):").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.comp_score_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.comp_score_var, width=15).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(entry_frame, text="Rate Score (WPM):").grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.rate_score_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.rate_score_var, width=15).grid(row=1, column=3, padx=5, pady=2)

        ttk.Label(entry_frame, text="Notes:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.notes_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.notes_var, width=50).grid(row=2, column=1, columnspan=3, padx=5,
                                                                           pady=2)

        ttk.Button(entry_frame, text="Add Progress Entry", command=self.add_progress_entry).grid(row=3, column=0,
                                                                                                 columnspan=4, pady=10)

        # Progress history
        history_frame = ttk.LabelFrame(self.progress_frame, text="Progress History", padding=10)
        history_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Treeview for progress history
        progress_columns = ('Date', 'SRA Level', 'Grade Equiv.', 'Lexile', 'Comprehension', 'Rate (WPM)', 'Notes')
        self.progress_tree = ttk.Treeview(history_frame, columns=progress_columns, show='headings', height=10)

        for col in progress_columns:
            self.progress_tree.heading(col, text=col)
            self.progress_tree.column(col, width=100)

        progress_scrollbar = ttk.Scrollbar(history_frame, orient='vertical', command=self.progress_tree.yview)
        self.progress_tree.configure(yscrollcommand=progress_scrollbar.set)

        self.progress_tree.pack(side='left', fill='both', expand=True)
        progress_scrollbar.pack(side='right', fill='y')

        self.update_student_combo()

    def create_analytics_tab(self):
        # Control frame
        control_frame = ttk.Frame(self.analytics_frame)
        control_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(control_frame, text="Select Student:").pack(side='left', padx=5)
        self.analytics_student_var = tk.StringVar()
        self.analytics_combo = ttk.Combobox(control_frame, textvariable=self.analytics_student_var, width=30)
        self.analytics_combo.pack(side='left', padx=5)

        ttk.Button(control_frame, text="Generate Report", command=self.generate_analytics).pack(side='left', padx=10)
        ttk.Button(control_frame, text="Class Overview", command=self.show_class_overview).pack(side='left', padx=5)

        # Canvas for matplotlib
        self.analytics_canvas_frame = ttk.Frame(self.analytics_frame)
        self.analytics_canvas_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.update_analytics_combo()

    def calculate_age(self, birth_date):
        try:
            birth = datetime.strptime(birth_date, '%Y-%m-%d').date()
            today = date.today()
            return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except:
            return "Invalid"

    def add_student(self):
        if not all([self.first_name_var.get(), self.last_name_var.get(), self.dob_var.get(), self.grade_var.get()]):
            messagebox.showerror("Error", "Please fill in all fields")
            return

        try:
            datetime.strptime(self.dob_var.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return

        student_id = len(self.students) + 1
        self.students[student_id] = {
            'first_name': self.first_name_var.get(),
            'last_name': self.last_name_var.get(),
            'dob': self.dob_var.get(),
            'grade': self.grade_var.get(),
            'progress': []
        }

        self.save_data()
        self.refresh_student_list()
        self.update_student_combo()
        self.update_analytics_combo()
        self.clear_form()
        messagebox.showinfo("Success", "Student added successfully!")

    def update_student(self):
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a student to update")
            return

        student_id = int(self.student_tree.item(selected[0])['values'][0])

        if not all([self.first_name_var.get(), self.last_name_var.get(), self.dob_var.get(), self.grade_var.get()]):
            messagebox.showerror("Error", "Please fill in all fields")
            return

        try:
            datetime.strptime(self.dob_var.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return

        self.students[student_id].update({
            'first_name': self.first_name_var.get(),
            'last_name': self.last_name_var.get(),
            'dob': self.dob_var.get(),
            'grade': self.grade_var.get()
        })

        self.save_data()
        self.refresh_student_list()
        self.update_student_combo()
        self.update_analytics_combo()
        messagebox.showinfo("Success", "Student updated successfully!")

    def delete_student(self):
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a student to delete")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this student?"):
            student_id = int(self.student_tree.item(selected[0])['values'][0])
            del self.students[student_id]
            self.save_data()
            self.refresh_student_list()
            self.update_student_combo()
            self.update_analytics_combo()
            self.clear_form()
            messagebox.showinfo("Success", "Student deleted successfully!")

    def clear_form(self):
        self.first_name_var.set('')
        self.last_name_var.set('')
        self.dob_var.set('')
        self.grade_var.set('')

    def on_student_select(self, event):
        selected = self.student_tree.selection()
        if selected:
            values = self.student_tree.item(selected[0])['values']
            self.first_name_var.set(values[1])
            self.last_name_var.set(values[2])
            self.dob_var.set(values[3])
            self.grade_var.set(values[4])

    def refresh_student_list(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        for student_id, student in self.students.items():
            age = self.calculate_age(student['dob'])
            current_level = "Not started"
            if student['progress']:
                current_level = student['progress'][-1]['sra_level']

            self.student_tree.insert('', 'end', values=(
                student_id,
                student['first_name'],
                student['last_name'],
                student['dob'],
                student['grade'],
                age,
                current_level
            ))

    def update_student_combo(self):
        student_list = [f"{s['first_name']} {s['last_name']} (ID: {sid})"
                        for sid, s in self.students.items()]
        self.student_combo['values'] = student_list

    def update_analytics_combo(self):
        student_list = [f"{s['first_name']} {s['last_name']} (ID: {sid})"
                        for sid, s in self.students.items()]
        self.analytics_combo['values'] = student_list

    def on_student_change(self, event):
        self.refresh_progress_history()

    def add_progress_entry(self):
        if not self.selected_student_var.get():
            messagebox.showerror("Error", "Please select a student")
            return

        if not all([self.progress_date_var.get(), self.sra_level_var.get(),
                    self.comp_score_var.get(), self.rate_score_var.get()]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return

        try:
            datetime.strptime(self.progress_date_var.get(), '%Y-%m-%d')
            float(self.comp_score_var.get())
            float(self.rate_score_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid date format or scores")
            return

        # Extract student ID
        student_id = int(self.selected_student_var.get().split("ID: ")[1].rstrip(")"))

        progress_entry = {
            'date': self.progress_date_var.get(),
            'sra_level': self.sra_level_var.get(),
            'comprehension_score': float(self.comp_score_var.get()),
            'rate_score': float(self.rate_score_var.get()),
            'notes': self.notes_var.get()
        }

        self.students[student_id]['progress'].append(progress_entry)
        self.save_data()
        self.refresh_progress_history()
        self.refresh_student_list()

        # Clear progress form
        self.progress_date_var.set(str(date.today()))
        self.sra_level_var.set('')
        self.comp_score_var.set('')
        self.rate_score_var.set('')
        self.notes_var.set('')

        messagebox.showinfo("Success", "Progress entry added successfully!")

    def refresh_progress_history(self):
        for item in self.progress_tree.get_children():
            self.progress_tree.delete(item)

        if not self.selected_student_var.get():
            return

        student_id = int(self.selected_student_var.get().split("ID: ")[1].rstrip(")"))

        for entry in self.students[student_id]['progress']:
            sra_info = self.sra_levels.get(entry['sra_level'], {})
            self.progress_tree.insert('', 'end', values=(
                entry['date'],
                entry['sra_level'],
                sra_info.get('grade', 'N/A'),
                sra_info.get('lexile', 'N/A'),
                f"{entry['comprehension_score']}%",
                entry['rate_score'],
                entry['notes']
            ))

    def generate_analytics(self):
        if not self.analytics_student_var.get():
            messagebox.showerror("Error", "Please select a student")
            return

        # Clear previous plots
        for widget in self.analytics_canvas_frame.winfo_children():
            widget.destroy()

        student_id = int(self.analytics_student_var.get().split("ID: ")[1].rstrip(")"))
        student = self.students[student_id]

        if not student['progress']:
            messagebox.showinfo("Info", "No progress data available for this student")
            return

        # Create matplotlib figure
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(f"Progress Report: {student['first_name']} {student['last_name']}", fontsize=16)

        # Extract data
        dates = [datetime.strptime(p['date'], '%Y-%m-%d') for p in student['progress']]
        comp_scores = [p['comprehension_score'] for p in student['progress']]
        rate_scores = [p['rate_score'] for p in student['progress']]
        levels = [p['sra_level'] for p in student['progress']]

        # Plot 1: Comprehension scores over time
        ax1.plot(dates, comp_scores, 'b-o', linewidth=2, markersize=6)
        ax1.set_title('Comprehension Scores Over Time')
        ax1.set_ylabel('Score (%)')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)

        # Plot 2: Reading rate over time
        ax2.plot(dates, rate_scores, 'g-o', linewidth=2, markersize=6)
        ax2.set_title('Reading Rate Over Time')
        ax2.set_ylabel('Words Per Minute')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)

        # Plot 3: SRA Level progression
        level_numbers = list(range(len(levels)))
        ax3.bar(level_numbers, [1] * len(levels),
                color=['red', 'orange', 'yellow', 'green', 'blue', 'purple'][:len(levels)])
        ax3.set_title('SRA Level Progression')
        ax3.set_ylabel('Progress')
        ax3.set_xticks(level_numbers)
        ax3.set_xticklabels([l[:10] + '...' if len(l) > 10 else l for l in levels], rotation=45)

        # Plot 4: Performance summary
        avg_comp = np.mean(comp_scores)
        avg_rate = np.mean(rate_scores)
        latest_comp = comp_scores[-1]
        latest_rate = rate_scores[-1]

        categories = ['Avg\nComprehension', 'Latest\nComprehension', 'Avg\nRate', 'Latest\nRate']
        values = [avg_comp, latest_comp, avg_rate / 10, latest_rate / 10]  # Scale rate for visibility
        colors = ['lightblue', 'blue', 'lightgreen', 'green']

        bars = ax4.bar(categories, values, color=colors)
        ax4.set_title('Performance Summary')
        ax4.set_ylabel('Score / Rate (scaled)')

        # Add value labels on bars
        for bar, val in zip(bars, [avg_comp, latest_comp, avg_rate, latest_rate]):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width() / 2., height + 0.5,
                     f'{val:.1f}', ha='center', va='bottom')

        plt.tight_layout()

        # Add to tkinter
        canvas = FigureCanvasTkAgg(fig, self.analytics_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def show_class_overview(self):
        # Clear previous plots
        for widget in self.analytics_canvas_frame.winfo_children():
            widget.destroy()

        if not self.students:
            messagebox.showinfo("Info", "No students available")
            return

        # Create matplotlib figure
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle("Class Overview Report", fontsize=16)

        # Collect class data
        all_levels = []
        grade_distribution = defaultdict(int)
        avg_comp_by_student = []
        student_names = []

        for student_id, student in self.students.items():
            grade_distribution[student['grade']] += 1

            if student['progress']:
                current_level = student['progress'][-1]['sra_level']
                all_levels.append(current_level)

                comp_scores = [p['comprehension_score'] for p in student['progress']]
                avg_comp_by_student.append(np.mean(comp_scores))
                student_names.append(f"{student['first_name']} {student['last_name']}")

        # Plot 1: Grade distribution
        grades = list(grade_distribution.keys())
        counts = list(grade_distribution.values())
        ax1.pie(counts, labels=grades, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Grade Level Distribution')

        # Plot 2: Current SRA levels
        level_counts = defaultdict(int)
        for level in all_levels:
            level_counts[level] += 1

        if level_counts:
            levels = list(level_counts.keys())
            level_counts_values = list(level_counts.values())
            ax2.bar(range(len(levels)), level_counts_values, color='skyblue')
            ax2.set_title('Current SRA Level Distribution')
            ax2.set_xlabel('SRA Levels')
            ax2.set_ylabel('Number of Students')
            ax2.set_xticks(range(len(levels)))
            ax2.set_xticklabels([l[:8] + '...' if len(l) > 8 else l for l in levels], rotation=45)

        # Plot 3: Average comprehension by student
        if avg_comp_by_student:
            x_pos = range(len(student_names))
            bars = ax3.bar(x_pos, avg_comp_by_student, color='lightcoral')
            ax3.set_title('Average Comprehension by Student')
            ax3.set_xlabel('Students')
            ax3.set_ylabel('Average Score (%)')
            ax3.set_xticks(x_pos)
            ax3.set_xticklabels([name[:10] + '...' if len(name) > 10 else name for name in student_names], rotation=45)

            # Add horizontal line for class average
            class_avg = np.mean(avg_comp_by_student)
            ax3.axhline(y=class_avg, color='red', linestyle='--', label=f'Class Avg: {class_avg:.1f}%')
            ax3.legend()

        # Plot 4: Class statistics
        if avg_comp_by_student:
            stats = {
                'Total Students': len(self.students),
                'Students with Progress': len(avg_comp_by_student),
                'Class Avg Comprehension': np.mean(avg_comp_by_student),
                'Highest Score': max(avg_comp_by_student),
                'Lowest Score': min(avg_comp_by_student)
            }

            ax4.axis('off')
            y_pos = 0.9
            for stat, value in stats.items():
                if isinstance(value, float):
                    text = f"{stat}: {value:.1f}%"
                else:
                    text = f"{stat}: {value}"
                ax4.text(0.1, y_pos, text, fontsize=12, transform=ax4.transAxes)
                y_pos -= 0.15

        plt.tight_layout()

        # Add to tkinter
        canvas = FigureCanvasTkAgg(fig, self.analytics_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def save_data(self):
        with open('sra_students.json', 'w') as f:
            json.dump(self.students, f, indent=2)

    def load_data(self):
        if os.path.exists('sra_students.json'):
            try:
                with open('sra_students.json', 'r') as f:
                    data = json.load(f)
                    # Convert string keys back to integers
                    self.students = {int(k): v for k, v in data.items()}
            except Exception as e:
                print(f"Error loading data: {e}")
                self.students = {}
        else:
            self.students = {}


def main():
    root = tk.Tk()
    app = SRAReadingTracker(root)
    root.mainloop()


if __name__ == "__main__":
    main()

