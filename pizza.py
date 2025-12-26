import ctypes
import sys
import tkinter as tk
import customtkinter as ctk
import pymem
from tkinter import ttk, colorchooser, filedialog
import json
import tkinter.font as tkfont
from typing import Iterable
import threading
import time
import math
from ctypes import wintypes
import os

sys.stdout.reconfigure(encoding='utf-8')

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# base menu color; header_color and button_color are equal to this
menu_base_color = "#0077CC"

# compute text contrast color (black on light backgrounds, white otherwise)
text_contrast_color = "#FFFFFF"

def _is_light_color(hexcol: str, threshold: int = 180) -> bool:
    try:
        h = hexcol.lstrip('#')
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        # perceived brightness
        brightness = (0.299 * r + 0.587 * g + 0.114 * b)
        return brightness >= threshold
    except Exception:
        return False

def darken_color(hexcol: str, amount: float = 0.15) -> str:
    try:
        hexcol = hexcol.lstrip('#')
        r = int(hexcol[0:2], 16)
        g = int(hexcol[2:4], 16)
        b = int(hexcol[4:6], 16)
        r = max(0, int(r * (1 - amount)))
        g = max(0, int(g * (1 - amount)))
        b = max(0, int(b * (1 - amount)))
        return f"#{r:02X}{g:02X}{b:02X}"
    except Exception:
        return hexcol

# compute current colors
header_color = menu_base_color
button_color = menu_base_color
button_hover_color = darken_color(button_color, 0.15)

def apply_ui_colors():
    global button_hover_color
    global text_contrast_color
    try:
        # recalc hover in case base changed
        button_hover_color = darken_color(button_color, 0.15)
    except Exception:
        pass
    try:
        # set text contrast based on menu color
        text_contrast_color = "#000000" if _is_light_color(menu_base_color) else "#FFFFFF"
    except Exception:
        text_contrast_color = "#FFFFFF"
    try:
        header.configure(fg_color=header_color, text_color=text_contrast_color)
    except Exception:
        pass
    try:
        # update immediate children in left_menu: only buttons get text_color changed,
        # checkboxes keep their own text color and must never be overwritten.
        for widget in left_menu.winfo_children():
            try:
                if isinstance(widget, ctk.CTkButton):
                    try:
                        widget.configure(fg_color=button_color, hover_color=button_hover_color, text_color=text_contrast_color)
                    except Exception:
                        try:
                            widget.configure(fg_color=button_color, hover_color=button_hover_color)
                        except Exception:
                            pass
                elif isinstance(widget, ctk.CTkCheckBox):
                    # DO NOT change text_color for checkboxes — preserve their original color
                    try:
                        widget.configure(fg_color=button_color, hover_color=button_hover_color)
                    except Exception:
                        try:
                            widget.configure(fg_color=button_color)
                        except Exception:
                            pass
                else:
                    # fallback for other widgets: try to set button-like colors including contrasting text
                    try:
                        widget.configure(fg_color=button_color, hover_color=button_hover_color, text_color=text_contrast_color)
                    except Exception:
                        try:
                            widget.configure(fg_color=button_color, hover_color=button_hover_color)
                        except Exception:
                            pass
            except Exception:
                pass
    except Exception:
        pass
    try:
        # рекурсивно применяем стиль ко всем виджетам меню и правой панели
        try:
            style_widget_recursive(left_menu)
        except Exception:
            pass
        try:
            style_widget_recursive(right_panel)
        except Exception:
            pass
    except Exception:
        pass

# --- color animation helpers for hover ---
def _hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def _rgb_to_hex(rgb):
    return '#%02x%02x%02x' % (max(0, min(255, int(rgb[0]))), max(0, min(255, int(rgb[1]))), max(0, min(255, int(rgb[2]))))

def _lerp(a, b, t):
    return a + (b - a) * t

def animate_widget_color(widget, start_hex, end_hex, duration=150, steps=10):
    try:
        # cancel previous animation if running
        try:
            if hasattr(widget, '_hover_anim_after') and widget._hover_anim_after:
                try:
                    widget.after_cancel(widget._hover_anim_after)
                except Exception:
                    pass
                widget._hover_anim_after = None
        except Exception:
            pass
        # compute start from stored current color if available to avoid jumps
        cur_hex = getattr(widget, '_current_fg', None) or start_hex
        start_rgb = _hex_to_rgb(cur_hex)
        end_rgb = _hex_to_rgb(end_hex)
        step = {'i': 0}
        step_duration = max(1, duration // max(1, steps))

        def _step():
            try:
                t = step['i'] / float(steps)
                r = _lerp(start_rgb[0], end_rgb[0], t)
                g = _lerp(start_rgb[1], end_rgb[1], t)
                b = _lerp(start_rgb[2], end_rgb[2], t)
                col = _rgb_to_hex((r, g, b))
                # update both fg_color and hover_color to avoid CTk internal hover conflicting
                try:
                    widget.configure(fg_color=col)
                except Exception:
                    pass
                try:
                    # попытка также установить hover_color, но в безопасном try
                    widget.configure(hover_color=col)
                except Exception:
                    pass
                # remember current color
                try:
                    widget._current_fg = col
                except Exception:
                    pass
                step['i'] += 1
                if step['i'] <= steps:
                    widget._hover_anim_after = widget.after(step_duration, _step)
                else:
                    widget._hover_anim_after = None
            except Exception:
                try:
                    widget._hover_anim_after = None
                except Exception:
                    pass

        _step()
    except Exception:
        pass

# added: recursively apply styles to buttons/checkboxes inside container
def style_widget_recursive(container):
    try:
        for w in container.winfo_children():
            try:
                if isinstance(w, ctk.CTkButton):
                    try:
                        w.configure(fg_color=button_color, hover_color=button_hover_color, text_color=text_contrast_color)
                    except Exception:
                        try:
                            w.configure(fg_color=button_color, hover_color=button_hover_color)
                        except Exception:
                            try:
                                w.configure(fg_color=button_color)
                            except Exception:
                                pass
                    # attach animated hover handlers once (also to children to catch events over inner widgets)
                    try:
                        if not getattr(w, '_hover_bind_attached', False):
                            def _on_enter(e, widget=w):
                                try:
                                    # use current stored color as start to avoid jump
                                    s = getattr(widget, '_current_fg', button_color) or button_color
                                    animate_widget_color(widget, s, button_hover_color, duration=120, steps=8)
                                except Exception:
                                    pass

                            def _on_leave(e, widget=w):
                                try:
                                    s = getattr(widget, '_current_fg', button_hover_color) or button_hover_color
                                    animate_widget_color(widget, s, button_color, duration=120, steps=8)
                                except Exception:
                                    pass

                            # bind to widget and all its children so enter/leave fire reliably
                            try:
                                w.bind("<Enter>", _on_enter)
                                w.bind("<Leave>", _on_leave)
                                for child in w.winfo_children():
                                    try:
                                        child.bind("<Enter>", _on_enter)
                                        child.bind("<Leave>", _on_leave)
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                            w._hover_bind_attached = True
                    except Exception:
                        pass
                elif isinstance(w, ctk.CTkCheckBox):
                    # DO NOT modify text_color for checkboxes — preserve their label color
                    try:
                        try:
                            w.configure(fg_color=button_color, hover_color=button_hover_color)
                        except Exception:
                            w.configure(fg_color=button_color)
                    except Exception:
                        pass
                    # attach animated hover handlers once (same behavior as buttons)
                    try:
                        if not getattr(w, '_hover_bind_attached', False):
                            def _on_enter_cb(e, widget=w):
                                try:
                                    s = getattr(widget, '_current_fg', button_color) or button_color
                                    animate_widget_color(widget, s, button_hover_color, duration=120, steps=8)
                                except Exception:
                                    pass

                            def _on_leave_cb(e, widget=w):
                                try:
                                    s = getattr(widget, '_current_fg', button_hover_color) or button_hover_color
                                    animate_widget_color(widget, s, button_color, duration=120, steps=8)
                                except Exception:
                                    pass

                            try:
                                w.bind("<Enter>", _on_enter_cb)
                                w.bind("<Leave>", _on_leave_cb)
                                for child in w.winfo_children():
                                    try:
                                        child.bind("<Enter>", _on_enter_cb)
                                        child.bind("<Leave>", _on_leave_cb)
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                            w._hover_bind_attached = True
                    except Exception:
                        pass
            except Exception:
                pass
            # recursively process child widgets
            try:
                if w.winfo_children():
                    style_widget_recursive(w)
            except Exception:
                pass
    except Exception:
        pass

# replace root creation with overlay-like small window (centered, frameless, topmost)
root = ctk.CTk()
root.title("PMH")
w, h = 900, 550
sw = ctypes.windll.user32.GetSystemMetrics(0)
sh = ctypes.windll.user32.GetSystemMetrics(1)
x = (sw - w) // 2
y = (sh - h) // 2
root.geometry(f"{w}x{h}+{x}+{y}")
root.overrideredirect(True)            # no titlebar
root.attributes("-topmost", True)      # keep on top
try:
    root.attributes("-alpha", 0.95)    # slight transparency
except Exception:
    pass

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
        "base": module_base + 0x05A38E78,
        "offsets": [0xE8, 0xA0, 0x840, 0x20, 0x6E0, 0xA0, 0xA10],
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
        time.sleep(0.01)

threading.Thread(target=godmode_loop, daemon=True).start()

# ---------------------------------------------------------
# INFINITY AMMO
# ---------------------------------------------------------
infinity_ammo_enabled = False

# ---------------------------------------------------------
# MACHINEGUN
# ---------------------------------------------------------
machine_gun_enabled = False

MACHINEGUN_POINTERS = {
    "Sniper": {
        "base": module_base + 0x05A515E0,
        "offsets": [0x288, 0x78, 0xA0, 0x50, 0x8B8, 0x20, 0xC08]
    },
    "Blunderbuss": {
        "base": module_base + 0x05A4D200,
        "offsets": [0xB0, 0x0, 0x30, 0x800, 0x20, 0xA0, 0x96C]
    },
    "Pistol": {
        "base": module_base + 0x05A38E78,
        "offsets": [0x158, 0xA0, 0x808, 0xA0, 0x7C0, 0x20, 0x96C]
    }
}

machine_pistol_enabled = False
machine_sniper_enabled = False
machine_blunderbuss_enabled = False

def machine_gun_loop():
    global machine_gun_enabled, machine_pistol_enabled, machine_sniper_enabled, machine_blunderbuss_enabled
    while True:
        if machine_gun_enabled:
            try:
                if machine_sniper_enabled:
                    addr = safe_resolve(MACHINEGUN_POINTERS["Sniper"]["base"], MACHINEGUN_POINTERS["Sniper"]["offsets"])
                    if addr:
                        pm.write_int(addr, 1)
                if machine_blunderbuss_enabled:
                    addr = safe_resolve(MACHINEGUN_POINTERS["Blunderbuss"]["base"], MACHINEGUN_POINTERS["Blunderbuss"]["offsets"])
                    if addr:
                        pm.write_int(addr, 1)
                if machine_pistol_enabled:
                    addr = safe_resolve(MACHINEGUN_POINTERS["Pistol"]["base"], MACHINEGUN_POINTERS["Pistol"]["offsets"])
                    if addr:
                        pm.write_int(addr, 1)
            except:
                pass
        time.sleep(0.01)

threading.Thread(target=machine_gun_loop, daemon=True).start()

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
        time.sleep(0.01)

threading.Thread(target=infinity_ammo_loop, daemon=True).start()

# ---------------------------------------------------------
# AIMBOT
# ---------------------------------------------------------
aimbot_enabled = False
aimbot_fov = 45.0  # degrees
aimbot_color = "#00FF88"
# whether to show the FOV circle in UI and overlay (default: enabled)
show_aimbot_fov = True

AIMBOT_POINTERS = {
	"LocalPlayer": {
		"base": module_base + 0x05A00000,
		"view_pitch_offset": 0x4,
		"view_yaw_offset": 0x8,
		"pos_offsets": [0x30, 0x34, 0x38],
	},
	"EntityList": {
		"base": module_base + 0x05B00000,
		"entity_size": 0x10,
		"pos_offsets": [0x30, 0x34, 0x38],
		"health_offset": 0xF8
	},
	"max_entities": 32
}

def calc_angles(local_pos, target_pos):
	(dx, dy, dz) = (target_pos[0] - local_pos[0], target_pos[1] - local_pos[1], target_pos[2] - local_pos[2])
	hyp = math.sqrt(dx * dx + dy * dy)
	if hyp == 0:
		return 0.0, 0.0
	pitch = -math.degrees(math.atan2(dz, hyp))
	yaw = math.degrees(math.atan2(dy, dx))
	# normalize yaw
	if yaw < -180: yaw += 360
	if yaw > 180: yaw -= 360
	return pitch, yaw

def read_vec3(base, offsets):
	try:
		x = pm.read_float(base + offsets[0])
		y = pm.read_float(base + offsets[1])
		z = pm.read_float(base + offsets[2])
		return (x, y, z)
	except Exception:
		return None

def is_in_fov(current_pitch, current_yaw, target_pitch, target_yaw, fov):
	# simple angle distance check
	dp = target_pitch - current_pitch
	dy = target_yaw - current_yaw
	# normalize
	while dy < -180: dy += 360
	while dy > 180: dy -= 360
	dist = math.sqrt(dp*dp + dy*dy)
	return dist <= fov

def aimbot_loop():
	global aimbot_enabled
	while True:
		if aimbot_enabled:
			try:
				# resolve local view pointer
				lp_base = safe_resolve(AIMBOT_POINTERS["LocalPlayer"]["base"], [0x0])  # adapt as needed
				el_base = AIMBOT_POINTERS["EntityList"]["base"]

				# try read current view angles
				view_pitch_addr = lp_base + AIMBOT_POINTERS["LocalPlayer"]["view_pitch_offset"] if lp_base else None
				view_yaw_addr = lp_base + AIMBOT_POINTERS["LocalPlayer"]["view_yaw_offset"] if lp_base else None
				current_pitch = pm.read_float(view_pitch_addr) if view_pitch_addr else 0.0
				current_yaw = pm.read_float(view_yaw_addr) if view_yaw_addr else 0.0

				# read local position
				local_pos = read_vec3(lp_base, AIMBOT_POINTERS["LocalPlayer"]["pos_offsets"]) if lp_base else None
				if not local_pos:
					time.sleep(0.05)
					continue

				best_dist = 1e9
				best_angles = None

				for i in range(AIMBOT_POINTERS["max_entities"]):
					ent_base = el_base + i * AIMBOT_POINTERS["EntityList"]["entity_size"]
					try:
						health = pm.read_int(ent_base + AIMBOT_POINTERS["EntityList"]["health_offset"])
						if health <= 0:
							continue
					except Exception:
						continue
					target_pos = read_vec3(ent_base, AIMBOT_POINTERS["EntityList"]["pos_offsets"])
					if not target_pos:
						continue

					pitch, yaw = calc_angles(local_pos, target_pos)
					if is_in_fov(current_pitch, current_yaw, pitch, yaw, aimbot_fov):
						dang = math.hypot(pitch - current_pitch, yaw - current_yaw)
						if dang < best_dist:
							best_dist = dang
							best_angles = (pitch, yaw)
				if best_angles and view_pitch_addr and view_yaw_addr:
					try:
						pm.write_float(view_pitch_addr, float(best_angles[0]))
						pm.write_float(view_yaw_addr, float(best_angles[1]))
					except Exception:
						pass
			except Exception:
				pass
		time.sleep(0.01)

threading.Thread(target=aimbot_loop, daemon=True).start()

# ---------------------------------------------------------
# UI HEADER
# ---------------------------------------------------------
header = ctk.CTkLabel(
    root,
    text="Pizza Mega Hack 🍕",
    font=ctk.CTkFont(size=50, weight="bold"),
    fg_color="#0077CC",
    text_color=text_contrast_color,
    height=80
)
header.pack(fill="x")

# after header is created, add dragging handlers so overlay-like window can be moved
# (insert right after header.pack(fill="x"))
def _start_move(event):
    try:
        root._drag_x = event.x_root - root.winfo_x()
        root._drag_y = event.y_root - root.winfo_y()
    except Exception:
        pass

def _on_move(event):
    try:
        nx = event.x_root - root._drag_x
        ny = event.y_root - root._drag_y
        root.geometry(f"+{nx}+{ny}")
    except Exception:
        pass

# bind dragging
try:
    header.bind("<ButtonPress-1>", _start_move)
    header.bind("<B1-Motion>", _on_move)
except Exception:
    pass

# ---------------------------------------------------------
# MAIN AREA
# ---------------------------------------------------------
main_area = ctk.CTkFrame(root, fg_color="black")
main_area.pack(fill="both", expand=True)

left_menu = ctk.CTkFrame(main_area, width=200, fg_color="#111111")
left_menu.pack(side="left", fill="y")

right_panel = ctk.CTkFrame(main_area, fg_color="black")
right_panel.pack(side="right", fill="both", expand=True)

# initialize overlay (canvas on a transparent fullscreen Toplevel)
_overlay = None
_overlay_canvas = None
_menu_visible = True

def _create_overlay():
    global _overlay, _overlay_canvas
    try:
        _overlay = tk.Toplevel(root)
        _overlay.overrideredirect(True)
        _overlay.attributes("-topmost", True)
        sw = ctypes.windll.user32.GetSystemMetrics(0)
        sh = ctypes.windll.user32.GetSystemMetrics(1)
        _overlay.geometry(f"{sw}x{sh}+0+0")
        _overlay.config(bg="black")
        try:
            _overlay.wm_attributes("-transparentcolor", "black")
        except Exception:
            pass
        # make overlay semi-transparent (alpha 0.95 like the menu)
        try:
            _overlay.attributes("-alpha", 0.95)
        except Exception:
            pass
        _overlay_canvas = tk.Canvas(_overlay, width=sw, height=sh, bg="black", highlightthickness=0)
        _overlay_canvas.pack()
        _overlay.update_idletasks()
        try:
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x80000
            WS_EX_TRANSPARENT = 0x20
            hwnd = _overlay.winfo_id()
            cur = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, cur | WS_EX_LAYERED | WS_EX_TRANSPARENT)
            LWA_COLORKEY = 0x1
            colorkey = 0x000000
            ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, colorkey, 0, LWA_COLORKEY)
        except Exception:
            pass
    except Exception:
        pass

# create the overlay so drawing functions have a canvas
try:
    _create_overlay()
except Exception:
    pass

# HOTKEY (global hook for F12)
_hotkey_id = 1
_hotkey_vk = 0x7B  # VK_F12
_hotkey_mod = 0
_hotkey_running = False
_hotkey_thread = None
_overlay_visible = True
_selected_hotkey = 0x7B  # Default F12
_selected_hotkey_name = "F12"  # Store the key name

def _toggle_menu():
    global _menu_visible
    try:
        if _menu_visible:
            # fade out animation (faster)
            # сделать закрытие чуть медленнее и плавнее
            _animate_alpha(0.95, 0.0, duration=80, is_closing=True)
            _menu_visible = False
        else:
            # fade in animation (faster)
            # сделать открытие чуть медленнее и плавнее
            _animate_alpha(0.0, 0.95, duration=80, is_closing=False)
            _menu_visible = True
    except Exception:
        pass

def _animate_alpha(start_alpha, end_alpha, duration=30, is_closing=False, on_complete=None):
    """Animate window alpha from start to end over duration milliseconds.
    Optionally call on_complete() after animation finishes."""
    # увеличить число шагов для более плавной и чуть более медленной анимации
    steps = 12
    # сделать фейд чуть быстрее: уменьшить дефолт при использовании стандартного значения
    if duration == 60:
        duration = 40
    step_duration = max(1, duration // steps)
    current_step = [0]
    # ensure starting alpha set
    try:
        root.attributes("-alpha", start_alpha)
    except Exception:
        pass

    def animate_step():
        if current_step[0] <= steps:
            progress = current_step[0] / steps
            current_alpha = start_alpha + (end_alpha - start_alpha) * progress
            try:
                root.attributes("-alpha", current_alpha)
            except Exception:
                pass
            current_step[0] += 1
            root.after(step_duration, animate_step)
        else:
            # Ensure final value is set
            try:
                root.attributes("-alpha", end_alpha)
            except Exception:
                pass
            # call completion callback if provided
            if callable(on_complete):
                try:
                    on_complete()
                except Exception:
                    pass

    animate_step()

# Global hook constants
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

# совместимый тип ULONG_PTR (fallback если wintypes.ULONG_PTR отсутствует)
ULONG_PTR_TYPE = getattr(wintypes, "ULONG_PTR", ctypes.c_void_p)

# структура для KBDLLHOOKSTRUCT
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR_TYPE),
    ]

# корректный тип для хук-процедуры
HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

# Define keyboard hook function (fixed: read vkCode properly)
def _keyboard_hook_proc(nCode, wParam, lParam):
    if nCode >= 0 and wParam == WM_KEYDOWN:
        try:
            kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            vk = int(kb.vkCode)
            if vk == _selected_hotkey:
                # немедленный вызов в основном потоке
                try:
                    root.after(0, _toggle_menu)
                except Exception:
                    _toggle_menu()
        except Exception:
            pass
    return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)

_hook_proc_type = HOOKPROC
_hook_proc = _hook_proc_type(_keyboard_hook_proc)
_hook_handle = None

def register_global_hook():
    global _hook_handle
    try:
        hmod = ctypes.windll.kernel32.GetModuleHandleW(None)
        if not hmod:
            hmod = 0
        _hook_handle = ctypes.windll.user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            _hook_proc,
            hmod,
            0
        )
        if _hook_handle:
            print("Global keyboard hook registered ✅")
            return True
        else:
            print("Failed to register global keyboard hook, trying fallback... ⚠️")
            # Fallback: use thread-based hotkey instead
            threading.Thread(target=_hotkey_thread_listener, daemon=True).start()
            print("Fallback hotkey listener started ✅")
            return True
    except Exception as e:
        print(f"Hook error: {e} ⚠️, using fallback...")
        threading.Thread(target=_hotkey_thread_listener, daemon=True).start()
        print("Fallback hotkey listener started ✅")
        return True

def _hotkey_thread_listener():
    """Fallback: listen for selected hotkey in separate thread using GetAsyncKeyState"""
    while True:
        try:
            state = ctypes.windll.user32.GetAsyncKeyState(_selected_hotkey)
            # проверяем только старший бит — клавиша нажата
            if state & 0x8000:
                # сразу запланировать переключение в основном потоке
                try:
                    root.after(0, _toggle_menu)
                except Exception:
                    _toggle_menu()
                # дождаться отпускания клавиши, чтобы не сработало многократно
                while True:
                    try:
                        st2 = ctypes.windll.user32.GetAsyncKeyState(_selected_hotkey)
                        if not (st2 & 0x8000):
                            break
                    except Exception:
                        break
                    time.sleep(0.01)
                # короткий cooldown
                time.sleep(0.08)
        except Exception:
            pass
        time.sleep(0.005)

def unregister_global_hook():
    global _hook_handle
    try:
        if _hook_handle:
            ctypes.windll.user32.UnhookWindowsHookEx(_hook_handle)
            _hook_handle = None
    except Exception:
        pass

def on_exit():
    try:
        # save default config on exit
        try:
            save_config_default()
        except Exception:
            pass
        unregister_global_hook()
    except Exception:
        pass
    try:
        root.destroy()
    except Exception:
        pass

# register global hook on startup
try:
    register_global_hook()
except Exception:
    pass

try:
    root.protocol("WM_DELETE_WINDOW", on_exit)
except Exception:
    pass

# ---------------------------------------------------------
# PAGE SYSTEM
# ---------------------------------------------------------
# helper: create/destroy overlay covering only right_panel
def _create_right_panel_overlay():
    try:
        # ensure geometry updated
        right_panel.update_idletasks()
        rx = right_panel.winfo_rootx()
        ry = right_panel.winfo_rooty()
        rw = right_panel.winfo_width()
        rh = right_panel.winfo_height()
        if rw <= 0 or rh <= 0:
            return None
        ov = tk.Toplevel(root)
        ov.overrideredirect(True)
        ov.attributes("-topmost", True)
        ov.geometry(f"{rw}x{rh}+{rx}+{ry}")
        ov.config(bg="black")
        try:
            ov.attributes("-alpha", 0.0)
        except Exception:
            pass
        return ov
    except Exception:
        return None

def _animate_overlay_alpha(ov, start_alpha, end_alpha, duration=60, on_complete=None):
    try:
        # увеличить шаги и дефолтную длительность для более плавного, чуть более медленного фейда
        steps = 12
        # сделать фейд чуть быстрее: уменьшить дефолт при использовании стандартного значения
        if duration == 60:
            duration = 40
        step_duration = max(1, duration // steps)
        current = [0]
        try:
            ov.attributes("-alpha", start_alpha)
        except Exception:
            pass
        def step():
            if current[0] <= steps:
                t = current[0] / steps
                a = start_alpha + (end_alpha - start_alpha) * t
                try:
                    ov.attributes("-alpha", a)
                except Exception:
                    pass
                current[0] += 1
                root.after(step_duration, step)
            else:
                try:
                    ov.attributes("-alpha", end_alpha)
                except Exception:
                    pass
                if callable(on_complete):
                    try:
                        on_complete()
                    except Exception:
                        pass
        step()
    except Exception:
        if callable(on_complete):
            try:
                on_complete()
            except Exception:
                pass

def show_page(page):
    """Fade only right_panel content: overlay fades in (covering), switch content, fade out and destroy overlay."""
    try:
        def do_switch_and_fadeout(ov):
            # switch content while overlay hides content
            for widget in right_panel.winfo_children():
                widget.destroy()
            if page == "Misc":
                build_misc_page()
            elif page == "Weapon":
                build_weapon_page()
            elif page == "Player":
                build_player_page()
            elif page == "Settings":
                build_settings_page()
            try:
                apply_ui_colors()
                style_widget_recursive(right_panel)
            except Exception:
                pass

            # обеспечить отрисовку новых виджетов перед началом fade-out
            try:
                right_panel.update_idletasks()
                root.update()
            except Exception:
                pass

            # небольшая пауза чтобы тяжёлые виджеты успели отрисоваться (можно уменьшить)
            def start_fade_out():
                # fade overlay out to reveal new content, then destroy it
                def after_hide():
                    try:
                        ov.destroy()
                    except Exception:
                        pass
                _animate_overlay_alpha(ov, 0.95, 0.0, duration=40, on_complete=after_hide)

            try:
                # убрать искусственную задержку — переключаемся сразу, чтобы элементы загружались без лишней задержки
                root.after(0, start_fade_out)
            except Exception:
                # fallback сразу запустить fade-out если after не сработал
                start_fade_out()

        ov = _create_right_panel_overlay()
        if not ov:
            # fallback: immediate switch
            for widget in right_panel.winfo_children():
                widget.destroy()
            if page == "Misc":
                build_misc_page()
            elif page == "Weapon":
                build_weapon_page()
            elif page == "Player":
                build_player_page()
            elif page == "Settings":
                build_settings_page()
            try:
                apply_ui_colors()
                style_widget_recursive(right_panel)
            except Exception:
                pass
            return

        # fade overlay in then switch content
        _animate_overlay_alpha(ov, 0.0, 0.95, duration=40, on_complete=lambda: do_switch_and_fadeout(ov))
    except Exception:
        pass

# восстановим текущую страницу и helper для открытия страницы (обновляет current_page)
current_page = "Player"
def open_page(p):
    global current_page
    current_page = p
    show_page(p)

# создаём кнопки вкладок в левом меню (Player/Weapon/Misc/Settings)
for b in ["Player", "Weapon", "Misc", "Settings"]:
    ctk.CTkButton(
        left_menu,
        text=b,
        height=45,
        corner_radius=8,
        font=ctk.CTkFont(size=22, weight="bold"),
        fg_color=button_color,
        hover_color=button_hover_color,
        command=lambda p=b: open_page(p)
    ).pack(fill="x", padx=15, pady=10)

# применим цвета к только что созданным кнопкам
try:
    apply_ui_colors()
except Exception:
    pass

# try load default config and build initial page
try:
    load_config_default()
except Exception:
    pass
try:
    show_page(current_page)
except Exception:
    # fallback: build player page directly
    try:
        for widget in right_panel.winfo_children():
            widget.destroy()
        build_player_page()
    except Exception:
        pass

# default config path for autosave/autoload
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "pizza_config.json")

def save_config_default():
    try:
        cfg = get_config_dict()
        with open(DEFAULT_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def load_config_default():
    try:
        if os.path.exists(DEFAULT_CONFIG_PATH):
            with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            apply_config(cfg)
            print(f"Default config loaded: {DEFAULT_CONFIG_PATH}")
            return True
    except Exception as e:
        print(f"Failed to load default config: {e}")
    return False

# ---------------------------------------------------------
# PLAYER PAGE
# ---------------------------------------------------------
# ------------------ ESP: globals and placeholder offsets ------------------
esp_enabled = False

# ESP visual settings (user-configurable)
esp_box_color = "#00FF88"
esp_show_boxes = True
esp_show_health = True
esp_box_scale = 1.0
esp_box_outline_width = 2

ESP_PLACEHOLDERS = {
    "EntityList": {
        "base": module_base + 0x05B00000,            # base address of entity array (example)
        "entity_size": 0x10,                         # size/stride of entity structure
        "pos": {
            "base": module_base + 0x05B00000,        # base for positions (may match EntityList.base)
            "offsets": {"x": 0x30, "y": 0x34, "z": 0x38}  # PLACEHOLDERS: replace with real offsets
        },
        "health": {
            "base": module_base + 0x05B00000,        # base for health (may match)
            "offset": 0xF8                           # PLACEHOLDER: replace with real health offset
        },
        "name": {
            "base": module_base + 0x05B00000,
            "offset": 0x0
        }
    },
    "max_entities": 32
}

def world_to_screen_local(local_pos, current_pitch, current_yaw, target_pos, sw, sh):
    """Simple projection approximation using angle offset (used instead of real matrix)."""
    try:
        pitch, yaw = calc_angles(local_pos, target_pos)
        dp = pitch - (current_pitch or 0.0)
        dy = yaw - (current_yaw or 0.0)
        while dy < -180: dy += 360
        while dy > 180: dy -= 360
        cx = sw // 2
        cy = sh // 2
        max_r = min(cx, cy) - 60
        # Нормируем по текущему aimbot_fov (безопасно >0)
        fov = max(1.0, aimbot_fov)
        x = cx + int((dy / fov) * max_r)
        y = cy - int((dp / fov) * max_r)
        return x, y
    except Exception:
        return None, None

def build_player_page():
    content = ctk.CTkFrame(right_panel, fg_color="black")
    content.pack(pady=30, padx=20, anchor="nw")
    # ESP checkbox toggles esp_enabled and redraws the overlay
    def toggle_esp():
        global esp_enabled
        esp_enabled = bool(esp_checkbox.get())
        try:
            _draw_overlay_once()
        except Exception:
            pass
        try:
            draw_esp_preview()
        except Exception:
            pass
        print("ESP ON 💀" if esp_enabled else "ESP OFF ❌")

    esp_checkbox = ctk.CTkCheckBox(
        content,
        text="ESP 💀",
        font=ctk.CTkFont(size=18),
        command=toggle_esp
    )
    try:
        if esp_enabled:
            esp_checkbox.select()
        else:
            esp_checkbox.deselect()
    except Exception:
        pass
    esp_checkbox.pack(anchor="w", pady=10, padx=10)
    # --- ESP visual options: boxes, health display, color and scale ---
    def toggle_esp_boxes():
        global esp_show_boxes
        try:
            esp_show_boxes = bool(esp_boxes_cb.get())
        except Exception:
            esp_show_boxes = False
        try:
            _draw_overlay_once()
        except Exception:
            pass
        try:
            draw_esp_preview()
        except Exception:
            pass


    def toggle_esp_health():
        global esp_show_health
        try:
            esp_show_health = bool(esp_health_cb.get())
        except Exception:
            esp_show_health = False
        try:
            _draw_overlay_once()
        except Exception:
            pass
        try:
            draw_esp_preview()
        except Exception:
            pass

    def choose_esp_color():
        global esp_box_color
        try:
            col = colorchooser.askcolor(title="Choose ESP box color")[1]
            if col:
                esp_box_color = col
                try:
                    esp_color_btn.configure(fg_color=esp_box_color)
                except Exception:
                    pass
                try:
                    _draw_overlay_once()
                except Exception:
                    pass
        except Exception:
            pass
        try:
            draw_esp_preview()
        except Exception:
            pass

    def set_box_scale(val):
        global esp_box_scale
        try:
            esp_box_scale = float(val)
        except Exception:
            try:
                esp_box_scale = float(int(val))
            except Exception:
                esp_box_scale = 1.0
        try:
            _draw_overlay_once()
        except Exception:
            pass
        try:
            draw_esp_preview()
        except Exception:
            pass

    # layout: preview (left) + controls (right) similar to Aimbot tab
    esp_frame = ctk.CTkFrame(content, fg_color="black")
    esp_frame.pack(anchor="w", pady=6, padx=10)

    preview_size = 220
    preview_canvas = tk.Canvas(esp_frame, width=preview_size, height=preview_size, bg="#0b0b0b", highlightthickness=0)
    preview_canvas.pack(side="left", padx=(10,20))

    def draw_esp_preview():
        try:
            preview_canvas.delete("all")
            cx = cy = preview_size // 2

            # compute base short/long sides and apply proportional scale
            col = esp_box_color or "#00FF88"
            base_short = max(6, int(preview_size * 0.18))
            base_long = max(10, int(base_short * 1.7))
            short_side = max(4, int(base_short * esp_box_scale))
            long_side = max(6, int(base_long * esp_box_scale))

            # short side should be horizontal (rotate/flip rectangle)
            box_w = short_side
            box_h = long_side

            left = cx - box_w // 2
            right = cx + box_w // 2
            top = cy - box_h // 2
            bottom = cy + box_h // 2

            # clamp to canvas bounds (leave 2px margin)
            left = max(2, left)
            top = max(2, top)
            right = min(preview_size - 2, right)
            bottom = min(preview_size - 2, bottom)

            if esp_show_boxes:
                try:
                    # if ESP disabled, show gray like aimbot preview
                    draw_col = (esp_box_color if esp_enabled else "#666666")
                    preview_canvas.create_rectangle(left, top, right, bottom, outline=draw_col, width=max(1, int(esp_box_outline_width)))
                except Exception:
                    pass
            else:
                # draw faint crosshair when boxes disabled
                ch = 10
                preview_canvas.create_line(cx - ch, cy, cx + ch, cy, fill="#666666")
                preview_canvas.create_line(cx, cy - ch, cx, cy + ch, fill="#666666")

            if esp_show_health:
                try:
                    # draw HP text inside top-left of the box but ensure visibility
                    tx = left + 4
                    ty = max(4, top - 12)
                    preview_canvas.create_text(tx, ty, anchor="nw", text="HP:100", fill="#FFFFFF", font=("Arial", 9))
                except Exception:
                    pass
        except Exception:
            pass

    control_frame = ctk.CTkFrame(esp_frame, fg_color="black")
    control_frame.pack(side="left", fill="both", expand=True)

    esp_boxes_cb = ctk.CTkCheckBox(control_frame, text="Show Boxes", font=ctk.CTkFont(size=16), command=toggle_esp_boxes)
    try:
        if esp_show_boxes:
            esp_boxes_cb.select()
        else:
            esp_boxes_cb.deselect()
    except Exception:
        pass
    esp_boxes_cb.pack(anchor="w", pady=(6,2), padx=10)

    esp_health_cb = ctk.CTkCheckBox(control_frame, text="Show Health", font=ctk.CTkFont(size=16), command=toggle_esp_health)
    try:
        if esp_show_health:
            esp_health_cb.select()
        else:
            esp_health_cb.deselect()
    except Exception:
        pass
    esp_health_cb.pack(anchor="w", pady=(2,10), padx=10)

    # color + scale row
    c_row = ctk.CTkFrame(control_frame, fg_color="black")
    c_row.pack(anchor="w", pady=6, padx=10)
    esp_color_btn = ctk.CTkButton(c_row, text="", width=30, height=30, fg_color=esp_box_color, command=choose_esp_color)
    esp_color_btn.pack(side="left", padx=(0,10))
    ctk.CTkLabel(c_row, text="Box color", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0,10))

    # scale slider
    scale_row = ctk.CTkFrame(control_frame, fg_color="black")
    scale_row.pack(anchor="w", pady=6, padx=10)
    ctk.CTkLabel(scale_row, text="Box scale:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0,8))
    scale_slider = ctk.CTkSlider(scale_row, from_=0.5, to=2.5, number_of_steps=20, command=set_box_scale)
    try:
        scale_slider.set(esp_box_scale)
    except Exception:
        pass
    scale_slider.pack(side="left", fill="x", expand=True)

    # preview is drawn above inside esp_frame
    try:
        draw_esp_preview()
    except Exception:
        pass

# ---------------------------------------------------------
# WEAPON PAGE
# ---------------------------------------------------------
def build_weapon_page():
    content = ctk.CTkFrame(right_panel, fg_color="black")
    content.pack(pady=30, padx=20, anchor="nw")

    # Aimbot checkbox + FOV visualizer
    def toggle_aimbot():
        global aimbot_enabled
        aimbot_enabled = bool(aimbot_checkbox.get())
        draw_fov()
        # обновляем только оверлей при взаимодействии
        try:
            _draw_overlay_once()
        except Exception:
            pass
        print("Aimbot ON 🎯" if aimbot_enabled else "Aimbot OFF ❌")

    aimbot_checkbox = ctk.CTkCheckBox(content, text="Aimbot 🎯", font=ctk.CTkFont(size=18), command=toggle_aimbot)
    try:
        if aimbot_enabled:
            aimbot_checkbox.select()
        else:
            aimbot_checkbox.deselect()
    except Exception:
        pass
    aimbot_checkbox.pack(anchor="w", pady=6)

    # FOV display (tk.Canvas inside CTkFrame)
    fov_frame = ctk.CTkFrame(content, fg_color="black")
    fov_frame.pack(anchor="w", pady=6)
    canvas_size = 220
    canvas = tk.Canvas(fov_frame, width=canvas_size, height=canvas_size, bg="#0b0b0b", highlightthickness=0)
    canvas.pack(side="left", padx=(10,20))

    fov_label = ctk.CTkLabel(fov_frame, text=f"FOV: {int(aimbot_fov)}°", font=ctk.CTkFont(size=16))
    fov_label.pack(anchor="n", pady=6)

    # color picker next to slider (for FOV color)
    def choose_color():
        global aimbot_color
        try:
            col = colorchooser.askcolor(title="Choose FOV color")[1]
            if col:
                aimbot_color = col
                try:
                    color_button.configure(fg_color=aimbot_color)
                except Exception:
                    pass
                draw_fov()
                try:
                    _draw_overlay_once()
                except Exception:
                    pass
        except Exception:
            pass

    color_button = ctk.CTkButton(fov_frame, text="", width=30, height=30, fg_color=aimbot_color, command=choose_color)
    color_button.pack(anchor="n", pady=6)

    def set_fov(val):
        global aimbot_fov
        try:
            aimbot_fov = float(val)
        except:
            aimbot_fov = float(int(val))
        try:
            fov_label.configure(text=f"FOV: {int(aimbot_fov)}°")
        except Exception:
            pass
        draw_fov()
        try:
            _draw_overlay_once()
        except Exception:
            pass

    fov_slider = ctk.CTkSlider(fov_frame, from_=5, to=180, number_of_steps=175, command=set_fov)
    try:
        fov_slider.set(aimbot_fov)
    except Exception:
        pass
    fov_slider.pack(anchor="n", pady=6, padx=(0,12), fill="x")

    def draw_fov():
            canvas.delete("all")
            cx = cy = canvas_size // 2
            max_radius = min(cx, cy) - 10
            radius = int((aimbot_fov / 180.0) * max_radius)
            outline = aimbot_color if aimbot_enabled else "#666666"
            try:
                # draw circle only if user wants to see it
                if show_aimbot_fov:
                    canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline=outline, width=2)
                # keep crosshair and center dot when aimbot enabled
                if aimbot_enabled:
                    ch = 10
                    canvas.create_line(cx - ch, cy, cx + ch, cy, fill=outline)
                    canvas.create_line(cx, cy - ch, cx, cy + ch, fill=outline)
                    canvas.create_oval(cx-3, cy-3, cx+3, cy+3, fill=outline, outline=outline)
                canvas.create_text(10, canvas_size-10, anchor="w", fill="#BBBBBB", text=f"FOV {int(aimbot_fov)}°")
            except Exception:
                pass

    draw_fov()

    # Machinegun and sub-checkboxes (existing logic)
    def toggle_machinegun():
        global machine_gun_enabled
        machine_gun_enabled = bool(machine_checkbox.get())
        state = "normal" if machine_gun_enabled else "disabled"
        for cb in (sniper_cb, blunderbuss_cb, pistol_cb):
            try:
                cb.configure(state=state)
            except Exception:
                pass
        try:
            _draw_overlay_once()  # обновляем статусный бокс
        except Exception:
            pass
        print("Machinegun ON 🔫" if machine_gun_enabled else "Machinegun OFF ❌")

    machine_checkbox = ctk.CTkCheckBox(
        content,
        text="Machinegun 🔫",
        font=ctk.CTkFont(size=18),
        command=toggle_machinegun
    )
    try:
        if machine_gun_enabled:
            machine_checkbox.select()
        else:
            machine_checkbox.deselect()
    except Exception:
        pass
    machine_checkbox.pack(anchor="w", pady=10)

    sub_frame = ctk.CTkFrame(content, fg_color="black")
    sub_frame.pack(padx=30, anchor="w")

    def on_sniper_toggle():
        global machine_sniper_enabled
        try:
            machine_sniper_enabled = bool(sniper_cb.get())
        except Exception:
            machine_sniper_enabled = False
        try:
            _draw_overlay_once()
        except Exception:
            pass

    def on_blunderbuss_toggle():
        global machine_blunderbuss_enabled
        try:
            machine_blunderbuss_enabled = bool(blunderbuss_cb.get())
        except Exception:
            machine_blunderbuss_enabled = False
        try:
            _draw_overlay_once()
        except Exception:
            pass

    def on_pistol_toggle():
        global machine_pistol_enabled
        try:
            machine_pistol_enabled = bool(pistol_cb.get())
        except Exception:
            machine_pistol_enabled = False
        try:
            _draw_overlay_once()
        except Exception:
            pass

    init_state = "normal" if machine_gun_enabled else "disabled"

    sniper_cb = ctk.CTkCheckBox(sub_frame, text="Sniper", font=ctk.CTkFont(size=16), state=init_state, command=on_sniper_toggle)
    try:
        if machine_sniper_enabled:
            sniper_cb.select()
        else:
            sniper_cb.deselect()
    except Exception:
        pass
    sniper_cb.pack(anchor="w", pady=2)

    blunderbuss_cb = ctk.CTkCheckBox(sub_frame, text="Blunderbuss", font=ctk.CTkFont(size=16), state=init_state, command=on_blunderbuss_toggle)
    try:
        if machine_blunderbuss_enabled:
            blunderbuss_cb.select()
        else:
            blunderbuss_cb.deselect()
    except Exception:
        pass
    blunderbuss_cb.pack(anchor="w", pady=2)

    pistol_cb = ctk.CTkCheckBox(sub_frame, text="Pistol", font=ctk.CTkFont(size=16), state=init_state, command=on_pistol_toggle)
    try:
        if machine_pistol_enabled:
            pistol_cb.select()
        else:
            pistol_cb.deselect()
    except Exception:
        pass
    pistol_cb.pack(anchor="w", pady=2)

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
        try:
            _draw_overlay_once()
        except Exception:
            pass
        print("Godmode ON ❤️‍🔥" if godmode_enabled else "Godmode OFF ❌")

    godmode_checkbox = ctk.CTkCheckBox(
        content,
        text="Godmode ❤️",
        font=ctk.CTkFont(size=20),
        command=toggle_godmode
    )
    try:
        if godmode_enabled:
            godmode_checkbox.select()
        else:
            godmode_checkbox.deselect()
    except Exception:
        pass
    godmode_checkbox.pack(anchor="w", pady=20, padx=20)

    # ---- Infinity Ammo ----
    def toggle_infinity_ammo():
        global infinity_ammo_enabled
        infinity_ammo_enabled = bool(inf_checkbox.get())
        try:
            _draw_overlay_once()
        except Exception:
            pass
        print("Infinity Ammo ON ♾️" if infinity_ammo_enabled else "Infinity Ammo OFF ❌")

    inf_checkbox = ctk.CTkCheckBox(
        content,
        text="Infinity Ammo ♾️",
        font=ctk.CTkFont(size=20),
        command=toggle_infinity_ammo
    )
    try:
        if infinity_ammo_enabled:
            inf_checkbox.select()
        else:
            inf_checkbox.deselect()
    except Exception:
        pass
    inf_checkbox.pack(anchor="w", pady=10, padx=20)

# ---------------------------------------------------------
# SETTINGS PAGE
# ---------------------------------------------------------
def build_settings_page():
    content = ctk.CTkFrame(right_panel, fg_color="black")
    content.pack(pady=30, padx=20, anchor="nw", fill="both")

    row = ctk.CTkFrame(content, fg_color="black")
    row.pack(anchor="w", pady=10)

    ctk.CTkLabel(row, text="Menu color:", font=ctk.CTkFont(size=18)).pack(side="left", padx=(0,10))

    def choose_menu_color():
        global menu_base_color, header_color, button_color, button_hover_color, aimbot_color, esp_box_color
        try:
            col = colorchooser.askcolor(title="Choose menu color")[1]
            if col:
                menu_base_color = col
                header_color = menu_base_color
                button_color = menu_base_color
                button_hover_color = darken_color(button_color, 0.15)
                # sync aimbot color with menu color
                aimbot_color = menu_base_color
                # also sync ESP box color with menu color
                try:
                    esp_box_color = menu_base_color
                except Exception:
                    pass
                try:
                    color_preview.configure(fg_color=menu_base_color)
                except Exception:
                    pass
                apply_ui_colors()
                # сразу рекурсивно обновляем виджеты в интерфейсе
                try:
                    style_widget_recursive(left_menu)
                except Exception:
                    pass
                try:
                    style_widget_recursive(right_panel)
                except Exception:
                    pass
                # перестроим текущую страницу, чтобы кнопки/отображение цвета обновились
                try:
                    show_page(current_page)
                except Exception:
                    pass
                try:
                    _draw_overlay_once()  # обновляем оверлей при смене цвета
                except Exception:
                    pass
        except Exception:
            pass

    color_preview = ctk.CTkButton(row, text="", width=40, height=30, fg_color=menu_base_color, command=choose_menu_color)
    color_preview.pack(side="left", padx=(0,10))

    ctk.CTkButton(row, text="Choose", command=choose_menu_color, font=ctk.CTkFont(size=16)).pack(side="left")

    # ---- Hotkey Selection ----
    hotkey_row = ctk.CTkFrame(content, fg_color="black")
    hotkey_row.pack(anchor="w", pady=20)

    ctk.CTkLabel(hotkey_row, text="Toggle hotkey:", font=ctk.CTkFont(size=18)).pack(side="left", padx=(0,10))

    hotkey_label = ctk.CTkLabel(hotkey_row, text=_selected_hotkey_name, font=ctk.CTkFont(size=16, weight="bold"), text_color="#00FF88")
    hotkey_label.pack(side="left", padx=(0,10))

    def set_hotkey():
        """Listen for next keypress and set it as hotkey"""
        global _selected_hotkey, _selected_hotkey_name
        hotkey_label.configure(text="Press any key...", text_color="#FFFF00")
        root.update()
        
        def wait_for_key(event):
            global _selected_hotkey, _selected_hotkey_name
            try:
                vk_code = event.keycode
                key_name = event.keysym.upper()
                _selected_hotkey = vk_code
                _selected_hotkey_name = key_name
                hotkey_label.configure(text=key_name, text_color="#00FF88")
                print(f"Hotkey changed to {key_name} (VK: {vk_code}) ✅")
                root.unbind("<KeyPress>")
            except Exception as e:
                print(f"Error setting hotkey: {e}")
                hotkey_label.configure(text=_selected_hotkey_name, text_color="#00FF88")
        
        root.bind("<KeyPress>", wait_for_key)

    ctk.CTkButton(hotkey_row, text="Set Hotkey", command=set_hotkey, font=ctk.CTkFont(size=16)).pack(side="left")

    # Save / Load row (верхний)
    save_load_row = ctk.CTkFrame(content, fg_color="black")
    save_load_row.pack(anchor="w", pady=10)

    ctk.CTkButton(
        save_load_row,
        text="Save Config",
        font=ctk.CTkFont(size=16),
        fg_color=button_color,
        hover_color=button_hover_color,
        command=save_config_dialog,
        width=120,
        height=36
    ).pack(side="left", padx=(0,6))

    ctk.CTkButton(
        save_load_row,
        text="Load Config",
        font=ctk.CTkFont(size=16),
        fg_color=button_color,
        hover_color=button_hover_color,
        command=load_config_dialog,
        width=120,
        height=36
    ).pack(side="left", padx=(6,0))

    # Exit button в отдельном нижнем ряду
    exit_row_bottom = ctk.CTkFrame(content, fg_color="black")
    exit_row_bottom.pack(anchor="w", pady=20)

    ctk.CTkButton(
        exit_row_bottom,
        text="Exit",
        font=ctk.CTkFont(size=16, weight="bold"),
        fg_color="#D43F3A",
        hover_color=darken_color("#D43F3A", 0.12),
        command=on_exit,
        width=110,
        height=36
    ).pack(side="left", padx=(0,6))

# ------------------ Конфиг: save/load/apply ------------------
def get_config_dict():
    return {
        "menu_base_color": menu_base_color,
        "aimbot_fov": aimbot_fov,
        "aimbot_color": aimbot_color,
        "esp_box_color": esp_box_color,
        "esp_show_boxes": esp_show_boxes,
        "esp_show_health": esp_show_health,
        "esp_box_scale": esp_box_scale,
        "esp_box_outline_width": esp_box_outline_width,
        "_selected_hotkey": _selected_hotkey,
        "_selected_hotkey_name": _selected_hotkey_name,
        "esp_enabled": esp_enabled,
        "aimbot_enabled": aimbot_enabled,
        "machine_gun_enabled": machine_gun_enabled,
        "machine_pistol_enabled": machine_pistol_enabled,
        "machine_sniper_enabled": machine_sniper_enabled,
        "machine_blunderbuss_enabled": machine_blunderbuss_enabled,
        "godmode_enabled": godmode_enabled,
        "infinity_ammo_enabled": infinity_ammo_enabled
    }

def apply_config(cfg: dict):
    global menu_base_color, header_color, button_color, button_hover_color
    global aimbot_fov, aimbot_color, _selected_hotkey, _selected_hotkey_name
    global esp_enabled, aimbot_enabled, machine_gun_enabled, machine_pistol_enabled, machine_sniper_enabled, machine_blunderbuss_enabled
    global esp_box_color, esp_show_boxes, esp_show_health, esp_box_scale, esp_box_outline_width
    global godmode_enabled, infinity_ammo_enabled

    try:
        if "menu_base_color" in cfg:
            menu_base_color = cfg["menu_base_color"]
            header_color = menu_base_color
            button_color = menu_base_color
            button_hover_color = darken_color(button_color, 0.15)
        if "aimbot_fov" in cfg:
            aimbot_fov = float(cfg["aimbot_fov"])
        if "aimbot_color" in cfg:
            aimbot_color = cfg["aimbot_color"]
        if "esp_box_color" in cfg:
            esp_box_color = cfg["esp_box_color"]
        if "esp_show_boxes" in cfg:
            esp_show_boxes = bool(cfg["esp_show_boxes"])
        if "esp_show_health" in cfg:
            esp_show_health = bool(cfg["esp_show_health"])
        if "esp_box_scale" in cfg:
            try:
                esp_box_scale = float(cfg["esp_box_scale"])
            except Exception:
                esp_box_scale = float(1.0)
        if "esp_box_outline_width" in cfg:
            try:
                esp_box_outline_width = int(cfg["esp_box_outline_width"])
            except Exception:
                esp_box_outline_width = 2
        if "_selected_hotkey" in cfg:
            _selected_hotkey = int(cfg["_selected_hotkey"])
        if "_selected_hotkey_name" in cfg:
            _selected_hotkey_name = str(cfg["_selected_hotkey_name"])
        # boolean flags
        esp_enabled = bool(cfg.get("esp_enabled", esp_enabled))
        aimbot_enabled = bool(cfg.get("aimbot_enabled", aimbot_enabled))
        machine_gun_enabled = bool(cfg.get("machine_gun_enabled", machine_gun_enabled))
        machine_pistol_enabled = bool(cfg.get("machine_pistol_enabled", machine_pistol_enabled))
        machine_sniper_enabled = bool(cfg.get("machine_sniper_enabled", machine_sniper_enabled))
        machine_blunderbuss_enabled = bool(cfg.get("machine_blunderbuss_enabled", machine_blunderbuss_enabled))
        godmode_enabled = bool(cfg.get("godmode_enabled", godmode_enabled))
        infinity_ammo_enabled = bool(cfg.get("infinity_ammo_enabled", infinity_ammo_enabled))
    except Exception:
        pass

    # apply UI updates
    try:
        apply_ui_colors()
    except Exception:
        pass
    try:
        style_widget_recursive(left_menu)
        style_widget_recursive(right_panel)
    except Exception:
        pass
    try:
        # rebuild current page to refresh widgets (sloppy but simple)
        show_page(current_page)
    except Exception:
        pass
    try:
        _draw_overlay_once()
    except Exception:
        pass

def save_config_dialog():
    cfg = get_config_dict()
    path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files","*.json")], title="Save config as")
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Save config failed: {e}")

def load_config_dialog():
    path = filedialog.askopenfilename(filetypes=[("JSON files","*.json")], title="Load config")
    if not path:
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        apply_config(cfg)
        print(f"Config loaded: {path}")
    except Exception as e:
        print(f"Load config failed: {e}")

# ---------------------------------------------------------
# ------------------ доработка _draw_overlay_once: добавление ESP ------------------
def _draw_overlay_once():
    global _overlay_canvas
    if not _overlay_canvas:
        return
    try:
        _overlay_canvas.delete("all")
        # Only draw overlay status box even if aimbot and esp are disabled
        if not aimbot_enabled and not esp_enabled:
            sw = _overlay_canvas.winfo_width()
            sh = _overlay_canvas.winfo_height()
            if sw > 0 and sh > 0:
                try:
                    _draw_status_box(sw, sh)
                except Exception:
                    pass
            return
        sw = _overlay_canvas.winfo_width()
        sh = _overlay_canvas.winfo_height()
        if sw <= 0 or sh <= 0:
            return
        cx = sw // 2
        cy = sh // 2
        max_r = min(cx, cy) - 20
        radius = int((aimbot_fov / 180.0) * max_r)
        # draw FOV circle (only when user enabled showing it) and crosshair/dot when aimbot is enabled
        color = aimbot_color if aimbot_enabled else "#666666"
        outline_width = 2 if aimbot_enabled else 1
        try:
            # circle visibility controlled by show_aimbot_fov
            if show_aimbot_fov:
                try:
                    _overlay_canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline=color, width=outline_width)
                except Exception:
                    pass
            # crosshair and center dot still drawn when aimbot is enabled
            if aimbot_enabled:
                try:
                    ch = 12
                    _overlay_canvas.create_line(cx - ch, cy, cx + ch, cy, fill=color)
                    _overlay_canvas.create_line(cx, cy - ch, cx, cy + ch, fill=color)
                    _overlay_canvas.create_oval(cx-4, cy-4, cx+4, cy+4, fill=color, outline=color)
                except Exception:
                    pass
        except Exception:
            pass

        # ESP drawing (использует отдельные base для pos/health/name и offsets x/y/z)
        try:
            if esp_enabled:
                # попытка получить локального игрока и углы обзора (если доступны)
                lp_base = safe_resolve(AIMBOT_POINTERS["LocalPlayer"]["base"], [0x0])
                view_pitch_addr = lp_base + AIMBOT_POINTERS["LocalPlayer"]["view_pitch_offset"] if lp_base else None
                view_yaw_addr = lp_base + AIMBOT_POINTERS["LocalPlayer"]["view_yaw_offset"] if lp_base else None
                try:
                    current_pitch = pm.read_float(view_pitch_addr) if view_pitch_addr else 0.0
                    current_yaw = pm.read_float(view_yaw_addr) if view_yaw_addr else 0.0
                except Exception:
                    current_pitch = 0.0; current_yaw = 0.0

                # локальная позиция (fallback если не удалось прочитать)
                local_pos = read_vec3(lp_base, AIMBOT_POINTERS["LocalPlayer"]["pos_offsets"]) if lp_base else None
                if not local_pos:
                    local_pos = (0.0, 0.0, 0.0)

                ent_cfg = ESP_PLACEHOLDERS["EntityList"]
                el_base = ent_cfg["base"]
                entity_size = ent_cfg.get("entity_size", 0x10)

                for i in range(ESP_PLACEHOLDERS["max_entities"]):
                    # базовый адрес текущей записи (если используется один большой массив)
                    ent_base = el_base + i * entity_size

                    # читаем здоровье: используем health.base + i*entity_size + offset
                    try:
                        hp_base = ent_cfg["health"]["base"]
                        hp_offset = ent_cfg["health"]["offset"]
                        health_addr = hp_base + i * entity_size + hp_offset
                        health = pm.read_int(health_addr)
                        if health <= 0:
                            continue
                    except Exception:
                        continue

                    # читаем позицию по отдельным оффсетам (x/y/z)
                    try:
                        pos_base = ent_cfg["pos"]["base"]
                        offs = ent_cfg["pos"]["offsets"]
                        tx = pm.read_float(pos_base + i * entity_size + offs["x"])
                        ty = pm.read_float(pos_base + i * entity_size + offs["y"])
                        tz = pm.read_float(pos_base + i * entity_size + offs["z"])
                        target_pos = (tx, ty, tz)
                    except Exception:
                        continue

                    sx, sy = world_to_screen_local(local_pos, current_pitch, current_yaw, target_pos, sw, sh)
                    if sx is None or sy is None:
                        continue

                    # размер бокса завязан на дистанции (аппроксимация)
                    dx = target_pos[0] - local_pos[0]
                    dy = target_pos[1] - local_pos[1]
                    dist = math.hypot(dx, dy)
                    size = max(10, int(500 / (dist + 1)))
                    try:
                        draw_size = max(4, int(size * esp_box_scale))
                        # rectangular proportions: short side horizontally (flipped)
                        short_side = draw_size
                        long_side = max(6, int(draw_size * 1.6))
                        box_w = short_side
                        box_h = long_side

                        left = int(sx - box_w // 2)
                        right = int(sx + box_w // 2)
                        top = int(sy - box_h // 2)
                        bottom = int(sy + box_h // 2)

                        # clamp to screen bounds
                        left = max(0, left)
                        top = max(0, top)
                        right = min(sw - 1, right)
                        bottom = min(sh - 1, bottom)

                        # draw box if enabled
                        if esp_show_boxes:
                            try:
                                _overlay_canvas.create_rectangle(left, top, right, bottom, outline=esp_box_color, width=max(1, int(esp_box_outline_width)))
                            except Exception:
                                pass
                        # HP текст если включено
                        if esp_show_health:
                            try:
                                _overlay_canvas.create_text(left + 4, top - 12, anchor="nw", fill="#FFFFFF", text=f"HP:{health}", font=("Arial", 10))
                            except Exception:
                                pass
                    except Exception:
                        pass
            else:
                # ESP отключён: показать демонстрационную серую коробку в центре (не трогаем память)
                try:
                    draw_size = max(8, int(min(cx, cy) * 0.18 * esp_box_scale))
                    short_side = draw_size
                    long_side = max(10, int(draw_size * 1.6))
                    box_w = short_side
                    box_h = long_side
                    left = cx - box_w // 2
                    right = cx + box_w // 2
                    top = cy - box_h // 2
                    bottom = cy + box_h // 2
                    left = max(0, left)
                    top = max(0, top)
                    right = min(sw - 1, right)
                    bottom = min(sh - 1, bottom)
                    if esp_show_boxes:
                        _overlay_canvas.create_rectangle(left, top, right, bottom, outline="#666666", width=max(1, int(esp_box_outline_width)))
                    if esp_show_health:
                        _overlay_canvas.create_text(left + 4, top - 12, anchor="nw", fill="#BBBBBB", text=f"HP:---", font=("Arial", 10))
                except Exception:
                    pass
        except Exception:
            pass

        # after main drawing draw the status box
        try:
            _draw_status_box(sw, sh)
        except Exception:
            pass
    except Exception:
        pass

# добавляем вспомогательную функцию отрисовки статуса (правый верхний угол)
def _draw_status_box(sw, sh):
    try:
        padding = 12
        box_w = 220
        # collect feature statuses (no per-weapon entries)
        lines = [
            ("ESP", esp_enabled),
            ("Aimbot", aimbot_enabled),
            ("Machinegun", machine_gun_enabled),
            ("Godmode", godmode_enabled),
            ("Infinity Ammo", infinity_ammo_enabled)
        ]
        # шрифт и размеры
        fnt = tkfont.Font(family="Arial", size=11)
        line_h = fnt.metrics("linespace") + 2
        box_h = padding * 2 + len(lines) * line_h
        x2 = sw - padding
        x1 = x2 - box_w
        y1 = padding
        y2 = y1 + box_h
        # фон и цвет привязан к menu_base_color для активного состояния
        bg = "#111111"
        border = menu_base_color if menu_base_color else "#00FF88"
        _overlay_canvas.create_rectangle(x1, y1, x2, y2, fill=bg, outline=border, width=1)
        # заголовок
        _overlay_canvas.create_text(x1 + 8, y1 + 6, anchor="nw", text="Enabled:", fill="#FFFFFF", font=tkfont.Font(family="Arial", size=12, weight="bold"))
        # список
        oy = y1 + 6 + line_h
        for (name, val) in lines:
            col = menu_base_color if val and menu_base_color else ("#00FF88" if val else "#888888")
            text = f"• {name}"
            _overlay_canvas.create_text(x1 + 10, oy, anchor="nw", text=text, fill=col, font=fnt)
            oy += line_h
    except Exception:
        pass

root.mainloop()