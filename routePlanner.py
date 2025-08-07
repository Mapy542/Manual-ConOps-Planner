import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import math
import json


class ArenaPlanner:
    def __init__(self, master):
        self.master = master
        self.master.title("Robot Arena Route Planner")

        # Set arena size
        self.arena_width = simpledialog.askinteger(
            "Arena Width", "Enter arena width (px):", initialvalue=800
        )
        self.arena_height = simpledialog.askinteger(
            "Arena Height", "Enter arena height (px):", initialvalue=600
        )
        self.canvas = tk.Canvas(
            master, width=self.arena_width, height=self.arena_height, bg="white"
        )
        self.canvas.pack()

        # Speed input and active segment multiplier
        self.speed = simpledialog.askfloat(
            "Speed", "Enter robot speed (pixels/sec):", initialvalue=50.0
        )
        self.active_multiplier = simpledialog.askfloat(
            "Active Time Multiplier", "Enter multiplier for active paths:", initialvalue=2.0
        )

        # Data
        self.waypoints = []  # (x, y)
        self.active_indices = set()  # indices of waypoints considered "active"
        self.landmarks = []  # (x, y, radius)
        self.rectangles = []  # (x, y, width, height)
        self.radius = 30  # Default radius for landmarks

        # Bind events
        self.canvas.bind("<Button-1>", self.add_waypoint)
        self.canvas.bind("<Button-3>", self.toggle_active)
        self.master.bind("l", self.add_landmark)
        self.master.bind("r", self.reset)
        self.master.bind("e", self.export_json)
        self.master.bind("i", self.import_json)
        self.master.bind("h", self.show_help)
        self.master.bind("p", self.add_rectangle)

        # Output window
        self.info_label = tk.Label(
            master, text="", justify="left", font=("Courier", 10), anchor="w"
        )
        self.info_label.pack(fill=tk.X)

    def add_waypoint(self, event):
        self.waypoints.append((event.x, event.y))
        self.redraw()

    def toggle_active(self, event):
        # Find the nearest waypoint within 8 pixels
        for i, (x, y) in enumerate(self.waypoints):
            if (event.x - x) ** 2 + (event.y - y) ** 2 < 64:
                if i in self.active_indices:
                    self.active_indices.remove(i)
                else:
                    self.active_indices.add(i)
                break
        self.redraw()

    def add_landmark(self, event=None):
        x, y = (
            self.canvas.winfo_pointerx() - self.canvas.winfo_rootx(),
            self.canvas.winfo_pointery() - self.canvas.winfo_rooty(),
        )
        r = simpledialog.askfloat("Landmark Radius", "Enter radius (px):", initialvalue=self.radius)
        if r:
            self.landmarks.append((x, y, r))
            self.redraw()

    def reset(self, event=None):
        self.waypoints.clear()
        self.active_indices.clear()
        self.landmarks.clear()
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        # Draw landmarks
        for x, y, r in self.landmarks:
            self.canvas.create_oval(x - r, y - r, x + r, y + r, outline="red", width=2)

            # Draw rectangles
        for x, y, w, h in self.rectangles:
            self.canvas.create_rectangle(
                x - w / 2, y - h / 2, x + w / 2, y + h / 2, outline="black", width=2
            )

        # Draw waypoints and lines
        for i, (x, y) in enumerate(self.waypoints):
            color = "red" if i in self.active_indices else "blue"
            self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=color)
            self.canvas.create_text(x + 10, y - 10, text=str(i + 1), fill="black")

            if i > 0:
                x0, y0 = self.waypoints[i - 1]
                active = i - 1 in self.active_indices and i in self.active_indices
                path_color = "red" if active else "black"
                self.canvas.create_line(x0, y0, x, y, fill=path_color, width=2)

        self.update_info()

    def update_info(self):
        total_distance = 0
        total_time = 0
        info_lines = []

        for i in range(1, len(self.waypoints)):
            x0, y0 = self.waypoints[i - 1]
            x1, y1 = self.waypoints[i]
            dist = math.hypot(x1 - x0, y1 - y0)
            is_active = i - 1 in self.active_indices and i in self.active_indices
            multiplier = self.active_multiplier if is_active else 1.0
            time = (dist / self.speed) * multiplier

            total_distance += dist
            total_time += time

            info_lines.append(
                f"Segment {i}: {dist:.1f}px, {time:.2f}s{' [ACTIVE]' if is_active else ''}"
            )

        info_text = (
            f"Total Distance: {total_distance:.1f}px\n"
            f"Total Time: {total_time:.2f}s\n" + "\n".join(info_lines)
        )
        self.info_label.config(text=info_text)

    def export_json(self, event=None):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON Files", "*.json")]
        )
        if not file_path:
            return
        data = {
            "arena_width": self.arena_width,
            "arena_height": self.arena_height,
            "speed": self.speed,
            "active_multiplier": self.active_multiplier,
            "waypoints": self.waypoints,
            "active_indices": list(self.active_indices),
            "landmarks": self.landmarks,
            "rectangles": self.rectangles,
        }
        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Export", f"Exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def import_json(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            self.arena_width = data["arena_width"]
            self.arena_height = data["arena_height"]
            self.speed = data["speed"]
            self.active_multiplier = data.get("active_multiplier", 2.0)
            self.waypoints = [tuple(wp) for wp in data["waypoints"]]
            self.active_indices = set(data.get("active_indices", []))
            self.landmarks = [tuple(lm) for lm in data["landmarks"]]
            self.rectangles = [tuple(r) for r in data.get("rectangles", [])]
            self.canvas.config(width=self.arena_width, height=self.arena_height)
            self.redraw()
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    def show_help(self, event=None):
        help_win = tk.Toplevel(self.master)
        help_win.title("Help & Settings")
        help_win.geometry("400x400")
        help_win.resizable(False, False)

        instructions = """
ROBOT ARENA PLANNER — CONTROLS

Left Click         : Add waypoint
Right Click        : Toggle active waypoint (red)
L key              : Add circular landmark (at mouse)
P key              : Add rectangular landmark (black)
R key              : Reset all data
E key              : Export current arena as JSON
I key              : Import arena from JSON
H key              : Show this help message

Active segments appear red and use a time multiplier.
"""

        # Instructions
        tk.Label(help_win, text=instructions, justify="left", anchor="w").pack(
            padx=10, pady=10, fill=tk.X
        )

        # Speed inputs
        form = tk.Frame(help_win)
        form.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(form, text="Base Speed (px/sec):").grid(row=0, column=0, sticky="w")
        speed_entry = tk.Entry(form)
        speed_entry.insert(0, str(self.speed))
        speed_entry.grid(row=0, column=1)

        tk.Label(form, text="Active Time Multiplier:").grid(row=1, column=0, sticky="w")
        multiplier_entry = tk.Entry(form)
        multiplier_entry.insert(0, str(self.active_multiplier))
        multiplier_entry.grid(row=1, column=1)

        # Save button
        def apply_settings():
            try:
                new_speed = float(speed_entry.get())
                new_multiplier = float(multiplier_entry.get())
                if new_speed <= 0 or new_multiplier <= 0:
                    raise ValueError
                self.speed = new_speed
                self.active_multiplier = new_multiplier
                self.update_info()
                help_win.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter positive numeric values.")

        tk.Button(help_win, text="Apply Settings", command=apply_settings).pack(pady=10)

    def add_rectangle(self, event=None):
        x, y = (
            self.canvas.winfo_pointerx() - self.canvas.winfo_rootx(),
            self.canvas.winfo_pointery() - self.canvas.winfo_rooty(),
        )
        width = simpledialog.askfloat(
            "Rectangle Width", "Enter rectangle width (px):", initialvalue=60
        )
        height = simpledialog.askfloat(
            "Rectangle Height", "Enter rectangle height (px):", initialvalue=40
        )
        if width and height:
            self.rectangles.append((x, y, width, height))
            self.redraw()


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = ArenaPlanner(root)
    root.mainloop()
