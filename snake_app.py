from __future__ import annotations

import random

from textual.app import App, ComposeResult
from textual.containers import Center
from textual.widgets import Footer, Header, Static


class SnakeBoard(Static):
    def __init__(self, game: "SnakeApp", **kwargs) -> None:
        super().__init__(**kwargs)
        self.game = game

    def render(self) -> str:
        game = self.game
        cells = {pos: "█" for pos in game.snake}
        if game.snake:
            cells[game.snake[0]] = "▓"
        if game.food is not None:
            cells[game.food] = "●"
        border = "+" + "--" * game.width + "+"
        lines = [border]
        for y in range(game.height):
            row = [f"{cells.get((x, y), ' '):2}" for x in range(game.width)]
            lines.append("|" + "".join(row) + "|")
        lines.append(border)
        return "\n".join(lines)


class SnakeApp(App[None]):
    """Small keyboard-controlled Snake game."""

    CSS = """
    Screen { align: center middle; }
    #board { width: auto; height: auto; border: round green; padding: 1; }
    #status { width: auto; height: 1; margin: 1 0; }
    """
    BINDINGS = [("q", "quit", "Quit"), ("r", "restart", "Restart")]
    width = 20
    height = 12

    def __init__(self) -> None:
        super().__init__()
        self.snake: list[tuple[int, int]] = []
        self.direction = (1, 0)
        self.food: tuple[int, int] | None = None
        self.score = 0
        self.game_over = False
        self.restart_game()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Center():
            yield Static(id="status")
            yield SnakeBoard(self, id="board")
        yield Footer()

    def on_mount(self) -> None:
        self.update_view()

    def restart_game(self) -> None:
        cy, cx = self.height // 2, self.width // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.score = 0
        self.game_over = False
        self.food = (min(cx + 5, self.width - 1), cy)

    def action_restart(self) -> None:
        self.restart_game()
        self.update_view()

    def on_key(self, event) -> None:
        directions = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        if event.key in directions and not self.game_over:
            new_direction = directions[event.key]
            if new_direction != (-self.direction[0], -self.direction[1]):
                self.direction = new_direction
                self.move_snake()
                event.stop()

    def move_snake(self) -> None:
        if self.game_over:
            return
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        hits_wall = not (0 <= new_head[0] < self.width and 0 <= new_head[1] < self.height)
        hits_self = new_head in self.snake[:-1]
        if hits_wall or hits_self:
            self.game_over = True
            self.update_view()
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()
        self.update_view()

    def spawn_food(self) -> tuple[int, int] | None:
        empty = [(x, y) for y in range(self.height) for x in range(self.width) if (x, y) not in self.snake]
        return random.choice(empty) if empty else None

    def update_view(self) -> None:
        if not self.is_mounted:
            return
        self.query_one("#status", Static).update(
            f"Score: {self.score}  |  " + ("GAME OVER — press R to restart" if self.game_over else "Arrow keys: move")
        )
        self.query_one("#board", SnakeBoard).refresh()


if __name__ == "__main__":
    SnakeApp().run()
