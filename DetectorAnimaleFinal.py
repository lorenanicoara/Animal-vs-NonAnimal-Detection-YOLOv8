# =====================================================================
#  DETECTOR ANIMAL / NON-ANIMAL - aplicație cu butoane (fără cod pentru utilizator)
#  Utilizatorul alege o poză, iar aplicația spune dacă în ea sunt animale,
#  desenează dreptunghiurile și numără animalele și obiectele.
# =====================================================================
import os, sys, threading, traceback, multiprocessing
from pathlib import Path

# În aplicația .exe fără consolă nu există "ecran" pentru mesaje - le trimitem în gol,
# altfel bibliotecile care scriu mesaje ar da eroare.
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont

TITLU   = "Detector Animal / Non-Animal"
CULORI  = {0: (255, 140, 0), 1: (40, 200, 40)}        # Non_Animal = portocaliu, Animal = verde
NUME    = {0: "Non_Animal", 1: "Animal"}
PRAG    = 0.45                                       # încrederea minimă (fixă) pentru o detecție
FORMATE = [("Imagini", "*.jpg *.jpeg *.png *.bmp *.webp"), ("Toate fișierele", "*.*")]


def folder_aplicatie():
    """Folderul în care se află aplicația (merge și ca script .py, și ca .exe)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def gaseste_modelul():
    """Caută modelul: întâi lângă aplicație, apoi în folderele de antrenare."""
    baza = folder_aplicatie()
    candidati = [baza / "model_animal.pt"]
    for b in (baza, baza.parent, baza.parent.parent):
        for nume in ("animal_gpu_mare", "animal_gpu_s", "animal_v2", "animal_vs_non_animal"):
            candidati.append(b / "animal_project" / "runs" / nume / "weights" / "best.pt")
    return next((p for p in candidati if p.exists()), None)


def font(marime):
    for f in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, marime)
        except OSError:
            pass
    return ImageFont.load_default()


def detecteaza(model, cale_poza, prag):
    """Rulează modelul pe poză. Întoarce poza desenată și numărul de animale / obiecte."""
    img = Image.open(cale_poza).convert("RGB")
    rez = model.predict(img, conf=prag, verbose=False)[0]
    clase   = rez.boxes.cls.int().tolist()
    scoruri = rez.boxes.conf.tolist()
    cutii   = rez.boxes.xyxy.tolist()

    desen = ImageDraw.Draw(img)
    grosime = max(2, round(max(img.size) / 300))
    f = font(max(12, round(max(img.size) / 45)))
    for (x1, y1, x2, y2), c, s in zip(cutii, clase, scoruri):
        desen.rectangle([x1, y1, x2, y2], outline=CULORI[c], width=grosime)
        text = f"{NUME[c]} {s:.0%}"                    # numele clasei + cât de sigur e modelul
        st, sus, dr, jos = desen.textbbox((x1, y1), text, font=f)
        y_text = y1 - (jos - sus) - 4 if y1 - (jos - sus) - 4 > 0 else y1
        desen.rectangle([x1, y_text, x1 + (dr - st) + 6, y_text + (jos - sus) + 4], fill=CULORI[c])
        desen.text((x1 + 3, y_text + 1), text, fill="black", font=f)

    return img, clase.count(1), clase.count(0)


class Aplicatie:
    def __init__(self, root):
        self.root = root
        self.model = None
        self.cale_poza = None
        self.poza_rezultat = None

        root.title(TITLU)
        root.geometry("1000x760")
        root.minsize(700, 550)
        root.configure(bg="#f4f4f4")

        # --- Bara de sus cu butoane ---
        bara = tk.Frame(root, bg="#f4f4f4", pady=10)
        bara.pack(fill="x")
        stil = dict(font=("Segoe UI", 12, "bold"), padx=16, pady=6, cursor="hand2", relief="flat")
        self.btn_alege = tk.Button(bara, text="📂  Alege o poză", bg="#2b6cb0", fg="white",
                                   command=self.alege_poza, state="disabled", **stil)
        self.btn_alege.pack(side="left", padx=(16, 8))
        self.btn_salveaza = tk.Button(bara, text="💾  Salvează rezultatul", bg="#4a5568", fg="white",
                                      command=self.salveaza, state="disabled", **stil)
        self.btn_salveaza.pack(side="left", padx=8)

        # --- Rezultatul mare (DA / NU) ---
        self.lbl_rezultat = tk.Label(root, text="Se încarcă modelul... (poate dura câteva secunde)",
                                     font=("Segoe UI", 20, "bold"), bg="#f4f4f4", fg="#4a5568")
        self.lbl_rezultat.pack(pady=(4, 0))
        self.lbl_detalii = tk.Label(root, text="", font=("Segoe UI", 13), bg="#f4f4f4", fg="#2d3748")
        self.lbl_detalii.pack(pady=(2, 8))

        # --- Zona pentru poză ---
        self.panou = tk.Label(root, bg="#e2e8f0", text="Poza va apărea aici",
                              font=("Segoe UI", 12), fg="#718096")
        self.panou.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.panou.bind("<Configure>", lambda _e: self.afiseaza_poza())

        threading.Thread(target=self.incarca_modelul, daemon=True).start()

    # ----- Încărcarea modelului (în fundal, ca fereastra să nu înghețe) -----
    def incarca_modelul(self):
        try:
            cale = gaseste_modelul()
            if cale is None:
                raise FileNotFoundError(
                    "Nu găsesc modelul.\n\nPune fișierul 'model_animal.pt' în același folder cu aplicația:\n"
                    f"{folder_aplicatie()}")
            from ultralytics import YOLO
            self.model = YOLO(str(cale))
            self.root.after(0, self.model_gata, cale)
        except Exception as e:
            self.root.after(0, self.eroare, e)

    def model_gata(self, cale):
        self.btn_alege.config(state="normal")
        self.lbl_rezultat.config(text="Gata! Apasă „Alege o poză”.", fg="#2b6cb0")
        self.lbl_detalii.config(text=f"Model: {cale.parent.parent.name if cale.name == 'best.pt' else cale.name}")

    # ----- Butoane -----
    def alege_poza(self):
        cale = filedialog.askopenfilename(title="Alege o poză", filetypes=FORMATE,
                                          initialdir=str(Path.home() / "Desktop"))
        if cale:
            self.cale_poza = cale
            self.analizeaza()

    def analizeaza(self):
        self.btn_alege.config(state="disabled")
        self.lbl_rezultat.config(text="Analizez poza...", fg="#4a5568")
        threading.Thread(target=self._analizeaza_fundal, args=(self.cale_poza, PRAG), daemon=True).start()

    def _analizeaza_fundal(self, cale, prag):
        try:
            rezultat = detecteaza(self.model, cale, prag)
            self.root.after(0, self.arata_rezultat, rezultat)
        except Exception as e:
            self.root.after(0, self.eroare, e)

    def arata_rezultat(self, rezultat):
        img, n_animale, n_obiecte = rezultat
        self.poza_rezultat = img
        if n_animale > 0:
            self.lbl_rezultat.config(text=f"✅ DA – în poză {'este un animal' if n_animale == 1 else f'sunt {n_animale} animale'}",
                                     fg="#2f855a")
        else:
            self.lbl_rezultat.config(text="❌ NU – nu am găsit niciun animal", fg="#c53030")
        self.lbl_detalii.config(text=f"Animale detectate: {n_animale}     |     "
                                     f"Obiecte non-animale detectate: {n_obiecte}     "
                                     f"({Path(self.cale_poza).name})")
        self.btn_alege.config(state="normal")
        self.btn_salveaza.config(state="normal")
        self.afiseaza_poza()

    def afiseaza_poza(self):
        if self.poza_rezultat is None:
            return
        w, h = max(self.panou.winfo_width(), 100), max(self.panou.winfo_height(), 100)
        copie = self.poza_rezultat.copy()
        copie.thumbnail((w - 10, h - 10))
        self._foto = ImageTk.PhotoImage(copie)        # păstrăm referința, altfel dispare poza
        self.panou.config(image=self._foto, text="")

    def salveaza(self):
        if self.poza_rezultat is None:
            return
        nume = Path(self.cale_poza).stem + "_rezultat.jpg"
        cale = filedialog.asksaveasfilename(title="Salvează rezultatul", initialfile=nume,
                                            defaultextension=".jpg",
                                            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
        if cale:
            self.poza_rezultat.save(cale)
            messagebox.showinfo(TITLU, f"Rezultatul a fost salvat:\n{cale}")

    def eroare(self, e):
        self.btn_alege.config(state="normal" if self.model is not None else "disabled")
        self.lbl_rezultat.config(text="A apărut o eroare", fg="#c53030")
        try:
            (folder_aplicatie() / "eroare.txt").write_text(traceback.format_exc(), encoding="utf-8")
        except Exception:
            pass
        messagebox.showerror(TITLU, str(e))


if __name__ == "__main__":
    multiprocessing.freeze_support()      # necesar pentru aplicațiile .exe pe Windows
    root = tk.Tk()
    Aplicatie(root)
    root.mainloop()
