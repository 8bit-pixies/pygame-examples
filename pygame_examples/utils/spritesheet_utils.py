from typing import Tuple
import pygame

from pathlib import Path

BASE_ASSET_PATH = Path(__file__).parent.parent.joinpath("assets")
string_printable = """ !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"""


class SpritesheetUtils:
    def __init__(self, filename, *, with_basename=True, tile_size=16, colorkey=None):
        if with_basename:
            filename = BASE_ASSET_PATH.joinpath(filename)
        try:
            self.sheet = pygame.image.load(filename).convert()
        except Exception as e:
            print("Unable to load spritesheet image:", filename)
            raise Exception(e)

        self.tile_size = tile_size
        self.colorkey = colorkey

    def image_at_tile(self, tile, colorkey=None):
        row, column = tile
        tile_size = self.tile_size
        if isinstance(tile_size, int):
            tile_size = (tile_size, tile_size)
        x, y = row * tile_size[0], column * tile_size[1]
        image_at_rect = (x, y, tile_size[0], tile_size[1])
        return self.image_at(image_at_rect, colorkey=colorkey)

    def image_at(self, rectangle, colorkey=None):
        """Loads image from x,y,x+offset,y+offset"""
        colorkey = self.colorkey if colorkey is None else colorkey
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey=None):
        """Loads multiple images, supply a list of coordinates"""
        return [self.image_at(rect, colorkey) for rect in rects]

    def images_at_tiles(self, tiles, colorkey=None):
        """Loads multiple images, supply a list of coordinates"""
        return [self.image_at_tile(tile, colorkey) for tile in tiles]

    def load_strip(self, rect, image_count, colorkey=None):
        """Loads a strip of images and returns them as a list"""
        tups = [
            (rect[0] + rect[2] * x, rect[1], rect[2], rect[3])
            for x in range(image_count)
        ]
        return self.images_at(tups, colorkey)


class FontUtils:
    def __init__(self):
        self.bitmap_size = (8, 16)
        self.ss = SpritesheetUtils(
            "bitmap_font/kenney-pixel.png",
            tile_size=self.bitmap_size,
            colorkey=(0, 0, 0),
        )
        self.character_mapping = {v: idx for idx, v in enumerate(string_printable)}

    def character_to_image(self, character):
        tile_index = self.character_mapping[character]
        return self.ss.image_at_tile((tile_index, 0))

    def text_to_image(self, text: str, set_color: Tuple[int, int, int] | None = None):
        image = pygame.Surface(
            (len(text) * self.bitmap_size[0], self.bitmap_size[1])
        ).convert()
        image.set_colorkey((0, 0, 0))

        for i, character in enumerate(text):
            image.blit(self.character_to_image(character), (i * self.bitmap_size[0], 0))

        if set_color is not None:
            color_image = pygame.Surface(image.get_size()).convert_alpha()
            color_image.fill(set_color)
            image.blit(color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return image

    def text_to_image_shadow_effect(
        self,
        text,
        set_color=None,
        offsets=[(1, 1), (0, 1), (1, 0), (2, 2)],
        shadow_color=(25, 25, 25),
    ):
        max_x_offset = max([x[0] for x in offsets])
        max_y_offset = max([x[1] for x in offsets])
        if any([x[0] < 0 for x in offsets]) or any([x[1] < 0 for x in offsets]):
            raise Exception("Negative offsets not supported")
        image = pygame.Surface(
            (
                len(text) * self.bitmap_size[0] + max_x_offset,
                self.bitmap_size[1] + max_y_offset,
            )
        ).convert()
        image.set_colorkey((0, 0, 0))
        shadow = self.text_to_image(text, shadow_color)
        display_text = self.text_to_image(text, set_color)

        for offset in offsets:
            image.blit(shadow, (offset[0], offset[0]))
        image.blit(display_text, (0, 0))
        return image
