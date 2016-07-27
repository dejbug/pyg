import pygame


class Cell(object):
	def __init__(self, col, row):
		assert isinstance(col, int)
		assert isinstance(row, int)
		self.col, self.row = col, row
		
	def __getitem__(self, key):
		if 0 == key: return self.col
		if 1 == key: return self.row
		raise KeyError
		
	def __setitem__(self, key, value):
		if 0 == key: self.col = value
		if 1 == key: self.row = value
		raise KeyError
		
	def __str__(self):
		return "Cell(%d, %d)" % (self.col, self.row)
		
		
class GridModel(object):
	def __init__(self, grid):
		self.grid = grid
		self.size = (self.grid.cols, self.grid.rows)
		self.data = [0] * self.count()
		
	def count(self):
		return self.grid.rows * self.grid.cols
		
	def contains(self, obj):
		if None == obj:
			return False
		elif isinstance(obj, (tuple, Cell)):
			if obj[0] < 0 or obj[0] >= self.grid.cols: return False
			if obj[1] < 0 or obj[1] >= self.grid.rows: return False
			return True
		elif isinstance(obj, (int, long)):
			return obj >= 0 and obj < len(self.data)
		raise TypeError, "argument must be Cell instance or integer."
		
	def index2cell(self, index):
		assert isinstance(index, (int, long))
		return Cell(index % self.grid.cols, index / self.grid.rows)
		
	def cell2index(self, cell):
		assert isinstance(cell, (tuple, Cell))
		return cell[0] + cell[1] * self.grid.cols
		
	def bounds(self, cell):
		assert isinstance(cell, (tuple, Cell))
		
		return pygame.Rect(
			self.grid.pos[0] + cell[0] * self.grid.edge,
			self.grid.pos[1] + cell[1] * self.grid.edge,
			self.grid.edge, self.grid.edge)
			
	def hit(self, pos):
		c = Cell(
			(pos[0]-self.grid.pos[0])/self.grid.edge,
			(pos[1]-self.grid.pos[1])/self.grid.edge)
		return c if self.contains(c) else None
		
	def toggle(self, cell, value, clr=0):
		index = cell if isinstance(cell, (int, long)) else self.cell2index(cell)
		if not self.contains(index): return None
		if self.data[index] == value:
			self.data[index] = clr
		else:
			self.data[index] = value
		return index
		
	def set(self, cell, value):
		index = cell if isinstance(cell, (int, long)) else self.cell2index(cell)
		if not self.contains(index): return None
		self.data[index] = value
		return index
		
	def get(self, cell):
		index = cell if isinstance(cell, int) else self.cell2index(cell)
		return self.data[index]
		
	def iterate(self):
		index = 0
		for row in xrange(self.grid.rows):
			for col in xrange(self.grid.cols):
				yield index, col, row
				index += 1
				
	def actives(self):
		for i, c, r in self.iterate():
			if 0 != self.data[i]:
				yield Cell(c, r)
			
	def clear(self, *args, **kwargs):
		val = kwargs["val"] if "val" in kwargs else 0
		
		if len(args) == 0:
			for i, c, r in self.iterate():
				self.data[i] = val
				
		elif len(args) == 1:
			for i, c, r in self.iterate():
				if self.data[i] == args[0]:
					self.data[i] = val
					
		elif len(args) == 2 or "min" in kwargs and "max" in kwargs:
			minVal = kwargs["min"] if "min" in kwargs else args[0]
			maxVal = kwargs["max"] if "max" in kwargs else args[1]
			
			for i, c, r in self.iterate():
				if self.data[i] >= minVal and self.data[i] <= maxVal:
					self.data[i] = val
			
			
class GridModel2(GridModel):
	#TODO: test if this class is any faster.
	
	def __init__(self, grid):
		GridModel.__init__(self, grid)
		self.active = set()
		
	def set(self, cell, value):
		index = GridModel.set(self, cell, value)
		
		if 0 != value:
			self.actives.add(index)
		elif index in self.actives:
			self.actives.remove(index)
			
	def clear(self):
		for index in self.actives:
			self.data[index] = 0
		self.actives.clear()
		
		
class GridModelCA(GridModel):
	def __init__(self, grid):
		GridModel.__init__(self, grid)
		
	def neighbors8(self, cell):
		# Moore neighborhood.
		if not cell: return []
		h = Neighborhood(self, cell)
		return h.n8()
				
	def neighbors4(self, cell):
		# von Neumann neighborhood.
		if not cell: return []
		h = Neighborhood(self, cell)
		return h.n4()
		
		
class Neighborhood(object):
	"""A generator for cell neighborhoods."""
	
	def __init__(self, grid, cell, continuous=False):
		if not grid.contains(cell):
			raise ValueError, "'cell' must be a valid 'grid' coordinate"
		self.grid = grid
		self.cell = cell
		self.cont = continuous
		
	def _dec(self, key):
		v = self.cell[key]-1
		if v < 0:
			v = v + self.grid.size[key] if self.cont else 0
		return v
		
	def _inc(self, key):
		v = self.cell[key]+1
		if v > self.grid.size[key]-1:
			v = v - self.grid.size[key] if self.cont else self.grid.size[key]-1
		return v
		
	def n4(self):
		return [self.w(), self.s(), self.e(), self.n()]
		
	def n8(self):
		return [self.w(), self.sw(), self.s(), self.se(), self.e(), self.ne(), self.n(), self.nw()]
		
	def w(self):
		return Cell(self._dec(0), self.cell[1])
		
	def e(self):
		return Cell(self._inc(0), self.cell[1])
		
	def n(self):
		return Cell(self.cell[0], self._dec(1))
		
	def s(self):
		return Cell(self.cell[0], self._inc(1))
		
	def nw(self):
		return Cell(self._dec(0), self._dec(1))
		
	def se(self):
		return Cell(self._inc(0), self._inc(1))
		
	def ne(self):
		return Cell(self._inc(0), self._dec(1))
		
	def sw(self):
		return Cell(self._dec(0), self._inc(1))
		
		
class Grid(object):
	def __init__(self, cols, rows, edge, pos=None, lc=None, bg=None, bc=None):
		if cols < 1: raise ValueError, "must have at least one column"
		if rows < 1: raise ValueError, "must have at least one row"
		if edge < 1: raise ValueError, "edge must be a positive length"
		
		self.cols, self.rows, self.edge = cols, rows, edge
		self.pos = pos or (0,0)
		self.lc = lc or pygame.Color("black")
		self.bg = bg
		self.bc = bc
		
		self.cc = [
				pygame.Color("#666666"),
				pygame.Color("#999999"),
				]
		
		self.bounds = pygame.Rect(self.pos[0], self.pos[1],
			self.edge * self.cols + 1, self.edge * self.rows + 1)
		
		self.model = GridModel(self)
		
	def hit(self, pos):
		return self.bounds.collidepoint(pos)
		
	def drawBackground(self, surf, w, h):
		if self.bg:
			pygame.draw.rect(surf, self.bg,
				(self.pos[0], self.pos[1], w, h), 0)
				
	def drawForeground(self, surf, w, h):
		self.drawInnerGrid(surf, w, h)
		self.drawBorder(surf, w, h)
		
	def drawInnerGrid(self, surf, w, h):
		y = self.pos[1] + self.edge if self.bc else self.pos[1]
		x = self.pos[0]
		rows = self.rows - 1 if self.bc else self.rows + 1
		
		for row in xrange(rows):
			pygame.draw.aaline(surf, self.lc,
				(x, y), (x + w, y))
			y += self.edge
		
		x = self.pos[0] + self.edge if self.bc else self.pos[0]
		y = self.pos[1]
		cols = self.cols - 1 if self.bc else self.cols + 1
		
		for col in xrange(cols):
			pygame.draw.aaline(surf, self.lc,
				(x, self.pos[1]), (x, self.pos[1] + h))
			x += self.edge
			
	def drawBorder(self, surf, w, h):
		if self.bc:
			pygame.draw.rect(surf, self.bc,
				(self.pos[0], self.pos[1], w+1, h+1), 1)
				
	def drawCells(self, surf, w, h):
		for c in self.model.actives():
			r = self.model.bounds(c)
			if self.model.get(c) < 0:
				pygame.draw.rect(surf, pygame.Color("pink"), r)
			else:
				ci = self.model.get(c) % len(self.cc)
				pygame.draw.rect(surf, self.cc[ci], r)
				
	def draw(self, surf):
		w = self.edge * self.cols
		h = self.edge * self.rows
		
		if self.bg: self.drawBackground(surf, w, h)
		
		self.drawCells(surf, w, h)
		
		self.drawForeground(surf, w, h)
		
		if self.bc: self.drawBorder(surf, w, h)
		
		
class GridCA(Grid):
	def __init__(self, *args, **kwargs):
		Grid.__init__(self, *args, **kwargs)
		
		self.model = GridModelCA(self)
		self.ca = CA(self)
		
		self.clean = False
		
	def step(self):
		self.ca.step()
		
	def onMouseMove(self, event, button=None):
		if not self.hit(event.pos):
			if not self.clean:
				self.model.clear(-1)
				self.clean = True
			return
			
		self.clean = False
		
		c = self.model.hit(event.pos)
		nn = self.model.neighbors8(c)
		
		self.model.clear(-1)
		for n in nn:
			if self.model.get(n) == 0:
				self.model.set(n, -1)
			
	def onMouseDrag(self, event, button):
		if not self.hit(event.pos):
			return
			
		c = self.model.hit(event.pos)
		if c:
			if button == 1:
				self.model.set(c, 1)
			else:
				self.model.set(c, 0)
			
	def onMouseSet(self, event):
		self.onMouseDrag(event, 1)
			
	def onMouseClear(self, event):
		self.onMouseDrag(event, 0)
		
		
class CA(object):
	def __init__(self, grid):
		if not isinstance(grid.model, GridModelCA):
			raise TypeError, "'grid''s model must be based on GridModelCA"
		self.grid = grid
		
		self.next = self.next = [0] * len(self.grid.model.data)
		
	def clear(self):
		for i in xrange(len(self.next)): self.next[i] = 0
		
	def reset(self):
		self.clear()
		self.commitAll()
		
	def commit(self, index):
		self.grid.model.data[index] = self.next[index]
		
	def commitAll(self):
		for i in xrange(len(self.next)): self.commit(i)
		
	def update(self, index):
		cell = self.grid.model.index2cell(index)
		nn = self.grid.model.neighbors8(cell)
		
		c = 0
		for n in nn:
			if self.grid.model.get(n) == 1:
				c += 1
				
		if self.grid.model.data[index] == 0:
			if c == 3:
				self.next[index] = 1
		else:
			if c == 2 or c == 3:
				self.next[index] = 1
			elif c < 2 or c > 3:
				self.next[index] = 0
			
	def step(self):
		for i,c,r in self.grid.model.iterate():
			self.update(i)
		
		self.commitAll()
			