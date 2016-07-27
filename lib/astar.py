from sys import maxint


class Astar(object):
	neighborOffsets = [(-1,0), (0,-1), (0,1), (1,0)]
	
	@classmethod
	def estimatedPathLength(cls, s, e, penalizeDiagonals=False, straighten=False):
		dx = abs(e[0]-s[0])
		dy = abs(e[1]-s[1])
		if straighten: return max(dx, dy) + min(dx, dy)*2
		return dx+dy if penalizeDiagonals else max(dx, dy)
	
	@classmethod
	def getOpenSetCellWithLowestFScore(cls, openSet, fScores):
		f = maxint
		c = None
		
		for cell in openSet:
			if fScores[cell] < f:
				f = fScores[cell]
				c = cell
				
		return c
	
	@classmethod
	def reconstructPath(cls, cameFrom, current):
		p = [current]
		
		while current in cameFrom:
			current = cameFrom[current]
			p.append(current)
			
		return p
	
	@classmethod
	def containsCell(cls, cols, rows, c):
		return c[0] >= 0 and c[1] >= 0 and c[0] < cols and c[1] < rows
	
	@classmethod
	def neighborCells(cls, cols, rows, c, holes=[]):
		nn = []
		
		for o in cls.neighborOffsets:
			n = (c[0]+o[0], c[1]+o[1])
			if cls.containsCell(cols, rows, n) and n not in holes:
				nn.append(n)
		
		return nn
		
	@classmethod
	def isInBox(cls, s, e, c):
		l = min(s[0], e[0])
		r = max(s[0], e[0])
		t = min(s[1], e[1])
		b = max(s[1], e[1])
		return c[0] >= l and c[0] <= r and c[1] >= t and c[1] <= b
		
	@classmethod
	def isDiagonal(cls, s, e):
		return s[0] != e[0] and s[1] != e[1]
	
	@classmethod
	def _calculateFScore(cls, *args):
		gs, s, e = args
		return gs[s]+cls.estimatedPathLength(s, e)
	
	@classmethod
	def _calculateTentativeGScore(cls, *args):
		gs, s, e, c = args
		return gs[c] + 1
		
	@classmethod
	def path(cls, cols, rows, s, e, holes=[]):
		cs = set([])
		os = set([s])
		cf = {}
		
		gs = {s:0}
		fs = {s:cls._calculateFScore(gs, s, e)}
		
		while os:
			c = cls.getOpenSetCellWithLowestFScore(os, fs)
			if c == e:
				return cls.reconstructPath(cf, c)
			
			os.remove(c)
			cs.add(c)
			
			for n in cls.neighborCells(cols, rows, c, holes):
				if n in cs:
					continue
					
				tgs = cls._calculateTentativeGScore(gs, s, e, c)
			
				if n not in os or tgs < gs[n]:
					cf[n] = c
					gs[n] = tgs
					fs[n] = cls._calculateFScore(gs, n, e)
					os.add(n)
				
		return []


class Astar2(Astar):
	neighborOffsets = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
	
	@classmethod
	def estimatedPathLength(cls, s, e, penalizeDiagonals=True, straighten=True):
		dx = abs(e[0]-s[0])
		dy = abs(e[1]-s[1])
		if straighten: return max(dx, dy) + min(dx, dy)*2
		return dx+dy if penalizeDiagonals else max(dx, dy)
	
	@classmethod
	def _calculateTentativeGScore(cls, *args):
		keepInBox = True
		penalizeDiagonals = True
		
		gs, s, e, c = args
		tgs = gs[c] + 1
		if keepInBox: tgs += 0 if cls.isInBox(s, e, c) else 1
		if penalizeDiagonals: tgs += 1 if cls.isDiagonal(s, e) else 0
		return tgs
		
	
