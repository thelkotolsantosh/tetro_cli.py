import curses
import random
import time
import sys

# ========== ASCII INTRO ==========
INTRO = r"""
████████╗███████╗████████╗██████╗  ██████╗     ██████╗██╗     ██╗
╚══██╔══╝██╔════╝╚══██╔══╝██╔══██╗██╔═══██╗   ██╔════╝██║     ██║
   ██║   █████╗     ██║   ██████╔╝██║   ██║   ██║     ██║     ██║
   ██║   ██╔══╝     ██║   ██╔══██╗██║   ██║   ██║     ██║     ██║
   ██║   ███████╗   ██║   ██║  ██║╚██████╔╝   ╚██████╗███████╗██║
   ╚═╝   ╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝     ╚═════╝╚══════╝╚═╝

              made by Santosh Thelkotol
"""

# ========== TETRIS SHAPES ==========
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
]

# ========== MAIN GAME ==========
def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for i in range(1, 8):
        curses.init_pair(i, i, -1)

    stdscr.nodelay(True)
    stdscr.timeout(100)

    max_y, max_x = stdscr.getmaxyx()
    play_w = max_x - 10
    play_h = max_y - 5

    grid = [[0 for _ in range(play_w // 2)] for _ in range(play_h)]

    lives = 3
    score = 0

    def new_piece():
        shape = random.choice(SHAPES)
        color = random.randint(1, 7)
        return {"shape": shape, "x": len(grid[0]) // 2, "y": 0, "color": color}

    piece = new_piece()

    def draw_border():
        for y in range(play_h):
            for i in range(2):
                stdscr.addstr(y, 0 + i, "█", curses.color_pair((y % 7) + 1))
                stdscr.addstr(y, max_x - 2 + i, "█", curses.color_pair((y % 7) + 1))
        for x in range(max_x):
            stdscr.addstr(0, x, "█", curses.color_pair((x % 7) + 1))
            stdscr.addstr(play_h - 1, x, "█", curses.color_pair((x % 7) + 1))

    def draw_grid():
        for y in range(play_h):
            for x in range(len(grid[0])):
                if grid[y][x]:
                    stdscr.addstr(y, 2 + x * 2, "██", curses.color_pair(grid[y][x]))

    def draw_piece():
        for y, row in enumerate(piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    stdscr.addstr(
                        piece["y"] + y,
                        2 + (piece["x"] + x) * 2,
                        "██",
                        curses.color_pair(piece["color"]),
                    )

    def collision(dx=0, dy=0, rotate=None):
        shape = rotate if rotate else piece["shape"]
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    nx = piece["x"] + x + dx
                    ny = piece["y"] + y + dy
                    if ny >= play_h or nx < 0 or nx >= len(grid[0]):
                        return True
                    if ny >= 0 and grid[ny][nx]:
                        return True
        return False

    def freeze():
        nonlocal piece, score
        for y, row in enumerate(piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    grid[piece["y"] + y][piece["x"] + x] = piece["color"]
        clear_lines()
        piece = new_piece()
        if collision():
            return True
        return False

    def clear_lines():
        nonlocal score
        new_grid = [row for row in grid if any(cell == 0 for cell in row)]
        cleared = play_h - len(new_grid)
        score += cleared * 100
        while len(new_grid) < play_h:
            new_grid.insert(0, [0] * len(grid[0]))
        grid[:] = new_grid

    def rotate(shape):
        return list(zip(*shape[::-1]))

    last_time = time.time()
    speed = 0.5

    while True:
        stdscr.clear()
        draw_border()
        draw_grid()
        draw_piece()
        stdscr.addstr(1, max_x - 8, f"Lives: {lives}")
        stdscr.addstr(2, max_x - 8, f"Score: {score}")

        key = stdscr.getch()

        if key == curses.KEY_LEFT and not collision(dx=-1):
            piece["x"] -= 1
        elif key == curses.KEY_RIGHT and not collision(dx=1):
            piece["x"] += 1
        elif key == curses.KEY_DOWN and not collision(dy=1):
            piece["y"] += 1
        elif key == curses.KEY_UP:
            new_shape = rotate(piece["shape"])
            if not collision(rotate=new_shape):
                piece["shape"] = new_shape
        elif key == ord("q"):
            sys.exit()

        if time.time() - last_time > speed:
            if not collision(dy=1):
                piece["y"] += 1
            else:
                if freeze():
                    lives -= 1
                    grid[:] = [[0 for _ in range(len(grid[0]))] for _ in range(play_h)]
                    piece = new_piece()
                    if lives == 0:
                        stdscr.clear()
                        stdscr.addstr(play_h // 2, max_x // 2 - 5, "GAME OVER")
                        stdscr.refresh()
                        time.sleep(3)
                        return
            last_time = time.time()

        stdscr.refresh()

# ========== BOOT ==========
def boot():
    try:
        curses.wrapper(splash)
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass

def splash(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    for i, line in enumerate(INTRO.split("\n")):
        stdscr.addstr(i + 2, (w - len(line)) // 2, line)
    stdscr.addstr(h - 3, w // 2 - 12, "Press any key to start")
    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    boot()
