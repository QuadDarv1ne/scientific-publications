# Contributing to Traffic Analyzer

Спасибо за интерес к улучшению Traffic Analyzer 🎉

## 📋 Как внести вклад

### 1. Настройка окружения разработки

```powershell
# Клонируйте репозиторий
git clone https://github.com/QuadDarv1ne/scientific-publications.git
cd scientific-publications/projects/traffic-analyzer

# Запустите автоматическую настройку
.\scripts\dev_setup.ps1
```

### 2. Создание ветки для изменений

```bash
git checkout -b feature/your-feature-name
# или
git checkout -b fix/bug-description
```

### 3. Внесение изменений

При внесении изменений следуйте этим правилам:

#### Стиль кода

- ✅ Используйте **type hints** для всех параметров и возвращаемых значений
- ✅ Добавляйте **docstrings** в Google Style для всех публичных функций/классов
- ✅ Следуйте **PEP 8** (автоматически форматируется через black)
- ✅ Максимальная длина строки: **100 символов**
- ✅ Используйте **константы** вместо магических чисел

Пример правильно оформленной функции:

```python
from typing import List, Optional


def process_detections(
    detections: List[float], confidence_threshold: float = 0.5
) -> Optional[List[int]]:
    """
    Обрабатывает детекции объектов и фильтрует по порогу уверенности.

    Args:
        detections: Список координат детекций [x1, y1, x2, y2, conf]
        confidence_threshold: Минимальный порог уверенности (0.0-1.0)

    Returns:
        Список отфильтрованных индексов или None если детекций нет

    Raises:
        ValueError: Если confidence_threshold вне диапазона [0, 1]
    """
    if not 0.0 <= confidence_threshold <= 1.0:
        raise ValueError("confidence_threshold должен быть в диапазоне [0, 1]")

    # Ваш код здесь
    pass
```

#### Тестирование

- ✅ Добавляйте тесты для всего нового функционала
- ✅ Убедитесь, что покрытие кода не упало ниже **50%**
- ✅ Запустите тесты перед коммитом:

```powershell
.\scripts\run_tests.ps1 -Coverage
```

#### Проверка качества

Перед коммитом запустите проверку качества:

```powershell
# Проверка с автоисправлением
.\scripts\code_quality.ps1 -Fix

# Или используйте pre-commit (установится автоматически)
pre-commit run --all-files
```

### 4. Коммит изменений

Используйте осмысленные сообщения коммитов:

```bash
# Хорошие примеры:
git commit -m "feat: добавлена поддержка RTSP потоков"
git commit -m "fix: исправлена утечка памяти в VideoReader"
git commit -m "docs: обновлена документация API"
git commit -m "refactor: улучшена обработка ошибок в DetectionNode"
git commit -m "test: добавлены тесты для FPS_Counter"

# Плохие примеры:
git commit -m "fix"
git commit -m "updates"
git commit -m "changes"
```

Префиксы коммитов:
- `feat:` - новая функциональность
- `fix:` - исправление бага
- `docs:` - изменения в документации
- `style:` - форматирование, отступы и т.д.
- `refactor:` - рефакторинг кода
- `test:` - добавление/изменение тестов
- `perf:` - улучшение производительности
- `chore:` - обновление зависимостей, конфигов

### 5. Push и Pull Request

```bash
git push origin feature/your-feature-name
```

Затем создайте Pull Request на GitHub со следующей информацией:

**Шаблон описания PR:**

```markdown
## Описание изменений
Краткое описание что было изменено и зачем

## Тип изменения
- [ ] Bug fix (исправление бага)
- [ ] New feature (новая функциональность)
- [ ] Breaking change (изменения несовместимые с предыдущими версиями)
- [ ] Documentation update (обновление документации)

## Чеклист
- [ ] Код соответствует стилю проекта
- [ ] Добавлены/обновлены docstrings
- [ ] Добавлены тесты для новой функциональности
- [ ] Все тесты проходят успешно
- [ ] Обновлена документация (если необходимо)
- [ ] Обновлен CHANGELOG.md

## Скриншоты/Примеры (если применимо)

## Связанные Issue
Closes #123
```

## 🐛 Сообщение об ошибках

Используйте [GitHub Issues](https://github.com/QuadDarv1ne/scientific-publications/issues) для сообщения об ошибках.

При создании issue включите:
- Описание проблемы
- Шаги для воспроизведения
- Ожидаемое поведение
- Фактическое поведение
- Версия Python, ОС
- Логи (если есть)

## 💡 Предложения улучшений

Мы открыты к предложениям! Создайте Issue с меткой `enhancement` и опишите:
- Какую проблему решает ваше предложение
- Предлагаемое решение
- Альтернативные варианты (если есть)

## 📚 Полезные ссылки

- [Документация проекта](README.md)
- [Changelog](CHANGELOG.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## ⚖️ Лицензия

Внося вклад в проект, вы соглашаетесь с тем, что ваш код будет распространяться под [MIT License](LICENSE).

---

Спасибо за ваш вклад! 🙏
