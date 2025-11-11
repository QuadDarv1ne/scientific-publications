import argparse
import sys
from datetime import datetime

from .utils.time_utils import TimeUtils
from .utils.math_utils import MathUtils


def cmd_info(args: argparse.Namespace) -> int:
    print("HelioPy v0.1.0 — CLI")
    print("- Анализ солнечной активности")
    print("- Прогноз космической погоды")
    print("- Визуализация и утилиты")
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    # Демонстрационный анализ: вычислим номер вращения Кэррингтона и преобразования координат
    when = args.time or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    t = TimeUtils.parse_time(when)
    cr = TimeUtils.carrington_rotation(t)
    print(f"Время: {when}")
    print(f"Вращение Кэррингтона: {cr:.2f}")

    r, theta, phi = 1.0, 0.5, 0.2
    x, y, z = MathUtils.spherical_to_cartesian(r, theta, phi)
    print(f"Sph->Cart: ({r}, {theta}, {phi}) -> ({x:.4f}, {y:.4f}, {z:.4f})")
    return 0


def cmd_web(args: argparse.Namespace) -> int:
    try:
        from .web_app import main as web_main
    except Exception as e:
        print("Не удалось запустить веб-приложение. Убедитесь, что установлен пакет 'Flask' (установите с extras: heliopy[web]).", file=sys.stderr)
        print(f"Ошибка: {e}", file=sys.stderr)
        return 1
    # Пробрасываем параметры
    return web_main(host=args.host, port=args.port, debug=args.debug)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="heliopy", description="HelioPy — инструменты CLI и веб")
    sub = parser.add_subparsers(dest="command", required=True)

    p_info = sub.add_parser("info", help="Показать информацию о пакете")
    p_info.set_defaults(func=cmd_info)

    p_an = sub.add_parser("analyze", help="Запустить пример анализа")
    p_an.add_argument("--time", help="Время в формате 'YYYY-MM-DD HH:MM:SS' (UTC)")
    p_an.set_defaults(func=cmd_analyze)

    p_web = sub.add_parser("web", help="Запустить веб-интерфейс")
    p_web.add_argument("--host", default="127.0.0.1", help="Хост для Flask (по умолчанию 127.0.0.1)")
    p_web.add_argument("--port", type=int, default=5000, help="Порт для Flask (по умолчанию 5000)")
    p_web.add_argument("--debug", action="store_true", help="Включить режим отладки")
    p_web.set_defaults(func=cmd_web)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
