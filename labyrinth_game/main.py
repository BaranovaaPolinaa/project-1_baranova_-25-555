from typing import Any

from labyrinth_game.player_actions import (
    get_input,
    move_player,
    show_inventory,
    take_item,
    use_item,
)
from labyrinth_game.utils import (
    attempt_open_treasure,
    describe_current_room,
    show_help,
    solve_puzzle,
)

game_state: dict[str, Any] = {
    "player_inventory": [],
    "current_room": "entrance",
    "game_over": False,
    "steps_taken": 0,
}


def process_command(game_state: dict[str, Any], command: str):
    """
    Обрабатывает введённую пользователем команду и вызывает соответствующую функцию.
    """
    parts = command.strip().lower().split(maxsplit=1)
    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else None

    match cmd:
        case "look" | "describe":
            describe_current_room(game_state)
        case "inventory" | "inv":
            show_inventory(game_state)
        case "north" | "south" | "east" | "west":
            move_player(game_state, cmd)
        case "go":
            if arg and arg in ["north", "south", "east", "west"]:
                move_player(game_state, arg)
            else:
                print("Укажите направление. Пример: go north")
        case "take":
            if arg:
                take_item(game_state, arg)
            else:
                print("Укажите предмет для взятия. Пример: take torch")
        case "use":
            if arg:
                use_item(game_state, arg)
            else:
                print("Укажите предмет для использования. Пример: use torch")
        case "solve":
            if game_state.get("current_room") == "treasure_room":
                success = attempt_open_treasure(game_state)
                if success:
                    game_state["game_over"] = True
                    print("Поздравляем с победой! Игра завершена.")
            else:
                solve_puzzle(game_state)
        case "help":
            show_help()
        case "quit" | "exit":
            print("Вы вышли из игры. До новых встреч!")
            game_state["game_over"] = True
        case _:
            print("Неизвестная команда. Введите 'help' для справки.")


def main() -> None:
    """
    Основной игровой цикл.
    """
    print("Добро пожаловать в Лабиринт сокровищ!\n")
    print("Введите 'help' для просмотра доступных команд.\n")

    describe_current_room(game_state)

    while not game_state["game_over"]:
        command = get_input("> ")

        if command:
            process_command(game_state, command)

    print(f"\nИгра завершена! Вы сделали {game_state['steps_taken']} шагов.")


if __name__ == "__main__":
    main()
