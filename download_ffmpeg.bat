@echo off
REM MacTube - Script de téléchargement FFmpeg portable pour Windows
REM Télécharge et configure FFmpeg pour le build de l'application
REM Compatible Windows 10+ (x64)

echo MacTube - Téléchargement FFmpeg portable pour Windows
echo ====================================================

REM Créer le répertoire de travail
if not exist "ffmpeg_bundle" mkdir ffmpeg_bundle
cd ffmpeg_bundle

REM URL de FFmpeg portable pour Windows (version statique)
set "FFMPEG_URL=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
set "FFMPEG_ZIP=ffmpeg-windows.zip"

echo Téléchargement de FFmpeg...
powershell -Command "Invoke-WebRequest -Uri '%FFMPEG_URL%' -OutFile '%FFMPEG_ZIP%'"

if %ERRORLEVEL% EQU 0 (
    echo SUCCES: Téléchargement terminé
    
    echo Extraction de l'archive...
    powershell -Command "Expand-Archive -Path '%FFMPEG_ZIP%' -DestinationPath '.' -Force"
    
    if %ERRORLEVEL% EQU 0 (
        echo SUCCES: Extraction terminée
        
        REM Trouver l'exécutable FFmpeg
        if exist "ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe" (
            echo INFO: FFmpeg trouvé: ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe
            
            REM Copier vers le répertoire principal
            copy "ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe" "..\ffmpeg.exe"
            
            echo SUCCES: FFmpeg copié vers le répertoire principal
            echo INFO: Emplacement: %CD%\..\ffmpeg.exe
            
            REM Nettoyer
            cd ..
            rmdir /s /q ffmpeg_bundle
            
            echo INFO: Nettoyage terminé
            echo SUCCES: FFmpeg portable prêt pour Windows
            
        ) else (
            echo ERREUR: FFmpeg exécutable non trouvé
            exit /b 1
        )
    ) else (
        echo ERREUR: Échec de l'extraction
        exit /b 1
    )
) else (
    echo ERREUR: Échec du téléchargement
    exit /b 1
)

pause
