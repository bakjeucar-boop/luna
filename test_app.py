import pytest

from snake_app import SnakeApp


@pytest.mark.asyncio
async def test_snake_moves_with_pilot_input() -> None:
    async with SnakeApp().run_test() as pilot:
        app = pilot.app
        start = app.snake[0]
        await pilot.press("right")
        assert app.snake[0] == (start[0] + 1, start[1])


@pytest.mark.asyncio
async def test_eating_food_increases_score() -> None:
    async with SnakeApp().run_test() as pilot:
        app = pilot.app
        head_x, head_y = app.snake[0]
        app.food = (head_x + 1, head_y)
        await pilot.press("right")
        assert app.score == 1
        assert len(app.snake) == 4


@pytest.mark.asyncio
async def test_wall_collision_causes_game_over() -> None:
    async with SnakeApp().run_test() as pilot:
        app = pilot.app
        app.snake = [(0, 0), (1, 0), (2, 0)]
        app.direction = (-1, 0)
        await pilot.press("left")
        assert app.game_over is True


@pytest.mark.asyncio
async def test_self_collision_causes_game_over() -> None:
    async with SnakeApp().run_test() as pilot:
        app = pilot.app
        app.snake = [(2, 2), (2, 3), (1, 3), (1, 2)]
        app.direction = (0, 1)
        await pilot.press("down")
        assert app.game_over is True


def test_initial_screen_snapshot(snap_compare) -> None:
    assert snap_compare(SnakeApp(), terminal_size=(40, 12))


def test_after_move_screen_snapshot(snap_compare) -> None:
    async def run_before(pilot) -> None:
        pilot.app.move_snake()
        await pilot.pause()

    assert snap_compare(
        SnakeApp(),
        run_before=run_before,
        terminal_size=(40, 12),
    )


# Snapshot tests intentionally use a fixed terminal size for stable baselines.
