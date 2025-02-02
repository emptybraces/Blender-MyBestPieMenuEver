@echo off
powershell.exe -Command "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\zipped_release.ps1"
