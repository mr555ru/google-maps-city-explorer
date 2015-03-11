import pygame
from pygame import *
import urllib
import cStringIO
from math import sin, cos, radians

class Player:
  def __init__(self, x, y):
    self.x = float(x)
    self.y = float(y)
    self.vel = 0
    self.angle = 90
    self.angvel = 0
    self.vel_coefficient = 1
    self.color = Color("#FF0000")
    
  def move(self):
    self.angle += self.angvel
    self.angle % 360
    self.x += self.vel*cos(radians(self.angle))*self.vel_coefficient
    self.y += self.vel*-sin(radians(self.angle))*self.vel_coefficient
    
  def doesMapChange(self, map_dimensions):
    if self.x < 0:
      return 'left'
    elif self.x > map_dimensions[0]:
      return 'right'
    elif self.y < 0:
      return 'up'
    elif self.y > map_dimensions[1]:
      return 'down'
    else:
      return None
    
  def mapChange(self, map_dimensions):
    if self.x < 0:
      self.x += map_dimensions[0]/2
    elif self.x > map_dimensions[0]:
      self.x -= map_dimensions[0]/2
    elif self.y < 0:
      self.y += map_dimensions[1]/2
    elif self.y > map_dimensions[1]:
      self.y -= map_dimensions[1]/2
    else:
      return None
    
  def xyFromCenter(self, map_dimensions):
    dx = self.x - map_dimensions[0]/2
    dy = self.y - map_dimensions[1]/2
    return dx, dy
    
  def getCoords(self, map_dimensions, center):
    dx, dy = self.xyFromCenter(map_dimensions)
    dy = -dy #inverse y axis to south-north
    guessed_scales = (1.15/2**18, 1.45/2**18) #TODO Magic numbers
    lat = center[1] + dx*guessed_scales[1]
    lon = center[0] + dy*guessed_scales[0]
    ang = - (self.angle - 90) % 360
    return (lon, lat, ang)

class Map:
  def __init__(self):
    #self.center = [47.226129, 39.745793]
    self.center = [35.7185436,139.858941]
    #self.scale = 19 # 1 grad = 5000 px
    self.dimensions = (1280, 960)
    self.getmap()
    
  def getmap(self):
    url = "http://maps.googleapis.com/maps/api/staticmap?size=" + str(self.dimensions[0]//2) + "x" + str(self.dimensions[1]//2) + "&center=" + str(self.center[0]) + "," +  str(self.center[1]) + "&zoom=17&scale=2&maptype=satellite&sensor=false&key=AIzaSyC1g3u02s1UyaruEOIPcpzh0oVFHFJd7wo"
    #print "getmap"
    self.mapfile = cStringIO.StringIO(urllib.urlopen(url).read())
    
  def mapChange(self, direction):
    if direction == 'left':
      self.center[1] -= 0.9/(2**8)
    if direction == 'right':
      self.center[1] += 0.9/(2**8) #TODO: MAGIC NUMBERS
    if direction == 'up':
      self.center[0] += 1.0/(2**9)
    if direction == 'down':
      self.center[0] -= 1.0/(2**9)
    self.getmap() 
    
class Viewer:
  def __init__(self):
    self.dimensions = (400, 400)
    self.viewfile = None
    
  def getView(self, lon, lat, angle):
    url = "http://maps.googleapis.com/maps/api/streetview?size=" + str(self.dimensions[0]) + "x" + str(self.dimensions[1]) + "&location=" + str(lon) + "," + str(lat) + "&fov=60&heading=" + str(angle) + "&pitch=10&sensor=false&key=AIzaSyC1g3u02s1UyaruEOIPcpzh0oVFHFJd7wo"
    self.viewfile = cStringIO.StringIO(urllib.urlopen(url).read())
      
    
class VisibleMap:
  def __init__(self, map):
    self.map = map
    self.surface = Surface(self.map.dimensions)
    self.set_surface()
    
  def set_surface(self):
    newsurface = pygame.image.load(self.map.mapfile)
    self.surface.blit(newsurface, (0,0))
        
  def draw(self, screen):
    screen.blit(self.surface, (0, 0))
    
class VisibleViewer:
  def __init__(self, viewer):
    self.viewer = viewer
    self.surface = Surface(self.viewer.dimensions)
    self.surface.fill(Color("#000000"))
    self.corner = 1 # 0 1
                    # 2 3
    
  def update(self, lon, lat, angle):
    self.viewer.getView(lon, lat, angle)
    newsurface = pygame.image.load(self.viewer.viewfile)
    self.surface.blit(newsurface, (0,0))
        
  def draw(self, screen, screen_dimensions):
    if self.corner == 0:
      screen.blit(self.surface, (0, 0)) 
    elif self.corner == 1:
      screen.blit(self.surface, (screen_dimensions[0]-self.viewer.dimensions[0], 0)) 
    elif self.corner == 3:
      screen.blit(self.surface, (screen_dimensions[0]-self.viewer.dimensions[0],
                                 screen_dimensions[1]-self.viewer.dimensions[1]))
    elif self.corner == 2:
      screen.blit(self.surface, (0, screen_dimensions[1]-self.viewer.dimensions[1])) 
    
class VisiblePlayer:
  def __init__(self, player):
    self.player = player
    self.size = 7
    self.surface = Surface((self.size, self.size))
    self.surface.fill(player.color)
    self.heading = Surface((3, 3))
    self.heading.fill(player.color)
  
  def move(self):
    self.player.move()
    #self.surface = pygame.transform.rotate(self.surface, self.player.angvel)
    #self.surface.blit(newsurface, (0,0))
  
  def draw(self, screen):
    screen.blit(self.surface, (int(self.player.x-self.size/2), int(self.player.y-self.size/2)))
    
    headingX = self.player.x + 15 * cos(radians(self.player.angle))
    headingY = self.player.y + 15 * -sin(radians(self.player.angle))
    screen.blit(self.heading, (int(headingX), int(headingY)))
    
    
#beginning main code

pygame_map = Map()
player = Player(pygame_map.dimensions[0]//2, pygame_map.dimensions[1]//2)

pygame.init()
screen = pygame.display.set_mode(pygame_map.dimensions)
timer = pygame.time.Clock()
ticker = 0

visible_map = VisibleMap(pygame_map)

visible_player = VisiblePlayer(player)

viewer = Viewer()
visible_viewer = VisibleViewer(viewer)
  
  
while 1:
  timer.tick(30)
  ticker += 1
  for e in pygame.event.get():
    if e.type == QUIT:
      raise SystemExit, "QUIT"
    if e.type == KEYDOWN:
      if e.key == K_UP:
        player.vel = 1.7
      elif e.key == K_DOWN:
        player.vel = -0.3
      elif e.key == K_RIGHT:
        player.angvel = -5
      elif e.key == K_LEFT:
        player.angvel = 5
      elif e.key == K_LSHIFT:
        player.vel_coefficient = 2.2
      elif e.key == K_SPACE:
        player_viewer = player.getCoords(visible_map.map.dimensions, visible_map.map.center)
        visible_viewer.update(player_viewer[0], player_viewer[1], player_viewer[2])
    if e.type == KEYUP:
      if e.key == K_UP or e.key == K_DOWN:
        player.vel = 0
      elif e.key == K_RIGHT or e.key == K_LEFT:
        player.angvel = 0
      elif e.key == K_LSHIFT:
        player.vel_coefficient = 1
      
  visible_player.move()
  if visible_player.player.doesMapChange(visible_map.map.dimensions) is not None:
    visible_map.map.mapChange(visible_player.player.doesMapChange(visible_map.map.dimensions))
    visible_player.player.mapChange(visible_map.map.dimensions)
    visible_map.set_surface()
    
  if ticker % 6000 == 0:
    player_viewer = player.getCoords(visible_map.map.dimensions, visible_map.map.center)
    #print player_viewer
    visible_viewer.update(player_viewer[0], player_viewer[1], player_viewer[2])
    #print "blop"
  #else:
  #  print ticker % 200
    
  dx, dy = player.xyFromCenter(visible_map.map.dimensions)
  if dx < 0 and dy < 0:
    visible_viewer.corner = 3
  elif dx < 0 and dy >= 0:
    visible_viewer.corner = 1
  elif dx >= 0 and dy < 0:
    visible_viewer.corner = 2
  elif dx >= 0 and dy >= 0:
    visible_viewer.corner = 0
      
  visible_map.draw(screen)
  visible_player.draw(screen)
  visible_viewer.draw(screen, visible_map.map.dimensions)
  pygame.display.update()
  