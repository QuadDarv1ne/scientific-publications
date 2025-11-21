# Test Runner Script for Traffic Analyzer
# Запуск тестов с различными опциями

param(
    [switch]$Coverage,
    [switch]$Verbose,
    [switch]$Fast,
    [string]$Pattern = "test_*.py"
)

$ErrorActionPreference = "Stop"

Write-Host "`n╔═══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  TRAFFIC ANALYZER - TEST RUNNER                  ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Сборка аргументов pytest
$pytestArgs = @()

if ($Verbose) {
    $pytestArgs += "-vv"
} else {
    $pytestArgs += "-v"
}

if ($Fast) {
    $pytestArgs += "-m", "not slow"
    Write-Host "⚡ Быстрый режим (пропуск медленных тестов)`n" -ForegroundColor Yellow
}

if ($Coverage) {
    $pytestArgs += "--cov=.", "--cov-report=html", "--cov-report=term-missing"
    Write-Host "📊 Режим покрытия кода включен`n" -ForegroundColor Yellow
}

if ($Pattern) {
    $pytestArgs += "-k", $Pattern
}

# Запуск тестов
Write-Host "🧪 Запуск тестов..." -ForegroundColor Green
Write-Host "   Команда: pytest $($pytestArgs -join ' ')`n" -ForegroundColor Gray

try {
    pytest @pytestArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Все тесты пройдены успешно!" -ForegroundColor Green
        
        if ($Coverage) {
            Write-Host "`n📊 HTML отчет покрытия: htmlcov/index.html" -ForegroundColor Cyan
        }
    } else {
        Write-Host "`n❌ Некоторые тесты провалились" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "`n❌ Ошибка при выполнении тестов: $_" -ForegroundColor Red
    exit 1
}
