import pygame


class HUD:
    bg_color = (40, 10, 10)
    text_color = (30, 30, 200)

    def __init__(self, g):
        self.g = g
        self.font = pygame.font.Font("freesansbold.ttf", 22)

    def draw(self, section_name, level_name):
        # Draw a background for the HUD.
        pygame.draw.rect(self.g.surface, self.bg_color,
            (0, self.g.height, self.g.width, self.g.hud_height), 0)
        
        t = "%s: %s" % (section_name, level_name)

        text_surface = self.font.render(t, True, self.text_color, self.bg_color)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.g.width//2, self.g.height+self.g.hud_height//2)
        self.g.surface.blit(text_surface, text_rect)



