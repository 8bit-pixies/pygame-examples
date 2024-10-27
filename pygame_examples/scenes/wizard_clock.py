"""
This is a study into using transform rotation
"""

import pygame
from common import SCREEN_HEIGHT, SCREEN_WIDTH

from pygame import transform
from base import BaseScene
from utils.spritesheet_utils import SpritesheetUtils, FontUtils
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
POTION_TILE = (5, 10)
MOVEMENT_SPEED = 0.5

SCALE = 6

PADDING = 16
LINE_HEIGHT = 16
TEXT_SCALE = 2

FPS = 60


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
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def update(self, x, y, screen_size):
        self.rect.x += x
        self.rect.y += y
        self.rect.x = min(max(self.rect.x, 0), screen_size[0] - self.tile_size_scale[0])
        self.rect.y = min(max(self.rect.y, 0), screen_size[1] - self.tile_size_scale[1])


class Potion(pygame.sprite.Sprite):
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
        self.image = transform.scale_by(self.ss.image_at_tile(POTION_TILE), self.scale)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2 + SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
        self.angle = 0

    def update(self, angle, center=None):
        radius = LINE_HEIGHT * SCALE
        loc = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2) if center is None else center
        self.image = transform.rotate(
            transform.scale_by(
                transform.flip(
                    self.ss.image_at_tile(POTION_TILE), flip_x=False, flip_y=True
                ),
                self.scale,
            ),
            angle,
        )
        self.rect = self.image.get_rect()
        loc_x, loc_y = (
            radius * math.sin(math.radians(angle)),
            radius * math.cos(math.radians(angle)),
        )
        self.rect.center = (loc[0] + loc_x, loc[1] + loc_y)


class WizardClock(BaseScene):
    def __init__(self):
        self.font = FontUtils()
        self.tile_size = (16, 16)
        self.tile_size_scale = tuple([x * SCALE for x in list(self.tile_size)])
        self.screen = None
        self.screen_size = (600, 400)

        self.wizard_group = pygame.sprite.Group()
        self.potion_group = pygame.sprite.Group()
        self.wizard = Wizard()
        self.potion = Potion()
        self.wizard_group.add(self.wizard)
        self.potion_group.add(self.potion)
        self.angle = 0

    def calculate_angle(self, ticks):
        # 60 secs per rotation, clockwise: -= (ticks/1000) * 2 * math.pi
        SPEED = 10
        self.angle += (ticks / 1000) * 2 * math.pi * SPEED
        self.angle = self.angle % 360

    def draw_text(self):
        screen_text_color = [
            "Watch the clock move",
            "Arrow keys move the wizard around",
            f"Hand angle is currently {int(self.angle)}",
        ]

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
        dt = clock.tick(FPS)
        self.screen = screen
        self.screen_size = screen.get_size()
        self.calculate_angle(dt)

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
        self.potion_group.update(self.angle, self.wizard.rect.center)
        self.wizard_group.draw(screen)
        self.potion_group.draw(screen)
        self.draw_text()
