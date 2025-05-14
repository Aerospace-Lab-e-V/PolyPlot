@echo off
set ENV_DIR=Ashby
set PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

REM 1. Prüfen, ob Python installiert ist
where python >nul 2>nul
if errorlevel 1 (
    echo ==== Python wird heruntergeladen und installiert... ====
    curl -L -o python_installer.exe %PYTHON_URL%
    start /wait python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    del python_installer.exe
) else (
    echo ==== Python ist bereits installiert ====
)

REM 2. Virtuelle Umgebung erstellen
echo ==== Virtuelle Umgebung '%ENV_DIR%' wird erstellt... ====
python -m venv %ENV_DIR%

REM 3. Aktivieren
call %ENV_DIR%\Scripts\activate.bat

REM 4. Pip aktualisieren und Pakete installieren
echo ==== Benötigte Pakete werden installiert... ====
python -m pip install --upgrade pip
pip install numpy pandas matplotlib scikit-learn scipy openpyxl

REM 5. Test-Ausgabe
echo ==== Installierte Versionen: ====
python -c "import numpy, pandas, matplotlib, sklearn, scipy, openpyxl; print('numpy:', numpy.__version__); print('pandas:', pandas.__version__); print('matplotlib:', matplotlib.__version__); print('scikit-learn:', sklearn.__version__); print('scipy:', scipy.__version__); print('openpyxl:', openpyxl.__version__)"

pause
