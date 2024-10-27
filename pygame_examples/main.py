import pygame
from pygame import K_ESCAPE
import asyncio

from scenes.warrior_swing import WarriorSwing
from scenes.wizard_clock import WizardClock
from scenes.animate_movement import AnimateMovement
from scenes.collect_potions import CollectPotions
from scenes.title_menu import TitleMenu

from mapping.title_menu_enum import TitleMenuEnum
from common import SCREEN_HEIGHT, SCREEN_WIDTH, BASE_COLOR

# Initialize pygame
pygame.init()

screen_display = pygame.display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

title_screen = TitleMenu()
collect_potions = CollectPotions()
animate_movement = AnimateMovement()
wizard_clock = WizardClock()
warrior_swing = WarriorSwing()


async def main():
    running = True
    title_selected = None
    while running:
        events = []
        for event in pygame.event.get():
            events.append(event.type)
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BASE_COLOR)
        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE]:
            title_selected = TitleMenuEnum.TitleMenu
        if title_selected is None or title_selected == TitleMenuEnum.TitleMenu:
            title_selected: TitleMenuEnum | None = title_screen.render(
                screen, clock, events, keys
            )
        elif title_selected == TitleMenuEnum.CollectPotions:
            collect_potions.render(screen, clock, events, keys)
        elif title_selected == TitleMenuEnum.AnimateMovement:
            animate_movement.render(screen, clock, events, keys)
        elif title_selected == TitleMenuEnum.WizardClock:
            wizard_clock.render(screen, clock, events, keys)
        elif title_selected == TitleMenuEnum.WarriorSwing:
            warrior_swing.render(screen, clock, events, keys)

        screen_display.update()
        pygame.display.flip()
        await asyncio.sleep(0)  # Let other tasks run


# This is the program entry point
asyncio.run(main())
