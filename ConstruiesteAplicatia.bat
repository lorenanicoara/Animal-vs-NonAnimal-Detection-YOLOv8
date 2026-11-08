@echo off
cd /d "%~dp0"
echo ==========================================================
echo   Construiesc aplicatia DetectorAnimaleFinal.exe
echo ==========================================================
echo.
echo [1/3] Copiez modelul final...
if exist "animal_project\runs\animal_gpu_mare\weights\best.pt" (
    copy /Y "animal_project\runs\animal_gpu_mare\weights\best.pt" "model_animal.pt" >nul
)
if not exist "model_animal.pt" (
    echo EROARE: nu gasesc modelul model_animal.pt
    echo Pune model_animal.pt in acelasi folder cu acest fisier .bat.
    pause
    exit /b 1
)
echo [2/3] Instalez PyInstaller...
py -3.12 -m pip install -q pyinstaller
echo [3/3] Construiesc aplicatia - dureaza 5-15 minute, nu inchide fereastra...
py -3.12 -m PyInstaller --noconfirm --onedir --windowed --name DetectorAnimaleFinal --collect-all ultralytics DetectorAnimaleFinal.py
if errorlevel 1 (
    echo.
    echo EROARE la construire. Trimite o captura de ecran cu mesajul de mai sus.
    pause
    exit /b 1
)
copy /Y "model_animal.pt" "dist\DetectorAnimaleFinal\" >nul
echo.
echo ==========================================================
echo   GATA! Aplicatia este in folderul:
echo   %~dp0dist\DetectorAnimaleFinal
echo   Porneste-o cu dublu-click pe DetectorAnimaleFinal.exe
echo ==========================================================
explorer "dist\DetectorAnimaleFinal"
pause
