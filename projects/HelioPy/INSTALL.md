# Руководство по установке HelioPy

## Требования

- Python 3.8 или новее
- pip (менеджер пакетов Python)

## Установка

### Установка из исходного кода

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/heliopy.git
cd heliopy
```

2. Создайте виртуальное окружение (рекомендуется):
```bash
python -m venv venv
```

3. Активируйте виртуальное окружение:
   - Windows (PowerShell):
     ```powershell
     venv\Scripts\Activate.ps1
     ```
   - Windows (CMD):
     ```cmd
     venv\Scripts\activate.bat
     ```
   - Linux/MacOS:
     ```bash
     source venv/bin/activate
     ```

4. Установите зависимости:
```bash
pip install -r requirements/base.txt
```

5. Установите библиотеку в режиме разработки:
```bash
pip install -e .
```

## Проверка установки

Запустите простой тест:

```python
import heliopy
print(f"HelioPy версия: {heliopy.__version__}")
```

## Установка зависимостей для разработки

Если вы планируете разрабатывать библиотеку:

```bash
pip install -r requirements/dev.txt
```

## Установка зависимостей для документации

Для сборки документации:

```bash
pip install -r requirements/docs.txt
```

## Примечания

- Для работы с данными SDO/SOHO требуется библиотека SunPy, которая будет установлена автоматически
- Некоторые функции требуют подключения к интернету для загрузки данных
- Для работы с большими объемами данных рекомендуется иметь минимум 4 ГБ оперативной памяти

