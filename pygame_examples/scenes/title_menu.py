import pygame
from base import BaseScene
from utils.spritesheet_utils import FontUtils
from mapping.title_menu_enum import TitleMenuEnum
from common import TEXT_COLOR, RED_COLOR
from pygame import transform
import re

PADDING = 16
LINE_HEIGHT = 16
SCALE = 2


SCENE_NAMES = {
    title: re.sub(r"(\w)([A-Z])", r"\1 \2", str(title.value)).strip()
    for title in TitleMenuEnum
    if title != TitleMenuEnum.TitleMenu
}


class SceneText(pygame.sprite.Sprite):
    def __init__(self, scene, index=0):
        super().__init__()
        self.font = FontUtils()
        self.scene = scene
        self._selected_color = RED_COLOR
        self._unselected_color = TEXT_COLOR
        self.set_image()
        self.rect = self.image.get_rect()
        self.rect.x = PADDING * SCALE
        self.rect.y = PADDING * SCALE + LINE_HEIGHT * index * SCALE

    def set_image(self, collide: bool = False):
        self.image = transform.scale_by(
            self.font.text_to_image_shadow_effect(
                f" {SCENE_NAMES[self.scene]}",
                self._selected_color if collide else self._unselected_color,
            ),
            SCALE,
        )


class TitleMenu(BaseScene):
    def __init__(self):
        self.font = FontUtils()
        self.screen = None

        self.text_groups = {}
        self.text = {}

        for indx, scene in enumerate(SCENE_NAMES.keys()):
            self.text_groups[scene.value] = pygame.sprite.Group()
            self.text[scene.value] = SceneText(scene.value, indx)
            self.text_groups[scene.value].add(self.text[scene.value])

    def render(self, screen, clock, events, keys):
        pygame.mouse.set_visible(True)
        self.screen = screen
        point = pygame.mouse.get_pos()

        selected_menu = None

        for key, text_group in self.text_groups.items():
            is_collide = self.text[key].rect.collidepoint(point)
            self.text[key].set_image(is_collide)
            text_group.draw(screen)
            if is_collide and pygame.MOUSEBUTTONDOWN in events:
                selected_menu = key

        return selected_menu
