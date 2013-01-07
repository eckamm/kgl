import pygame


class LevelTitle:
    def __init__(self, g):
        self.g = g
        self.font = pygame.font.Font("freesansbold.ttf", 28)

    def draw(self, txt):
        text_surface = self.font.render(txt, True, (0, 255, 0), (20,20,20))
        text_rect = text_surface.get_rect()
        text_rect.center = (self.g.width//2, self.g.height//2)
        self.g.surface.blit(text_surface, text_rect)



