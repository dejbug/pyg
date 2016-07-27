import pygame, pygame.draw
import typ, com, trig
import hex


class HexTest1(object):
	def __init__(self, fg=pygame.Color("green")):
		self.tout = com.TextOut("Courier New", 12)
		
		self.cur = typ.Point(0, 0)
		self.radius = 67
		
		self.h1 = hex.Hex(typ.Point(80, 200), 30)
		self.h2 = hex.Hex(typ.Point(300, 150), self.radius, fg)
		self.h3 = hex.Hex(typ.Point(self.h2.c.x, self.h2.c.y-(self.radius*0.866)*2), self.radius, fg)
		self.h4 = hex.Hex(typ.Point(self.h2.c.x+(self.radius*(0.866-0.5)*2+1)*2, self.h2.c.y-(self.radius*0.866)), self.radius, fg)
		
	def onMouseMotion(self, p):
		self.cur = typ.Point(*p)
		
		self.h1.setbg(pygame.Color(180,200,220) if self.h1.hit(p) else None)
		
	def onDraw(self, surface):
		self.h1.draw(surface)
		self.h2.draw(surface)
		self.h3.draw(surface)
		self.h4.draw(surface)
		
		self.h2.centerPointSize = 3
		self.h2.centerPointColor = pygame.Color("red")
		
		pygame.draw.aaline(surface, pygame.Color("grey"), self.h2.c, self.cur)
		
		a, b = self.h1.getshield(self.cur)
		pygame.draw.aaline(surface, pygame.Color("red"), a, b)
		
		
		lc = hex.LineCalc(self.h2.c, self.cur)
		t = "(%+4d, %+4d) [%3d] %+4d" % (lc.dx, lc.dy, lc.len, int(lc.deg))
		self.tout(surface, (10, 30), t, pygame.Color("red"))
		
		sixth = (lc.deg / 60) % 6
		pygame.draw.aaline(surface, pygame.Color("red"), *hex.hexlines(self.h2.c, self.radius)[sixth])
		
		sixthdeg = lc.deg % 60
		len = self.radius*trig.sin(60)/trig.sin(120-sixthdeg)
		cut = typ.Point(int(round(len*trig.cos(lc.deg))), int(round(len*trig.sin(lc.deg))))
		t = "%+4d {%2d} (%+4d, %+4d)" % ((sixthdeg, len, ) + cut)
		self.tout(surface, (10, 50), t, pygame.Color("blue"))
		
		hexhit = lc.len < len
		
		pygame.draw.circle(surface, pygame.Color("red"), (self.h2.c.x+cut.x, self.h2.c.y+cut.y), 3)
		
		t = "(%d:%d)" % self.cur + (" | x" if hexhit else " | =")
		self.tout(surface, (10, 10), t)
		


class HexTest2(object):
	def __init__(self, radius=19, cols=13, rows=7):
		assert cols % 2 != 0, "'cols' must be odd; the current onDraw method is not yet general enough!"
		assert rows > 1, "'rows' must be greater than one; the current onDraw method is not yet general enough!"
		self.radius, self.cols, self.rows = radius, cols, rows
		self.cur = typ.Point(0, 0)
		self.tout = com.TextOut("Courier New", 12)
		
		self.fg = pygame.Color(0,0,0)
		self.hitColor = pygame.Color(140,180,170)
		
		self.offset = typ.Point(radius*3, radius*2)
		
		self.tiles = typ.GridList(self.cols, self.rows)
		
		for p in hex.GridPointsGenerator(radius, cols, rows, self.offset):
			self.tiles.append(hex.Hex(p, radius,
				fg=self.fg, blend=True))
			
		self.testHex = hex.DemoHex((520, 150), 80, fg=self.fg)
		self.hexClickGrid = hex.HexClickGrid(self.cols, self.rows, self.radius, self.offset)
		
	def onMouseMotion(self, p):
		for tile in self.tiles:
			tile.setbg(None)
			
		cell = self.hexClickGrid.hit(p)
			
		for col, row in self.hexClickGrid.getTilesForCell(*cell):
			tile = self.tiles.get(col, row)
			if tile.hit(p):
				tile.setbg(self.hitColor)
		
	def onDraw_naive(self, surface):
		for tile in self.tiles:
			tile.draw(surface)
				
	def onDraw(self, surface):
		for col, row in typ.enumerateGridCells(self.cols, self.rows):
			tile = self.tiles.get(col, row)
			
			tile.drawBackground(surface)
			
		for col, row in typ.enumerateGridCells(self.cols, self.rows):
			tile = self.tiles.get(col, row)
			
			if col % 2 == 0:
				if row == self.rows-1:
					tile.drawForeground(surface)
				else:
					tile.drawForeground(surface, excludeLines=[1])
			else:
				# exclude a couple of lines in the hex tile
				# so we don't draw shared edges twice (which
				# will look thick and ugly in 'blend mode').
				
				if row == self.rows-1:
					# the last (bottom) tile of a column.
					tile.drawForeground(surface, excludeLines=[3,5])
				else:
					# all other tiles.
					tile.drawForeground(surface, excludeLines=[0,1,2,3,5])
					
		self.testHex.draw(surface)
		#self.hexClickGrid.draw(surface)
		


