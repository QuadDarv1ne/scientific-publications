# Code Quality Check Script for Starlink Performance Monitor
# Проверка качества кода: форматирование, линтинг, типизация

param(
    [switch]$Fix,
    [switch]$SkipFormat,
    [switch]$SkipLint,
    [switch]$SkipTypes
)

$ErrorActionPreference = "Continue"

Write-Host "`n╔═══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  STARLINK MONITOR - CODE QUALITY CHECK           ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$allPassed = $true

# 1. Проверка форматирования (Black + isort)
if (-not $SkipFormat) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "🎨 Проверка форматирования кода" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
    
    if ($Fix) {
        Write-Host "  Запуск Black (с исправлением)..." -ForegroundColor Cyan
        black src/ --line-length=100
        
        Write-Host "`n  Запуск isort (с исправлением)..." -ForegroundColor Cyan
        isort src/ --profile=black --line-length=100
        
        Write-Host "  ✓ Форматирование применено`n" -ForegroundColor Green
    } else {
        Write-Host "  Проверка Black..." -ForegroundColor Cyan
        black src/ --check --line-length=100
        
        if ($LASTEXITCODE -ne 0) {
            $allPassed = $false
            Write-Host "  ✗ Найдены проблемы форматирования" -ForegroundColor Red
            Write-Host "    Запустите с ключом -Fix для автоисправления`n" -ForegroundColor Yellow
        } else {
            Write-Host "  ✓ Форматирование в порядке`n" -ForegroundColor Green
        }
    }
}

# 2. Линтинг (Ruff)
if (-not $SkipLint) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "🔍 Линтинг кода (Ruff)" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
    
    if ($Fix) {
        Write-Host "  Запуск Ruff (с автоисправлением)..." -ForegroundColor Cyan
        ruff check src/ --fix
        
        Write-Host "  ✓ Линтинг с исправлениями завершен`n" -ForegroundColor Green
    } else {
        Write-Host "  Проверка Ruff..." -ForegroundColor Cyan
        ruff check src/
        
        if ($LASTEXITCODE -ne 0) {
            $allPassed = $false
            Write-Host "  ✗ Найдены проблемы линтинга" -ForegroundColor Red
            Write-Host "    Запустите с ключом -Fix для автоисправления`n" -ForegroundColor Yellow
        } else {
            Write-Host "  ✓ Линтинг пройден`n" -ForegroundColor Green
        }
    }
}

# 3. Проверка типов (MyPy)
if (-not $SkipTypes) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "🔎 Проверка типов (MyPy)" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
    
    Write-Host "  Запуск MyPy..." -ForegroundColor Cyan
    mypy src/ --ignore-missing-imports --check-untyped-defs
    
    if ($LASTEXITCODE -ne 0) {
        $allPassed = $false
        Write-Host "  ⚠️  Обнаружены проблемы с типизацией`n" -ForegroundColor Yellow
    } else {
        Write-Host "  ✓ Проверка типов пройдена`n" -ForegroundColor Green
    }
}

# Итоговый результат
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
if ($allPassed) {
    Write-Host "✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
    exit 0
} else {
    Write-Host "❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ КАЧЕСТВА КОДА" -ForegroundColor Red
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
    Write-Host "Запустите с ключом -Fix для автоматического исправления`n" -ForegroundColor Yellow
    exit 1
}
