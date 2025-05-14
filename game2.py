# Battle Arena Advanced + Background Luar Angkasa dengan Bintang Bergerak

import pygame
import sys
import random
import math

#init
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battle Arena: XP & Boss - Space Edition")
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
GRAY = (128, 128, 128)

# Bintang latar belakang
stars = [{"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), "radius": random.randint(1, 2)} for _ in range(100)]

# Entity dan status
player = pygame.Rect(WIDTH//2, HEIGHT//2, 80, 80)
player_health = 100
max_health = 100
player_level = 1
player_xp = 0
xp_to_level = 100

# Orb settings
orb_radius = 50  # Distance from player
orb_size = 15    # Size of each orb
orb_speed = 0.05 # Rotation speed
orb_angles = [0, 2.09, 4.18]  # Start angles for 3 orbs (0, 120, 240 degrees)
orb_active = False

#Upload Gambar Mob
player_img = pygame.image.load("player.png")
player_img = pygame.transform.scale(player_img, (80, 80))

enemy_img = pygame.image.load("enemy.png")
enemy_img = pygame.transform.scale(enemy_img, (80, 80))

boss_img = pygame.image.load("boss.png")
boss_img = pygame.transform.scale(boss_img, (80, 80))

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

current_weapon = "basic"  # Player starts with no weapon
weapon_cooldown = 0

projectiles = []
enemies = []
powerups = []
boss = None
spawn_timer = 0
boss_spawned = False

# Fonts
font = pygame.font.SysFont(None, 30)
font_large = pygame.font.SysFont(None, 40)

# Shop items
shop_items = {
    "Max Health": {"cost": 50, "currency": "xp", "description": "Increase max health by 20"},
    "Fire Rate": {"cost": 75, "currency": "xp", "description": "Increase fire rate"},
    "Damage": {"cost": 100, "currency": "xp", "description": "Increase projectile damage"},
    "Speed": {"cost": 60, "currency": "xp", "description": "Increase movement speed"},
    "Basic Gun": {"cost": 100, "currency": "gold", "description": "Standard balanced weapon", "type": "weapon", 
                 "stats": {"speed": 7, "cooldown": 20, "damage": 10}},
    "Rapid Gun": {"cost": 200, "currency": "gold", "description": "Fast firing rate, low damage", "type": "weapon",
                 "stats": {"speed": 10, "cooldown": 5, "damage": 5}},
    "Sniper Gun": {"cost": 300, "currency": "gold", "description": "High damage, slow firing rate", "type": "weapon",
                 "stats": {"speed": 15, "cooldown": 40, "damage": 25}}
}

player_gold = 0
shop_active = False
selected_item = 0

# Pause menu variables
pause_menu_active = False
pause_selected_option = 0

def draw_pause_menu():
    # Draw semi-transparent background
    pause_bg = pygame.Surface((WIDTH, HEIGHT))
    pause_bg.fill(BLACK)
    pause_bg.set_alpha(180)
    screen.blit(pause_bg, (0, 0))
    
    # Draw pause menu panel
    panel_rect = pygame.Rect(WIDTH//4, HEIGHT//4 - 50, WIDTH//2, HEIGHT//2)
    pygame.draw.rect(screen, BLACK, panel_rect)
    pygame.draw.rect(screen, WHITE, panel_rect, 2)
    
    # Draw pause menu title
    draw_text("PAUSED", WIDTH//2 - 50, HEIGHT//4 - 30, WHITE, True)
    
    # Menu options
    options = ["Resume", "Restart", "Quit"]
    for i, option in enumerate(options):
        y_pos = HEIGHT//4 + 50 + i * 60
        color = CYAN if i == pause_selected_option else WHITE
        if i == pause_selected_option:
            pygame.draw.rect(screen, GRAY, (WIDTH//4, y_pos - 5, WIDTH//2, 40))
        draw_text(option, WIDTH//2 - 40, y_pos, color)


def draw_health_bar(x, y, health, max_health):
    pygame.draw.rect(screen, RED, (x, y, 100, 10))
    pygame.draw.rect(screen, GREEN, (x, y, max(0, 100 * (health / max_health)), 10))

def draw_text(text, x, y, color=WHITE, large=False):
    font_to_use = font_large if large else font
    surface = font_to_use.render(text, True, color)
    screen.blit(surface, (x, y))

def draw_shop():
    # Draw semi-transparent background
    shop_bg = pygame.Surface((WIDTH, HEIGHT))
    shop_bg.fill(BLACK)
    shop_bg.set_alpha(128)
    screen.blit(shop_bg, (0, 0))
    
    # Draw shop panel
    panel_rect = pygame.Rect(WIDTH//4, HEIGHT//4 - 50, WIDTH//2, HEIGHT//2)
    pygame.draw.rect(screen, BLACK, panel_rect)
    pygame.draw.rect(screen, WHITE, panel_rect, 2)
    
    # Draw instructions
    draw_text("Press ESC to close shop", WIDTH//2 - 100, HEIGHT//4 + HEIGHT//2 - 30, GRAY)
    draw_text("Press ENTER to purchase", WIDTH//2 - 100, HEIGHT//4 + HEIGHT//2 - 60, GRAY)
    
    # Draw shop title
    draw_text("SHOP", WIDTH//2 - 50, HEIGHT//4 - 30, WHITE, True)
    draw_text(f"XP: {player_xp}", WIDTH//2 - 50, HEIGHT//4, YELLOW)
    draw_text(f"Gold: {player_gold}", WIDTH//2 - 50, HEIGHT//4 + 25, ORANGE)
    
    # Draw shop items
    for i, (item_name, item_info) in enumerate(shop_items.items()):
        y_pos = HEIGHT//4 + 50 + i * 60
        color = CYAN if i == selected_item else WHITE
        if i == selected_item:
            pygame.draw.rect(screen, GRAY, (WIDTH//4, y_pos - 5, WIDTH//2, 40))
        
        currency = "Gold" if item_info['currency'] == "gold" else "XP"
        draw_text(f"{item_name}: {item_info['cost']} {currency}", WIDTH//4 + 20, y_pos, color)
        draw_text(item_info['description'], WIDTH//4 + 20, y_pos + 20, GREEN)

def purchase_item():
    global player_xp, player_gold, max_health, shop_active, player_health, current_weapon, weapons
    item_name = list(shop_items.keys())[selected_item]
    item = shop_items[item_name]
    
    # Check if player has enough currency
    if item['currency'] == "gold":
        if player_gold < item['cost']:
            draw_text("Not enough gold!", WIDTH//2 - 60, HEIGHT//4 - 60, RED)
            pygame.display.flip()
            pygame.time.wait(500)
            return
        player_gold -= item['cost']
    else:  # XP currency
        if player_xp < item['cost']:
            draw_text("Not enough XP!", WIDTH//2 - 60, HEIGHT//4 - 60, RED)
            pygame.display.flip()
            pygame.time.wait(500)
            return
        player_xp -= item['cost']
    
    # Apply item effects
    if item.get("type") == "weapon":
        weapon_name = item_name.lower().replace(" ", "")
        current_weapon = weapon_name
        weapons[weapon_name] = item["stats"]
    elif item_name == "Max Health":
        old_health_percent = player_health / max_health
        max_health += 20
        player_health = int(old_health_percent * max_health)
    elif item_name == "Fire Rate":
        skills["fire_rate"] += 0.3
    elif item_name == "Damage":
        skills["projectile_damage"] += 5
    elif item_name == "Speed":
        skills["speed"] += 1
    
    # Visual feedback
    draw_text("Item purchased!", WIDTH//2 - 60, HEIGHT//4 - 60, GREEN)
    pygame.display.flip()
    pygame.time.wait(500)

def spawn_enemy():
    x = random.choice([0, WIDTH])
    y = random.randint(0, HEIGHT)
    return {"rect": pygame.Rect(x, y, 80, 80), "health": 30, "damage": 10, "xp": 25}

def spawn_powerup():
    kind = random.choice(["heal", "xp", "gold"])
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

    # Gambar background luar angkasa dengan bintang bergerak
    screen.fill((0, 0, 20))  # Biru gelap
    for star in stars:
        pygame.draw.circle(screen, WHITE, (star["x"], star["y"]), star["radius"])
        star["y"] += 1
        if star["y"] > HEIGHT:
            star["y"] = 0
            star["x"] = random.randint(0, WIDTH)

    # Input pemain (only if shop is not active and pause menu not active)
    if not shop_active and not pause_menu_active:
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
            if event.key == pygame.K_p and not pause_menu_active:  # Toggle shop only if pause menu not active
                shop_active = not shop_active
            
            # Pause menu toggle with ESC key (only if shop not active)
            if event.key == pygame.K_ESCAPE and not shop_active:
                pause_menu_active = not pause_menu_active
                pause_selected_option = 0  # Reset selection when toggling pause menu
            
            if pause_menu_active:
                if event.key == pygame.K_UP:
                    pause_selected_option = (pause_selected_option - 1) % 3
                elif event.key == pygame.K_DOWN:
                    pause_selected_option = (pause_selected_option + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if pause_selected_option == 0:  # Resume
                        pause_menu_active = False
                    elif pause_selected_option == 1:  # Restart
                        # Reset game state variables
                        player.x, player.y = WIDTH//2, HEIGHT//2
                        player_health = max_health
                        player_level = 1
                        player_xp = 0
                        xp_to_level = 100
                        skills["fire_rate"] = 1
                        skills["projectile_damage"] = 10
                        skills["speed"] = 5
                        current_weapon = "basic"
                        weapon_cooldown = 0
                        projectiles.clear()
                        enemies.clear()
                        powerups.clear()
                        boss = None
                        spawn_timer = 0
                        boss_spawned = False
                        pause_menu_active = False
                    elif pause_selected_option == 2:  # Quit
                        running = False
            
            # Shop controls
            if shop_active:
                if event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(shop_items)
                elif event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(shop_items)
                elif event.key == pygame.K_RETURN:  # Enter key to purchase
                    purchase_item()
                elif event.key == pygame.K_ESCAPE:  # ESC to close shop
                    shop_active = False
                    
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # Right click
                orb_active = not orb_active  # Toggle orbs

    # Only allow shooting if shop is not active and pause menu not active and player has a weapon
    if not shop_active and not pause_menu_active and current_weapon:
        if keys[pygame.K_SPACE] and weapon_cooldown == 0:
            mx, my = pygame.mouse.get_pos()
            angle = math.atan2(my - player.centery, mx - player.centerx)
            weapon = weapons[current_weapon]
            dx = math.cos(angle) * weapon["speed"]
            dy = math.sin(angle) * weapon["speed"]
            projectiles.append({
                "rect": pygame.Rect(player.centerx, player.centery, 10, 10),
                "dx": dx,
                "dy": dy,
                "damage": weapon["damage"]
            })
            weapon_cooldown = weapon["cooldown"]

    if weapon_cooldown > 0:
        weapon_cooldown -= 1

    # Only update projectiles and enemies if shop is not active and pause menu not active
    if not shop_active and not pause_menu_active:
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
                continue

            for proj in projectiles[:]:
                if proj["rect"].colliderect(enemy["rect"]):
                    enemy["health"] -= proj["damage"]
                    if enemy["health"] <= 0:
                        player_xp += enemy["xp"]
                        enemies.remove(enemy)
                    projectiles.remove(proj)
                    break

    # Only update boss if shop is not active and pause menu not active
    if not shop_active and not pause_menu_active:
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

    # Only spawn enemies if shop is not active and pause menu not active
    if not shop_active and not pause_menu_active:
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
            elif kind == "gold":
                player_gold += 25
            powerups.remove((kind, rect))
        color = YELLOW if kind == "heal" else (CYAN if kind == "xp" else ORANGE)  # Gold is orange
        pygame.draw.rect(screen, color, rect)

    while player_xp >= xp_to_level:
        player_xp -= xp_to_level
        level_up()

    # Update game state only if shop is not active and pause menu not active
    if not shop_active and not pause_menu_active:
        # Update and draw orbs
        if orb_active:
            # Update orb positions
            for i in range(len(orb_angles)):
                orb_angles[i] = (orb_angles[i] + orb_speed) % (2 * math.pi)
                orb_x = player.centerx + math.cos(orb_angles[i]) * orb_radius
                orb_y = player.centery + math.sin(orb_angles[i]) * orb_radius
                
                # Draw orb
                pygame.draw.circle(screen, CYAN, (int(orb_x), int(orb_y)), orb_size)
                
                # Check for enemy collisions
                orb_rect = pygame.Rect(orb_x - orb_size, orb_y - orb_size, orb_size * 2, orb_size * 2)
                for enemy in enemies[:]:
                    if orb_rect.colliderect(enemy["rect"]):
                        # Calculate push direction away from player
                        dx = enemy["rect"].centerx - player.centerx
                        dy = enemy["rect"].centery - player.centery
                        # Normalize and apply push force
                        length = math.sqrt(dx * dx + dy * dy)
                        if length > 0:
                            dx = dx / length * 20  # Push force
                            dy = dy / length * 20
                            enemy["rect"].x += dx
                            enemy["rect"].y += dy

        screen.blit(player_img, player.topleft)
        draw_health_bar(player.x, player.y - 15, player_health, max_health)

        for enemy in enemies:
            screen.blit(enemy_img, enemy["rect"].topleft)
            draw_health_bar(enemy["rect"].x, enemy["rect"].y - 10, enemy["health"], 30)

        for proj in projectiles:
            pygame.draw.rect(screen, ORANGE, proj["rect"])
    elif shop_active:
        # Draw shop UI when active
        draw_shop()
    elif pause_menu_active:
        # Draw pause menu UI when active
        draw_pause_menu()

    # UI
    draw_text(f"HP: {player_health}", 10, 10)
    draw_text(f"XP: {player_xp}/{xp_to_level}", 10, 30)
    draw_text(f"Level: {player_level}", 10, 50)
    draw_text(f"Weapon: {current_weapon if current_weapon else 'None'}", 10, 70)
    draw_text(f"Gold: {player_gold}", 10, 90)

    if player_health <= 0:
        draw_text("YOU DIED", WIDTH//2 - 60, HEIGHT//2, RED)
        pygame.display.flip()
        pygame.time.wait(3000)
        break
    
    pygame.display.flip()

pygame.quit()
sys.exit()
