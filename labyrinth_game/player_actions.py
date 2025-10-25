from typing import Any

from labyrinth_game.constants import ROOMS
from labyrinth_game.utils import attempt_open_treasure, describe_current_room


def show_inventory(game_state: dict[str, Any]) -> None:
    """
    Выводит содержимое инвентаря игрока.

    Parameters:
        game_state (dict): Состояние игры, включая ключ 'player_inventory'.
    """
    inventory = game_state.get("player_inventory", [])

    if not inventory:
        print("Ваш инвентарь пуст.")
    else:
        print("В вашем инвентаре:")
        for item in inventory:
            print(f" - {item}")


def get_input(prompt: str = "> ") -> str | None:
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из игры.")
        return "quit"


def move_player(game_state: dict[str, Any], direction: str) -> None:
    """
    Перемещает игрока в указанном направлении, если это возможно.

    Parameters:
        game_state (dict): Состояние игры.
        direction (str): Направление движения ('north', 'south', 'east', 'west').
    """
    current_room_key = game_state.get("current_room")
    if not current_room_key:
        print("Ошибка: текущее местоположение неизвестно.")
        return

    room = ROOMS.get(current_room_key)
    if not room:
        print("Ошибка: текущая комната некорректна.")
        return

    exits = room.get("exits", {})
    next_room_key = exits.get(direction.lower())

    if next_room_key:
        game_state["current_room"] = next_room_key
        game_state["steps_taken"] = game_state.get("steps_taken", 0) + 1
        describe_current_room(game_state)
    else:
        print("Нельзя пойти в этом направлении.")


def take_item(game_state: dict[str, Any], item_name: str) -> None:
    current_room_key = game_state.get("current_room")
    if not current_room_key:
        print("Ошибка: текущее местоположение неизвестно.")
        return

    room = ROOMS.get(current_room_key)
    if not room:
        print("Ошибка: текущая комната некорректна.")
        return

    room_items = room.get("items", {})

    if item_name in room_items:
        game_state.setdefault("player_inventory", []).append(item_name)
        room_items.remove(item_name)
        print(f"Вы подняли: {item_name}")
    else:
        print("Такого предмета здесь нет.")


def use_item(game_state: dict[str, Any], item_name: str) -> None:
    """
    Использует предмет из инвентаря с уникальным эффектом для некоторых предметов.
    """
    inventory = game_state.get("player_inventory", [])

    if item_name not in inventory:
        print("У вас нет такого предмета.")
        return

    if item_name == "torch":
        print("Вы зажгли факел. Стало светлее, и вы видите окрестности лучше.")
    elif item_name == "sword":
        print("Вы держите меч в руках. Чувствуете уверенность и силу.")
    elif item_name == "bronze box":
        print("Вы открыли бронзовую шкатулку.")
        if "rusty key" not in inventory:
            inventory.append("rusty key")
            print("В шкатулке вы нашли: rusty key")
    elif item_name == "treasure_key":
        if game_state.get("current_room") == "treasure_room":
            if attempt_open_treasure(game_state):
                game_state["game_over"] = True
        else:
            print("Здесь не к чему применить этот ключ.")
    else:
        print("Вы не знаете, как использовать этот предмет.")
