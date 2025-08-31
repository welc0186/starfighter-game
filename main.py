import asyncio
import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Starfighter")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Player settings
player_width = 50
player_height = 50
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 10
player_speed = 5

# Enemy settings
enemy_width = 50
enemy_height = 50
enemy_speed = 2
enemies = []

# Bullet settings
bullet_width = 5
bullet_height = 10
bullets = []
bullet_speed = 7

# Game loop control
clock = pygame.time.Clock()


def spawn_enemy():
    while True:
        x = random.randint(0, WIDTH - enemy_width)
        new_enemy = pygame.Rect(x, 0, enemy_width, enemy_height)
        if not any(new_enemy.colliderect(enemy) for enemy in enemies):
            enemies.append(new_enemy)
            break


def draw_player():
    pygame.draw.rect(screen, WHITE, (player_x, player_y, player_width, player_height))


def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(screen, RED, enemy)


def draw_bullets():
    for bullet in bullets:
        pygame.draw.rect(screen, WHITE, bullet)


async def main():
    global player_x, player_y
    score = 0
    running = True
    player_speed = 5
    last_space_time = 0
    last_bullet_time = 0
    refractory_period = 300  # milliseconds

    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = pygame.time.get_ticks()

        keys = pygame.key.get_pressed()
        if (
            keys[pygame.K_SPACE]
            and (current_time - last_space_time) > refractory_period
        ):
            player_speed = -player_speed  # Toggle direction
            last_space_time = current_time
        if player_x < 0:
            player_x = 0
            player_speed = abs(player_speed)
        elif player_x > WIDTH - player_width:
            player_x = WIDTH - player_width
            player_speed = -abs(player_speed)

        player_x += player_speed

        # Fire a bullet every second
        if current_time - last_bullet_time > 1000:  # 1000 milliseconds = 1 second
            bullet = pygame.Rect(
                player_x + player_width // 2 - bullet_width // 2,
                player_y,
                bullet_width,
                bullet_height,
            )
            bullets.append(bullet)
            last_bullet_time = current_time

        # Update enemies
        if random.randint(1, 50) == 1:  # Spawn an enemy randomly
            spawn_enemy()
        for enemy in enemies:
            enemy.y += enemy_speed
            if enemy.y > HEIGHT:
                enemies.remove(enemy)

        # Update bullets
        for bullet in bullets:
            bullet.y -= bullet_speed
            if bullet.y < 0:
                bullets.remove(bullet)

        # Collision detection

        for bullet in bullets:
            for enemy in enemies:
                if bullet.colliderect(enemy):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 1  # Increment score
                    break

        # Display score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))  # Draw score at the top-left corner

        # Check for collisions between enemies and player
        for enemy in enemies:
            if enemy.colliderect(
                pygame.Rect(player_x, player_y, player_width, player_height)
            ):
                # Flash game over screen
                for _ in range(3):  # Flash 3 times
                    screen.fill(RED)
                    pygame.display.flip()
                    await asyncio.sleep(0.5)
                    screen.fill(BLACK)
                    pygame.display.flip()
                    await asyncio.sleep(0.5)
                # Restart the game
                enemies.clear()
                bullets.clear()
                score = 0
                player_x = WIDTH // 2 - player_width // 2
                player_y = HEIGHT - player_height - 10

        draw_player()
        draw_enemies()
        draw_bullets()

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


asyncio.run(main())
