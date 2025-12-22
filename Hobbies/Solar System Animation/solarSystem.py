import turtle
import math
import time

screen = turtle.Screen()
screen.bgcolor("black")
screen.title("3D Solar System Simulation")
screen.setup(width=900, height=700)

sun = turtle.Turtle()
sun.shape("circle")
sun.color("yellow")
sun.shapesize(3)
sun.penup()

class Planet:
    def __init__(self, color, distance, radius, speed):
        self.t = turtle.Turtle()
        self.t.shape("circle")
        self.t.color(color)
        self.t.shapesize(radius)
        self.t.penup()
        
        self.distance = distance
        self.angle = 0
        self.speed = speed

    def move(self):
        x = self.distance * math.cos(math.radians(self.angle))
        y = (self.distance * 0.4) * math.sin(math.radians(self.angle))

        depth = math.sin(math.radians(self.angle))

        scale = 1 + depth * 0.3
        self.t.shapesize(scale)

        self.t.goto(x, y)

        self.angle = (self.angle + self.speed) % 360

mercury = Planet("gray", 70, 0.25, 4)
venus   = Planet("orange", 110, 0.45, 2)
earth   = Planet("blue", 150, 0.5, 1.4)
mars    = Planet("red", 190, 0.4, 1)
jupiter = Planet("brown", 240, 1.2, 0.8)
saturn = Planet("gold", 290, 1.0, 0.6)
neptune = Planet("blue", 340, 0.9, 0.5)
uranus = Planet("light blue", 390, 0.8, 0.4)

planets = [mercury, venus, earth, mars, jupiter, saturn, neptune, uranus]

orbit = turtle.Turtle()
orbit.hideturtle()
orbit.speed(0)
orbit.color("white")

def draw_orbits():
    orbit.clear()
    orbit.width(1)
    orbit.color("white")

    for d in [70, 110, 150, 190, 240, 290, 340, 390]:
        orbit.penup()
        for angle in range(0, 360, 2):
            x = d * math.cos(math.radians(angle))
            y = (d * 0.4) * math.sin(math.radians(angle))
            orbit.goto(x, y)
            orbit.pendown()

draw_orbits()

while True:
    for p in planets:
        p.move()

    time.sleep(0.02)
