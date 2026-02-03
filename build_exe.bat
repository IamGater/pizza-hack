@echo off

python -m pip install --upgrade pip
python -m pip install pyinstaller pillow

python -m PyInstaller --noconfirm --onefile --windowed ^
  --icon "%~dp0img\pizza.ico" ^
  --add-data "%~dp0img;img" ^
  --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=PIL.ImageTk ^
  --hidden-import=customtkinter --hidden-import=pymem ^
  --name "Pizza Mega Hack" ^
  "pizza.py"

echo.
echo  Build complete. The executable is located in the "dist" folder.
exit
