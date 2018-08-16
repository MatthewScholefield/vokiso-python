import atexit
from itertools import zip_longest

import pygame
from pygame import Surface
from random import random
from typing import Callable


class UiManager:
    colors = [
        (150, 90, 90),
        (90, 90, 150),
    ]
    default_color = (50, 50, 50)
    bg_color = (230, 210, 200)
    box_size = 0.05  # 1.0 is whole screen
    move_speed = 0.01

    def __init__(self, on_new_pos: Callable):
        pygame.init()
        atexit.register(pygame.quit)
        pygame.display.set_caption('Vokiso')
        pygame.display.set_icon(pygame.image.load('logo.png'))
        self.screen = self.create_screen(640, 480)
        self.clock = pygame.time.Clock()
        self.pos = [random(), random()]
        self.on_new_pos = on_new_pos
        self.on_new_pos(self.pos)
        self.eased_positions = []

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit
            elif event.type == pygame.VIDEORESIZE:
                self.screen = self.create_screen(event.w, event.h)

        pressed = pygame.key.get_pressed()
        for key, xdir, ydir in [
            (pygame.K_w, 0, -1),
            (pygame.K_s, 0, 1),
            (pygame.K_a, -1, 0),
            (pygame.K_d, 1, 0),
        ]:
            if pressed[key]:
                self.pos[0] += xdir * self.move_speed
                self.pos[1] += ydir * self.move_speed
                self.on_new_pos(self.pos)

    def render(self, other_users: list):
        users = [self.pos] + other_users
        self.screen.fill(self.bg_color)
        width, height = self.screen.get_width(), self.screen.get_height()

        self.eased_positions = self.eased_positions[:len(users)] + [
            list(i) for i in users[len(self.eased_positions):]
        ]

        for color, pos, eased in zip_longest(self.colors, users, self.eased_positions):
            for i, (pos_val, eased_val) in enumerate(zip(pos, eased)):
                eased[i] += 0.1 * (pos_val - eased_val)
            world_x, world_y = eased
            px, py = int(width * world_x), int(height * world_y)
            sz = int(width * self.box_size)
            pygame.draw.rect(
                self.screen, color or self.default_color, (px - sz // 2, py - sz // 2, sz, sz)
            )
        pygame.display.flip()
        self.clock.tick(30)

    @staticmethod
    def create_screen(w, h) -> Surface:
        params = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
        return pygame.display.set_mode((w, h), params)
