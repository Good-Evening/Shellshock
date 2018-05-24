import random, pygame, time, sys, math

# Global Variables
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WIN_W = 1000
WIN_H = 500
timer = 0
groundArray = [None] * (WIN_W + 1)

tankGroup = pygame.sprite.Group()
bulletGroup = pygame.sprite.Group()
pointGroup = pygame.sprite.Group()


class Text:
    def __init__(self, s, t, x, y, color):
        self.color = color
        self.font = pygame.font.SysFont("fonts/SourceSansPro-Regular.ttf", s)
        self.image = self.font.render(t, 1, color)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x - self.rect.width / 2, y - self.rect.height / 2)

    def update(self, t, x, y):
        self.image = self.font.render(t, 1, self.color)
        self.rect.center = x, y


class Point(pygame.sprite.Sprite):
    def __init__(self, x, y):
        global bulletGroup

        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((1, 1)).convert()
        self.rect = self.image.get_rect()
        self.image.fill((0, 0, 0))
        self.rect.center = x, y

    def update(self, x, y):
        self.rect.center = x, y


class groundPoint(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((1, 1)).convert()
        self.rect = self.image.get_rect()
        self.image.fill((0, 0, 0))
        self.rect.center = x, y
        self.count = 0

    def update(self):
        if self.rect.y > WIN_H - 10:
            self.rect.y = WIN_H - 10


def coorLoc(x, y, r, cx, cy):
    rotatedX = x + (cx * math.cos(math.radians(r))) - (cy * math.sin(math.radians(r)))
    rotatedY = y + (cx * math.sin(math.radians(r))) + (cy * math.cos(math.radians(r)))
    x = rotatedX
    y = rotatedY
    return x, y


class Bullet(pygame.sprite.Sprite):
    def __init__(self, start, radius, damage, explosionRadius, terrainDamage, velocity):
        global pointGroup, groundArray

        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((radius * 2, radius * 2)).convert()
        self.oriImage = self.image
        self.rect = self.image.get_rect()
        self.rect.center = start.point.rect.center
        self.damage = 1
        self.velocity = velocity
        self.angle = start.theta - 11
        self.image.fill((0, 0, 0))
        self.t = 0
        self.damage = damage
        self.explosionRadius = explosionRadius
        self.terrainDamage = terrainDamage
        self.radius = radius

    def update(self):
        self.t += 1

        self.rect.x += math.cos(math.radians(self.angle)) * 10
        self.rect.y -= math.sin(math.radians(self.angle)) * 10

        self.rect.y += (self.t**2) / (self.velocity * 60)

        if self.rect.bottom > WIN_H or self.rect.left < 0 or self.rect.right > WIN_W:
            self.kill()

        # bullet detection and creating divots
        if self.rect.bottom >= groundArray[self.rect.x].rect.y:

            if groundArray[self.rect.x].rect.x - self.explosionRadius < 0:
                start = 0
            else:
                start = groundArray[self.rect.x].rect.x - self.explosionRadius

            if groundArray[self.rect.x].rect.x + self.explosionRadius > WIN_W:
                end = WIN_W + 1
            else:
                end = groundArray[self.rect.x].rect.x + self.explosionRadius + 1

            for gp in range(start, end):
                if gp == self.rect.x:
                    groundArray[gp].rect.y -= 1

                diff = math.sqrt(self.explosionRadius ** 2 - (groundArray[gp].rect.x - groundArray[self.rect.x].rect.x) ** 2)
                groundArray[gp].rect.y += diff

            self.kill()


class Tank(pygame.sprite.Sprite):
    global bulletGroup, pointGroup, groundArray

    def __init__(self, x, y, armor, weaponGroup, fuel):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((45, 25)).convert()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.image.fill((0, 0, 0))

        self.gunImage = pygame.Surface((83.3333, 16.6666))
        self.gunOriImage = self.gunImage
        self.gunRect = self.gunImage.get_rect()
        self.gunRect.center = self.rect.center
        self.theta = 11

        self.pointX = self.gunRect.x + self.gunRect.width
        self.pointY = self.gunRect.top + (self.gunRect.height/2)
        self.velocity = 1

        self.point = Point(self.pointX, self.pointY)
        #pointGroup.add(self.point)

        self.health = 100
        self.armor = armor
        self.speed = 3
        self.weapons = weaponGroup
        self.fuel = fuel

        self.shootingSpecs = Text(15, str(self.theta - 11) + ", " + str(self.velocity), self.rect.center[0], self.rect.y + 15, BLACK)

    def update(self):
        # print self.theta
        self.turn()

        self.rect.bottom = groundArray[self.rect.center[0]].rect.y
        self.pointX, self.pointY = coorLoc(self.rect.center[0], self.rect.center[1], -self.theta,
                                           self.gunRect.width / 2, self.gunRect.height / 2)
        self.gunRect = self.gunImage.get_rect()
        self.gunRect.center = self.rect.center
        self.shootingSpecs.update(str(self.theta - 11) + ", " + str(self.velocity), self.rect.center[0], self.rect.y - 20)

    def turn(self):
        #print self.theta -11
        key = pygame.key.get_pressed()
        if self.fuel > 0:
            if key[pygame.K_a]:
                self.rect.x -= self.speed
                self.pointX -= self.speed
                self.fuel -= 1
            if key[pygame.K_d]:
                self.rect.x += self.speed
                self.pointX += self.speed
                self.fuel -= 1
        if key[pygame.K_LEFT] and self.theta < 191:
            self.theta += 1
        if key[pygame.K_RIGHT] and self.theta > 11:
            self.theta -= 1
        if key[pygame.K_UP]:
            self.velocity += 0.02
        if key[pygame.K_DOWN] and self.velocity > 0.02:
            self.velocity -= 0.02
        if key[pygame.K_SPACE] and timer % 10 == 0:
            b1 = Bullet(self, 5, 1, 10, True, self.velocity)
            bulletGroup.add(b1)


def main():
    pygame.init()

    global tankGroup, bulletGroup, pointGroup, timer, groundArray
    # variables
    screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.SRCALPHA)

    tank = Tank(375, 375, 0, 0, 100000)
    tankGroup.add(tank)

    play = True
    clock = pygame.time.Clock()
    fps = 60

    for x in range(WIN_W + 1):
        p = groundPoint(x, 400)
        groundArray[x] = p

    while play:
        # Checks if window exit button pressed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Update
        tank.update()
        bulletGroup.update()
        tank.point.update(tank.pointX, tank.pointY)
        for i in range(0, WIN_W + 1):
            groundArray[i].update()

        # Blit
        screen.fill(WHITE)
        for t in tankGroup:
            screen.blit(t.image, t.rect)
            pygame.draw.line(screen, (0, 0, 0), tank.rect.center, tank.point.rect.center, 7)
            screen.blit(t.shootingSpecs.image, t.shootingSpecs.rect)

        for b in bulletGroup:
            screen.blit(b.image, b.rect)

        for p in pointGroup:
            screen.blit(p.image, p.rect)

        for i in range(0, WIN_W + 1):
            screen.blit(groundArray[i].image, groundArray[i].rect)
            if 1 <= groundArray[i].rect.x < WIN_W + 1:
                j = i - 1
                pygame.draw.line(screen, (0, 0, 0), groundArray[i].rect.center, groundArray[j].rect.center, 1)

        # bullet's x is constantly compared to the groundPoint[x] then compare their y's to see if they have indeed come intact
        # this limits iterating through the entire array to check for collision!

        # Limits FPS
        clock.tick(fps)
        # Writes to surface
        pygame.display.flip()
        timer += 1


main()