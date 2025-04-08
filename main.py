from tkinter import ttk,messagebox ,filedialog
from threading import Thread
from playsound import playsound
import tkinter as tk 
import os
import math
import winsound
import json
import time
import datetime
import pytz

class ClockApp:
        def __init__(self, root):
            self.root = root
            self.root.title("برنامه پیشرفته")
            self.root.geometry("800x700")
            self.root.configure(bg="#2e2e2e")  # background temp

            self.tabs = ttk.Notebook(root)
            self.tabs.pack(fill="both", expand=True)

            self.clock_tab = tk.Frame(self.tabs, bg="#2e2e2e")
            self.analog_tab = tk.Frame(self.tabs, bg="#2e2e2e")
            self.alarm_tab = tk.Frame(self.tabs, bg="#2e2e2e")
            self.timer_tab = tk.Frame(self.tabs, bg="#2e2e2e")
            self.stopwatch_tab = tk.Frame(self.tabs, bg="#2e2e2e")
            
            # Menus
            self.tabs.add(self.clock_tab, text="ساعت جهانی")
            self.tabs.add(self.analog_tab, text="ساعت آنالوگ")
            self.tabs.add(self.alarm_tab, text="زنگ هشدار")
            self.tabs.add(self.timer_tab, text="تایمر")
            self.tabs.add(self.stopwatch_tab, text="کرونومتر")

            self.running = True
            self.stopwatch_running = False
            self.stopwatch_time = 0
            self.alarms = []
            self.timers = []
            self.stopwatch_history = []
            self.max_items = 10  

            self.load_data()  # Loading data
            self.setup_clock_tab()
            self.setup_analog_tab()
            self.setup_alarm_tab()
            self.setup_timer_tab()
            self.setup_stopwatch_tab()

            self.update_clock()
            self.update_analog()
            Thread(target=self.check_alarms, daemon=True).start()
        
        #saved data
        def save_data(self):
            data = {
                "alarms": self.alarms,
                "timers": self.timers,
                "stopwatch_history": self.stopwatch_history,
                "max_items": self.max_items
            }
            with open("clock_data.json", "w") as f:
                json.dump(data, f)
        
        # Load data
        def load_data(self):
            if os.path.exists("clock_data.json"):
               with open("clock_data.json", "r") as f:
                    data = json.load(f)
                    self.alarms = data.get("alarms", [])
                    self.timers = data.get("timers", [])
                    self.stopwatch_history = data.get("stopwatch_history", [])
                    self.max_items = data.get("max_items", 10)
        
        # config
        def setup_clock_tab(self):
            self.time_label = tk.Label(self.clock_tab, font=("Helvetica", 50), fg="white", bg="#2e2e2e")
            self.time_label.pack(pady=20)
            
            tk.Label(self.clock_tab, text="جستجو:", fg="white", bg="#2e2e2e").pack()
            self.search_var = tk.StringVar()
            self.search_entry = tk.Entry(self.clock_tab, textvariable=self.search_var, bg="#3e3e3e", fg="white")
            self.search_entry.pack(pady=5)
            self.search_entry.bind("<KeyRelease>", self.update_timezone_list)

            self.timezone_var = tk.StringVar()
            self.timezone_combobox = ttk.Combobox(self.clock_tab, textvariable=self.timezone_var)
            self.timezone_combobox['values'] = pytz.all_timezones
            self.timezone_combobox.set("Asia/Tehran")
            self.timezone_combobox.pack(pady=10)

        def update_timezone_list(self, event):
            search_text = self.search_var.get().lower()
            filtered = [tz for tz in pytz.all_timezones if search_text in tz.lower()]
            self.timezone_combobox['values'] = filtered if filtered else pytz.all_timezones

        def update_clock(self):
            if self.running:
                tz = pytz.timezone(self.timezone_var.get())
                current_time = datetime.datetime.now(tz).strftime("%H:%M:%S")
                self.time_label.config(text=current_time)
                self.root.after(1000, self.update_clock)

        # Analog Clock
        def setup_analog_tab(self):
            self.canvas = tk.Canvas(self.analog_tab, width=300, height=300, bg="#2e2e2e", highlightthickness=0)
            self.canvas.pack(pady=20)
            self.draw_clock_face()

        def draw_clock_face(self):
            self.canvas.delete("all")
            center_x, center_y = 150, 150
            radius = 140
            self.canvas.create_oval(10, 10, 290, 290, width=2, outline="white")
            for i in range(12):
                angle = i * math.pi / 6 - math.pi / 2
                x = center_x + radius * 0.85 * math.cos(angle)
                y = center_y + radius * 0.85 * math.sin(angle)
                self.canvas.create_text(x, y, text=str(i + 1), font=("Helvetica", 12), fill="white")

        def update_analog(self):
            if self.running:
                self.draw_clock_face()
                tz = pytz.timezone(self.timezone_var.get())
                now = datetime.datetime.now(tz)
                center_x, center_y = 150, 150
                radius = 120
                hour = now.hour % 12 + now.minute / 60
                hour_angle = hour * 30 - 90
                hour_x = center_x + radius * 0.5 * math.cos(math.radians(hour_angle))
                hour_y = center_y + radius * 0.5 * math.sin(math.radians(hour_angle))
                self.canvas.create_line(center_x, center_y, hour_x, hour_y, width=4, fill="white")
                minute_angle = now.minute * 6 - 90
                minute_x = center_x + radius * 0.8 * math.cos(math.radians(minute_angle))
                minute_y = center_y + radius * 0.8 * math.sin(math.radians(minute_angle))
                self.canvas.create_line(center_x, center_y, minute_x, minute_y, width=2, fill="white")
                second_angle = now.second * 6 - 90
                second_x = center_x + radius * 0.9 * math.cos(math.radians(second_angle))
                second_y = center_y + radius * 0.9 * math.sin(math.radians(second_angle))
                self.canvas.create_line(center_x, center_y, second_x, second_y, fill="red")
                self.root.after(1000, self.update_analog)

        # Alarm
        def setup_alarm_tab(self):
            tk.Label(self.alarm_tab, text="تنظیم زنگ (ساعت:دقیقه):", fg="white", bg="#2e2e2e").pack(pady=5)
            frame = tk.Frame(self.alarm_tab, bg="#2e2e2e")
            frame.pack(pady=5)
            self.alarm_hour = tk.IntVar(value=0)
            self.alarm_minute = tk.IntVar(value=0)
            tk.Spinbox(frame, from_=0, to=23, width=5, textvariable=self.alarm_hour, bg="#3e3e3e", fg="white").pack(side="left")
            tk.Label(frame, text=":", fg="white", bg="#2e2e2e").pack(side="left")
            tk.Spinbox(frame, from_=0, to=59, width=5, textvariable=self.alarm_minute, bg="#3e3e3e", fg="white").pack(side="left")

            self.alarm_sound_var = tk.StringVar(value="alarm.mp3")
            tk.Button(frame, text="انتخاب صدا", command=self.choose_alarm_sound, bg="#3e3e3e", fg="white").pack(side="left", padx=5)

            tk.Button(self.alarm_tab, text="اضافه کردن زنگ", command=self.add_alarm, bg="#3e3e3e", fg="white").pack(pady=5)
            
            self.alarm_listbox = tk.Listbox(self.alarm_tab, height=10, selectmode="single", bg="#3e3e3e", fg="white")
            self.alarm_listbox.pack(pady=5)
            self.alarm_listbox.bind("<<ListboxSelect>>", self.on_alarm_select)
            self.update_alarm_listbox()

            btn_frame = tk.Frame(self.alarm_tab, bg="#2e2e2e")
            btn_frame.pack(pady=5)
            tk.Button(btn_frame, text="حذف زنگ", command=self.delete_alarm, bg="#3e3e3e", fg="white").pack(side="left", padx=5)
            tk.Button(btn_frame, text="ویرایش زنگ", command=self.edit_alarm, bg="#3e3e3e", fg="white").pack(side="left", padx=5)
            tk.Button(btn_frame, text="فعال/غیرفعال", command=self.toggle_alarm, bg="#3e3e3e", fg="white").pack(side="left", padx=5)

            tk.Label(btn_frame, text="حداکثر تعداد:", fg="white", bg="#2e2e2e").pack(side="left", padx=5)
            self.max_items_var = tk.IntVar(value=self.max_items)
            tk.Entry(btn_frame, textvariable=self.max_items_var, width=5, bg="#3e3e3e", fg="white").pack(side="left")
            tk.Button(btn_frame, text="ثبت", command=self.update_max_items, bg="#3e3e3e", fg="white").pack(side="left", padx=5)

            self.alarm_status = tk.Label(self.alarm_tab, text="", fg="white", bg="#2e2e2e")
            self.alarm_status.pack(pady=5)

        def choose_alarm_sound(self):
            sound_file = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
            if sound_file:
                self.alarm_sound_var.set(sound_file)

        def add_alarm(self):
            if len(self.alarms) >= self.max_items:
                messagebox.showwarning("محدودیت", f"نمی‌تونی بیشتر از {self.max_items} زنگ داشته باشی!")
                return
            alarm_time = f"{self.alarm_hour.get():02d}:{self.alarm_minute.get():02d}"
            if alarm_time not in [a["time"] for a in self.alarms]:
                self.alarms.append({"time": alarm_time, "active": True, "sound": self.alarm_sound_var.get()})
                self.update_alarm_listbox()
                self.alarm_status.config(text=f"زنگ {alarm_time} اضافه شد")
                self.save_data()

        def delete_alarm(self):
            selected = self.alarm_listbox.curselection()
            if selected:
                self.alarms.pop(selected[0])
                self.update_alarm_listbox()
                self.alarm_status.config(text="زنگ حذف شد")
                self.save_data()

        def on_alarm_select(self, event):
            selected = self.alarm_listbox.curselection()
            if selected:
                alarm = self.alarms[selected[0]]
                hour, minute = map(int, alarm["time"].split(":"))
                self.alarm_hour.set(hour)
                self.alarm_minute.set(minute)
                self.alarm_sound_var.set(alarm["sound"])

        def edit_alarm(self):
            selected = self.alarm_listbox.curselection()
            if selected:
                new_time = f"{self.alarm_hour.get():02d}:{self.alarm_minute.get():02d}"
                if new_time not in [a["time"] for a in self.alarms if a != self.alarms[selected[0]]]:
                    self.alarms[selected[0]]["time"] = new_time
                    self.alarms[selected[0]]["sound"] = self.alarm_sound_var.get()
                    self.update_alarm_listbox()
                    self.alarm_status.config(text=f"زنگ به {new_time} ویرایش شد")
                    self.save_data()

        def toggle_alarm(self):
            selected = self.alarm_listbox.curselection()
            if selected:
                self.alarms[selected[0]]["active"] = not self.alarms[selected[0]]["active"]
                self.update_alarm_listbox()
                self.alarm_status.config(text=f"زنگ {'فعال' if self.alarms[selected[0]]['active'] else 'غیرفعال'} شد")
                self.save_data()

        def update_alarm_listbox(self):
            self.alarm_listbox.delete(0, tk.END)
            for alarm in self.alarms:
                status = "فعال" if alarm["active"] else "غیرفعال"
                self.alarm_listbox.insert(tk.END, f"{alarm['time']} ({status}) - {os.path.basename(alarm['sound'])}")

        def play_alarm_sound(self, sound_file):
            if os.path.exists(sound_file):
                playsound(sound_file)
            else:
                winsound.Beep(1000, 2000)

        def show_alarm_popup(self, alarm):
            popup = tk.Toplevel(self.root)
            popup.title("زنگ هشدار")
            popup.geometry("300x150")
            popup.configure(bg="#2e2e2e")
            tk.Label(popup, text=f"زنگ {alarm['time']} رسید!", font=("Helvetica", 14), fg="white", bg="#2e2e2e").pack(pady=20)
            
            def stop_alarm():
                popup.destroy()
                self.alarm_status.config(text=f"زنگ {alarm['time']} متوقف شد")

            def snooze_alarm():
                popup.destroy()
                new_hour, new_minute = map(int, alarm["time"].split(":"))
                new_minute += 10
                if new_minute >= 60:
                    new_minute -= 60
                    new_hour = (new_hour + 1) % 24
                new_time = f"{new_hour:02d}:{new_minute:02d}"
                if len(self.alarms) < self.max_items:
                    self.alarms.append({"time": new_time, "active": True, "sound": alarm["sound"]})
                    self.update_alarm_listbox()
                    self.alarm_status.config(text=f"زنگ {alarm['time']} به {new_time} به تعویق افتاد")
                    self.save_data()
                else:
                    self.alarm_status.config(text=f"محدودیت {self.max_items} زنگ! اسنوز نشد.")

            tk.Button(popup, text="Stop", command=stop_alarm, bg="#3e3e3e", fg="white").pack(side="left", padx=20, pady=20)
            tk.Button(popup, text="Snooze (10 دقیقه)", command=snooze_alarm, bg="#3e3e3e", fg="white").pack(side="right", padx=20, pady=20)
            Thread(target=self.play_alarm_sound, args=(alarm["sound"],), daemon=True).start()

        def check_alarms(self):
            while self.running:
                current_time = datetime.datetime.now().strftime("%H:%M")
                for alarm in self.alarms[:]:
                    if alarm["active"] and alarm["time"] == current_time:
                        alarm["active"] = False
                        self.root.after(0, self.show_alarm_popup, alarm)
                        self.update_alarm_listbox()
                time.sleep(1)

        # Timers
        def setup_timer_tab(self):
            tk.Label(self.timer_tab, text="تنظیم تایمر (ساعت:دقیقه:ثانیه):", fg="white", bg="#2e2e2e").pack(pady=5)
            frame = tk.Frame(self.timer_tab, bg="#2e2e2e")
            frame.pack(pady=5)
            self.timer_hour = tk.IntVar(value=0)
            self.timer_minute = tk.IntVar(value=0)
            self.timer_second = tk.IntVar(value=0)
            tk.Spinbox(frame, from_=0, to=23, width=5, textvariable=self.timer_hour, bg="#3e3e3e", fg="white").pack(side="left")
            tk.Label(frame, text=":", fg="white", bg="#2e2e2e").pack(side="left")
            tk.Spinbox(frame, from_=0, to=59, width=5, textvariable=self.timer_minute, bg="#3e3e3e", fg="white").pack(side="left")
            tk.Label(frame, text=":", fg="white", bg="#2e2e2e").pack(side="left")
            tk.Spinbox(frame, from_=0, to=59, width=5, textvariable=self.timer_second, bg="#3e3e3e", fg="white").pack(side="left")

            self.timer_sound_var = tk.StringVar(value="alarm.mp3")
            tk.Button(frame, text="انتخاب صدا", command=self.choose_timer_sound, bg="#3e3e3e", fg="white").pack(side="left", padx=5)

            tk.Button(self.timer_tab, text="اضافه کردن تایمر", command=self.add_timer, bg="#3e3e3e", fg="white").pack(pady=5)
            
            self.timer_listbox = tk.Listbox(self.timer_tab, height=10, selectmode="single", bg="#3e3e3e", fg="white")
            self.timer_listbox.pack(pady=5)
            self.timer_listbox.bind("<<ListboxSelect>>", self.on_timer_select)
            self.update_timer_listbox()

            btn_frame = tk.Frame(self.timer_tab, bg="#2e2e2e")
            btn_frame.pack(pady=5)
            tk.Button(btn_frame, text="حذف تایمر", command=self.delete_timer, bg="#3e3e3e", fg="white").pack(side="left", padx=5)
            tk.Button(btn_frame, text="شروع تایمر", command=self.start_timer, bg="#3e3e3e", fg="white").pack(side="left", padx=5)
            
            self.timer_status = tk.Label(self.timer_tab, text="", fg="white", bg="#2e2e2e")
            self.timer_status.pack(pady=5)

        def choose_timer_sound(self):
            sound_file = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
            if sound_file:
                self.timer_sound_var.set(sound_file)

        def add_timer(self):
            if len(self.timers) >= self.max_items:
                messagebox.showwarning("محدودیت", f"نمی‌تونی بیشتر از {self.max_items} تایمر داشته باشی!")
                return
            total_seconds = (self.timer_hour.get() * 3600 + 
                            self.timer_minute.get() * 60 + 
                            self.timer_second.get())
            if total_seconds > 0:
                timer_str = f"{self.timer_hour.get():02d}:{self.timer_minute.get():02d}:{self.timer_second.get():02d}"
                timer = {"original": timer_str, "remaining": total_seconds, "active": False, "sound": self.timer_sound_var.get()}
                self.timers.append(timer)
                self.update_timer_listbox()
                self.timer_status.config(text=f"تایمر {timer_str} اضافه شد")
                self.save_data()

        def delete_timer(self):
            selected = self.timer_listbox.curselection()
            if selected:
                self.timers[selected[0]]["active"] = False
                self.timers.pop(selected[0])
                self.update_timer_listbox()
                self.timer_status.config(text="تایمر حذف شد")
                self.save_data()

        def on_timer_select(self, event):
            selected = self.timer_listbox.curselection()
            if selected:
                timer = self.timers[selected[0]]
                hours, remainder = divmod(timer["remaining"], 3600)
                mins, secs = divmod(remainder, 60)
                self.timer_hour.set(hours)
                self.timer_minute.set(mins)
                self.timer_second.set(secs)
                self.timer_sound_var.set(timer["sound"])

        def start_timer(self):
            selected = self.timer_listbox.curselection()
            if selected:
                timer = self.timers[selected[0]]
                if not timer["active"]:
                    timer["active"] = True
                    timer["remaining"] = (self.timer_hour.get() * 3600 + 
                                        self.timer_minute.get() * 60 + 
                                        self.timer_second.get())
                    Thread(target=self.run_timer, args=(selected[0],), daemon=True).start()
                    self.timer_status.config(text=f"تایمر {timer['original']} شروع شد")

        def update_timer_listbox(self):
            self.timer_listbox.delete(0, tk.END)
            for timer in self.timers:
                status = "فعال" if timer["active"] else "متوقف"
                display_time = f"{timer['remaining']//3600:02d}:{(timer['remaining']%3600)//60:02d}:{timer['remaining']%60:02d}"
                self.timer_listbox.insert(tk.END, f"{timer['original']} ({status}: {display_time}) - {os.path.basename(timer['sound'])}")

        def show_timer_popup(self, timer):
            popup = tk.Toplevel(self.root)
            popup.title("تایمر")
            popup.geometry("300x150")
            popup.configure(bg="#2e2e2e")
            tk.Label(popup, text=f"تایمر {timer['original']} تموم شد!", font=("Helvetica", 14), fg="white", bg="#2e2e2e").pack(pady=20)
            
            def stop_timer():
                popup.destroy()
                self.timer_status.config(text=f"تایمر {timer['original']} متوقف شد")

            def snooze_timer():
                popup.destroy()
                if len(self.timers) < self.max_items:
                    total_seconds = 10 * 60
                    new_timer_str = "00:10:00"
                    new_timer = {"original": new_timer_str, "remaining": total_seconds, "active": True, "sound": timer["sound"]}
                    self.timers.append(new_timer)
                    self.update_timer_listbox()
                    Thread(target=self.run_timer, args=(len(self.timers) - 1,), daemon=True).start()
                    self.timer_status.config(text=f"تایمر {timer['original']} به 10 دقیقه بعد به تعویق افتاد")
                    self.save_data()
                else:
                    self.timer_status.config(text=f"محدودیت {self.max_items} تایمر! اسنوز نشد.")

            tk.Button(popup, text="Stop", command=stop_timer, bg="#3e3e3e", fg="white").pack(side="left", padx=20, pady=20)
            tk.Button(popup, text="Snooze (10 دقیقه)", command=snooze_timer, bg="#3e3e3e", fg="white").pack(side="right", padx=20, pady=20)
            Thread(target=self.play_alarm_sound, args=(timer["sound"],), daemon=True).start()

        def run_timer(self, index):
            while self.timers[index]["active"] and self.timers[index]["remaining"] > 0 and self.running:
                seconds = self.timers[index]["remaining"]
                hours, remainder = divmod(seconds, 3600)
                mins, secs = divmod(remainder, 60)
                display_time = f"{hours:02d}:{mins:02d}:{secs:02d}"
                self.timer_listbox.delete(index)
                self.timer_listbox.insert(index, f"{self.timers[index]['original']} (فعال: {display_time}) - {os.path.basename(self.timers[index]['sound'])}")
                time.sleep(1)
                self.timers[index]["remaining"] -= 1
                self.save_data()
            if self.timers[index]["remaining"] <= 0 and self.timers[index]["active"] and self.running:
                self.timers[index]["active"] = False
                timer = self.timers[index]
                self.root.after(0, self.show_timer_popup, timer)
                self.update_timer_listbox()
                self.save_data()

        # Stopwatch
        def setup_stopwatch_tab(self):
            self.stopwatch_label = tk.Label(self.stopwatch_tab, font=("Helvetica", 40), text="00:00:00.00", fg="white", bg="#2e2e2e")
            self.stopwatch_label.pack(pady=20)
            tk.Button(self.stopwatch_tab, text="شروع", command=self.start_stopwatch, bg="#3e3e3e", fg="white").pack(pady=5)
            tk.Button(self.stopwatch_tab, text="توقف", command=self.stop_stopwatch, bg="#3e3e3e", fg="white").pack(pady=5)
            tk.Button(self.stopwatch_tab, text="ریست", command=self.reset_stopwatch, bg="#3e3e3e", fg="white").pack(pady=5)
            
            self.stopwatch_listbox = tk.Listbox(self.stopwatch_tab, height=10, bg="#3e3e3e", fg="white")
            self.stopwatch_listbox.pack(pady=5)
            for record in self.stopwatch_history:
                self.stopwatch_listbox.insert(tk.END, record)

        def start_stopwatch(self):
            if not self.stopwatch_running:
                self.stopwatch_running = True
                self.start_time = time.time() - self.stopwatch_time
                self.update_stopwatch()

        def update_stopwatch(self):
            if self.stopwatch_running:
                self.stopwatch_time = time.time() - self.start_time
                mins, secs = divmod(self.stopwatch_time, 60)
                hours, mins = divmod(mins, 60)
                time_str = f"{int(hours):02d}:{int(mins):02d}:{int(secs):02d}.{int((secs % 1) * 100):02d}"
                self.stopwatch_label.config(text=time_str)
                self.root.after(10, self.update_stopwatch)

        def stop_stopwatch(self):
            if self.stopwatch_running:
                self.stopwatch_running = False
                time_str = self.stopwatch_label.cget("text")
                if len(self.stopwatch_history) >= self.max_items:
                    self.stopwatch_history.pop(0)
                self.stopwatch_history.append(time_str)
                self.stopwatch_listbox.delete(0, tk.END)
                for record in self.stopwatch_history:
                    self.stopwatch_listbox.insert(tk.END, record)
                self.save_data()

        def reset_stopwatch(self):
            self.stopwatch_running = False
            self.stopwatch_time = 0
            self.stopwatch_label.config(text="00:00:00.00")

        def update_max_items(self):
            new_max = self.max_items_var.get()
            if new_max > 0:
                self.max_items = new_max
                self.save_data()
                messagebox.showinfo("موفق", f"حداکثر تعداد به {self.max_items} تغییر کرد.")
            else:
                messagebox.showwarning("خطا", "تعداد باید مثبت باشه!")

        def on_closing(self):
            self.running = False
            self.save_data()
            self.root.after(100, self.root.destroy)
            
if __name__ == "__main__":
    root = tk.Tk()
    app = ClockApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()