import pygame


class ModalMessage:
    bg_color = (60, 20, 60)
    text_color = (30, 200, 30)
    border = True
    padding = 10
    border_color = (150, 150, 150)
    border_size = 10

    def __init__(self, g):
        self.g = g
        self.font = pygame.font.Font("freesansbold.ttf", 28)

    def draw(self, txt):
        # Work with strings or lists of strings.
        if not isinstance(txt, (list, tuple)):
            lines = [txt]
        else:
            lines = txt

        # Save a copy of the surface.
        save = self.g.surface.copy()

        # Make the text surface.
        text_surface = renderLines(lines, self.font, True, self.text_color, self.bg_color)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.g.width//2, (self.g.height-self.g.hud_height)//2)

        # Make a background for the text.
        bg_rect = text_rect.inflate(self.padding, self.padding)
        bg_surface = pygame.Surface(bg_rect[2:])
        bg_surface.fill(self.bg_color)

        # Make a border.
        border_rect = bg_rect.inflate(self.border_size, self.border_size)
        border_surface = pygame.Surface(border_rect[2:])
        border_surface.fill(self.border_color)

        # Blit things.
        self.g.surface.blit(border_surface, border_rect)
        self.g.surface.blit(bg_surface, bg_rect)
        self.g.surface.blit(text_surface, text_rect)
        pygame.display.flip()

        self._wait_for_keypress()

        # Restore surface.
        self.g.surface.blit(save, (0, 0))
        pygame.display.flip()


    def _wait_for_keypress(self):
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


class GoodModalMessage(ModalMessage):
    bg_color = (30, 30, 200)   # dark blue
    text_color = (255, 140, 30)   # light blue
    border_color = (100, 150, 240)  # yellow


class BadModalMessage(ModalMessage):
    bg_color = (10, 10, 10) # black
    text_color = (200, 200, 30) # yellow
    border_color = (100, 100, 100) # grey




