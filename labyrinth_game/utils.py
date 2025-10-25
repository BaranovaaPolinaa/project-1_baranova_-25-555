from typing import Any, Dict

from labyrinth_game.constants import ROOMS


def describe_current_room(game_state: Dict[str, Any]) -> None:
    """
    Выводит полную информацию о текущей комнате:
    - название
    - описание
    - заметные предметы
    - доступные выходы
    - сообщение о загадке

    Parameters:
        game_state (dict): Состояние игры, включая ключ 'current_room'.

    Raises:
        ValueError: если имя комнаты некорректное.
    """
    current_room_key = game_state.get("current_room")
    if current_room_key is None:
        raise ValueError("game_state не содержит 'current_room'!")

    room_data = ROOMS.get(current_room_key)
    if room_data is None:
        raise ValueError("Неверное имя комнаты! Проверьте 'current_room'.")

    print(f"== {current_room_key.upper()} ==")

    description = room_data.get("description", "")
    print(description)

    items = room_data.get("items", [])
    if items:
        print("Заметные предметы:")
        for item in items:
            print(f" - {item}")

    exits = room_data.get("exits", {})
    if exits:
        exits_list = ", ".join(exits.keys())
        print(f"Выходы: {exits_list}")

    puzzle = room_data.get("puzzle")
    if puzzle is not None:
        print("Кажется, здесь есть загадка (используйте команду solve).")


def solve_puzzle(game_state: dict[str, Any]) -> None:
    """
    Решает загадку в текущей комнате.
    """
    current_room_key = game_state.get("current_room")
    if not current_room_key:
        print("Ошибка: неизвестное местоположение.")
        return

    room = ROOMS.get(current_room_key)
    if not room:
        print("Ошибка: комната не найдена.")
        return

    puzzle = room.get("puzzle")
    if not puzzle:
        print("Загадок здесь нет.")
        return

    question, correct_answer = puzzle
    print(f"Загадка: {question}")

    user_answer = input("Ваш ответ: ").strip().lower()

    if user_answer == correct_answer.lower():
        print("Правильно! Загадка решена.")

        room["puzzle"] = None

        if current_room_key == "treasure_room":
            print("Вы получаете доступ к сундуку!")
        elif current_room_key == "portal_room":
            print("Портал активирован! Вы можете использовать его для выхода.")
            if "portal_key" not in game_state["player_inventory"]:
                game_state["player_inventory"].append("portal_key")
        else:
            print("Вы чувствуете, что стали ближе к разгадке тайны лабиринта.")
    else:
        print("Неверно. Попробуйте снова.")


def attempt_open_treasure(game_state: dict[str, Any]) -> bool:
    """
    Пытается открыть сундук с сокровищами.
    Возвращает True, если игра завершена (победа).
    """
    current_room_key = game_state.get("current_room")
    if current_room_key != "treasure_room":
        print("Здесь нет сундука с сокровищами.")
        return False

    room = ROOMS.get("treasure_room")
    if not room or "treasure chest" not in room.get("items", []):
        print("Сундук с сокровищами уже открыт или отсутствует.")
        return False

    inventory = game_state.get("player_inventory", [])

    if "treasure_key" in inventory:
        print("Вы применяете ключ, и замок щёлкает. Сундук открыт!")
        room["items"].remove("treasure chest")
        print("В сундуке сокровище! Вы победили!")
        return True

    print("Сундук заперт. У вас нет ключа, но можно попробовать ввести код.")
    choice = input("Ввести код? (да/нет): ").strip().lower()

    if choice == "да":
        code = input("Введите код: ").strip()
        puzzle = room.get("puzzle")

        if puzzle and code == puzzle[1]:
            print("Код принят! Замок щёлкает, и сундук открывается.")
            room["items"].remove("treasure chest")
            print("В сундуке сокровище! Вы победили!")
            return True
        else:
            print("Неверный код. Сундук остается запертым.")
            return False
    else:
        print("Вы отступаете от сундука.")
        return False


def show_help():
    print("\nДоступные команды:")
    print("  go <direction>  - перейти в направлении (north/south/east/west)")
    print("  look            - осмотреть текущую комнату")
    print("  take <item>     - поднять предмет")
    print("  use <item>      - использовать предмет из инвентаря")
    print("  inventory       - показать инвентарь")
    print("  solve           - попытаться решить загадку в комнате")
    print("  quit            - выйти из игры")
    print("  help            - показать это сообщение")
