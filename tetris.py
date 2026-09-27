import random

import pygame


def tetris():
    pygame.init()
    cols, rows, size = 10, 20, 28
    screen = pygame.display.set_mode((cols * size, rows * size))
    clock = pygame.time.Clock()
    board = [[0] * cols for _ in range(rows)]
    shapes = [
        ["1111"], ["11", "11"], ["010", "111"],
        ["011", "110"], ["110", "011"],
        ["100", "111"], ["001", "111"],
    ]
    colors = [
        (20, 22, 30), (0, 220, 220), (240, 220, 0),
        (170, 70, 220), (50, 210, 90), (230, 60, 70),
        (60, 100, 240), (240, 150, 40),
    ]
    score = elapsed = 0
    running = True

    def spawn():
        color = random.randrange(1, 8)
        piece = [[color * int(c) for c in row]
                 for row in shapes[color - 1]]
        return piece, (cols - len(piece[0])) // 2, 0

    def fits(piece, x, y):
        return all(
            0 <= x + dx < cols and 0 <= y + dy < rows
            and not board[y + dy][x + dx]
            for dy, row in enumerate(piece)
            for dx, cell in enumerate(row) if cell
        )

    piece, x, y = spawn()
    try:
        while running:
            elapsed += clock.tick(60)
            drop = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        step = 1 if event.key == pygame.K_RIGHT else -1
                        if fits(piece, x + step, y):
                            x += step
                    elif event.key == pygame.K_UP:
                        rotated = [list(row) for row in zip(*piece[::-1])]
                        if fits(rotated, x, y):
                            piece = rotated
                    elif event.key == pygame.K_SPACE:
                        while fits(piece, x, y + 1):
                            y += 1
                        drop = True

            if not running:
                break

            delay = 50 if pygame.key.get_pressed()[pygame.K_DOWN] else 500
            if drop or elapsed >= delay:
                elapsed = 0
                if not drop and fits(piece, x, y + 1):
                    y += 1
                else:
                    for dy, row in enumerate(piece):
                        for dx, cell in enumerate(row):
                            if cell:
                                board[y + dy][x + dx] = cell

                    remaining = [row for row in board if not all(row)]
                    cleared = rows - len(remaining)
                    score += (0, 100, 300, 500, 800)[cleared]
                    board = [[0] * cols for _ in range(cleared)] + remaining
                    piece, x, y = spawn()
                    if not fits(piece, x, y):
                        break

            pygame.display.set_caption(f"Tetris - Score: {score}")
            screen.fill(colors[0])
            for grid, ox, oy in ((board, 0, 0), (piece, x, y)):
                for dy, row in enumerate(grid):
                    for dx, cell in enumerate(row):
                        if cell:
                            pygame.draw.rect(
                                screen, colors[cell],
                                ((ox + dx) * size, (oy + dy) * size,
                                 size - 1, size - 1),
                            )
            pygame.display.flip()
    finally:
        pygame.quit()

    return score


if __name__ == "__main__":
    print("Final score:", tetris())
