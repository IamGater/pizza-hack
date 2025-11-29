import tkinter as tk
import customtkinter as ctk
import pymem
from tkinter import ttk
from typing import Iterable

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Mod Menu")
root.geometry("900x550")

# ---------------------------------------------------------
# PYMEM INIT
# ---------------------------------------------------------
pm = pymem.Pymem("PirateFS-Win64-Shipping.exe")
module_base = pymem.process.module_from_name(
    pm.process_handle, "PirateFS-Win64-Shipping.exe"
).lpBaseOfDll

# ---------------------------------------------------------
# POINTER CHAIN RESOLVER
# ---------------------------------------------------------
def resolve_ptr_chain(
        pm: pymem.Pymem,
        start_addr: int,
        offsets: Iterable[int],
        *,
        final_add_only: bool = True,
) -> int:
    is_64 = pymem.process.is_64_bit(pm.process_handle)
    read_ptr = pm.read_ulonglong if is_64 else pm.read_uint

    addr = read_ptr(start_addr)

    for off in offsets[:-1]:
        addr = read_ptr(addr + off)

    last = offsets[-1]
    return addr + last if final_add_only else read_ptr(addr + last)

# ---------------------------------------------------------
# DYNAMIC BANANA POINTER CHAIN
# ---------------------------------------------------------
banana_ptr_base = module_base + 0x05A38E78
banana_offsets = [0x10, 0x58, 0x20, 0x1F8, 0xB0, 0xA0, 0xC54]

def set_bananas_dynamic(amount: int):
    final_addr = resolve_ptr_chain(pm, banana_ptr_base, banana_offsets)
    pm.write_int(final_addr, amount)
    return f"bananas set to {amount}"

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
# MAIN AREA
# ---------------------------------------------------------
main_area = ctk.CTkFrame(root, fg_color="black")
main_area.pack(fill="both", expand=True)

left_menu = ctk.CTkFrame(main_area, width=200, fg_color="#111111")
left_menu.pack(side="left", fill="y")

right_panel = ctk.CTkFrame(main_area, fg_color="black")
right_panel.pack(side="right", fill="both", expand=True)

# ---------------------------------------------------------
# NAVIGATION
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
# PLAYER PAGE
# ---------------------------------------------------------
def build_player_page():
    content = ctk.CTkFrame(right_panel, fg_color="black")
    content.pack(pady=30, padx=20, anchor="nw")

    chk_bone_esp = ctk.CTkCheckBox(content, text="Bone ESP")
    chk_bone_esp.pack(anchor="w", pady=10, padx=10)

# ---------------------------------------------------------
# WEAPON PAGE
# ---------------------------------------------------------
def build_weapon_page():
    content = ctk.CTkFrame(right_panel, fg_color="black")
    content.pack(pady=30, padx=20, anchor="nw")

    chk_silent_aimbot = ctk.CTkCheckBox(content, text="Silent Aimbot")
    chk_silent_aimbot.pack(anchor="w", pady=10, padx=10)

    chk_machinegun = ctk.CTkCheckBox(content, text="Machinegun")
    chk_machinegun.pack(anchor="w", pady=10, padx=10)

# ---------------------------------------------------------
# MISC PAGE (bananas only)
# ---------------------------------------------------------
def build_misc_page():
    content = ctk.CTkFrame(right_panel, fg_color="black")
    content.pack(pady=30, padx=20, anchor="nw", fill="both")

    # ---------------- BANANAS -----------------
    row_banana = ctk.CTkFrame(content, fg_color="black")
    row_banana.pack(pady=10, anchor="w")

    entry_banana = ctk.CTkEntry(row_banana, width=200, placeholder_text="Amount")
    entry_banana.pack(side="left", padx=10)

    def add_bananas():
        try:
            value = int(entry_banana.get())
            set_bananas_dynamic(value)
            print(f"Bananas set to {value}")
        except Exception as e:
            print("Failed to set bananas:", e)

    ctk.CTkButton(row_banana, text="ADD", width=80, corner_radius=8, command=add_bananas).pack(side="left", padx=10)
    ctk.CTkLabel(row_banana, text="add bananas 🍌", font=ctk.CTkFont(size=16)).pack(side="left", padx=10)

    # ---------------- INFINITE AMMO -----------------
    chk_infinite_ammo = ctk.CTkCheckBox(content, text="Infinite ammo")
    chk_infinite_ammo.pack(anchor="w", pady=10, padx=10)

    def toggle_infinite_ammo():
        print("Infinite ammo ON" if chk_infinite_ammo.get() else "Infinite ammo OFF")

    chk_infinite_ammo.configure(command=toggle_infinite_ammo)

root.mainloop()
