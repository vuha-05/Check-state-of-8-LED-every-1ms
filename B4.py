import tkinter as tk
from tkinter import messagebox
import serial
import threading

class STM32DIDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("STM32 DI Monitor (PA0-PA7)")
        # Thu gọn kích thước vì đã bỏ 2 nút Start/Stop
        self.root.geometry("600x250") 
        self.root.resizable(False, False)

        self.serial_port = None
        self.is_reading = False
        self.latest_state = 0xFF  # Mặc định tất cả các chân đều HIGH (Pull-Up)
        self.leds = []

        self.setup_ui()

    def setup_ui(self):
        # --- Khung Cấu hình & Kết nối ---
        frame_ctrl = tk.Frame(self.root)
        frame_ctrl.pack(fill="x", padx=10, pady=15)

        tk.Label(frame_ctrl, text="Cổng COM:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.com_entry = tk.Entry(frame_ctrl, width=15, font=("Arial", 10))
        self.com_entry.insert(0, "COM9")
        self.com_entry.pack(side=tk.LEFT, padx=5)

        self.btn_connect = tk.Button(frame_ctrl, text="Kết nối", bg="lightblue", font=("Arial", 10, "bold"), width=15, command=self.toggle_connection)
        self.btn_connect.pack(side=tk.LEFT, padx=15)

        # --- Khung Hiển thị 8 LED ---
        frame_led = tk.LabelFrame(self.root, text="Trạng Thái Đầu Vào (PA7 -> PA0)", font=("Arial", 11, "bold"))
        frame_led.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(frame_led, height=100)
        self.canvas.pack(fill="x", pady=10)

        start_x = 25
        for i in range(8):
            pin_idx = 7 - i 
            
            led = self.canvas.create_oval(start_x, 20, start_x + 50, 70, fill="gray", outline="#333", width=2)
            self.leds.append(led)
            
            self.canvas.create_text(start_x + 25, 90, text=f"PA{pin_idx}", font=("Arial", 10, "bold"))
            
            start_x += 65

    def toggle_connection(self):
        if self.serial_port is None or not self.serial_port.is_open:
            com = self.com_entry.get()
            try:
                self.serial_port = serial.Serial(com, 115200, timeout=0.1)
                
                self.btn_connect.config(text="Ngắt kết nối", bg="orange")
                self.com_entry.config(state=tk.DISABLED)
                
                self.is_reading = True
                threading.Thread(target=self.read_from_port, daemon=True).start()
                self.update_gui()
                
            except serial.SerialException as e:
                messagebox.showerror("Lỗi Cổng COM", f"Không thể kết nối tới {com}.\nChi tiết: {e}")
        else:
            self.is_reading = False
            self.serial_port.close()
            
            self.btn_connect.config(text="Kết nối", bg="lightblue")
            self.com_entry.config(state=tk.NORMAL)
            
            self.latest_state = 0xFF
            self.redraw_leds()

    def read_from_port(self):
        """Hàm chạy ngầm liên tục để đọc dữ liệu từ UART"""
        while self.is_reading and self.serial_port and self.serial_port.is_open:
            try:
                waiting = self.serial_port.in_waiting
                if waiting > 0:
                    raw_data = self.serial_port.read(waiting)
                    if raw_data:
                        self.latest_state = raw_data[-1]
            except Exception:
                break

    def update_gui(self):
        """Vòng lặp chạy trên luồng chính để vẽ lại GUI"""
        if not self.is_reading:
            return
        
        self.redraw_leds()
        self.root.after(50, self.update_gui)

    def redraw_leds(self):
        """Phân tích byte nhận được và đổi màu LED"""
        for i in range(8):
            pin_idx = 7 - i 
            bit_val = (self.latest_state >> pin_idx) & 1
            
            # 0 -> Sáng (Xanh), 1 -> Tắt (Xám)
            color = "lime" if bit_val == 0 else "gray"
            self.canvas.itemconfig(self.leds[i], fill=color)

if __name__ == "__main__":
    app = tk.Tk()
    dashboard = STM32DIDashboard(app)
    app.mainloop()