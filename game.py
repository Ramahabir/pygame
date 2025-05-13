import pygame

pygame.init()
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()

sprite_sheet = pygame.image.load("player_idle.png").convert_alpha()
frame_width = 96
frame_height = 96
frames = []

# Potong tiap frame dari spritesheet
for i in range(10):
    frame = sprite_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
    frames.append(frame)

current_frame = 0
animation_timer = 0
animation_delay = 100  # ms per frame

running = True
while running:
    dt = clock.tick(60)
    animation_timer += dt

    if animation_timer >= animation_delay:
        current_frame = (current_frame + 1) % len(frames)
        animation_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))
    screen.blit(frames[current_frame], (200, 200))
    pygame.display.flip()

pygame.quit()
