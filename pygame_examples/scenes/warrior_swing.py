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


WARRIOR_TILE = (3, 7)
BATTLEAXE_TILE = (10, 9)
MOVEMENT_SPEED = 0.5

SCALE = 6

PADDING = 16
LINE_HEIGHT = 16
TEXT_SCALE = 2

FPS = 60


class Warrior(pygame.sprite.Sprite):
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
        self.image = transform.scale_by(self.ss.image_at_tile(WARRIOR_TILE), self.scale)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def update(self, x, y, screen_size):
        self.rect.x += x
        self.rect.y += y
        self.rect.x = min(max(self.rect.x, 0), screen_size[0] - self.tile_size_scale[0])
        self.rect.y = min(max(self.rect.y, 0), screen_size[1] - self.tile_size_scale[1])


class BattleAxe(pygame.sprite.Sprite):
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
        self.image = transform.scale_by(
            self.ss.image_at_tile(BATTLEAXE_TILE), self.scale
        )
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2 + SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
        self.target_angle = 0
        self.target_angle_sign = 1

        self._animate_frame_time = None
        self._animating = False
        self._weapon_frame_time = None

    def _current_angle(self, center, mouse_position):
            if center is None or mouse_position is None:
                return None
            x_len = mouse_position[0] - center[0]
            y_len = mouse_position[1] - center[1]

            if y_len == 0 and x_len > 0:
                angle = 90
            elif x_len == 0 and y_len > 0:
                angle = 0
            elif y_len == 0 and x_len <0:
                angle = 270
            elif x_len == 0 and y_len < 0:
                angle = 180
            else:
                angle = math.degrees(math.atan(x_len/y_len))
                if x_len > 0 and y_len < 0:
                    angle = angle + 180
                if y_len < 0 and x_len < 0:
                    angle = angle + 180
            return angle, x_len, y_len



    def update(self, trigger: bool = False, center=None, mouse_position=None):
        current_tick = pygame.time.get_ticks()
        animation_time = 50
        cooldown_time = 200
        swing_angle = 60
        if trigger and (self._animate_frame_time is None or self._animate_frame_time < current_tick):
            self._weapon_frame_time = current_tick + animation_time
            self._animate_frame_time = self._weapon_frame_time + cooldown_time
            self.target_angle, x_len, _ = self._current_angle(center, mouse_position)
            self.target_angle_sign = sign(x_len)


        if self._animate_frame_time is not None and self._animate_frame_time > current_tick:
            # animate
            angle_ratio = max(self._weapon_frame_time - current_tick, 0)/animation_time
            angle = self.target_angle + angle_ratio * swing_angle * self.target_angle_sign
            radius = LINE_HEIGHT * SCALE
            loc = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2) if center is None else center
            self.image = transform.rotate(
                transform.scale_by(
                    transform.flip(
                        self.ss.image_at_tile(BATTLEAXE_TILE), flip_x=False, flip_y=True
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
        elif mouse_position is not None and center is not None:
            angle, _, _ = self._current_angle(center, mouse_position)

            radius = LINE_HEIGHT * SCALE * 0.5
            loc = center
            self.image = transform.rotate(
                transform.scale_by(
                    transform.flip(
                        self.ss.image_at_tile(BATTLEAXE_TILE), flip_x=False, flip_y=True
                    ),
                    self.scale,
                ),
                angle,
            )
            self.rect = self.image.get_rect()
            loc_x, loc_y = (
                radius * math.sin(math.radians(angle)),
                radius * math.cos(math.radians(angle))
            )
            self.rect.center = (loc[0] + loc_x, loc[1] + loc_y)





class WarriorSwing(BaseScene):
    def __init__(self):
        self.font = FontUtils()
        self.tile_size = (16, 16)
        self.tile_size_scale = tuple([x * SCALE for x in list(self.tile_size)])
        self.screen = None
        self.screen_size = (600, 400)

        self.warrior_group = pygame.sprite.Group()
        self.battleaxe_group = pygame.sprite.Group()
        self.warrior = Warrior()
        self.battle_axe = BattleAxe()
        self.warrior_group.add(self.warrior)
        self.battleaxe_group.add(self.battle_axe)
        self.angle = 0

    def calculate_angle(self, ticks):
        # 60 secs per rotation, clockwise: -= (ticks/1000) * 2 * math.pi
        SPEED = 10
        self.angle += (ticks / 1000) * 2 * math.pi * SPEED
        self.angle = self.angle % 360

    def draw_text(self):
        screen_text_color = [
            "Press [w,a,s,b] to move",
            "Mouse click to swing",

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

        trigger = False
        if pygame.MOUSEBUTTONDOWN in events:
            trigger = True

        x, y = 0, 0
        if keys[pygame.K_w] and not keys[pygame.K_s]:
            y = -MOVEMENT_SPEED * dt
        elif keys[pygame.K_s] and not keys[pygame.K_w]:
            y = MOVEMENT_SPEED * dt
        if keys[pygame.K_a] and not keys[pygame.K_d]:
            x = -MOVEMENT_SPEED * dt
        elif keys[pygame.K_d] and not keys[pygame.K_a]:
            x = MOVEMENT_SPEED * dt

        self.battleaxe_group.update(trigger, self.warrior.rect.center, pygame.mouse.get_pos())
        self.warrior_group.update(x, y, self.screen_size)
        self.battleaxe_group.draw(screen)
        self.warrior_group.draw(screen)
        self.draw_text()
