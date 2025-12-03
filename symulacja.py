import pygame as pg
import random
import pygame.image
import csv
import matplotlib as plt
import numpy as np
pg.init()
screen = pg.display.set_mode((800, 500))
clock = pg.time.Clock()
image_path= pygame.image.load("serwerownia.png")
font = pg.font.SysFont(None, 24)
class Server:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.working = True
        self.width= 80
        self.height= 100
        self.repair_time = 0
        self.working_time = 0
        self.just_failed = False
        self.total_repair_time =0
        self.sim_hours =0
        self.freeze = False
        self.fail_count =0
    def draw_shape(self):
        if self.working:
            square_color = (30,30,30)
            orbit_color = (0,255,0)
        else:
            square_color = (30,30,30)
            orbit_color = (255,0,0)
        pg.draw.rect(screen, square_color,
                     (self.x, self.y, self.width, self.height))
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        radius = min(self.width, self.height) // 2
        pg.draw.circle(screen, orbit_color, ((cx), (cy)), radius)
    def update(self,sim_minutes):
        if self.working:
            if self.freeze==False:
               self.working_time += sim_minutes / 60
        if self.working:
            if random.random() < 0.0001:
                self.working = False
                self.just_failed = True
                self.fail_count += 1
        else:
            self.repair_time -= sim_minutes
            self.total_repair_time += sim_minutes
            if self.repair_time <= 0:
                self.working = True

    @staticmethod
    def repair_draw(servers):
        x = 10
        y = 50
        spacing = 22

        title = font.render("Repair", True, (255, 255, 255))
        screen.blit(title, (x, y))

        for i, s in enumerate(servers):
            hours = s.total_repair_time / 60
            text = f"S{i + 1}: {hours:.1f}h"
            label = font.render(text, True, (255, 255, 255))
            screen.blit(label, (x, y + (i + 1) * spacing))

    def draw(self):
        self.draw_shape()
        text_color = (0,255,0) if self.working else (255,0,0)
        text= f"{self.working_time:.1f} h"
        label= font.render(text, True, text_color)
        text_x = self.x + self.width / 2 - label.get_width() / 2
        text_y = self.y - 20
        screen.blit(label, (text_x, text_y))

def save_to_csv(servers):
    with open('servers.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(["Server ID", "Sim Hours", "Total Repair Time (h)", "Failures"])
        for i,s in enumerate(servers):
            writer.writerow([i+1,round(s.working_time,2), round(s.total_repair_time/ 60,2), s.fail_count if hasattr(s,"fail_count") else 0])

        print("zapisano dane")


servers = []
for i in range(10):
    x = 100 + (i % 5) * 140
    y = 100 + (i // 5) * 180
    servers.append(Server(x, y))
running = True
while  running:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            save_to_csv(servers)
            running = False
    dt = clock.tick(60) / 1000.0
    SIM_MINUTES = dt * (60/0.083333333)
    SIM_MIN_CRASH =dt*(60/5)
    failed_servers = [s for s in servers if not s.working]
    failed_count = len(failed_servers)
    someone_failed = any(not s.working for s in servers)
    assigned_time =0
    if failed_count ==1:
        assigned_time = 8*60
    elif failed_count in (2,3):
        assigned_time = 4*60
    elif failed_count >=4:
        assigned_time = 0.5*60
    else:
        assigned_time = None
    for s in failed_servers:
        if s.just_failed:
            s.repair_time = assigned_time
            s.just_failed = False
    for s in servers:
        if someone_failed:
           s.update(SIM_MIN_CRASH)
        else:
            s.update(SIM_MINUTES)
    screen.blit(image_path,(0, 0))
    for s in servers:
       s.repair_draw(servers)
       s.draw()
    pg.display.flip()
