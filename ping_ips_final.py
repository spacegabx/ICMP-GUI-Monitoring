import threading
import time
import tkinter as tk
from tkinter import Text
from ping3 import ping

class AutoScrollingText:
    def __init__(self, master, **kwargs):
        self.text = Text(master, **kwargs)
        self.text.config(yscrollcommand=False)

class PingApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Iloilo Convergent | Ping Monitor")

        # Set the window resolution
        self.geometry("1280x720")

        # Add an attribute to store the current full-screen state
        self.is_fullscreen = False

        # Bind F11 key to toggle full-screen mode
        self.bind("<F11>", self.toggle_fullscreen)

        self.ip_addresses = {
           "Google DNS": "8.8.8.8",
            "LVPN TSI": "198.153.241.237",
            "GVPN TSI": "172.81.92.237",
            "VDI1 TSI-CDE": "172.23.85.30",
            "2TP Core S": "10.15.0.101",
            "2FT Core S": "10.22.8.2"
        }

        self.configure(bg="black")

        self.frames = {}
        self.labels = {}
        for idx, name in enumerate(self.ip_addresses):
            row = idx // 3
            col = idx % 3
            frame = tk.Frame(self, bg="black")
            frame.grid(row=row * 2, column=col * 2, columnspan=2, padx=14, pady=26, sticky='nsew')
            self.grid_rowconfigure(row * 2, weight=1)
            self.grid_columnconfigure(col * 2, weight=1)

            self.frames[name] = frame

            label = tk.Label(frame, text=name, font=("Arial", 24), bg="black", fg="white")
            label.pack(anchor='w')
            result_label = tk.Label(frame, text="", font=("Arial", 18), bg="black", fg="white", wraplength="400",justify='center')
            result_label.pack(fill='both', expand=True)
            self.labels[name] = result_label

        for i in range(5):
            self.grid_rowconfigure(i, weight=1)
        for i in range(6):
            self.grid_columnconfigure(i, weight=1)

        self.console = AutoScrollingText(self, bg="black", fg="white", height=16, font=("Arial", 12))
        self.console.text.grid(row=4, column=0, columnspan=3, padx=10, pady=16, sticky="nsew")

        self.console_gvpn = AutoScrollingText(self, bg="black", fg="white", height=16, font=("Arial", 12))
        self.console_gvpn.text.grid(row=4, column=3, columnspan=3, padx=10, pady=16, sticky="nsew")

        self.update_ping_results()

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def update_ping_results(self):
        def ping_ip(name, ip_address, timeout=2):
            try:
                delay = ping(ip_address, timeout=timeout)
                if delay is not None:
                    delay_str = "{:.3f}".format(delay)
                    if delay >= 500:
                        result = f"High latency (>=500 ms)"
                    else:
                        result = f"Responded in {delay_str} ms"
                else:
                    result = f"Down or not responding within the timeout"
            except Exception as e:
                result = f"Error pinging {name} ({ip_address}): {e}"
            return result

        threads = []

        for name, ip in self.ip_addresses.items():
            t = threading.Thread(name=name, target=ping_ip, args=(name, ip))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
            if "Down" in t.result or "not responding" in t.result:
                self.labels[t.name].config(text=t.result, fg="red")
            else:
                self.labels[t.name].config(text=t.result, fg="white")
            if t.name == "LVPN TSI":
                self.console.text.insert(tk.END, f"{t.name}: {t.result}\n")
                self.console.text.see(tk.END)
            
        for name, ip in self.ip_addresses.items():
            if name == "GVPN TSI":
                t = threading.Thread(name=name, target=ping_ip, args=(name, ip))
                t.start()
                threads.append(t)

        for t in threads:
            t.join()
            if "Down" in t.result or "not responding" in t.result:
                self.labels[t.name].config(text=t.result, fg="red")
            else:
                self.labels[t.name].config(text=t.result, fg="white")
            if t.name == "GVPN TSI":
                self.console_gvpn.text.insert(tk.END, f"{t.name}: {t.result}\n")
                self.console_gvpn.text.see(tk.END)

        self.after(1000, self.update_ping_results)

if __name__ == "__main__":
    # Set the result attribute for the Thread class to store results
    threading.Thread.result = None
    def run_with_result(self, *args, **kwargs):
        self.result = self._target(*self._args, **self._kwargs)
    threading.Thread.run = run_with_result
    app = PingApp()
    app.mainloop()