import pygame


def main():
    pygame.init()
    width, height = 660, 760
    screen = pygame.display.set_mode((width, height))
    running = True
    tick = 60
    clock = pygame.time.Clock()

    s = pygame.surface.Surface((width, height))
    s3 = pygame.surface.Surface((width-20, height-20))
    s.fill((20, 20, 20))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
        #s2 = pygame.transform.scale(s, (width-20, height-20))
        #screen.blit(s2, (10, 10))
        pygame.transform.scale(s, (width-20, height-20), s3)
        screen.blit(s3, (10, 10))
        pygame.display.flip()
        clock.tick(tick)

if __name__=="__main__":
    import cProfile
    import pstats
    cProfile.run("main()", "profile.data")
    p = pstats.Stats("profile.data")
    p.strip_dirs().sort_stats('time').print_stats()

