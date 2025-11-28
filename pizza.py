import tkinter as tk
import customtkinter as ctk
import pymem
from tkinter import ttk

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
ctk.set_appearance_mode("dark")         # DARK MODE
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Mod Menu")
root.geometry("900x550")

# pymem init
pm = pymem.Pymem("PirateFS-Win64-Shipping.exe")
module_base = pymem.process.module_from_name(
    pm.process_handle, "PirateFS-Win64-Shipping.exe"
).lpBaseOfDll

def set_bananas(new_bananas: int):
    pm.write_int(module_base + 0x17FD20E4C84, new_bananas)
    return f"bananas set to {new_bananas}"

def set_blunders(new_blunders: int):
    pm.write_int(module_base + 0x1A0CBA767EC, new_blunders)
    return f"blunders set to {new_blunders}"

# ---------------------------------------------------------
#  HEADER
# ---------------------------------------------------------
header = ctk.CTkLabel(root,
                      text="PFS MOD MENU",
                      font=ctk.CTkFont(size=32, weight="bold"),
                      fg_color="#0077CC",
                      height=60)
header.pack(fill="x")

# ---------------------------------------------------------
#  MAIN AREA
# ---------------------------------------------------------
main_area = ctk.CTkFrame(root, fg_color="black")
main_area.pack(fill="both", expand=True)

# LEFT MENU
left_menu = ctk.CTkFrame(main_area, width=200, fg_color="#111111")
left_menu.pack(side="left", fill="y")

# RIGHT PANEL
right_panel = ctk.CTkFrame(main_area, fg_color="black")
right_panel.pack(side="right", fill="both", expand=True)

# ---------------------------------------------------------
# SWITCH PAGES
# ---------------------------------------------------------
def show_page(page):
    for widget in right_panel.winfo_children():
        widget.destroy()

    if page == "Misc":
        build_misc_page()
    elif page == "Weapon":
        build_weapon_page()
    elif page == "Player":
        build_player_page()
    else:
        ctk.CTkLabel(right_panel,
                     text=f"{page} Page",
                     font=ctk.CTkFont(size=28),
                     text_color="white").pack(pady=20)

# LEFT BUTTONS
menu_buttons = ["Player", "Weapon", "Misc"]

for b in menu_buttons:
    ctk.CTkButton(left_menu,
                  text=b,
                  height=45,
                  corner_radius=8,
                  font=ctk.CTkFont(size=18, weight="bold"),
                  command=lambda p=b: show_page(p)
                  ).pack(fill="x", padx=15, pady=10)

# ---------------------------------------------------------
#  PLAYER PAGE
# ---------------------------------------------------------
def build_player_page():
    content = ctk.CTkFrame(right_panel, fg_color="black")
    content.pack(pady=30, padx=20, anchor="nw")

    # Bone ESP checkbox
    chk_bone_esp = ctk.CTkCheckBox(content, text="Bone ESP")
    chk_bone_esp.pack(anchor="w", pady=10, padx=10)

# ---------------------------------------------------------
#  WEAPON PAGE
# ---------------------------------------------------------
def build_weapon_page():
    content = ctk.CTkFrame(right_panel, fg_color="black")
    content.pack(pady=30, padx=20, anchor="nw")

    # Silent Aimbot checkbox
    chk_silent_aimbot = ctk.CTkCheckBox(content, text="Silent Aimbot")
    chk_silent_aimbot.pack(anchor="w", pady=10, padx=10)

    # Machinegun checkbox
    chk_machinegun = ctk.CTkCheckBox(content, text="Machinegun")
    chk_machinegun.pack(anchor="w", pady=10, padx=10)

# ---------------------------------------------------------
#  MISC PAGE
# ---------------------------------------------------------
def build_misc_page():
    content = ctk.CTkFrame(right_panel, fg_color="black")
    content.pack(pady=30, padx=20, anchor="nw", fill="both")

    # ----------- Row 1 (BLUNDERBOMBS) ----------- 
    row1 = ctk.CTkFrame(content, fg_color="black")
    row1.pack(pady=10, anchor="w")

    entry1 = ctk.CTkEntry(row1, width=200, placeholder_text="Amount")
    entry1.pack(side="left", padx=10)

    def add_blunders():
        try:
            value = int(entry1.get())
            set_blunders(value)
            print(f"Blunderbombs set to {value}")
        except:
            print("Invalid number!")

    ctk.CTkButton(row1, text="ADD", width=80, corner_radius=8, command=add_blunders).pack(side="left", padx=10)
    ctk.CTkLabel(row1, text="add blunderbombs 💣", font=ctk.CTkFont(size=16)).pack(side="left", padx=10)

    # ----------- Row 2 (BANANAS) ----------- 
    row2 = ctk.CTkFrame(content, fg_color="black")
    row2.pack(pady=10, anchor="w")

    entry2 = ctk.CTkEntry(row2, width=200, placeholder_text="Amount")
    entry2.pack(side="left", padx=10)

    def add_bananas():
        try:
            value = int(entry2.get())
            set_bananas(value)
            print(f"Bananas set to {value}")
        except:
            print("Invalid number!")

    ctk.CTkButton(row2, text="ADD", width=80, corner_radius=8, command=add_bananas).pack(side="left", padx=10)
    ctk.CTkLabel(row2, text="add bananas 🍌", font=ctk.CTkFont(size=16)).pack(side="left", padx=10)

    # ----------- Infinite Ammo checkbox ----------- 
    chk_infinite_ammo = ctk.CTkCheckBox(content, text="Infinite ammo")
    chk_infinite_ammo.pack(anchor="w", pady=10, padx=10)

    def toggle_infinite_ammo():
        if chk_infinite_ammo.get():
            print("Infinite ammo ON")
            # pm.write_... (твой код для включения)
        else:
            print("Infinite ammo OFF")
            # pm.write_... (твой код для выключения)

    chk_infinite_ammo.configure(command=toggle_infinite_ammo)

root.mainloop()
