"""
    Jacob N.  Asteroids.
    Copyright (C) 2021 Jacob N

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You can contact the author and get a copy of the original code from:
    https://github.com/xftransformers

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
	This program is based on and extends 
	the examples from [https://simplegametutorials.github.io/]
"""

import pgzrun
import math
import random

arena_width = 800
arena_height = 600

ship_radius = 20

bullet_cooldown = 0.5
bullet_radius = 5

missile_cooldown = 4
missile_radius = 8

asteroid_stages = [
    {
        'speed': 90,
        'radius': 15,
    },
    {
        'speed': 70,
        'radius': 20,
    },
    {
        'speed': 50,
        'radius': 40,
    },
    {
        'speed': 20,
        'radius': 80,
    },
]

def reset():
    global ship_x
    global ship_y
    global ship_speed_x
    global ship_speed_y
    global ship_angle
    global bullet_timer
    global missile_timer
    global bullets
    global missiles
    global asteroids

    ship_x = arena_width / 2
    ship_y = arena_height / 2
    ship_speed_x = 0
    ship_speed_y = 0
    ship_angle = 0

    bullets = []
    bullet_timer = bullet_cooldown

    missiles = []
    missile_timer = missile_cooldown

    asteroids = [
        {
            'x': 100,
            'y': 100,
        },
        {
            'x': arena_width - 100,
            'y': 100,
        },
        {
            'x': arena_width / 2,
            'y': arena_height - 100,
        }
    ]

    for asteroid in asteroids:
        asteroid['angle'] = random.random() * (2 * math.pi)
        asteroid['stage'] = len(asteroid_stages) - 1
        asteroid['colour'] = (255, 255, 0)
        asteroid['collision'] = ''

reset()

def update(dt):
    global ship_x
    global ship_y
    global ship_speed_x
    global ship_speed_y
    global ship_angle
    global bullet_timer
    global missile_timer

    turn_speed = 10

    if keyboard.right:
        ship_angle += turn_speed * dt

    if keyboard.left:
        ship_angle -= turn_speed * dt

    ship_angle %= 2 * math.pi

    if keyboard.up:
        ship_speed = 100
        ship_speed_x += math.cos(ship_angle) * ship_speed * dt
        ship_speed_y += math.sin(ship_angle) * ship_speed * dt

    ship_x += ship_speed_x * dt
    ship_y += ship_speed_y * dt

    ship_x %= arena_width
    ship_y %= arena_height

    def are_circles_intersecting(a_x, a_y, a_radius, b_x, b_y, b_radius):
        return (a_x - b_x)**2 + (a_y - b_y)**2 <= (a_radius + b_radius)**2

    for bullet in bullets.copy():
        bullet['time_left'] -= dt

        if bullet['time_left'] <= 0:
            bullets.remove(bullet)
            continue

        bullet_speed = 500
        bullet['x'] += math.cos(bullet['angle']) * bullet_speed * dt
        bullet['y'] += math.sin(bullet['angle']) * bullet_speed * dt
        bullet['x'] %= arena_width
        bullet['y'] %= arena_height

        for asteroid in asteroids.copy():
            if are_circles_intersecting(
                bullet['x'], bullet['y'], bullet_radius,
                asteroid['x'], asteroid['y'],
                asteroid_stages[asteroid['stage']]['radius']
            ):
                bullets.remove(bullet)

                if asteroid['stage'] > 0:
                    angle1 = random.random() * (2 * math.pi)
                    angle2 = (angle1 - math.pi) % (2 * math.pi)

                    asteroids.append({
                        'x': asteroid['x'] + math.cos(angle1) * asteroid_stages[asteroid['stage'] - 1]['radius'] + 1,
                        'y': asteroid['y'] + math.sin(angle1) * asteroid_stages[asteroid['stage'] - 1]['radius'] + 1,
                        'angle': angle1,
                        'collision': '',
                        'stage': asteroid['stage'] - 1,
                        'colour': (255, 255, 0)
                    })
                    asteroids.append({
                        'x': asteroid['x'] + math.cos(angle2) * asteroid_stages[asteroid['stage'] - 1]['radius'] + 1,
                        'y': asteroid['y'] + math.sin(angle2) * asteroid_stages[asteroid['stage'] - 1]['radius'] + 1,
                        'angle': angle2,
                        'collision': '',
                        'stage': asteroid['stage'] - 1,
                        'colour': (255, 255, 0)
                    })

                asteroids.remove(asteroid)
                break

    def find_closest_asteroid(x, y, radius):
        smallest_distance = 801
        for asteroid in asteroids:
            asteroid_distance = math.sqrt(((asteroid['x'] - x)**2 + (asteroid['y'] - y)**2))
            asteroid_distance -= asteroid_stages[asteroid['stage']]['radius'] - radius
            if asteroid_distance < smallest_distance:
                smallest_distance = asteroid_distance
                closest_asteroid = asteroid
        closest_asteroid['colour'] = (255, 100, 0)
        return closest_asteroid

    for missile in missiles.copy():

        missile_speed = 250
        missile_turn_speed = math.pi
        if not missile['target'] in asteroids and len(asteroids) > 0:
            missile['target'] = find_closest_asteroid(missile['x'], missile['y'], missile_radius)

        missile_target_angle = math.atan(
            (missile['target']['y'] - missile['y']) / (missile['target']['x'] - missile['x'])
        )
        if (missile['target']['x'] - missile['x']) < 0:
            missile_target_angle += math.pi
        missile_target_angle %= 2 * math.pi

        if missile_target_angle - missile['angle'] < 0:
            missile['angle'] += max((missile_target_angle - missile['angle']), (-1 * missile_turn_speed * dt))
        else:
            missile['angle'] += min(missile_target_angle - missile['angle'], (missile_turn_speed * dt))
        missile['angle'] %= 2 * math.pi

        missile['x'] += math.cos(missile['angle']) * missile_speed * dt
        missile['y'] += math.sin(missile['angle']) * missile_speed * dt
        missile['x'] %= arena_width
        missile['y'] %= arena_height

        for asteroid in asteroids.copy():
            if are_circles_intersecting(
                missile['x'], missile['y'], missile_radius,
                asteroid['x'], asteroid['y'],
                asteroid_stages[asteroid['stage']]['radius']
            ):
                missile['target']['colour'] = (255, 255, 0)
                missiles.remove(missile)

                if asteroid['stage'] > 0:
                    angle1 = random.random() * (2 * math.pi)
                    angle2 = (angle1 - math.pi) % (2 * math.pi)

                    asteroids.append({
                        'x': asteroid['x'] + math.cos(angle1) * asteroid_stages[asteroid['stage'] - 1]['radius'] + 1,
                        'y': asteroid['y'] + math.sin(angle1) * asteroid_stages[asteroid['stage'] - 1]['radius'] + 1,
                        'angle': angle1,
                        'collision': '',
                        'stage': asteroid['stage'] - 1,
                        'colour': (255, 255, 0)
                    })
                    asteroids.append({
                        'x': asteroid['x'] + math.cos(angle2) * asteroid_stages[asteroid['stage'] - 1]['radius'] + 1,
                        'y': asteroid['y'] + math.sin(angle2) * asteroid_stages[asteroid['stage'] - 1]['radius'] + 1,
                        'angle': angle2,
                        'collision': '',
                        'stage': asteroid['stage'] - 1,
                        'colour': (255, 255, 0)
                    })

                asteroids.remove(asteroid)
                break

    bullet_timer += dt
    missile_timer += dt

    if keyboard.S:
        if bullet_timer >= bullet_cooldown:
            bullet_timer = 0

            bullets.append({
                'x': ship_x + math.cos(ship_angle) * ship_radius,
                'y': ship_y + math.sin(ship_angle) * ship_radius,
                'angle': ship_angle,
                'time_left': 4,
            })

    if keyboard.A:
        if missile_timer >= missile_cooldown:
            missile_timer = 0

            missiles.append({
                'x': ship_x + math.cos(ship_angle) * ship_radius,
                'y': ship_y + math.sin(ship_angle) * ship_radius,
                'angle': ship_angle,
                'target': find_closest_asteroid(
                    (ship_x + math.cos(ship_angle) * ship_radius),
                    (ship_y + math.sin(ship_angle) * ship_radius),
                    missile_radius
                ),
            })

    for asteroid in asteroids:
        asteroid['x'] += math.cos(asteroid['angle']) * asteroid_stages[asteroid['stage']]['speed'] * dt
        asteroid['y'] += math.sin(asteroid['angle']) * asteroid_stages[asteroid['stage']]['speed'] * dt
        asteroid['x'] %= arena_width
        asteroid['y'] %= arena_height

        if are_circles_intersecting(
            ship_x, ship_y, ship_radius,
            asteroid['x'], asteroid['y'],
            asteroid_stages[asteroid['stage']]['radius']
        ):
            reset()
            break

    for asteroid in asteroids:
        for comparison in asteroids:
            if (not asteroid == comparison) and (not asteroid['collision'] == comparison) and are_circles_intersecting(
                    asteroid['x'], asteroid['y'],
                    asteroid_stages[asteroid['stage']]['radius'],
                    comparison['x'], comparison['y'],
                    asteroid_stages[comparison['stage']]['radius'],
            ):

                asteroid_angle = asteroid['angle']
                asteroid['angle'] = comparison['angle']
                comparison['angle'] = asteroid_angle

                asteroid['collision'] = comparison
                comparison['collision'] = asteroid

    if len(asteroids) == 0:
        reset()

def draw():
    screen.fill((0, 0, 0))

    for y in range(-1, 2):
        for x in range(-1, 2):
            offset_x = x * arena_width
            offset_y = y * arena_height

            screen.draw.filled_circle(
                (ship_x + offset_x, ship_y + offset_y),
                ship_radius, color=(0, 0, 255)
            )

            ship_circle_distance = 10
            screen.draw.filled_circle((
                ship_x + offset_x +
                    math.cos(ship_angle) * ship_circle_distance,
                ship_y + offset_y +
                    math.sin(ship_angle) * ship_circle_distance),
                5, color=(0, 255, 255)
            )

            for bullet in bullets:
                screen.draw.filled_circle(
                    (bullet['x'] + offset_x, bullet['y'] + offset_y),
                    bullet_radius, color=(0, 255, 0)
                )

            for missile in missiles:
                screen.draw.filled_circle(
                    (missile['x'] + offset_x, missile['y'] + offset_y),
                    missile_radius, color=(255, 0, 0)
                )

            for asteroid in asteroids:
                screen.draw.filled_circle((
                    asteroid['x'] + offset_x, asteroid['y'] + offset_y),
                    asteroid_stages[asteroid['stage']]['radius'],
                    color=asteroid['colour']
                )

TITLE = "Asteroids"
WIDTH = 800
HEIGHT = 600

pgzrun.go()