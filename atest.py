
import pygame
import math

from lib import com
from lib.astar import Astar


SCREEN_SIZE = (640,300)
COLOR_BACKGROUND = (255,255,255)
EVENT_TIMER_1 = pygame.USEREVENT+1

# init
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE, pygame.DOUBLEBUF, 32)
pygame.display.set_caption("a*")
pygame.time.set_timer(EVENT_TIMER_1, 1000)


class Grid(object):
	def __init__(self, cols, rows, edge, offset=None, color=None):
		self.color = color or pygame.Color("black")
		self.off = offset or (0,0)
		self.cols = cols
		self.rows = rows
		self.edge = edge
		
	def draw(self, surface):
		dx = self.cols*self.edge
		for y in xrange(self.rows+1):
			dy = y*self.edge
			a = [self.off[0], self.off[1]+dy]
			b = [self.off[0]+dx, self.off[1]+dy]
			pygame.draw.aaline(screen, self.color, a, b)
		
		dy = self.rows*self.edge
		for x in xrange(self.cols+1):
			dx = x*self.edge
			a = [self.off[0]+dx, self.off[1]]
			b = [self.off[0]+dx, self.off[1]+dy]
			pygame.draw.aaline(screen, self.color, a, b)
			
	def point2cell(self, p):
		x = p[0]-self.off[0]
		y = p[1]-self.off[1]
		x /= self.edge
		y /= self.edge
		return (x, y)
		
	def cell2rect(self, c):
		x = self.off[0] + c[0]*self.edge
		y = self.off[1] + c[1]*self.edge
		return (x, y, self.edge, self.edge)
		
	def cell2index(self, c):
		return c[0] + c[1] * self.cols
		
	def index2cell(self, i):
		return (i % self.cols, i / self.cols)
		
	def index2rect(self, i):
		cell = self.index2cell(i)
		return self.cell2rect(cell)
		
	def index(self, c):
		return self.cell2index(c)
		
	def box(self, c):
		return self.cell2rect(c)
		
	def hit(self, p, strict=False):
		x, y = self.point2cell(p)
		if strict:
			if x < 0 or y < 0: return None
			if x >= self.cols or y >= self.rows: return None
		return (x, y)
		
	def bounds(self):
		return (self.off[0], self.off[1],
			self.edge * self.cols,
			self.edge * self.rows)
			
	def astar(self, s, e, holes=[]):
		if None == s or None == e:
			return []
			
		return Astar.path(self.cols, self.rows, s, e, holes)


def Main():
	textout = com.TextOut()
	
	sc = pygame.Color("grey")		# start point color
	ec = pygame.Color("orange")		# end point color
	wc = pygame.Color("pink")		# walls color
	pc = pygame.Color("red")		# path color
	
	grid = Grid(60, 20, 10, (10,10), pygame.Color("pink"))
	
	walls = []
	path = []
	
	start = None
	end = None
	
	updatePath = False
	
	while True:
		event = pygame.event.wait()
		
		if event.type == pygame.QUIT:
			break
			
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				break
				
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				hit = grid.hit(event.pos, strict=True)
				if hit and hit not in walls:
					if None == start:
						start = hit
						updatePath = True
					elif hit != start and hit != end:
						end = hit
						updatePath = True
					
			elif event.button == 2:	
				hit = grid.hit(event.pos, strict=True)
				if hit:
					if hit != start and hit != end:
						if hit not in walls:
							walls.append(hit)
						else:
							walls.remove(hit)
					updatePath = True
				
			elif event.button == 3:
				start = None
				end = None
				path = []
				
			elif event.button == 4:
				pass
				
			elif event.button == 5:
				pass
				
		elif event.type == pygame.MOUSEMOTION:
			pass
			
		elif event.type == EVENT_TIMER_1:
			pass
		
		
		if updatePath:
			path = grid.astar(start, end, walls)
			updatePath = False
		
		
		screen.fill(COLOR_BACKGROUND)
		
		
		if None != start:
			pygame.draw.rect(screen, sc, grid.box(start))
		
		if None != end:
			pygame.draw.rect(screen, ec, grid.box(end))
		
		for c in walls:
			r = grid.box(c)
			pygame.draw.rect(screen, wc, r)
		
		for c in path:
			r = grid.box(c)
			pygame.draw.rect(screen, pc, r)
		
		
		grid.draw(screen)
		
		
		if None == start:
			r = grid.bounds()
			textout(screen, (10, 10+r[1]+r[3]),
				"click LB to set start of path")
				
		elif None == end:
			r = grid.bounds()
			textout(screen, (10, 10+r[1]+r[3]),
				"click LB to set end of path")
		
		else:
			r = grid.bounds()
			textout(screen, (10, 10+r[1]+r[3]),
				"click LB to re-set end of path (or RB to clear it)")
		
		if not walls:
			r = grid.bounds()
			textout(screen, (10, 30+r[1]+r[3]),
				"click MB to toggle walls")
		
		
		pygame.display.update()


if "__main__" == __name__:
	Main()

	
# Dejan Budimir (day-un boo-dee-mere)
