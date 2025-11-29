# 🍕 Pizza Mega Hack --- Mod Menu

A simple Python-based mod menu for **PirateFight Simulator** using
Tkinter, CustomTkinter, and PyMem.\
The tool reads and writes values directly into the game's memory using
predefined pointer chains.

------------------------------------------------------------------------

## ✅ Working Features

### **Banana Editor 🍌**

-   Allows setting any banana amount.
-   Uses safe pointer-chain resolving.
-   Prints clear errors if pointer breaks.

### **Ammo Editor ⚔️**

Supports: - **Pistol** - **Sniper** - **Blunderbuss**

Each weapon uses its own pointer chain.\
Values are written directly into memory.

### **User Interface**

-   Dark theme using CustomTkinter\
-   Sidebar menu (Player / Weapon / Misc)\
-   Dynamic right-panel page system\
-   Clean and simple layout

------------------------------------------------------------------------

## ⚠ Partially Implemented (UI only, no logic)

### Player Page

-   Bone ESP 💀

### Weapon Page

-   Silent Aimbot 🎯\
-   Machinegun 🔫

------------------------------------------------------------------------

## 📦 Requirements

    pip install pymem customtkinter

Run after launching the game.

------------------------------------------------------------------------

## 🚀 How to Use

1.  Launch PirateFS\
2.  Run script\
3.  Wait for connection\
4.  Open Misc page\
5.  Set bananas/ammo

------------------------------------------------------------------------

## 🧠 Code Structure Overview

### Process Connection

Attaches to:

    PirateFS-Win64-Shipping.exe

### Pointer Resolving

-   resolve_ptr_chain()\
-   safe_resolve()

### Weapon Data Table

Stored in:

    WEAPON_POINTERS = { ... }

### UI Pages

-   Player\
-   Weapon\
-   Misc (working features)

------------------------------------------------------------------------

## 🔮 Future Improvements

-   Auto pointer rescanner\
-   Real ESP / Aimbot\
-   Hotkeys\
-   Config saving