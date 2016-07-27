
#hexrads = [(0.0, 1.0), (0.866, 0.5), (0.866, -0.5), (0.0, -1.0), (-0.866, -0.5), (-0.866, 0.5)]

hexdegs = range(0,360,60)
hexrads = [(trig.cos(d), trig.sin(d)) for d in hexdegs]

c = typ.Point(100, 100)
r = 10


def hexagonx(c, r, dd=[0, 60, 120, 180, 240, 300]):
	return [(c[0] + r * trig.sin(d), c[1] + r * trig.cos(d)) for d in dd]

	
def hexagon(c, r):
	return [(c[0] + r * h[0], c[1] + r * h[1]) for h in hexrads]


def inhexagon(c, r, p):
	return trig.sin(p[0]-c[0]) < r and trig.cos(p[1]-c[1]) < r

class Error(Exception): pass
class LineCalcError(Error): pass
class InfSlopeError(LineCalcError): pass
class ParallelError(LineCalcError): pass


class LineCalc1(object):
	MINpos = 0.000001
	MINneg = -MINpos
	
	def __init__(self, a, b):
		self.a, self.b = a, b
		
		self.dy = float(b[1]-a[1])
		self.dx = float(b[0]-a[0])
		
		if self.dx < LineCalc1.MINpos and self.dx > LineCalc1.MINneg:
			#raise InfSlopeError, "infinite slope"
			self.dx = LineCalc1.MINpos
			
		self.m = self.dy/self.dx
		self.rad = math.atan(self.m)
		self.deg = trig.rad2deg(self.rad)
		self.c = (a[0]-a[1]/self.m) if self.m else 0
		self.len = int(math.sqrt(self.dx*self.dx+self.dy*self.dy))
		
	def y(self, x):
		return self.m * x + self.c
		
	def cross(self, lc):
		assert isinstance(lc, LineCalc1)
		
		if self.dx == LineCalc1.MINpos and lc.dx == LineCalc1.MINpos:
			raise ParallelError, "parallel lines"
			
		if self.dx == LineCalc1.MINpos:
			x = self.a[0]
			y = lc.y(x)
			return typ.Point(int(x), int(y))
			
		elif lc.dx == LineCalc1.MINpos:
			x = lc.a[0]
			y = self.y(x)
			return typ.Point(int(x), int(y))
		
		m = self.m - lc.m
		c = self.c - lc.c
		
		if not m: raise ParallelError, "parallel lines"
		
		x = -c/m
		y = self.y(x)
		return typ.Point(int(x), int(y))
		


# call this class Hexline instead?
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
		self.c = (a[0]-a[1]/self.m) if self.m else 0
		self.len = int(math.sqrt(self.dx*self.dx+self.dy*self.dy))
		
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


def hexsect(c, r, p):
	lc = LineCalc(c, p)
	
	#print "(%+4d, %+4d) [%3d] %+4d" % (lc.dx, lc.dy, lc.len, int(lc.deg))
	x = int(c.x+r*trig.cos(lc.deg))
	y = int(c.y+r*trig.sin(lc.deg))
	return typ.Point(x, y)

def hexlines(c, r):
	vv = hexagon(c, r)
	return [(vv[i], vv[(i+1)%len(vv)]) for i in xrange(len(vv))]

def hexsect2(c, r, p):
	ll = hexlines(c, r)
	pp  = []
	
	for l in ll:
		try:
			lc = LineCalc(l[0], l[1])
			cp = LineCalc(c, p)
			pp.append(lc.cross(cp))
		except LineCalcError, e: print e
	
	return pp


def incircle(c, r, p):
	return (p[0]-c[0])*(p[0]-c[0])+(p[1]-c[1])*(p[1]-c[1]) <= r*r

