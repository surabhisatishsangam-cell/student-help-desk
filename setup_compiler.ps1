# PowerShell Compiler Setup Helper
# Run this script to automatically install or check for a C compiler on Windows.

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "     C Compiler Environment Setup for Windows       " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# 1. Check if gcc or clang is already accessible
$gcc = Get-Command gcc -ErrorAction SilentlyContinue
$clang = Get-Command clang -ErrorAction SilentlyContinue
$make = Get-Command make -ErrorAction SilentlyContinue

if ($gcc) {
    Write-Host "[OK] GCC is already installed at: $($gcc.Source)" -ForegroundColor Green
    & gcc --version
    exit 0
}

if ($clang) {
    Write-Host "[OK] Clang is already installed at: $($clang.Source)" -ForegroundColor Green
    & clang --version
    exit 0
}

Write-Host "[!] No GCC or Clang detected in PATH." -ForegroundColor Yellow
Write-Host ""
Write-Host "Recommended Installation Methods:" -ForegroundColor Cyan
Write-Host "1. Install via Windows Package Manager (winget):" -ForegroundColor White
Write-Host "   Run the following command in PowerShell:" -ForegroundColor Gray
Write-Host "   winget install --id BrechtSanders.WinLibs.POSIX.UCRT" -ForegroundColor Green
Write-Host ""
Write-Host "2. Alternative via LLVM-MinGW (includes clang and gcc wrappers):" -ForegroundColor White
Write-Host "   winget install --id MartinStorsjo.LLVM-MinGW.UCRT" -ForegroundColor Green
Write-Host ""
Write-Host "3. Portable Zero-Install (w64devkit):" -ForegroundColor White
Write-Host "   Download from https://github.com/skeeto/w64devkit/releases" -ForegroundColor Gray
Write-Host "   Extract the zip and add its 'bin' directory to your PATH." -ForegroundColor Gray
Write-Host ""
Write-Host "4. Instant Alternative inside this workspace (Zero-Install):" -ForegroundColor White
Write-Host "   You can run the full project immediately using Python:" -ForegroundColor Gray
Write-Host "   python helpdesk.py sample_helpdesk_data.csv" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Cyan
