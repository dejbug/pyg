import pygame, math
import typ, trig

from sys import maxint as MAXINT


class Error(Exception): pass
class LineCalcError(Error): pass
class InfSlopeError(LineCalcError): pass
class ParallelError(LineCalcError): pass


hexdegs = range(0,360,60)
hexrads = [(trig.cos(d), trig.sin(d)) for d in hexdegs]


def hexagon(c, r):
	return [typ.Point(round(c[0]+r*h[0]), round(c[1]+r*h[1])) for h in hexrads]


def hexlines(c, r):
	vv = hexagon(c, r)
	return [(vv[i], vv[(i+1)%len(vv)]) for i in xrange(len(vv))]
	
	
class GridPointsGenerator(object):
	def __init__(self, radius, cols, rows, offset=None, extra=None):
		self.radius, self.cols, self.rows = radius, cols, rows
	
		self.offset = typ.Point(*(offset if offset else (radius+1,radius+1)))
		self.extra = extra or (0,0)
	
		self.inc = typ.Point(
			int(round(self.radius*(0.866-0.5)*2+self.extra[0])),
			int(round(self.radius*0.866+self.extra[1]))
			)
			
	def __iter__(self):
		for j in xrange(self.rows):
			for i in xrange(self.cols):
				yield typ.Point(
					self.offset.x + (i<<1)*self.inc.x,
					self.offset.y + ((j<<1)+(i&1))*self.inc.y)



class HexClickGrid(object):

	class SectorBounds(object):
		"""a sector is one of the (equal) squares into which the
		hexgrid will be partitioned (for quicker hittest response)."""
		def __init__(self, origin, radius):
			points = HexClickGrid.getHexPointsAroundOrigin(origin, radius)
			
			a = typ.Point(points[3].x, points[4].y)
			b = typ.Point(points[1].x, points[1].y)
			self.x = a.x
			self.y = a.y
			self.w = b.x-a.x
			self.h = b.y-a.y
			self.r = pygame.Rect(self.x, self.y, self.w, self.h)
			
		def applySizeCorrection(self, correction):
			"""see: HexClickGrid.computeCorrections()"""
			self.w += correction[0]
			self.h += correction[1]
			
	@classmethod
	def getHexPointsAroundOrigin(cls, origin, radius):
		return [typ.Point(p.x, p.y) for p in hexagon(origin, radius)]
		
	@classmethod
	def computeCorrections(cls, origin1, origin2, origin3, radius):
		"""due to (i suppose) rounding errors, the
		hex tiles will be shifted by a couple of pixels for
		hex grids with certain radii. the way to determine this
		constant offset, we need to compare three consecutive
		tiles in both the x and y direction, and see by how
		much their expected positions differ.
		"""
		sb1 = HexClickGrid.SectorBounds(origin1, radius)
		sb2 = HexClickGrid.SectorBounds(origin2, radius)
		sb3 = HexClickGrid.SectorBounds(origin3, radius)
		
		c1 = typ.Point(sb2.x - (sb1.x+sb1.w), sb2.y-sb1.y-sb1.h)
		c2 = typ.Point(sb3.x - (sb1.x+sb1.w)-sb2.w, sb3.y - (sb1.y+sb1.h)-sb2.h)
		
		return typ.Point(c2.x-c1.x, c2.y-c1.y)
		
	def __init__(self, cols, rows, radius, offset=(0,0)):
		self.cols, self.rows, self.radius, self.offset = cols, rows, radius, offset
		
		self.color = pygame.Color("red")
		
		self.origins = list(GridPointsGenerator(radius, 3, 3, offset))
		
		self.correction = typ.Point(
			HexClickGrid.computeCorrections(self.origins[0], self.origins[1], self.origins[2], self.radius).x,
			HexClickGrid.computeCorrections(self.origins[0], self.origins[3], self.origins[6], self.radius).y
			)
			
		self.sb = HexClickGrid.SectorBounds(self.origins[0], self.radius)
		self.sb.applySizeCorrection(self.correction)
		
	def draw(self, surface):
		ri = lambda f: round(int(f))
		rip = lambda p: typ.Point(ri(p[0]), ri(p[1]))
		rit = lambda x,y: typ.Point(ri(x), ri(y))
		
		x1 = self.sb.x
		x2 = x1 + (self.cols+1) * self.sb.w
		for row in xrange(self.rows+2):
			y = self.sb.y + row * self.sb.h
			pygame.draw.aaline(surface, self.color, rit(x1, y), rit(x2, y))
			
		y1 = self.sb.y
		y2 = y1 + (self.rows+1) * self.sb.h
		for col in xrange(self.cols+2):
			x = self.sb.x + col * self.sb.w
			pygame.draw.aaline(surface, self.color, rit(x, y1), rit(x, y2))
			
	def containsTile(self, col, row):
		return col >= 0 and col < self.cols and row >= 0 and row < self.rows
			
	def containsTileP(self, p):
		return p.x >= 0 and p.x < self.cols and p.y >= 0 and p.y < self.rows
		
	def getTilesForCell(self, col, row):
		cc = None
		if col % 2 == 0:
			cc = (typ.Point(*p) for p in ((col, row), (col-1, row), (col-1, row-1)))
		else:
			cc = (typ.Point(*p) for p in ((col, row), (col, row-1), (col-1, row)))
		
		return filter(self.containsTileP, cc)
		
	def hit(self, p):
		return typ.Point(
			int(round((p[0]-self.sb.x))/self.sb.w),
			int(round((p[1]-self.sb.y))/self.sb.h))
		
		
class Hex(object):
	def __init__(self, center, radius, fg=None, blend=True):
		self.c, self.r = typ.Point(int(round(center[0])), int(round(center[1]))), int(radius)
		self.lines = hexlines(self.c, self.r)
		self.fg = fg or pygame.Color("black")
		self.bg = None
		self.blend = blend
		self.box = self._calculateBox()
		self.centerPointSize = 0
		self.centerPointColor = pygame.Color("black")
		
	def _calculateBox(self):
		left, top, right, bottom = MAXINT, MAXINT, 0, 0
		for a, b in self.lines:
			if a.x < left: left = a.x
			if b.x < left: left = b.x
			if a.x > right: right = a.x
			if b.x > right: right = b.x
			if a.y < top: top = a.y
			if b.y < top: top = b.y
			if a.y > bottom: bottom = a.y
			if b.y > bottom: bottom = b.y
		return typ.Rect(left, top, right-left, bottom-top)
		
	def hitbox(self, p):
		return self.box.collidepoint(p)
		
	def hit(self, p, borderGap=2):
		lc = LineCalc(self.c, p)
		sixth = (lc.deg / 60) % 6
		sixthdeg = lc.deg % 60
		len = self.r*trig.sin(60)/trig.sin(120-sixthdeg)
		return lc.len < max(0, len-borderGap)
		
	def getsixth(self, p):
		lc = LineCalc(self.c, p)
		return (lc.deg / 60) % 6
		
	def getshield(self, p):
		return self.lines[self.getsixth(p)]
		
	def getcut(self, p):
		lc = LineCalc(self.c, p)
		sixth = (lc.deg / 60) % 6
		sixthdeg = lc.deg % 60
		len = self.r*trig.sin(60)/trig.sin(120-sixthdeg)
		return typ.Point(len*trig.cos(lc.deg), len*trig.sin(lc.deg))
		
	def setfg(self, color):
		assert isinstance(color, (pygame.Color, type(None)))
		self.fg = color or pygame.Color("black")
		
	def setbg(self, color):
		assert isinstance(color, (pygame.Color, type(None)))
		self.bg = color or None
		
	def drawBackground(self, surface):
		if self.bg:
			pygame.draw.polygon(surface, self.bg, hexagon(self.c, self.r), 0)
		
	def drawForeground(self, surface, excludeLines=None):
		if self.centerPointSize > 0:
			pygame.draw.circle(surface, self.fg, self.c, self.centerPointSize)
			
		#pygame.draw.aalines(surface, self.fg, True, hexagon(self.c, self.r))
		
		if not excludeLines:
			for a, b in self.lines:
				pygame.draw.aaline(surface, self.fg, a, b, self.blend)
		else:
			for i, l in enumerate(self.lines):
				if i in excludeLines: continue
				a, b = l
				pygame.draw.aaline(surface, self.fg, a, b, self.blend)
		
	def draw(self, surface, excludeLines=None):
		if self.bg:
			self.drawBackground(surface)
			
		self.drawForeground(surface, excludeLines)
		
		
class DemoHex(Hex):
	def __init__(self, center, radius, fg=None, blend=True):
		Hex.__init__(self, center, radius, fg, blend)
		
		self.points = [typ.Point(int(p.x), int(p.y)) for p in hexagon(center, radius)]
		self.colors = [pygame.Color(c) for c in ("red", "green", "blue", "cyan", "magenta", "yellow")]
		
	def draw(self, surface, excludeLines=None):
		Hex.draw(self, surface, [5])
		
		for i in xrange(6):
			pygame.draw.circle(surface, self.colors[i], self.points[i], 4)
			
			
class LineCalc(object):
	MINpos = 0.000001
	MINneg = -MINpos
	
	def __init__(self, a, b):
		self.a = a
		self.b = b
		
		# which quadrant am i in?
		self.q = 0
		if b[0] >= a[0]:
			if b[1] >= a[1]: self.q = 1
			else: self.q = 4
		else:
			if b[1] >= a[1]: self.q = 2
			else: self.q = 3
		
		if self.q not in range(1,5): raise LineCalcError, "invalid quadrant"
		
		self.dy = float(b[1]-a[1])
		self.dx = float(b[0]-a[0])
		
		if self.dx < LineCalc.MINpos and self.dx > LineCalc.MINneg:
			#raise InfSlopeError, "infinite slope"
			self.dx = LineCalc.MINpos
		
		self.m = self.dy/self.dx
		self.rad = math.atan(self.m)
		
		if self.q == 1: pass
		elif self.q == 2: self.rad += math.pi
		elif self.q == 3: self.rad += math.pi
		elif self.q == 4: self.rad += 2*math.pi
		
		self.deg = trig.rad2deg(self.rad)
		self.len = int(math.sqrt(self.dx*self.dx+self.dy*self.dy))


class LineCalc2(LineCalc):
	def __init__(self, a, b):
		LineCalc.__init__(self, a, b)
		self.c = (a[0]-a[1]/self.m) if self.m else 0
		
	def y(self, x):
		return self.m * x + self.c
		
	def cross(self, lc):
		assert isinstance(lc, LineCalc)
		
		# see LineCalc1 !
		if self.dx == LineCalc.MINpos or lc.dx == LineCalc.MINpos:
			raise InfSlopeError, "infinite slope"
		
		m = self.m - lc.m
		c = self.c - lc.c
		#if not m: return None
		if not m: raise ParallelError, "parallel lines"
		
		x = -c/m
		y = self.y(x)
		return typ.Point(int(x), int(y))
		
	def __str__(self):
		if self.dx == LineCalc.MINpos:
			return "y = undef"
		
		return "y = %dx + %d" % (self.m, self.c)

