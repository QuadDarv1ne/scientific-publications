# Traffic Analyzer - Локальный тест (без Docker)
# Использование: .\test-local.ps1

$ErrorActionPreference = "Continue"

Write-Host "`n╔══════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  TRAFFIC ANALYZER - ЛОКАЛЬНОЕ ТЕСТИРОВАНИЕ  ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════╝`n" -ForegroundColor Green

Set-Location $PSScriptRoot
Write-Host "📂 Директория: $(Get-Location)`n" -ForegroundColor Gray

# Проверка Python
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "🐍 Проверка Python" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

$pythonVersion = python --version 2>&1
Write-Host "  ✓ $pythonVersion`n" -ForegroundColor Green

# Проверка зависимостей
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "📦 Проверка зависимостей" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

$packages = @("hydra", "cv2", "ultralytics", "shapely", "flask")
$missing = @()

foreach ($pkg in $packages) {
    $testImport = "import $pkg" 
    if ($pkg -eq "cv2") { $testImport = "import cv2" }
    
    python -c $testImport 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $pkg" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $pkg не установлен" -ForegroundColor Red
        $missing += $pkg
    }
}

if ($missing.Count -gt 0) {
    Write-Host "`n⚠️  Не хватает зависимостей: $($missing -join ', ')`n" -ForegroundColor Yellow
    Write-Host "Установить сейчас? (Y/N): " -ForegroundColor Cyan -NoNewline
    $install = Read-Host
    
    if ($install -eq 'Y' -or $install -eq 'y') {
        Write-Host "`n📥 Установка зависимостей...`n" -ForegroundColor Cyan
        pip install -r requirements.txt
        Write-Host "`n✅ Установка завершена`n" -ForegroundColor Green
    } else {
        Write-Host "`n⏭️  Пропуск установки`n" -ForegroundColor Yellow
    }
}

# Проверка файлов
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "📄 Проверка файлов проекта" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

$files = @(
    "main_optimized.py",
    "configs/app_config.yaml",
    "weights/yolov8m.pt"
)

$allFilesExist = $true
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file не найден" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host "`n❌ Не все файлы на месте`n" -ForegroundColor Red
    exit 1
}

# Запуск проекта
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "🚀 Запуск Traffic Analyzer" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

Write-Host "Режим: Локальный (без Kafka/InfluxDB/Grafana)" -ForegroundColor Cyan
Write-Host "Веб-интерфейс будет доступен на: http://127.0.0.1:8100`n" -ForegroundColor Cyan

Write-Host "Нажмите CTRL+C для остановки`n" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

# Запуск
try {
    python main_optimized.py pipeline.send_info_kafka=False
} catch {
    Write-Host "`n❌ Ошибка запуска: $_`n" -ForegroundColor Red
    exit 1
}
