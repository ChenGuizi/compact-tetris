# Compact Tetris

A compact Python Tetris game using Pygame, implemented in one function.

## Run

Requires Python 3.9 or newer.

```sh
python -m pip install -r requirements.txt
python tetris.py
```

## Controls

| Key | Action |
| --- | --- |
| Left / Right | Move |
| Up | Rotate clockwise |
| Down (hold) | Fall faster |
| Space | Drop immediately |
| Esc | Quit |

Clear full rows to score 100, 300, 500, or 800 points for clearing one,
two, three, or four rows at once. The game ends when a new piece cannot
spawn. Your final score is printed in the terminal. Run again to restart.
