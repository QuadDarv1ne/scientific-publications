# Development Setup Script for Starlink Performance Monitor
# Автоматическая настройка окружения разработки

param(
    [switch]$SkipVenv,
    [switch]$SkipPreCommit
)

$ErrorActionPreference = "Stop"

Write-Host "`n╔═══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  STARLINK MONITOR - DEV ENVIRONMENT SETUP        ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Проверка Python
Write-Host "🐍 Проверка Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ $pythonVersion`n" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python не найден! Установите Python 3.8+`n" -ForegroundColor Red
    exit 1
}

# Создание виртуального окружения
if (-not $SkipVenv) {
    Write-Host "📦 Создание виртуального окружения..." -ForegroundColor Yellow
    
    if (Test-Path ".venv") {
        Write-Host "  ⚠️  .venv уже существует, пропускаем создание" -ForegroundColor Yellow
    } else {
        python -m venv .venv
        Write-Host "  ✓ Виртуальное окружение создано" -ForegroundColor Green
    }
    
    Write-Host "`n  Активация окружения:" -ForegroundColor Cyan
    Write-Host "    PowerShell: .venv\Scripts\Activate.ps1" -ForegroundColor Gray
    Write-Host "    CMD:        .venv\Scripts\activate.bat`n" -ForegroundColor Gray
    
    # Активация для текущей сессии
    & .venv\Scripts\Activate.ps1
}

# Обновление pip
Write-Host "⬆️  Обновление pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "  ✓ pip обновлен`n" -ForegroundColor Green

# Установка зависимостей
Write-Host "📥 Установка зависимостей разработки..." -ForegroundColor Yellow
pip install -r requirements-dev.txt --quiet
Write-Host "  ✓ Зависимости установлены`n" -ForegroundColor Green

# Установка pre-commit hooks
if (-not $SkipPreCommit) {
    Write-Host "🪝 Установка pre-commit hooks..." -ForegroundColor Yellow
    try {
        pre-commit install
        Write-Host "  ✓ Pre-commit hooks установлены`n" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠️  Не удалось установить pre-commit hooks`n" -ForegroundColor Yellow
    }
}

# Проверка конфигурации
Write-Host "🔍 Проверка конфигурации проекта..." -ForegroundColor Yellow

if (Test-Path "config.json") {
    Write-Host "  ✓ config.json" -ForegroundColor Green
} elseif (Test-Path "config.example.json") {
    Write-Host "  ⚠️  config.json не найден" -ForegroundColor Yellow
    Write-Host "`n📝 Создание config.json из config.example.json..." -ForegroundColor Yellow
    Copy-Item "config.example.json" "config.json"
    Write-Host "  ✓ config.json создан. Отредактируйте его при необходимости`n" -ForegroundColor Green
} else {
    Write-Host "  ✗ Конфигурационные файлы не найдены" -ForegroundColor Red
}

# Проверка структуры директорий
Write-Host "`n🗂️  Проверка структуры проекта..." -ForegroundColor Yellow
$requiredDirs = @("src", "tests", "src/monitor", "src/web", "src/database")
foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "  ✓ $dir" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $dir не найден" -ForegroundColor Red
    }
}

# Итоговая информация
Write-Host "`n╔═══════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ ОКРУЖЕНИЕ РАЗРАБОТКИ ГОТОВО!                  ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "📋 Полезные команды:" -ForegroundColor Cyan
Write-Host "  • Запуск линтеров:     " -NoNewline; Write-Host "pre-commit run --all-files" -ForegroundColor White
Write-Host "  • Форматирование:      " -NoNewline; Write-Host "black src/" -ForegroundColor White
Write-Host "  • Проверка типов:      " -NoNewline; Write-Host "mypy src/" -ForegroundColor White
Write-Host "  • Запуск тестов:       " -NoNewline; Write-Host "pytest" -ForegroundColor White
Write-Host "  • Мониторинг:          " -NoNewline; Write-Host "python main.py monitor --config config.json`n" -ForegroundColor White
