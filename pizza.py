import ctypes
import sys
import tkinter as tk
import customtkinter as ctk
import pymem
from tkinter import ttk
from typing import Iterable
import threading
import time

sys.stdout.reconfigure(encoding='utf-8')
# ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("PMH")
root.geometry("900x550")

# ---------------------------------------------------------
# PYMEM INIT
# ---------------------------------------------------------
print("Connecting to the game... ⌛")

try:
    pm = pymem.Pymem("PirateFS-Win64-Shipping.exe")
    module_base = pymem.process.module_from_name(
        pm.process_handle, "PirateFS-Win64-Shipping.exe"
    ).lpBaseOfDll
    print("Connected to PirateFS! ✅")
except Exception as e:
    print(f"Failed to connect: {e} ❌")
    raise SystemExit

# ---------------------------------------------------------
# POINTER CHAIN RESOLVER (SAFE)
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

def safe_resolve(base: int, offsets: Iterable[int]):
    try:
        return resolve_ptr_chain(pm, base, offsets)
    except Exception:
        return None

# ---------------------------------------------------------
# BANANAS POINTER
# ---------------------------------------------------------
banana_ptr_base = module_base + 0x059B0798
banana_offsets = [0x0, 0x190, 0x8E8, 0x20, 0x830, 0x20, 0xC74]

def set_bananas_dynamic(amount: int):
    final_addr = safe_resolve(banana_ptr_base, banana_offsets)
    if final_addr is None:
        print("Bananas pointer chain broken ❌")
        return False
    try:
        pm.write_int(final_addr, amount)
        print(f"Bananas set to {amount} 🍌")
        return True
    except Exception as e:
        print(f"Bananas write failed: {e} ❌")
        return False

# ---------------------------------------------------------
# BLUNDERBOMBS POINTER
# ---------------------------------------------------------
blunderbomb_ptr_base = module_base + 0x05A43A28
blunderbomb_offsets = [0x10, 0xA0, 0x2C8, 0x1F8, 0xF0, 0xA0, 0x128C]

def set_blunderbombs_dynamic(amount: int):
    final_addr = safe_resolve(blunderbomb_ptr_base, blunderbomb_offsets)
    if final_addr is None:
        print("Blunderbombs pointer chain broken ❌")
        return False
    try:
        pm.write_int(final_addr, amount)
        print(f"Blunderbombs set to {amount} 💣")
        return True
    except Exception as e:
        print(f"Blunderbombs write failed: {e} ❌")
        return False

# ---------------------------------------------------------
# WEAPON POINTERS
# ---------------------------------------------------------
WEAPON_POINTERS = {
    "Pistol": {
        "base": module_base + 0x056E5B40,
        "offsets": [0x290, 0x20, 0x6B0, 0x20, 0x7A8, 0x20, 0xA10],
    },
    "Sniper": {
        "base": module_base + 0x05A43A28,
        "offsets": [0x0, 0x20, 0x608, 0x20, 0x770, 0xA0, 0xA14],
    },
    "Blunderbuss": {
        "base": module_base + 0x05A515E0,
        "offsets": [0x1B8, 0x10, 0x30, 0xA8, 0x40, 0x2C8, 0xA18],
    },
}

def set_ammo_dynamic(weapon: str, amount: int):
    data = WEAPON_POINTERS[weapon]
    final_addr = safe_resolve(data["base"], data["offsets"])
    if final_addr is None:
        print(f"{weapon} pointer chain broken ❌")
        return False
    try:
        pm.write_int(final_addr, amount)
        print(f"{weapon} ammo set to {amount} 🔫")
        return True
    except Exception as e:
        print(f"{weapon} write failed: {e} ❌")
        return False

# ---------------------------------------------------------
# GODMODE
# ---------------------------------------------------------
HEALTH_BASE_OFFSET = 0x05A38FB0
HEALTH_POINTER_CHAIN = [0x30, 0x50, 0x318, 0x300, 0xA0, 0x50, 0x974]

godmode_enabled = False
health_final_addr = None

def resolve_chain_simple(pm, base, chain):
    addr = pm.read_longlong(base)
    for off in chain[:-1]:
        addr = pm.read_longlong(addr + off)
    return addr + chain[-1]

health_final_addr = resolve_chain_simple(
    pm, module_base + HEALTH_BASE_OFFSET, HEALTH_POINTER_CHAIN
)

def godmode_loop():
    global godmode_enabled
    while True:
        if godmode_enabled and health_final_addr:
            try:
                pm.write_int(health_final_addr, 1079574528)
            except:
                pass
        time.sleep(0.03)

threading.Thread(target=godmode_loop, daemon=True).start()

# ---------------------------------------------------------
# >>> ADD: INFINITY AMMO
# ---------------------------------------------------------
infinity_ammo_enabled = False

def infinity_ammo_loop():
    global infinity_ammo_enabled
    while True:
        if infinity_ammo_enabled:
            for weapon in WEAPON_POINTERS:
                try:
                    addr = safe_resolve(
                        WEAPON_POINTERS[weapon]["base"],
                        WEAPON_POINTERS[weapon]["offsets"]
                    )
                    if addr:
                        pm.write_int(addr, 5)
                except:
                    pass
        time.sleep(0.1)

threading.Thread(target=infinity_ammo_loop, daemon=True).start()

# ---------------------------------------------------------
# UI HEADER
# ---------------------------------------------------------
header = ctk.CTkLabel(
    root,
    text="Pizza Mega Hack 🍕",
    font=ctk.CTkFont(size=50, weight="bold"),
    fg_color="#0077CC",
    height=80
)
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
# PAGE SYSTEM
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

for b in ["Player", "Weapon", "Misc"]:
    ctk.CTkButton(
        left_menu,
        text=b,
        height=45,
        corner_radius=8,
        font=ctk.CTkFont(size=22, weight="bold"),
        command=lambda p=b: show_page(p)
    ).pack(fill="x", padx=15, pady=10)

# ---------------------------------------------------------
# PLAYER PAGE
# ---------------------------------------------------------
def build_player_page():
    content = ctk.CTkFrame(right_panel, fg_color="black")
    content.pack(pady=30, padx=20, anchor="nw")
    ctk.CTkCheckBox(
        content,
        text="ESP 💀",
        font=ctk.CTkFont(size=18)
    ).pack(anchor="w", pady=10, padx=10)

# ---------------------------------------------------------
# WEAPON PAGE
# ---------------------------------------------------------
def build_weapon_page():
    content = ctk.CTkFrame(right_panel, fg_color="black")
    content.pack(pady=30, padx=20, anchor="nw")
    ctk.CTkCheckBox(content, text="Aimbot 🎯", font=ctk.CTkFont(size=18)).pack(anchor="w", pady=10)
    ctk.CTkCheckBox(content, text="Machinegun 🔫", font=ctk.CTkFont(size=18)).pack(anchor="w", pady=10)

# ---------------------------------------------------------
# MISC PAGE
# ---------------------------------------------------------
def build_misc_page():
    content = ctk.CTkFrame(right_panel, fg_color="black")
    content.pack(pady=30, padx=20, anchor="nw", fill="both")

    # ---- Bananas UI ----
    row_banana = ctk.CTkFrame(content, fg_color="black")
    row_banana.pack(pady=10, anchor="w")
    entry_banana = ctk.CTkEntry(row_banana, width=200, placeholder_text="Banana amount", font=ctk.CTkFont(size=18))
    entry_banana.pack(side="left", padx=10)
    ctk.CTkButton(
        row_banana,
        text="Set",
        command=lambda: set_bananas_dynamic(int(entry_banana.get())),
        font=ctk.CTkFont(size=18)
    ).pack(side="left", padx=10)
    ctk.CTkLabel(row_banana, text="Bananas 🍌", font=ctk.CTkFont(size=20)).pack(side="left")

    # ---- Blunderbombs UI ----
    row_bb = ctk.CTkFrame(content, fg_color="black")
    row_bb.pack(pady=10, anchor="w")
    entry_bb = ctk.CTkEntry(row_bb, width=200, placeholder_text="Blunderbombs amount", font=ctk.CTkFont(size=18))
    entry_bb.pack(side="left", padx=10)
    ctk.CTkButton(
        row_bb,
        text="Set",
        command=lambda: set_blunderbombs_dynamic(int(entry_bb.get())),
        font=ctk.CTkFont(size=18)
    ).pack(side="left", padx=10)
    ctk.CTkLabel(row_bb, text="Blunderbombs 💣", font=ctk.CTkFont(size=20)).pack(side="left")

    # ---- Godmode ----
    def toggle_godmode():
        global godmode_enabled
        godmode_enabled = bool(godmode_checkbox.get())
        print("Godmode ON ❤️‍🔥" if godmode_enabled else "Godmode OFF ❌")

    godmode_checkbox = ctk.CTkCheckBox(
        content,
        text="Godmode ❤️",
        font=ctk.CTkFont(size=20),
        command=toggle_godmode
    )
    godmode_checkbox.pack(anchor="w", pady=20, padx=20)

    # ---- >>> ADD: Infinity Ammo Checkbox ----
    def toggle_infinity_ammo():
        global infinity_ammo_enabled
        infinity_ammo_enabled = bool(inf_checkbox.get())
        print("Infinity Ammo ON ♾️" if infinity_ammo_enabled else "Infinity Ammo OFF ❌")

    inf_checkbox = ctk.CTkCheckBox(
        content,
        text="Infinity Ammo ♾️",
        font=ctk.CTkFont(size=20),
        command=toggle_infinity_ammo
    )
    inf_checkbox.pack(anchor="w", pady=10, padx=20)

# ---------------------------------------------------------
root.mainloop()
