import tkinter as tk
import math
import time
import threading
import platform

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


class InteractiveSpiderClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Spider Clock")
        self.root.geometry("650x550")
        self.root.configure(bg="#ffffff")
        self.root.resizable(False, False)

        # Tick sound state
        self.sound_enabled = True
        self.last_tick_second = -1

        # Main Canvas
        self.canvas = tk.Canvas(
            root, width=650, height=550, bg="#ffffff", highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.cx = 325  # Center X
        self.cy = 275  # Center Y
        self.radius = 205

        self.update_clock()

    def play_tick_sound(self, is_tock=False):
        """Har second par tick-tock aavaj background thread mein chalata hai (UI freeze na ho)"""
        if not self.sound_enabled:
            return

        def _sound():
            freq = 1050 if not is_tock else 820
            duration = 25  # 25ms crisp tick
            if HAS_WINSOUND and platform.system() == "Windows":
                try:
                    winsound.Beep(freq, duration)
                except Exception:
                    pass
            else:
                try:
                    self.root.bell()
                except Exception:
                    pass

        threading.Thread(target=_sound, daemon=True).start()

    def toggle_sound(self, event=None):
        self.sound_enabled = not self.sound_enabled

    def draw_sound_toggle(self):
        """Top-right corner mein clickable Sound ON/OFF badge"""
        label = "🔊 Tick: ON" if self.sound_enabled else "🔇 Tick: OFF"
        bg_col = "#f3c6d3" if self.sound_enabled else "#eeeeee"
        fg_col = "#222222" if self.sound_enabled else "#777777"

        btn_id = self.canvas.create_rectangle(
            525, 16, 632, 44, fill=bg_col, outline="#d8a3b4", width=1.2
        )
        txt_id = self.canvas.create_text(
            578, 30, text=label, font=("Segoe UI", 9, "bold"), fill=fg_col
        )

        self.canvas.tag_bind(btn_id, "<Button-1>", self.toggle_sound)
        self.canvas.tag_bind(txt_id, "<Button-1>", self.toggle_sound)

    def draw_mandala_cog(self, cx, cy, outer_r, inner_r, petals, color, angle_offset=0):
        """Background ke faint pink floral/cog gears draw karne ke liye"""
        points = []
        steps = petals * 8
        for i in range(steps):
            theta = (2 * math.pi * i / steps) + angle_offset
            wave = math.sin(petals * (theta - angle_offset))
            r = inner_r + (outer_r - inner_r) * (0.5 + 0.5 * wave)
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta)
            points.extend([x, y])

        self.canvas.create_polygon(
            points, outline=color, fill="", width=1.2, smooth=True
        )

        for scale in [0.72, 0.48, 0.25]:
            ring_pts = []
            for i in range(steps):
                theta = (2 * math.pi * i / steps) + angle_offset
                wave = math.cos(petals * (theta - angle_offset))
                r = (inner_r * scale) + 4 * wave
                ring_pts.extend([cx + r * math.cos(theta), cy + r * math.sin(theta)])
            self.canvas.create_polygon(
                ring_pts, outline=color, fill="", width=1, smooth=True
            )

    def draw_numbers(self):
        """Clock ke 1 se 12 tak stylized numbers"""
        for num in range(1, 13):
            angle = math.radians(num * 30 - 90)
            x = self.cx + self.radius * math.cos(angle)
            y = self.cy + self.radius * math.sin(angle)

            self.canvas.create_text(
                x,
                y,
                text=str(num),
                font=("Comic Sans MS", 22, "normal"),
                fill="#4a4a4a",
            )

    def draw_spider_and_hands(self, hour_angle, min_angle, sec_angle):
        """Spider ki body, red legs, aur lambi front legs jo Hour & Minute hands banati hain"""
        body_angle = min_angle

        # 1. Second Hand (Patli si black line)
        sec_len = 85
        sec_x = self.cx + sec_len * math.cos(sec_angle)
        sec_y = self.cy + sec_len * math.sin(sec_angle)
        self.canvas.create_line(
            self.cx, self.cy, sec_x, sec_y, fill="#1a1a1a", width=1.5
        )

        def rot(px, py, angle):
            a = angle + math.pi / 2
            rx = px * math.cos(a) - py * math.sin(a)
            ry = px * math.sin(a) + py * math.cos(a)
            return self.cx + rx, self.cy + ry

        # 2. Spider ki 6 Red Side Legs
        red_legs = [
            [(-6, -8), (-26, -24), (-34, -8)],
            [(-7, 0), (-30, -2), (-36, 18)],
            [(-6, 8), (-24, 22), (-22, 42)],
            [(6, -8), (26, -24), (34, -8)],
            [(7, 0), (30, -2), (36, 18)],
            [(6, 8), (24, 22), (22, 42)],
        ]

        for leg in red_legs:
            p0 = rot(leg[0][0], leg[0][1], body_angle)
            p1 = rot(leg[1][0], leg[1][1], body_angle)
            p2 = rot(leg[2][0], leg[2][1], body_angle)
            self.canvas.create_line(
                p0[0], p0[1], p1[0], p1[1], p2[0], p2[1],
                fill="#e61919", width=3.2, capstyle=tk.ROUND, joinstyle=tk.ROUND
            )

        # 3. Left Front Long Leg -> HOUR HAND
        h_len = 135
        h_mid_r = 65
        h_bend = hour_angle - 0.14
        hx_mid = self.cx + h_mid_r * math.cos(h_bend)
        hy_mid = self.cy + h_mid_r * math.sin(h_bend)
        hx_tip = self.cx + h_len * math.cos(hour_angle)
        hy_tip = self.cy + h_len * math.sin(hour_angle)

        h_start = rot(-4, -12, body_angle)
        self.canvas.create_line(
            h_start[0], h_start[1], hx_mid, hy_mid, hx_tip, hy_tip,
            fill="#0d0d0d", width=3.2, capstyle=tk.ROUND, joinstyle=tk.ROUND
        )

        # 4. Right Front Long Leg -> MINUTE HAND
        m_len = 180
        m_mid_r = 85
        m_bend = min_angle + 0.10
        mx_mid = self.cx + m_mid_r * math.cos(m_bend)
        my_mid = self.cy + m_mid_r * math.sin(m_bend)
        mx_tip = self.cx + m_len * math.cos(min_angle)
        my_tip = self.cy + m_len * math.sin(min_angle)

        m_start = rot(4, -12, body_angle)
        self.canvas.create_line(
            m_start[0], m_start[1], mx_mid, my_mid, mx_tip, my_tip,
            fill="#0d0d0d", width=2.4, capstyle=tk.ROUND, joinstyle=tk.ROUND
        )

        # 5. Spider Body
        head_pts = []
        for deg in range(0, 360, 20):
            rad = math.radians(deg)
            px = 6.5 * math.cos(rad)
            py = -10 + 8 * math.sin(rad)
            head_pts.extend(rot(px, py, body_angle))
        self.canvas.create_polygon(head_pts, fill="#0a0a0a", outline="#0a0a0a", smooth=True)

        abd_pts = []
        for deg in range(0, 360, 20):
            rad = math.radians(deg)
            px = 9 * math.cos(rad)
            py = 11 + 14 * math.sin(rad)
            abd_pts.extend(rot(px, py, body_angle))
        self.canvas.create_polygon(abd_pts, fill="#0a0a0a", outline="#0a0a0a", smooth=True)

        c_dot = rot(0, 8, body_angle)
        self.canvas.create_oval(
            c_dot[0] - 2, c_dot[1] - 3, c_dot[0] + 2, c_dot[1] + 3,
            fill="#e61919", outline=""
        )

    def update_clock(self):
        self.canvas.delete("all")

        now = time.localtime()
        whole_sec = now.tm_sec
        ms = time.time() % 1
        sec = whole_sec + ms
        minute = now.tm_min + sec / 60.0
        hour = (now.tm_hour % 12) + minute / 60.0

        # Har naye second par tick-tock aavaj
        if whole_sec != self.last_tick_second:
            self.last_tick_second = whole_sec
            self.play_tick_sound(is_tock=(whole_sec % 2 == 1))

        gear_rot = sec * (math.pi / 30) * 0.2

        # 1. Background Pink Mandala/Cog Gears
        self.draw_mandala_cog(self.cx - 48, self.cy - 22, 68, 52, 12, "#f3c6d3", gear_rot)
        self.draw_mandala_cog(self.cx + 52, self.cy - 12, 65, 50, 12, "#f5ccd8", -gear_rot)
        self.draw_mandala_cog(self.cx - 28, self.cy + 58, 55, 42, 10, "#f5ccd8", gear_rot * 1.2)

        # 2. Top se center tak aati hui Spider Silk Thread
        self.canvas.create_line(
            self.cx, 0, self.cx, self.cy, fill="#333333", width=1
        )

        # 3. Clock Numbers (1 to 12)
        self.draw_numbers()

        # 4. Angles calculate karna
        hour_angle = math.radians(hour * 30 - 90)
        min_angle = math.radians(minute * 6 - 90)
        sec_angle = math.radians(sec * 6 - 90)

        # 5. Spider & Hands draw karna
        self.draw_spider_and_hands(hour_angle, min_angle, sec_angle)

        # 6. Sound Toggle Button
        self.draw_sound_toggle()

        self.root.after(30, self.update_clock)


if __name__ == "__main__":
    root = tk.Tk()
    app = InteractiveSpiderClock(root)
    root.mainloop()