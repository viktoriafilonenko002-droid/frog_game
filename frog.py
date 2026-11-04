import math
import os
import random
import pygame

W, H, GROUND = 800, 300, 240
FILE = "record.txt"


def make_frog(jumping):
    s = pygame.Surface((50, 46), pygame.SRCALPHA)
    body = (70, 180, 60)
    dark = (40, 130, 40)
    belly = (200, 235, 160)

    if jumping:
        
        pygame.draw.line(s, dark, (14, 30), (1, 40), 7)
        pygame.draw.ellipse(s, dark, (0, 38, 12, 6))
        pygame.draw.line(s, dark, (40, 34), (48, 42), 5)
        pygame.draw.ellipse(s, dark, (42, 40, 8, 5))
    else:
        pygame.draw.ellipse(s, dark, (4, 26, 24, 18))
        pygame.draw.ellipse(s, dark, (2, 39, 18, 7))

        pygame.draw.ellipse(s, dark, (34, 34, 9, 11))
        pygame.draw.ellipse(s, dark, (36, 40, 12, 6))


    pygame.draw.ellipse(s, body, (6, 12, 36, 30))
    pygame.draw.ellipse(s, belly, (16, 26, 24, 14))
    pygame.draw.ellipse(s, body, (22, 6, 26, 22))


    for ex in (29, 39):
        pygame.draw.circle(s, body, (ex, 8), 7)
        pygame.draw.circle(s, (255, 255, 255), (ex, 8), 5)
        pygame.draw.circle(s, (0, 0, 0), (ex + 1, 8), 2)


    pygame.draw.line(s, dark, (48, 21), (36, 23), 2)
    pygame.draw.circle(s, (240, 130, 130), (38, 20), 2)
    return s


def make_mushroom(w, h):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cap_h = int(h * 0.6)
    stem_w = int(w * 0.4)
    stem_x = (w - stem_w) // 2
    
    pygame.draw.rect(s, (245, 235, 205), (stem_x, cap_h - 6, stem_w, h - cap_h + 6),
                     border_radius=4)
    pygame.draw.rect(s, (200, 185, 150), (stem_x, cap_h - 6, stem_w, h - cap_h + 6),
                     2, border_radius=4)
    
    pygame.draw.ellipse(s, (210, 40, 40), (0, 0, w, cap_h))
    pygame.draw.ellipse(s, (150, 20, 20), (0, 0, w, cap_h), 2)
   
    for dx, dy, r in ((0.28, 0.35, 3), (0.55, 0.22, 4), (0.72, 0.5, 3), (0.45, 0.55, 2)):
        pygame.draw.circle(s, (255, 255, 255), (int(w * dx), int(cap_h * dy)), r)
    return s


def make_lily(w, h):
    """Кувшинка: лужа, лист и розовый цветок."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    
    pygame.draw.ellipse(s, (90, 160, 220), (0, h - 12, w, 12))
    pygame.draw.ellipse(s, (60, 120, 190), (0, h - 12, w, 12), 2)
    
    pygame.draw.ellipse(s, (40, 150, 70), (5, h - 20, w - 10, 14))
    pygame.draw.ellipse(s, (25, 105, 50), (5, h - 20, w - 10, 14), 2)
    pygame.draw.line(s, (25, 105, 50), (w // 2, h - 13), (w - 10, h - 13), 1)
    
    cx, cy = w // 2, h - 22
    for dx in (-10, 10):
        pygame.draw.ellipse(s, (240, 150, 190), (cx + dx - 5, cy - 16, 10, 22))
    pygame.draw.ellipse(s, (250, 180, 215), (cx - 6, cy - 22, 12, 28))
    pygame.draw.ellipse(s, (220, 110, 160), (cx - 6, cy - 22, 12, 28), 1)
    pygame.draw.circle(s, (250, 215, 60), (cx, cy + 2), 3)
    return s



class GameObject:
    def __init__(self, x, w, h, image):
        self.rect = pygame.Rect(x, GROUND - h, w, h)
        self.image = image

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Frog(GameObject):
    def __init__(self):
        self.img_stand = make_frog(False)
        self.img_jump = make_frog(True)
        super().__init__(50, 50, 46, self.img_stand)
        self.speed_y = 0

    @property
    def hitbox(self):
        return self.rect.inflate(-14, -10)

    def jump(self):
        if self.rect.bottom >= GROUND:
            self.speed_y = -15

    def update(self):
        self.speed_y += 0.8
        self.rect.y += int(self.speed_y)
        if self.rect.bottom > GROUND:
            self.rect.bottom = GROUND
            self.speed_y = 0
        self.image = self.img_stand if self.rect.bottom >= GROUND else self.img_jump


class Obstacle(GameObject):
  

    def __init__(self, speed):
        self.kind = random.choice(("mushroom", "lily"))
        if self.kind == "mushroom":
            w = random.randint(28, 38)
            h = random.randint(34, 56)
            image = make_mushroom(w, h)
        else:
            w, h = 56, 44
            image = make_lily(w, h)
        super().__init__(W, w, h, image)
        self.speed = speed

    @property
    def hitbox(self):
        if self.kind == "mushroom":
            return self.rect.inflate(-8, -4)
        return self.rect.inflate(-24, -10)

    def update(self):
        self.rect.x -= self.speed

class Background:
    def __init__(self):
        self.sky = self._make_sky()
        self.sun_angle = 0.0
        self.scroll = 0.0
        self.clouds = [[random.randint(0, W), random.randint(20, 110),
                        random.uniform(0.2, 0.5)] for _ in range(4)]

    @staticmethod
    def _make_sky():
        s = pygame.Surface((W, H))
        
        for y in range(GROUND):
            t = y / GROUND
            color = (int(90 + 120 * t), int(170 + 70 * t), int(235 + 15 * t))
            pygame.draw.line(s, color, (0, y), (W, y))
        
        for cx, r in ((120, 70), (380, 90), (650, 75), (820, 60)):
            pygame.draw.ellipse(s, (130, 200, 120), (cx - r * 2, GROUND - r // 2, r * 4, r))
        
        pygame.draw.rect(s, (90, 185, 70), (0, GROUND, W, H - GROUND))
        pygame.draw.rect(s, (60, 150, 50), (0, GROUND, W, 6))
        return s

    def update(self, speed):
        self.sun_angle += 0.01
        self.scroll = (self.scroll + speed) % 40
        for c in self.clouds:
            c[0] -= c[2]
            if c[0] < -90:
                c[0] = W + 20
                c[1] = random.randint(20, 110)

    @staticmethod
    def _draw_cloud(screen, x, y):
        for dx, dy, r in ((0, 0, 14), (16, -8, 18), (36, 0, 15), (18, 6, 14)):
            pygame.draw.circle(screen, (255, 255, 255), (int(x + dx), int(y + dy)), r)

    def draw(self, screen):
        screen.blit(self.sky, (0, 0))


        sx, sy = 700, 60
        for i in range(12):
            a = self.sun_angle + i * math.pi / 6
            p1 = (sx + math.cos(a) * 38, sy + math.sin(a) * 38)
            p2 = (sx + math.cos(a) * 54, sy + math.sin(a) * 54)
            pygame.draw.line(screen, (255, 220, 60), p1, p2, 4)
        pygame.draw.circle(screen, (255, 235, 90), (sx, sy), 32)
        pygame.draw.circle(screen, (255, 200, 40), (sx, sy), 32, 3)

        for x, y, _ in self.clouds:
            self._draw_cloud(screen, x, y)

        x = -self.scroll
        while x < W:
            for dx, hh in ((0, 8), (6, 12), (12, 7)):
                bx = x + dx
                pygame.draw.polygon(screen, (45, 130, 40),
                                    [(bx, GROUND + 4), (bx + 3, GROUND + 4 - hh),
                                     (bx + 6, GROUND + 4)])
            x += 40

class Score:
    def __init__(self):
        self.current = 0
        self.record = self.load()

    def load(self):
        if os.path.exists(FILE):
            with open(FILE) as f:
                return int(f.read())
        return 0

    def save(self):
        with open(FILE, "w") as f:
            f.write(str(self.record))

    def update(self):
        self.current += 0.1

    def finish(self):
        if int(self.current) > self.record:
            self.record = int(self.current)
            self.save()

    def draw(self, screen, font):
        text = f"Путь: {int(self.current)} м   Рекорд: {self.record} м"
        screen.blit(font.render(text, True, (0, 0, 0)), (20, 20))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Лягушка")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 22)
        self.score = Score()
        self.background = Background()
        self.reset()

    def reset(self):
        self.frog = Frog()
        self.obstacles = []
        self.score.current = 0
        self.timer = 0
        self.game_over = False

    def update(self):
        speed = 7 + int(self.score.current) // 100
        self.background.update(speed)
        self.frog.update()
        self.score.update()
        self.timer -= 1
        if self.timer <= 0:
            self.obstacles.append(Obstacle(speed))
            self.timer = random.randint(50, 100)
        for o in self.obstacles:
            o.update()
            if o.hitbox.colliderect(self.frog.hitbox):
                self.game_over = True
                self.score.finish()
                break
        self.obstacles = [o for o in self.obstacles if o.rect.right > 0]

    def draw(self):
        self.background.draw(self.screen)
        for o in self.obstacles:
            o.draw(self.screen)
        self.frog.draw(self.screen)
        self.score.draw(self.screen, self.font)
        if self.game_over:
            msg = self.font.render("Игра окончена! Пробел - заново", True, (200, 0, 0))
            box = msg.get_rect(center=(W // 2, H // 2 - 30)).inflate(24, 14)
            pygame.draw.rect(self.screen, (255, 255, 255), box, border_radius=8)
            self.screen.blit(msg, msg.get_rect(center=box.center))
        pygame.display.flip()

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset()
                    else:
                        self.frog.jump()
            if not self.game_over:
                self.update()
            self.draw()
            self.clock.tick(60)


if __name__ == "__main__":
    Game().run()
