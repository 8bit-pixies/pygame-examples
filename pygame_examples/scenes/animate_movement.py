"""
This shows how to animate idle animations and reacting to
events where the character interacts with a in world object

A substitution for

- python -m arcade.examples.sprite_change_coins

Demonstrates how to:

- Animate an action on a specific collision and trigger
- Move sprites around with consideration on colliding with obstacles
- Add sound effects to the game
"""

import pygame
from common import SCREEN_HEIGHT, SCREEN_WIDTH

from pygame import transform
from base import BaseScene
from utils.spritesheet_utils import SpritesheetUtils, FontUtils, BASE_ASSET_PATH
from common import TEXT_COLOR
from enum import Enum
import math
import functools


sign = functools.partial(math.copysign, 1)


class AnimateOpenClose(Enum):
    CLOSE = 0
    OTHER = 1
    OPEN = 2


WIZARD_TILE = (0, 7)
CHEST_TILE = (5, 7)
SWITCH_TILE = (1, 5)
MOVEMENT_SPEED = 0.5
FPS = 60

SCALE = 6

PADDING = 16
LINE_HEIGHT = 16
TEXT_SCALE = 2


class Wizard(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.scale = SCALE
        self.tile_size = (16, 16)
        self.tile_size_scale = tuple([x * self.scale for x in list(self.tile_size)])
        self.ss = SpritesheetUtils(
            "tiny_dungeon/tilemap_packed.png",
            tile_size=self.tile_size,
            colorkey=(0, 0, 0),
        )
        self.image = transform.scale_by(self.ss.image_at_tile(WIZARD_TILE), self.scale)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 4
        self.rect.y = SCREEN_HEIGHT // 4

    def update(self, x, y, screen_size):
        self.rect.x += x
        self.rect.y += y
        self.rect.x = min(max(self.rect.x, 0), screen_size[0] - self.tile_size_scale[0])
        self.rect.y = min(max(self.rect.y, 0), screen_size[1] - self.tile_size_scale[1])


class Switch(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.scale = SCALE
        self.tile_size = (16, 16)
        self.tile_size_scale = tuple([x * self.scale for x in list(self.tile_size)])
        self.ss = SpritesheetUtils(
            "tiny_dungeon/tilemap_packed.png",
            tile_size=self.tile_size,
            colorkey=(0, 0, 0),
        )
        self.image = transform.scale_by(self.ss.image_at_tile(SWITCH_TILE), self.scale)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2 + SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)


class Chest(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.scale = SCALE
        self.tile_size = (16, 16)
        self.tile_size_scale = tuple([x * self.scale for x in list(self.tile_size)])
        self.ss = SpritesheetUtils(
            "tiny_dungeon/tilemap_packed.png",
            tile_size=self.tile_size,
            colorkey=(0, 0, 0),
        )
        self.images = [
            transform.scale_by(
                self.ss.image_at_tile((CHEST_TILE[0] + idx, CHEST_TILE[1])), self.scale
            )
            for idx in range(3)
        ]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        self._animate_frame_time = None
        self._frame = 0
        self.open_close_status: str = ""
        self.animating = AnimateOpenClose.OTHER

        self.sound_open = pygame.mixer.Sound(
            BASE_ASSET_PATH.joinpath("rpg_audio/doorOpen_1.ogg")
        )
        self.sound_open.set_volume(0.3)
        self.sound_close = pygame.mixer.Sound(
            BASE_ASSET_PATH.joinpath("rpg_audio/doorClose_4.ogg")
        )
        self.sound_close.set_volume(0.3)

    def update(self, trigger_chest: bool = False):
        if (
            trigger_chest and self.open_close_status == AnimateOpenClose.CLOSE
        ) or self.animating == AnimateOpenClose.OPEN:
            if (
                self._animate_frame_time is None
                or self._animate_frame_time > pygame.time.get_ticks()
            ):
                if trigger_chest:
                    self.sound_close.play()
                self._animate_frame_time = pygame.time.get_ticks() + 2000
                self._frame = min(self._frame + 1, AnimateOpenClose.OPEN.value)
                self.image = self.images[self._frame]
                self.animating = AnimateOpenClose.OPEN

        elif (
            trigger_chest and self.open_close_status == AnimateOpenClose.OPEN
        ) or self.animating == AnimateOpenClose.CLOSE:
            if (
                self._animate_frame_time is None
                or self._animate_frame_time > pygame.time.get_ticks()
            ):
                if trigger_chest:
                    self.sound_open.play()
                self._animate_frame_time = pygame.time.get_ticks() + 2000
                self._frame = max(self._frame - 1, AnimateOpenClose.CLOSE.value)
                self.image = self.images[self._frame]
                self.animating = AnimateOpenClose.CLOSE

        if self._frame == AnimateOpenClose.OPEN.value:
            self.open_close_status = AnimateOpenClose.OPEN
            self.animating = None
            self._animate_frame_time = None
        elif self._frame == AnimateOpenClose.CLOSE.value:
            self.open_close_status = AnimateOpenClose.CLOSE
            self.animating = None
            self._animate_frame_time = None
        else:
            self.open_close_status = AnimateOpenClose.OTHER


class AnimateMovement(BaseScene):
    def __init__(self):
        self.font = FontUtils()
        self.tile_size = (16, 16)
        self.tile_size_scale = tuple([x * SCALE for x in list(self.tile_size)])
        self.screen = None
        self.screen_size = (600, 400)

        self.wizard_group = pygame.sprite.Group()
        self.chest_group = pygame.sprite.Group()
        self.wizard = Wizard()
        self.chest = Chest()
        self.chest_group.add(Switch(), self.chest)
        self.wizard_group.add(self.wizard)

        self._trigger_update_lock = None

    def draw_text(self):
        screen_text_color = ["Move around using Keyboard", "Use [z] to interact"]

        for indx, text in enumerate(screen_text_color):
            self.screen.blit(
                transform.scale_by(
                    self.font.text_to_image_shadow_effect(text, TEXT_COLOR), TEXT_SCALE
                ),
                (
                    PADDING * TEXT_SCALE,
                    PADDING * TEXT_SCALE + LINE_HEIGHT * indx * TEXT_SCALE,
                ),
            )

    def render(self, screen, clock, events, keys):
        pygame.mouse.set_visible(True)
        self.screen = screen
        self.screen_size = screen.get_size()
        dt = clock.tick(FPS)

        x, y = 0, 0
        if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            y = -MOVEMENT_SPEED * dt
        elif keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
            y = MOVEMENT_SPEED * dt
        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            x = -MOVEMENT_SPEED * dt
        elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            x = MOVEMENT_SPEED * dt

        self.chest_group.update()
        collision_list = pygame.sprite.spritecollide(
            self.wizard, self.chest_group, False
        )

        if any([isinstance(x, Chest) for x in collision_list]):
            rect = [x for x in collision_list if isinstance(x, Chest)][0].rect
            if (
                rect.collidepoint(self.wizard.rect.midbottom)
                or rect.collidepoint(self.wizard.rect.bottomright)
                or rect.collidepoint(self.wizard.rect.bottomleft)
            ):
                if y > 0:
                    y *= -1
            elif (
                rect.collidepoint(self.wizard.rect.midtop)
                or rect.collidepoint(self.wizard.rect.topright)
                or rect.collidepoint(self.wizard.rect.topleft)
            ):
                if y < 0:
                    y *= -1
            if (
                rect.collidepoint(self.wizard.rect.midleft)
                or rect.collidepoint(self.wizard.rect.topleft)
                or rect.collidepoint(self.wizard.rect.bottomleft)
            ):
                if x < 0:
                    x *= -1
            elif (
                rect.collidepoint(self.wizard.rect.midright)
                or rect.collidepoint(self.wizard.rect.topright)
                or rect.collidepoint(self.wizard.rect.bottomright)
            ):
                if x > 0:
                    x *= -1
        if (
            any([isinstance(x, Switch) for x in collision_list])
            and keys[pygame.K_z]
            and (
                self._trigger_update_lock is None
                or self._trigger_update_lock < pygame.time.get_ticks()
            )
        ):
            self.chest_group.update(trigger_chest=True)
            self._trigger_update_lock = pygame.time.get_ticks() + 400  # lock for x ms

        self.wizard_group.update(x, y, self.screen_size)
        self.chest_group.draw(screen)
        self.wizard_group.draw(screen)

        self.draw_text()
