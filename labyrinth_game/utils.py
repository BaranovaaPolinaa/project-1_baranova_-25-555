import math
from typing import Any

from labyrinth_game.constants import COMMANDS, ROOMS

EVENT_PROBABILITY = 3
DAMAGE_THRESHOLD = 3
EVENT_TYPES = 3
TRAP_CHANCE = 8
TORCH_SAVE_CHANCE = 2
MOVEMENT_STEP = 1
RANDOM_MOVEMENT_CHANCE = 3

SIN_MULTIPLIER_1 = 12.9898
SIN_MULTIPLIER_2 = 43758.5453


def describe_current_room(game_state: dict[str, Any]) -> None:
    """
    Выводит полную информацию о текущей комнате:
    - название
    - описание
    - заметные предметы
    - доступные выходы
    - сообщение о загадке
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
    Решает загадку в текущей комнате с поддержкой альтернативных ответов.
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

    valid_answers = [correct_answer.lower()]

    number_alternatives = {
        "10": ["десять", "10"],
        "4": ["четыре", "4"],
        "8": ["восемь", "8"],
        "366": ["триста шестьдесят шесть", "366"],
    }

    if correct_answer in number_alternatives:
        valid_answers = number_alternatives[correct_answer]

    if user_answer in valid_answers:
        print("Правильно! Загадка решена.")

        room["puzzle"] = None

        if current_room_key == "treasure_room":
            print("Вы получаете доступ к сундуку!")
        elif current_room_key == "portal_room":
            print("Портал активирован! Вы можете использовать его для выхода.")
            if "portal_key" not in game_state["player_inventory"]:
                game_state["player_inventory"].append("portal_key")
        elif current_room_key == "trap_room":
            print("Ловушка деактивирована! Теперь вы можете безопасно перемещаться.")
        else:
            print("Вы чувствуете, что стали ближе к разгадке тайны лабиринта.")
    else:
        print("Неверно. Попробуйте снова.")
        if current_room_key == "trap_room":
            trigger_trap(game_state)


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

    if "rusty key" in inventory:
        print("Вы применяете ключ, и замок щёлкает. Сундук открыт!")
        room["items"].remove("treasure chest")
        print("В сундуке сокровище! Вы победили!")
        return True

    print("Сундук заперт. У вас нет ключа, но можно попробовать ввести код.")
    choice = input("Ввести код? (да/нет): ").strip().lower()

    if choice == "да":
        code = input("Введите код: ").strip()
        puzzle = room.get("puzzle")

        if puzzle and (code == puzzle[1] or code == "десять"):
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


def show_help() -> None:
    """
    Показывает список доступных команд.
    """
    print("\nДоступные команды:")
    for command, description in COMMANDS.items():
        print(f"  {command:<16} - {description}")


def pseudo_random(seed: int, modulo: int) -> int:
    """
    Генерирует псевдослучайное число в диапазоне [0, modulo)
    на основе переданного seed.
    """
    x = math.sin(seed * SIN_MULTIPLIER_1) * SIN_MULTIPLIER_2
    fractional_part = x - math.floor(x)
    return int(fractional_part * modulo)


def trigger_trap(game_state: dict[str, Any]) -> None:
    """
    Активирует ловушку с негативными последствиями для игрока.
    """
    print("Ловушка активирована! Пол стал дрожать...")

    inventory = game_state.get("player_inventory", [])

    if "sword" in inventory:
        print("Благодаря мечу вам удалось удержаться на ногах! Ловушка не сработала.")
        return

    if "torch" in inventory:
        torch_save = (
            pseudo_random(game_state.get("steps_taken", 0), TORCH_SAVE_CHANCE) == 0
        )
        if torch_save:
            print("Свет факла помог вовремя заметить ловушку! Вы успели отпрыгнуть.")
            return

    if inventory:
        item_index = pseudo_random(game_state.get("steps_taken", 0), len(inventory))
        lost_item = inventory.pop(item_index)
        print(f"Из-за тряски вы потеряли: {lost_item}!")

        if pseudo_random(game_state.get("steps_taken", 0), RANDOM_MOVEMENT_CHANCE) == 0:
            current_room = game_state["current_room"]
            exits = ROOMS.get(current_room, {}).get("exits", {})
            if exits:
                directions = list(exits.keys())
                random_dir = pseudo_random(
                    game_state.get("steps_taken", 0), len(directions)
                )
                random_room = exits[directions[random_dir]]
                print("Вас отбросило в случайном направлении!")
                game_state["current_room"] = random_room
                game_state["steps_taken"] = (
                    game_state.get("steps_taken", 0) + MOVEMENT_STEP
                )
                describe_current_room(game_state)
    else:
        damage_chance = pseudo_random(
            game_state.get("steps_taken", 0), EVENT_PROBABILITY
        )
        if damage_chance < DAMAGE_THRESHOLD:
            print("Ловушка нанесла смертельный урон! Игра окончена.")
            game_state["game_over"] = True
        else:
            print("Вам повезло! Вы смогли избежать ловушки, но сильно испугались.")


def random_event(game_state: dict[str, Any]) -> None:
    """
    Случайные события, происходящие во время перемещения игрока.
    """
    event_chance = pseudo_random(game_state.get("steps_taken", 0), EVENT_PROBABILITY)
    if event_chance != 0:
        return

    event_type = pseudo_random(game_state.get("steps_taken", 0) + 1, EVENT_TYPES)
    current_room = ROOMS.get(game_state["current_room"])

    match event_type:
        case 0:
            print("Вы заметили что-то блестящее на полу...")
            if "coin" not in current_room["items"]:
                current_room["items"].append("coin")
                print("Вы нашли монетку!")
            else:
                print("Но это оказалась всего лишь пыль...")

        case 1:
            print("Вы слышите странный шорох в темноте...")
            if "sword" in game_state.get("player_inventory", []):
                print(
                    "Благодаря мечу в руках,",
                    "вы чувствуете себя увереннее и отпугиваете существо.",
                )
            elif "torch" in game_state.get("player_inventory", []):
                print(
                    "Свет факла помог разглядеть маленького грызуна,",
                    "который быстро скрылся.",
                )
            else:
                print("Вы замираете от страха, но шорох быстро стихает.")

        case 2:
            trap_chance = (
                pseudo_random(game_state.get("steps_taken", 0), TRAP_CHANCE) == 0
            )
            if trap_chance and "torch" not in game_state.get("player_inventory", []):
                print("Внезапно пол под ногами подался! Это ловушка!")
                trigger_trap(game_state)
