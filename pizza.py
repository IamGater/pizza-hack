# import ctypes
# ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

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
print("Connecting to the game...")

try:
    pm = pymem.Pymem("PirateFS-Win64-Shipping.exe")
    module_base = pymem.process.module_from_name(pm.process_handle,
                                                 "PirateFS-Win64-Shipping.exe").lpBaseOfDll
    print("Connected to PirateFS!")
except Exception as e:
    print(f"Failed to connect: {e}")
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
banana_ptr_base = module_base + 0x05A38E78
banana_offsets = [0x10, 0x58, 0x20, 0x1F8, 0xB0, 0xA0, 0xC54]

def set_bananas_dynamic(amount: int):
    final_addr = safe_resolve(banana_ptr_base, banana_offsets)

    if final_addr is None:
        print("Bananas pointer chain broken 💀")
        return False

    try:
        pm.write_int(final_addr, amount)
        print(f"Bananas set to {amount} 🍌")
        return True
    except Exception as e:
        print(f"Bananas write failed: {e}")
        return False


# ---------------------------------------------------------
# BLUNDERBOMBS POINTER (новый)
# ---------------------------------------------------------
blunderbomb_ptr_base = module_base + 0x05902F18
blunderbomb_offsets = [0x30, 0x0, 0xC170, 0x40, 0x340, 0x10, 0x126C]

def set_blunderbombs_dynamic(amount: int):
    final_addr = safe_resolve(blunderbomb_ptr_base, blunderbomb_offsets)

    if final_addr is None:
        print("Blunderbombs pointer chain broken 💣")
        return False

    try:
        pm.write_int(final_addr, amount)
        print(f"Blunderbombs set to {amount} 💥")
        return True
    except Exception as e:
        print(f"Blunderbombs write failed: {e}")
        return False


# ---------------------------------------------------------
# WEAPON POINTERS
# ---------------------------------------------------------
WEAPON_POINTERS = {
    "Pistol": {
        "base": module_base + 0x05A38E78,
        "offsets": [0x118, 0x20, 0x20, 0x150, 0x8, 0x1E0, 0x9C8],
    },
    "Sniper": {
        "base": module_base + 0x05690DF0,
        "offsets": [0x120, 0x710, 0x20, 0x258, 0x268, 0xA0, 0x9F4],
    },
    "Blunderbuss": {
        "base": module_base + 0x059AC138,
        "offsets": [0x18, 0x8, 0x18, 0x84, 0x70, 0x20, 0x9F8],
    },
}

def set_ammo_dynamic(weapon: str, amount: int):
    data = WEAPON_POINTERS[weapon]
    final_addr = safe_resolve(data["base"], data["offsets"])

    if final_addr is None:
        print(f"{weapon} pointer chain broken 💥")
        return False

    try:
        pm.write_int(final_addr, amount)
        print(f"{weapon} ammo set to {amount} 🔫")
        return True
    except Exception as e:
        print(f"{weapon} write failed: {e}")
        return False


# ---------------------------------------------------------
# HEADER UI
# ---------------------------------------------------------
header = ctk.CTkLabel(root,
                      text="Pizza Mega Hack 🍕",
                      font=ctk.CTkFont(size=50, weight="bold"),
                      fg_color="#0077CC",
                      height=80)
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


menu_buttons = ["Player", "Weapon", "Misc"]

for b in menu_buttons:
    ctk.CTkButton(left_menu,
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

    ctk.CTkCheckBox(content, text="Bone ESP 💀",
                    font=ctk.CTkFont(size=18)).pack(anchor="w", pady=10, padx=10)


# ---------------------------------------------------------
# WEAPON PAGE
# ---------------------------------------------------------
def build_weapon_page():
    content = ctk.CTkFrame(right_panel, fg_color="black")
    content.pack(pady=30, padx=20, anchor="nw")

    ctk.CTkCheckBox(content, text="Silent Aimbot 🎯",
                    font=ctk.CTkFont(size=18)).pack(anchor="w", pady=10, padx=10)

    ctk.CTkCheckBox(content, text="Machinegun 🔫",
                    font=ctk.CTkFont(size=18)).pack(anchor="w", pady=10, padx=10)


# ---------------------------------------------------------
# MISC PAGE (BANANAS + BLUNDERBOMBS + AMMO)
# ---------------------------------------------------------
def build_misc_page():
    content = ctk.CTkFrame(right_panel, fg_color="black")
    content.pack(pady=30, padx=20, anchor="nw", fill="both")

    # ---------------- BANANAS -----------------
    row_banana = ctk.CTkFrame(content, fg_color="black")
    row_banana.pack(pady=10, anchor="w")

    entry_banana = ctk.CTkEntry(row_banana, width=200, placeholder_text="Banana amount",
                                font=ctk.CTkFont(size=18))
    entry_banana.pack(side="left", padx=10)

    def add_bananas():
        try:
            value = int(entry_banana.get())
            set_bananas_dynamic(value)
        except ValueError:
            print("Bananas: invalid number ❌")

    ctk.CTkButton(row_banana, text="Set", width=80,
                  font=ctk.CTkFont(size=18),
                  command=add_bananas).pack(side="left", padx=10)

    ctk.CTkLabel(row_banana, text="Bananas 🍌",
                 font=ctk.CTkFont(size=20)).pack(side="left", padx=10)

    # ---------------- BLUNDERBOMBS (новый) -----------------
    row_blunderbombs = ctk.CTkFrame(content, fg_color="black")
    row_blunderbombs.pack(pady=10, anchor="w")

    entry_blunderbombs = ctk.CTkEntry(
        row_blunderbombs,
        width=200,
        placeholder_text="Blunderbombs amount",
        font=ctk.CTkFont(size=18)
    )
    entry_blunderbombs.pack(side="left", padx=10)

    def add_blunderbombs():
        try:
            value = int(entry_blunderbombs.get())
            set_blunderbombs_dynamic(value)
        except ValueError:
            print("Blunderbombs: invalid number ❌")

    ctk.CTkButton(
        row_blunderbombs,
        text="Set",
        width=80,
        font=ctk.CTkFont(size=18),
        command=add_blunderbombs
    ).pack(side="left", padx=10)

    ctk.CTkLabel(
        row_blunderbombs,
        text="Blunderbombs 💣",
        font=ctk.CTkFont(size=20)
    ).pack(side="left", padx=10)

    # ---------------- AMMO (UNIVERSAL HANDLER) -----------------
    def add_ammo(weapon: str, entry_widget: ctk.CTkEntry):
        try:
            value = int(entry_widget.get())
            set_ammo_dynamic(weapon, value)
        except ValueError:
            print(f"{weapon}: invalid number ❌")

    # --- BLUNDERBUSS ---
    row_blunder = ctk.CTkFrame(content, fg_color="black")
    row_blunder.pack(pady=10, anchor="w")

    entry_blunder = ctk.CTkEntry(row_blunder, width=200, placeholder_text="Blunderbuss Ammo",
                                 font=ctk.CTkFont(size=18))
    entry_blunder.pack(side="left", padx=10)

    ctk.CTkButton(row_blunder, text="Set", width=80,
                  font=ctk.CTkFont(size=18),
                  command=lambda: add_ammo("Blunderbuss", entry_blunder)).pack(side="left", padx=10)

    ctk.CTkLabel(row_blunder, text="Blunderbuss Ammo 🧨",
                 font=ctk.CTkFont(size=20)).pack(side="left", padx=10)

    # --- SNIPER ---
    row_sniper = ctk.CTkFrame(content, fg_color="black")
    row_sniper.pack(pady=10, anchor="w")

    entry_sniper = ctk.CTkEntry(row_sniper, width=200, placeholder_text="Sniper Ammo",
                                font=ctk.CTkFont(size=18))
    entry_sniper.pack(side="left", padx=10)

    ctk.CTkButton(row_sniper, text="Set", width=80,
                  font=ctk.CTkFont(size=18),
                  command=lambda: add_ammo("Sniper", entry_sniper)).pack(side="left", padx=10)

    ctk.CTkLabel(row_sniper, text="Sniper Ammo 🔫",
                 font=ctk.CTkFont(size=20)).pack(side="left", padx=10)

    # --- PISTOL ---
    row_pistol = ctk.CTkFrame(content, fg_color="black")
    row_pistol.pack(pady=10, anchor="w")

    entry_pistol = ctk.CTkEntry(row_pistol, width=200, placeholder_text="Pistol Ammo",
                                font=ctk.CTkFont(size=18))
    entry_pistol.pack(side="left", padx=10)

    ctk.CTkButton(row_pistol, text="Set", width=80,
                  font=ctk.CTkFont(size=18),
                  command=lambda: add_ammo("Pistol", entry_pistol)).pack(side="left", padx=10)

    ctk.CTkLabel(row_pistol, text="Pistol Ammo 🔫",
                 font=ctk.CTkFont(size=20)).pack(side="left", padx=10)


# ---------------------------------------------------------
root.mainloop()
