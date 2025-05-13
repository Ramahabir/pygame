# Ini adalah game lanjutan: Battle Arena Advanced
# Tambahan fitur:
# - XP dan sistem level
# - Upgrade skill
# - Boss battle
# - Sistem senjata berbeda
# Catatan: Gambar tidak digunakan, hanya bentuk dan warna

import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battle Arena: XP & Boss")
clock = pygame.time.Clock()
FPS = 60

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 250)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (160, 32, 240)

# Entity dan status
player = pygame.Rect(WIDTH//2, HEIGHT//2, 80, 80)
player_health = 100
max_health = 100
player_level = 1
player_xp = 0
xp_to_level = 100
player_img = pygame.image.load("player.png")  # Gambar pemain (tidak digunakan dalam kode ini)
player_img = pygame.transform.scale(player_img, (80, 80))

enemy_img = pygame.image.load("enemy.png")  # Gambar pemain (tidak digunakan dalam kode ini)
enemy_img = pygame.transform.scale(enemy_img, (80, 80))

boss_img = pygame.image.load("boss.png")  # Gambar pemain (tidak digunakan dalam kode ini)
boss_img = pygame.transform.scale(boss_img, (120, 120))

# player_img = pygame.image.load("player.png")  # Gambar pemain (tidak digunakan dalam kode ini)
# player_img = pygame.transform.scale(player_img, (40, 40))

skills = {
    "fire_rate": 1,
    "projectile_damage": 10,
    "speed": 5
}

weapons = {
    "basic": {"speed": 7, "cooldown": 20, "damage": 10},
    "rapid": {"speed": 10, "cooldown": 5, "damage": 5},
    "sniper": {"speed": 15, "cooldown": 40, "damage": 25}
}
current_weapon = "basic"
weapon_cooldown = 0

projectiles = []
enemies = []
powerups = []
boss = None
spawn_timer = 0
boss_spawned = False

font = pygame.font.SysFont(None, 30)

def draw_health_bar(x, y, health, max_health):
    pygame.draw.rect(screen, RED, (x, y, 100, 10))
    pygame.draw.rect(screen, GREEN, (x, y, max(0, 100 * (health / max_health)), 10))

def draw_text(text, x, y, color=WHITE):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))

def spawn_enemy():
    x = random.choice([0, WIDTH])
    y = random.randint(0, HEIGHT)
    return {"rect": pygame.Rect(x, y, 80, 80), "health": 30, "damage": 10, "xp": 25}

def spawn_powerup():
    kind = random.choice(["heal", "xp", "weapon"])
    rect = pygame.Rect(random.randint(0, WIDTH-30), random.randint(0, HEIGHT-30), 20, 20)
    powerups.append((kind, rect))

def level_up():
    global player_level, xp_to_level
    player_level += 1
    xp_to_level += 50
    skills["projectile_damage"] += 5
    skills["fire_rate"] += 0.2
    skills["speed"] += 0.5

running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)

    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_w]: dy = -skills["speed"]
    if keys[pygame.K_s]: dy = skills["speed"]
    if keys[pygame.K_a]: dx = -skills["speed"]
    if keys[pygame.K_d]: dx = skills["speed"]

    player.move_ip(dx, dy)
    player.clamp_ip(screen.get_rect())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                current_weapon = "basic"
            elif event.key == pygame.K_2:
                current_weapon = "rapid"
            elif event.key == pygame.K_3:
                current_weapon = "sniper"

    if keys[pygame.K_SPACE] and weapon_cooldown == 0:
        mx, my = pygame.mouse.get_pos()
        angle = math.atan2(my - player.centery, mx - player.centerx)
        dx = math.cos(angle) * weapons[current_weapon]["speed"]
        dy = math.sin(angle) * weapons[current_weapon]["speed"]
        projectiles.append({
            "rect": pygame.Rect(player.centerx, player.centery, 10, 10),
            "dx": dx,
            "dy": dy,
            "damage": weapons[current_weapon]["damage"]
        })
        weapon_cooldown = weapons[current_weapon]["cooldown"]

    if weapon_cooldown > 0:
        weapon_cooldown -= 1

    for proj in projectiles[:]:
        proj["rect"].x += proj["dx"]
        proj["rect"].y += proj["dy"]
        if not screen.get_rect().contains(proj["rect"]):
            projectiles.remove(proj)

    for enemy in enemies[:]:
        angle = math.atan2(player.centery - enemy["rect"].centery, player.centerx - enemy["rect"].centerx)
        enemy["rect"].x += math.cos(angle) * 2
        enemy["rect"].y += math.sin(angle) * 2

        if player.colliderect(enemy["rect"]):
            player_health -= enemy["damage"]
            enemies.remove(enemy)

        for proj in projectiles[:]:
            if proj["rect"].colliderect(enemy["rect"]):
                enemy["health"] -= proj["damage"]
                if enemy["health"] <= 0:
                    player_xp += enemy["xp"]
                    enemies.remove(enemy)
                projectiles.remove(proj)
                break

    if not boss_spawned and player_level >= 5:
        boss = {"rect": pygame.Rect(100, 100, 80, 80), "health": 500, "damage": 20}
        boss_spawned = True

    if boss:
        angle = math.atan2(player.centery - boss["rect"].centery, player.centerx - boss["rect"].centerx)
        boss["rect"].x += math.cos(angle) * 1
        boss["rect"].y += math.sin(angle) * 1
        if boss["rect"].colliderect(player):
            player_health -= boss["damage"] // 10

        for proj in projectiles[:]:
            if proj["rect"].colliderect(boss["rect"]):
                boss["health"] -= proj["damage"]
                projectiles.remove(proj)
                if boss["health"] <= 0:
                    boss = None
                    draw_text("YOU DEFEATED THE BOSS!", WIDTH//2 - 150, HEIGHT//2, CYAN)

        screen.blit(boss_img, boss["rect"].topleft)
        draw_health_bar(boss["rect"].x, boss["rect"].y - 10, boss["health"], 500)

    spawn_timer += 1
    if spawn_timer >= 60:
        enemies.append(spawn_enemy())
        if random.random() < 0.3:
            spawn_powerup()
        spawn_timer = 0

    for kind, rect in powerups[:]:
        if player.colliderect(rect):
            if kind == "heal":
                player_health = min(max_health, player_health + 20)
            elif kind == "xp":
                player_xp += 50
            elif kind == "weapon":
                current_weapon = random.choice(list(weapons.keys()))
            powerups.remove((kind, rect))
        color = YELLOW if kind == "heal" else (CYAN if kind == "xp" else WHITE)
        pygame.draw.rect(screen, color, rect)

    while player_xp >= xp_to_level:
        player_xp -= xp_to_level
        level_up()

    # Draw section
    screen.blit(player_img, player.topleft)
    draw_health_bar(player.x, player.y - 15, player_health, max_health)

    for enemy in enemies:
        screen.blit(enemy_img, enemy["rect"].topleft)
        draw_health_bar(enemy["rect"].x, enemy["rect"].y - 10, enemy["health"], 30)

    for proj in projectiles:
        pygame.draw.rect(screen, ORANGE, proj["rect"])

    draw_text(f"HP: {player_health}", 10, 10)
    draw_text(f"XP: {player_xp}/{xp_to_level}", 10, 30)  
    draw_text(f"Level: {player_level}", 10, 50)
    draw_text(f"Weapon: {current_weapon}", 10, 70)

    if player_health <= 0:
        draw_text("YOU DIED", WIDTH//2 - 60, HEIGHT//2, RED)
        pygame.display.flip()
        pygame.time.wait(3000)
        break

    pygame.display.flip()

pygame.quit()
sys.exit()