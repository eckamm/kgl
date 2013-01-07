import pygame


class ModalMessage:
    bg_color = (20, 20, 20)
    text_color = (0, 200, 0)


    def __init__(self, g):
        self.g = g
        self.font = pygame.font.Font("freesansbold.ttf", 28)

    def draw(self, txt):
        if not isinstance(txt, (list, tuple)):
            lines = [txt]
        else:
            lines = txt

        # Save a copy of the surface.
        save = self.g.surface.copy()

        # Make the text surface.
        text_surface = renderLines(lines, self.font, True, self.text_color, self.bg_color)
        #text_surface = self.font.render(txt, True, self.text_color, self.bg_color)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.g.width//2, (self.g.height-self.g.hud_height)//2)

        # Draw a bounding box for the text.
        # finish
        # Blit things.
        self.g.surface.blit(text_surface, text_rect)
        pygame.display.flip()

        running = True
        tick = 20
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = False
            clock.tick(tick)

        # Restore surface.
        self.g.surface.blit(save, (0, 0))
        pygame.display.flip()


    def draw_and_wait(self, txt):
        lt.draw(msg)
        pygame.display.flip()



def renderLines(lines, font, antialias, color, background=None):
    fontHeight = font.get_height()

    surfaces = [font.render(ln, antialias, color) for ln in lines]
    # can't pass background to font.render, because it doesn't respect the alpha

    maxwidth = max([s.get_width() for s in surfaces])
    result = pygame.Surface((maxwidth, len(lines)*fontHeight), pygame.SRCALPHA)
    if background == None:
        result.fill((90,90,90,0))
    else:
        result.fill(background)

    for i in range(len(lines)):
      result.blit(surfaces[i], (0,i*fontHeight))
    return result
