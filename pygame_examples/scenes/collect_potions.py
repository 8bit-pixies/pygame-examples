"""
Sprite for collecting potions. This example encompasses the equivalent demo for

- python -m arcade.examples.sprite_collect_coins
- python -m arcade.examples.sprite_move_keyboard_better
- python -m arcade.examples.sprite_collect_coins_move_down

Key concepts:

- Responding to keyboard and mouse events
- Responding to timer events (locking how quickly gravity is switched on/off)
- Understanding sprite collisions and sprite groups

"""

from typing import Tuple
import pygame
import random

from common import SCREEN_HEIGHT, SCREEN_WIDTH
from pygame import transform
from base import BaseScene
from utils.spritesheet_utils import SpritesheetUtils, FontUtils
from common import TEXT_COLOR, BLUE_COLOR
from enum import Enum

POTION_TILE = (7, 9)
WIZARD_TILE = (0, 7)

NUM_POTIONS = 15
LINE_HEIGHT = 32

MOVEMENT_SPEED = 0.5
GRAVITY_SPEED = 0.1
FPS = 60

PADDING = 16
LINE_HEIGHT = 16
SCALE = 2


class InputMode(str, Enum):
    KEYBOARD = "KEYBOARD"
    MOUSE = "MOUSE"


class Wizard(pygame.sprite.Sprite):
    tile_size = (16, 16)

    def __init__(self):
        super().__init__()
        self.tile_size_scaled = tuple([x * SCALE for x in list(self.tile_size)])
        self.ss = SpritesheetUtils(
            "tiny_dungeon/tilemap_packed.png",
            tile_size=self.tile_size,
            colorkey=(0, 0, 0),
        )
        self.image = transform.scale_by(self.ss.image_at_tile(WIZARD_TILE), 2)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 4
        self.rect.y = SCREEN_HEIGHT // 4

    def update(self, x, y, screen_size):
        self.rect.x += x
        self.rect.y += y
        self.rect.x = min(
            max(self.rect.x, 0), screen_size[0] - self.tile_size_scaled[0]
        )
        self.rect.y = min(
            max(self.rect.y, 0), screen_size[1] - self.tile_size_scaled[1]
        )


class Potion(pygame.sprite.Sprite):
    tile_size = (16, 16)

    def __init__(self, x, y):
        super().__init__()
        self.ss = SpritesheetUtils(
            "tiny_dungeon/tilemap_packed.png",
            tile_size=self.tile_size,
            colorkey=(0, 0, 0),
        )
        self.image = transform.scale_by(self.ss.image_at_tile(POTION_TILE), SCALE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(
        self,
        gravity_enabled: bool = False,
        dt: float = 0,
        screen_size: Tuple[int, int] = (800, 800),
    ):
        if gravity_enabled:
            self.rect.y += GRAVITY_SPEED * dt
        if self.rect.bottom > screen_size[1]:
            self.rect.y = 0


class CollectPotions(BaseScene):
    def __init__(self):
        self.font = FontUtils()
        self.screen = None
        self.screen_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.input_mode: InputMode = InputMode.MOUSE
        self.gravity_enabled: bool = False
        self._gravity_update_lock: bool = None

        self.score = 0
        self.potion_group = pygame.sprite.Group()
        self.wizard_group = pygame.sprite.Group()
        self.wizard = Wizard()
        self.wizard_group.add(self.wizard)
        self._reset_potions()

    def draw_score(self):
        screen_text_color = [
            (f" Score: {self.score}", TEXT_COLOR),
            (
                " Keyboard mode [K]",
                TEXT_COLOR if not InputMode.KEYBOARD == self.input_mode else BLUE_COLOR,
            ),
            (
                " Mouse mode [M]",
                TEXT_COLOR if not InputMode.MOUSE == self.input_mode else BLUE_COLOR,
            ),
            (
                f" Toggle Gravity [G]: {'ON' if self.gravity_enabled else 'OFF'}",
                TEXT_COLOR,
            ),
        ]

        for indx, (text, color) in enumerate(screen_text_color):
            self.screen.blit(
                transform.scale_by(
                    self.font.text_to_image_shadow_effect(text, color), SCALE
                ),
                (PADDING * SCALE, PADDING * SCALE + LINE_HEIGHT * indx * SCALE),
            )

    def _reset_potions(self):
        x_range = self.screen_size[0] // Potion.tile_size[0] - 1
        y_range = self.screen_size[1] // Potion.tile_size[1] - 1
        for x, y in [
            (x * Potion.tile_size[0], y * Potion.tile_size[1])
            for x, y in zip(
                random.sample(range(x_range), k=NUM_POTIONS),
                random.sample(range(y_range), k=NUM_POTIONS),
            )
        ]:
            self.potion_group.add(Potion(x, y))

    def reset_potions_if_required(self):
        if len(self.potion_group.sprites()) == 0:
            self._reset_potions()

    def render(self, screen, clock, events, keys):
        self.screen = screen
        self.screen_size = screen.get_size()
        dt = clock.tick(FPS)
        pygame.mouse.set_visible(False)

        if keys[pygame.K_k]:
            self.input_mode = InputMode.KEYBOARD
        if keys[pygame.K_m]:
            self.input_mode = InputMode.MOUSE

        if keys[pygame.K_g] and (
            self._gravity_update_lock is None
            or self._gravity_update_lock < pygame.time.get_ticks()
        ):
            self.gravity_enabled = not self.gravity_enabled
            self._gravity_update_lock = pygame.time.get_ticks() + 400  # lock for x ms

        if self.input_mode == InputMode.MOUSE:
            self.wizard.rect.center = pygame.mouse.get_pos()
        if self.input_mode == InputMode.KEYBOARD:
            x, y = 0, 0
            if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
                y = -MOVEMENT_SPEED * dt
            elif keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
                y = MOVEMENT_SPEED * dt
            if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
                x = -MOVEMENT_SPEED * dt
            elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
                x = MOVEMENT_SPEED * dt

            self.wizard_group.update(x, y, self.screen_size)

        self.potion_group.update(self.gravity_enabled, dt, self.screen_size)

        # check collision, remove and update
        start = len(self.potion_group.sprites())
        pygame.sprite.groupcollide(
            self.wizard_group, self.potion_group, dokilla=False, dokillb=True
        )
        diff_score = start - len(self.potion_group.sprites())
        self.score += diff_score

        self.potion_group.draw(screen)
        self.wizard_group.draw(screen)

        self.draw_score()
        self.reset_potions_if_required()
