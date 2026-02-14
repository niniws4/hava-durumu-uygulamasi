import requests
import tkinter as tk
from tkinter import messagebox
import threading
import time
from PIL import Image, ImageTk
import io

class HavaDurumuUygulamasi:
    def __init__(self, root):
        self.root = root
        self.root.title("Global Hava Durumu v1.0")
        self.root.geometry("500x750") 
        self.root.configure(bg="#121212")

        self.is_loading = False
        self.api_key = "c8f30527586fe05db759ad544abe9e06"
        
        self.sehir_var = tk.StringVar(value="Ankara")
        
        self.arayuz_hazirla()
        
        self.verileri_baslat_thread()
        
        self.otomatik_guncelle_dongusu()

    def arayuz_hazirla(self):
        header = tk.Frame(self.root, bg="#1e1e1e", pady=15)
        header.pack(fill="x")
        tk.Label(header, text="GLOBAL HAVA DURUMU", font=("Segoe UI", 16, "bold"), fg="#00ff88", bg="#1e1e1e").pack()
        
        self.status_label = tk.Label(self.root, text="Veriler yükleniyor...", font=("Segoe UI", 9), fg="#555555", bg="#121212")
        self.status_label.pack(pady=5)

        search_frame = tk.Frame(self.root, bg="#121212", pady=10)
        search_frame.pack(fill="x", padx=35)
        
        tk.Label(search_frame, text="Şehir İsmi Giriniz:", fg="#aaaaaa", bg="#121212", font=("Segoe UI", 10)).pack(anchor="w")
        
        self.entry_sehir = tk.Entry(search_frame, textvariable=self.sehir_var, bg="#2a2a2a", fg="white", 
                                    insertbackground="white", borderwidth=0, font=("Segoe UI", 14))
        self.entry_sehir.pack(fill="x", ipady=10, pady=5)
        
        self.btn_ara = tk.Button(search_frame, text="HAVA DURUMUNU GETİR", command=self.verileri_baslat_thread,
                                 bg="#00ff88", fg="#121212", font=("Segoe UI", 11, "bold"), 
                                 activebackground="#00cc6e", cursor="hand2", borderwidth=0)
        self.btn_ara.pack(fill="x", pady=10)

        self.lbl_sicaklik = self.kart_olustur(self.root, "SICAKLIK", "#4da6ff")
        self.lbl_durum = self.kart_olustur(self.root, "HAVA DURUMU", "#ffcc00")
        self.lbl_nem = self.kart_olustur(self.root, "NEM ORANI", "#a29bfe")
        self.lbl_ikon = tk.Label(self.root, bg="#121212")
        self.lbl_ikon.pack(pady=10)

    def kart_olustur(self, parent, baslik, renk):
        f = tk.Frame(parent, bg="#1e1e1e", pady=18)
        f.pack(pady=10, padx=35, fill="x")
        tk.Label(f, text=baslik, font=("Segoe UI", 10, "bold"), fg="#888888", bg="#1e1e1e").pack()
        lbl = tk.Label(f, text="---", font=("Consolas", 26, "bold"), fg=renk, bg="#1e1e1e")
        lbl.pack()
        return lbl

    def verileri_baslat_thread(self):
        thread = threading.Thread(target=self.api_verilerini_cek, daemon=True)
        thread.start()

    def api_verilerini_cek(self):
        if self.is_loading: return
        
        sehir = self.sehir_var.get().strip()
        if not sehir:
            messagebox.showwarning("Uyarı", "Lütfen bir şehir ismi giriniz!")
            return

        self.is_loading = True
        self.status_label.config(text=f"{sehir} bilgisi alınıyor...", fg="#ffcc00")

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={sehir}&appid={self.api_key}&units=metric&lang=tr"
            response = requests.get(url, timeout=10)
            data = response.json()

            if response.status_code == 200:
                self.root.after(0, lambda: self.arayuz_verilerini_yansit(data))
            else:
                hata_mesaji = data.get("message", "Şehir bulunamadı")
                self.root.after(0, lambda: messagebox.showerror("Hata", f"Sorun oluştu: {hata_mesaji.capitalize()}"))
                self.root.after(0, lambda: self.status_label.config(text="Hata oluştu!", fg="#ff4d4d"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Bağlantı Hatası", "İnternet bağlantınızı kontrol edin."))
        finally:
            self.is_loading = False

    def arayuz_verilerini_yansit(self, data):
        try:
            sehir_adi = data['name']
            sicaklik = round(data['main']['temp'])
            durum = data['weather'][0]['description'].capitalize()
            ikon_kodu = data['weather'][0]['icon'] # Örn: '10d'

            ikon_url = f"http://openweathermap.org/img/wn/{ikon_kodu}@2x.png"
            ikon_yanit = requests.get(ikon_url)
            ikon_verisi = Image.open(io.BytesIO(ikon_yanit.content))
            self.foto = ImageTk.PhotoImage(ikon_verisi)
            
            self.lbl_sicaklik.config(text=f"{sicaklik}°C")
            self.lbl_durum.config(text=durum)
            self.lbl_nem.config(text=f"%{data['main']['humidity']}")
            
            self.lbl_ikon.config(image=self.foto)
            
            güncel_saat = time.strftime('%H:%M')
            self.status_label.config(text=f"Son Güncelleme: {sehir_adi} ({güncel_saat})", fg="#00ff88")
            
            if sicaklik > 28:
                yeni_renk = "#4a1a1a" # Sıcak
            elif sicaklik < 12:
                yeni_renk = "#1a2a4a" # Soğuk
            else:
                yeni_renk = "#121212" # Normal
                
            self.root.configure(bg=yeni_renk)
            self.lbl_ikon.configure(bg=yeni_renk)
            self.status_label.configure(bg=yeni_renk)

        except Exception as e:
            print(f"İkon veya veri hatası: {e}")

    def otomatik_guncelle_dongusu(self):
        if self.sehir_var.get().strip():
            self.verileri_baslat_thread()
        
        self.root.after(600000, self.otomatik_guncelle_dongusu)

if __name__ == "__main__":
    root = tk.Tk()
    app = HavaDurumuUygulamasi(root)
    root.mainloop()