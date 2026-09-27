"""Headless integration checks: python -m unittest -v."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from tetris import load_scores, save_scores, tetris


def key(code, unicode=""):
    return pygame.event.Event(pygame.KEYDOWN, key=code, unicode=unicode)


def click(x, y):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(x, y))


def name_events(name):
    return [key(ord(c.lower()), c) for c in name] + [key(pygame.K_RETURN)]


def clear_two_rows():
    # Five square pieces fill two rows, from left to right.
    frames = []
    for offset in (-4, -2, 0, 2, 4):
        move = pygame.K_LEFT if offset < 0 else pygame.K_RIGHT
        frames.append([key(move)] * abs(offset) + [key(pygame.K_SPACE)])
    return frames


class TetrisTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "scores.json"

    def run_game(self, frames):
        frames = frames + [[pygame.event.Event(pygame.QUIT)]]
        clock = Mock()
        clock.tick.return_value = 16
        with patch("pygame.event.get", side_effect=frames), \
                patch("pygame.time.Clock", return_value=clock), \
                patch("random.randrange", return_value=2):
            result = tetris(self.path)
        self.assertFalse(pygame.get_init())
        return result

    def test_pause_scoring_restart_and_players(self):
        frames = [[key(pygame.K_RETURN)], name_events("Alice")]
        frames += [[click(300, 682)]]  # Pause, then ignore input and gravity.
        frames += [[key(pygame.K_SPACE), key(pygame.K_LEFT)]] * 40
        frames += [[click(300, 682)]]
        frames += clear_two_rows()
        frames += [[click(400, 682)]]  # Restart, preserving Alice's best.
        frames += [[click(100, 682)], name_events("Bob")]
        frames += clear_two_rows()
        frames += clear_two_rows()
        self.assertEqual(self.run_game(frames), 600)
        self.assertEqual(load_scores(self.path), {"Alice": 300, "Bob": 600})
        # A new session and different capitalization reuse the same record.
        self.assertEqual(self.run_game([name_events("alice")]), 0)
        self.assertEqual(load_scores(self.path), {"Alice": 300, "Bob": 600})

    def test_game_over_can_restart(self):
        frames = [name_events("Player")]
        frames += [[key(pygame.K_SPACE)]] * 12
        frames += [[click(400, 682)]] + clear_two_rows()
        self.assertEqual(self.run_game(frames), 300)

    def test_cancel_new_game_and_scroll(self):
        save_scores(self.path, {f"Player {i}": i * 100 for i in range(20)})
        frames = [name_events("Alice"), [click(100, 682)],
                  [key(pygame.K_ESCAPE)],
                  [pygame.event.Event(pygame.MOUSEWHEEL, y=-100)],
                  [pygame.event.Event(pygame.MOUSEWHEEL, y=100)]]
        self.assertEqual(self.run_game(frames + clear_two_rows()), 300)
        self.assertEqual(len(load_scores(self.path)), 21)

    def test_score_storage_and_invalid_data(self):
        self.assertEqual(load_scores(self.path), {})
        self.path.write_text("invalid", encoding="utf-8")
        self.assertEqual(load_scores(self.path), {})
        self.path.write_text('[1, 2]', encoding="utf-8")
        self.assertEqual(load_scores(self.path), {})
        save_scores(self.path, {"Alice": 300, "Bob": -1, "Invalid": True})
        self.assertEqual(load_scores(self.path), {"Alice": 300})

    def test_save_error_does_not_crash_game(self):
        with patch("tetris.save_scores", side_effect=OSError("Read only")):
            self.assertEqual(self.run_game([name_events("Alice")]), 0)


if __name__ == "__main__":
    unittest.main()
