import pygame
import abc
import numpy
import random
from src.rendering import AnimatedSprite


class Entities(pygame.sprite.Sprite):
    def __init__(self, tex, sounds, difficulty: int, entity: list, colliderGroups=(())):
        super().__init__()
        self._setTex = tex
        self._sounds = sounds
        self.x, self.y = entity[:2]
        self.difficulty = difficulty / 100  # %

        self.entityType = entity[2]
        self.colliderGroups = colliderGroups
        self.state = "alive"
        self.hud = entity[3]
        if self.entityType:  # Если тип сущности персонаж
            self.hud.interaction_with_inventory("select", self.hud.inventory[0])
            self.weapon = None
            self.scope = TILESIZE * ENTITIES[self.entityType][5]
            self.iq = ENTITIES[self.entityType][4]
            self.dmgTimer, self.dmgSpeed = 0, ENTITIES[self.entityType][3]
            self.speed = ENTITIES[self.entityType][2]
            self.dmgChance = difficulty
            self.uron = ENTITIES[self.entityType][1]
        self.hp = ENTITIES[self.entityType][0]
        self.speedx, self.speedy = 0, 0

        # print("init", entity)

        self._load_sprites()

    def _load_sprites(self):  # Загрузка спрайтов
        self.image = self._setTex
        self.rect = self.image.get_rect()

        self.entityCollider = pygame.sprite.Sprite()
        self.entityCollider.rect = self.image.get_rect()

        self.particleGenerator = ParticleGenerator()

    def damage(self, entity):  # нанесение урона
        if pygame.time.get_ticks() - self.dmgTimer > self.dmgSpeed:
            self.dmgTimer = pygame.time.get_ticks()
            if self.dmgChance > random.randint(0, 100):
                entity.hurt(self.uron)

    def hurt(self, damage):  # получение урона
        print(self.entityType, "damaged", damage)
        self.hp -= damage
        self.particleGenerator.create((self.x, self.y), damage, self.image)
        if self.hp <= 0:
            self.state = "dead"
            self.kill()
        return self.state

    def update(self, direction_x_y: list, speed: float):  # передвигаемся
        self.speedx = speed * direction_x_y[0]
        self.speedy = speed * direction_x_y[1]
        if self.check_collide(direction_x_y):
            self.x += self.speedx
            self.y += self.speedy
            self.rect.center = self.x, self.y
            return True
        return False

    def weapon_check(self):  # выдаёт активное оружие
        self.weapon.weapon_check(self.hud.activeItem)

    def check_collide(self, direction_x_y):  # возвращает ИСТИНА если не столкнулся
        speedx, speedy = direction_x_y
        self.entityCollider.rect.center = (self.x + speedx), (self.y + speedy)
        for colliderGroup in self.colliderGroups:
            collided = pygame.sprite.spritecollide(self.entityCollider, colliderGroup, False)
            if collided:
                if str(collided[0]) == "W":
                    pass
                elif self.entityType == "Player":
                    if collided[0] == "F":
                        self.state = "escaped"
                    break
                elif str(collided[0]) != self.entityType:
                    self.damage(collided[0])
                self.entityCollider.rect.center = (self.x - speedx), (self.y - speedy)
                return False
        self.entityCollider.rect.center = (self.x - speedx), (self.y - speedy)
        return True

    def __str__(self):
        return self.entityType


class Player(Entities):
    def __init__(self, tex, sounds, difficulty: int, entity: list, colliderGroups=(())):
        super().__init__(tex, sounds, difficulty, entity, colliderGroups)
        self.hp -= self.hp * min(self.difficulty, 0.5)
        # self.speed -= self.difficulty
        self.uron -= self.difficulty
        self.dmgChance = 100 - self.difficulty * 10
        self.scope -= TILESIZE * self.difficulty
        self.sight = ''
        self.x, self.y = 768 // 2, 640 // 2
        self.rect.center = self.x, self.y

    def see(self, tXY, tType):
        if self.state == "alive":
            tX, tY = tXY
            dE = ((tX - self.x) ** 2 + (tY - self.y) ** 2) ** 0.5
            if dE < self.scope:
                self.sight = tType
            else:
                self.sight = ''
        # изменить на линии с обработкой столкновений
        # проблема, в том, что после удачного срабатывания идёт неудачное, и sight = ''


class Vrag(Entities):
    def __init__(self, tex, sounds, difficulty: int, entity: list, colliderGroups=(())):
        super(Vrag, self).__init__(tex, sounds, difficulty, entity, colliderGroups)
        self.uron += self.uron * self.difficulty
        self.speed += self.speed * self.difficulty
        self.scope += TILESIZE * self.difficulty
        self.hp += self.hp * self.difficulty
        self.agr = False

    def see(self, tXY, tType="Player"):
        if self.state == "alive":
            tX, tY = tXY
            dE = ((tX - self.x) ** 2 + (tY - self.y) ** 2) ** 0.5
            if dE < self.scope:
                self.agr = True
            else:
                self.agr = False
            if self.agr:
                directionX = numpy.sign(tX - self.x) * 1
                directionY = numpy.sign(tY - self.y) * 1
                self.update([directionX, directionY], random.uniform(0, self.speed) / 2)


class Fly(Entities):
    pass


class Weapon(pygame.sprite.Sprite):  # оружие
    def __init__(self, tex, sounds, difficulty: int, weapon: list, colliderGroups=(())):
        super().__init__()
        self._setTex = tex
        self._sounds = sounds
        self.x, self.y = 0, 0
        self.cX, self.cY = weapon[:-2]
        self.colliderGroups = colliderGroups

        self.ammo = weapon[3]  # список патронов калибра int
        self.dmgTimer = 0
        self.statistic = 0

        self.weapon_check(weapon[2])

    def _load_sprites(self):
        self.entityCollider = AnimatedSprite(self._setTex[WEAPONS[self.weaponType][-1]], 2, 2, 24, 24, 100)
        self.image = self.entityCollider.image
        self.rect = self.entityCollider.rect

    def weapon_check(self, activeWeapon):  # наделяет оружие свойствами активного
        self.weaponType = activeWeapon
        # урон выполняет роль калибра в огнестреле
        if activeWeapon in WEAPONS:
            self._load_sprites()
            self.melee = WEAPONS[self.weaponType][3]
            self.handShift = WEAPONS[self.weaponType][2]
            self.dmgSpeedCo = WEAPONS[self.weaponType][1]
            self.uron = WEAPONS[self.weaponType][0]  # if uron == bullet.caliber: ammo.append(booleit)
        else:
            self.melee = True
            self.handShift = 12
            self.dmgSpeedCo = 0
            self.uron = 0

    def check_collide(self, ownerDmg, ownerDmgChance, ownerType):  # проверяет столкновение с сущностями
        for colliderGroup in self.colliderGroups:
            collided = pygame.sprite.spritecollide(self.entityCollider, colliderGroup, False)
            if collided and ownerDmgChance > random.randint(0, 100):
                for entity in collided:
                    if str(entity) != ownerType:
                        if entity.hurt(self.uron + ownerDmg) == "ded":
                            self.statistic += 1

    def update(self):
        ownerCXY = 389, 320
        self.cX, self.cY = ownerCXY

    def damage(self, tXY, owner):  # нанесение урона
        tX, tY = tXY
        ownerDmgSpeed, ownerDmgChance, ownerDmg, ownerType = owner
        directionVector = tX - self.cX, tY - self.cY
        normedVector = directionVector / numpy.linalg.norm(directionVector)
        self.x = self.cX + self.handShift * (normedVector[0])
        self.y = self.cY + self.handShift * (normedVector[1])
        self.rect.center = self.x, self.y
        if pygame.time.get_ticks() - self.dmgTimer > self.dmgSpeedCo + ownerDmgSpeed:
            self.dmgTimer = pygame.time.get_ticks()
            self.entityCollider.runAnim = True
            self.check_collide(ownerDmg, ownerDmgChance, ownerType)

    def __str__(self):
        return "Weapon"


class Booleits(Fly, Weapon):
    def __init__(self):
        super().__init__(self._setTex, self._sounds, self.difficulty, [self.x, self.y, self.entityType])
        pass


class Particle:
    def __init__(self, emiter_pos, dx, dy, color):
        self.surface = pygame.Surface((random.randint(3, 6), random.randint(3, 6)))
        self.surface.fill(color)
        self.pos = emiter_pos
        self.velocity = [dx / 10, dy / 10]
        self.x, self.y = self.pos
        self.kill = False

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        if ((self.x - self.pos[0]) ** 2 + (self.y - self.pos[1]) ** 2) ** 0.5 > TILESIZE * 2:
            self.kill = True


class EntityCreator(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, textures, sounds, difficulty: int, colliderGroups: dict):
        self._textures = textures
        self._sounds = sounds
        self.difficulty = difficulty
        self.colliderGroups = colliderGroups

    def create_entity(self, entity: list):
        entityGroup, e = None, None
        if entity[2] in ENTITIES:
            colliderGroups = [v for k, v in self.colliderGroups.items() if
                              k != ENTITIES[entity[2]][-2] and k != "damagerS"]
            entityGroup = self.colliderGroups[ENTITIES[entity[2]][-2]]
            if entity[2] == "Player":
                e = Player(self._textures[ENTITIES[entity[2]][-1]], self._sounds, self.difficulty,
                           entity, colliderGroups)
            else:
                e = Vrag(self._textures[ENTITIES[entity[2]][-1]], self._sounds, self.difficulty, entity, colliderGroups)
        elif entity[2] in WEAPONS:
            colliderGroups = [v for k, v in self.colliderGroups.items() if k != WEAPONS[entity[2]][-2] and k != "wallS"]
            entityGroup = self.colliderGroups[WEAPONS[entity[2]][-2]]
            e = Weapon({k: v for k, v in self._textures.items() if "damage_" in k}, self._sounds, self.difficulty,
                       entity, colliderGroups)
        entityGroup.add(e)
        return e

    @staticmethod
    def entity_coord_improver(screenSize, initialShift: list, entities: list):
        unpackedEntities = []
        for enti in range(len(entities)):
            entitiesGroup = []
            for i in range(entities[enti][-1]):
                entity = [*entities[enti][:-1]]
                entity[0] += (-initialShift[0]) + (screenSize[0] // 2)
                entity[1] += (-initialShift[1]) + (screenSize[1] // 2)
                entitiesGroup.append(entity)
            entitiesGroup = EntityCreator.build_ranks(entitiesGroup)
            unpackedEntities += entitiesGroup
        return unpackedEntities

    @staticmethod
    def build_ranks(entities: list):  # [[x, y, ent]]
        count, entCount = 0, len(entities)
        rankSize, currentRankSize = int(entCount ** 0.6), 0
        shift = rankSize // 2 * TILESIZE
        x, y = 0 - shift, 0 - shift
        currentRank = 0
        while count < entCount:
            if currentRankSize >= rankSize:
                currentRankSize = 0
                currentRank += 1
                x, y = 0 - shift, 0 - shift + TILESIZE * currentRank
            entities[count][0] += x + random.randint(-TILESIZE // 4, TILESIZE // 4)
            entities[count][1] += y + random.randint(-TILESIZE // 4, TILESIZE // 4)
            x += TILESIZE
            currentRankSize += 1
            count += 1
        return entities


class ParticleGenerator(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self.particles = []

    def create(self, emiterXY, force, entityImage):  # force == damage
        particle_count = min(random.randint(0, 1 * int(force)), 11)
        color = entityImage.get_at((0, 0))
        dSpeeds = [ds for ds in range(-5, 6) if ds]
        for _ in range(particle_count):
            self.particles.append(Particle(emiterXY, random.choice(dSpeeds), random.choice(dSpeeds), color))

    def draw(self, surface):
        if self.particles:
            for particle in self.particles:
                particle.update()
                surface.blit(particle.surface, (particle.x, particle.y))
                if particle.kill:
                    self.particles.remove(particle)
