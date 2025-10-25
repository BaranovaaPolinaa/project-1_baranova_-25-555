from typing import Any

from labyrinth_game.constants import ROOMS
from labyrinth_game.utils import (
    attempt_open_treasure,
    describe_current_room,
    random_event,
)


def show_inventory(game_state: dict[str, Any]) -> None:
    """
    Выводит содержимое инвентаря игрока.
    """
    inventory = game_state.get("player_inventory", [])

    if not inventory:
        print("Ваш инвентарь пуст.")
    else:
        print("В вашем инвентаре:")
        for item in inventory:
            print(f" - {item}")


def get_input(prompt: str = "> ") -> str | None:
    """
    Безопасно получает ввод от пользователя с обработкой прерываний.
    """
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из игры.")
        return "quit"


def move_player(game_state: dict[str, Any], direction: str) -> None:
    """
    Перемещает игрока в указанном направлении, если это возможно.
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
        if next_room_key == "treasure_room":
            if "rusty key" in game_state.get("player_inventory", []):
                print(
                    "Вы используете найденный ключ,",
                    "чтобы открыть путь в комнату сокровищ.",
                )
            else:
                print("Дверь заперта. Нужен ключ, чтобы пройти дальше.")
                return

        game_state["current_room"] = next_room_key
        game_state["steps_taken"] = game_state.get("steps_taken", 0) + 1
        describe_current_room(game_state)

        random_event(game_state)
    else:
        print("Нельзя пойти в этом направлении.")


def take_item(game_state: dict[str, Any], item_name: str) -> None:
    """
    Позволяет игроку взять предмет из текущей комнаты.
    """

    current_room_key = game_state.get("current_room")
    if not current_room_key:
        print("Ошибка: текущее местоположение неизвестно.")
        return

    room = ROOMS.get(current_room_key)
    if not room:
        print("Ошибка: текущая комната некорректна.")
        return

    room_items = room.get("items", [])

    if item_name.lower() == "treasure chest":
        print("Вы не можете поднять сундук, он слишком тяжелый.")
        return

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
        print("Вы открыли бронзовую шкатулку. Там только пыль.")
        if "rusty key" not in inventory:
            inventory.append("rusty key")
            print("В шкатулке вы нашли: rusty key")
    elif item_name == "rusty key":
        if game_state.get("current_room") == "treasure_room":
            if attempt_open_treasure(game_state):
                game_state["game_over"] = True
        else:
            print("Здесь не к чему применить этот ключ.")
    elif item_name == "portal_key":
        if game_state.get("current_room") == "portal_room":
            print("Вы используете ключ портала. Портал активируется!")
            print("Поздравляем! Вы нашли выход из лабиринта!")
            game_state["game_over"] = True
        else:
            print("Этот ключ можно использовать только в комнате с порталом.")
    else:
        print("Вы не знаете, как использовать этот предмет.")
