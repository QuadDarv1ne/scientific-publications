# Traffic Analyzer - Скрипт автоматического тестирования
# Использование: .\test-project.ps1

$ErrorActionPreference = "Continue"

Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  TRAFFIC ANALYZER - АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Переход в директорию проекта
Set-Location $PSScriptRoot
Write-Host "📂 Директория: $(Get-Location)`n" -ForegroundColor Gray

# Шаг 1: Проверка Docker
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "🔍 ШАГ 1: Проверка Docker Desktop" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

docker info 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker Desktop работает`n" -ForegroundColor Green
    
    # Шаг 2: Проверка файлов
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "🔍 ШАГ 2: Проверка необходимых файлов" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
    
    $files = @(
        "docker-compose.yaml",
        ".env",
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
    Write-Host ""
    
    if (-not $allFilesExist) {
        Write-Host "⚠️  Не все файлы на месте. Проверьте проект.`n" -ForegroundColor Yellow
        exit 1
    }
    
    # Шаг 3: Запуск сервисов
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "🚀 ШАГ 3: Запуск Docker Compose" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
    
    Write-Host "Запуск сервисов (это может занять несколько минут)...`n" -ForegroundColor Cyan
    docker compose up -d --build
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Сервисы запущены`n" -ForegroundColor Green
        
        # Шаг 4: Ожидание готовности
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
        Write-Host "⏳ ШАГ 4: Ожидание готовности сервисов" -ForegroundColor Yellow
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
        
        Write-Host "Ожидание 30 секунд...`n" -ForegroundColor Cyan
        Start-Sleep -Seconds 30
        
        # Шаг 5: Проверка статуса
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
        Write-Host "📊 ШАГ 5: Проверка статуса контейнеров" -ForegroundColor Yellow
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
        
        docker compose ps
        
        # Шаг 6: Проверка портов
        Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
        Write-Host "🌐 ШАГ 6: Проверка доступности сервисов" -ForegroundColor Yellow
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
        
        $services = @(
            @{Name="Grafana"; Port=3111; Path="/"},
            @{Name="Kafka UI"; Port=9001; Path="/"},
            @{Name="Video Stream"; Port=8009; Path="/"}
        )
        
        foreach ($service in $services) {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:$($service.Port)$($service.Path)" -Method Head -TimeoutSec 5 -ErrorAction Stop
                Write-Host "  ✓ $($service.Name) (http://localhost:$($service.Port)) - доступен" -ForegroundColor Green
            } catch {
                Write-Host "  ⏳ $($service.Name) (http://localhost:$($service.Port)) - еще загружается..." -ForegroundColor Yellow
            }
        }
        
        # Итоговая информация
        Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
        Write-Host "✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО" -ForegroundColor Green
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
        
        Write-Host "Веб-интерфейсы:" -ForegroundColor Cyan
        Write-Host "  • Grafana:  http://localhost:3111 (admin/admin)" -ForegroundColor White
        Write-Host "  • Kafka UI: http://localhost:9001" -ForegroundColor White
        Write-Host "  • Video:    http://localhost:8009" -ForegroundColor White
        
        Write-Host "`nПолезные команды:" -ForegroundColor Cyan
        Write-Host "  • Статус:     docker compose ps" -ForegroundColor White
        Write-Host "  • Логи:       docker compose logs -f" -ForegroundColor White
        Write-Host "  • Остановка:  docker compose down" -ForegroundColor White
        Write-Host "  • Рестарт:    docker compose restart`n" -ForegroundColor White
        
    } else {
        Write-Host "`n❌ Ошибка запуска сервисов`n" -ForegroundColor Red
        Write-Host "Проверьте логи: docker compose logs`n" -ForegroundColor Yellow
        exit 1
    }
    
} else {
    Write-Host "❌ Docker Desktop не запущен`n" -ForegroundColor Red
    Write-Host "Пожалуйста:" -ForegroundColor Yellow
    Write-Host "  1. Запустите Docker Desktop" -ForegroundColor White
    Write-Host "  2. Дождитесь полной загрузки (зеленый значок)" -ForegroundColor White
    Write-Host "  3. Запустите этот скрипт снова: .\test-project.ps1`n" -ForegroundColor White
    exit 1
}
