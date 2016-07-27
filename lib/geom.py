import random


NUMTYPE = (int, long, float)


class P(object):
	def __init__(self, x=0, y=0):
		assert isinstance(x, NUMTYPE)
		assert isinstance(y, NUMTYPE)

		self.x = int(x)
		self.y = int(y)

	def __str__(self):
		return "P(%d,%d)" % (self.x, self.y)

	def __iter__(self):
		yield self.x
		yield self.y

	def __getitem__(self, key):
		if key == 0: return self.x
		elif key == 1: return self.y
		else: raise KeyError

	def __setitem__(self, key, value):
		assert isinstance(value, NUMTYPE)

		if key == 0: self.x = int(value)
		elif key == 1: self.y = int(value)
		else: raise KeyError

	def __len__(self):
		return 2

	def __nonzero__(self):
		return self.x != 0 or self.y != 0

	def __add__(self, other):
		if isinstance(other, P):
			return P(self.x + other.x, self.y + other.y)
		elif isinstance(other, S):
			return R(self.x, self.y, other.w, other.h)
		raise TypeError

	def rand(self, xmin, xmax, ymin, ymax):
		self.x = random.randint(xmin, xmax)
		self.y = random.randint(ymin, ymax)


class S(object):
	def __init__(self, w=0, h=0):
		assert isinstance(w, NUMTYPE)
		assert isinstance(h, NUMTYPE)

		self.w = int(w)
		self.h = int(h)

	def __str__(self):
		return "S(%d,%d)" % (self.w, self.h)

	def __iter__(self):
		yield self.w
		yield self.h

	def __getitem__(self, key):
		if key == 0: return self.w
		elif key == 1: return self.h
		else: raise KeyError

	def __setitem__(self, key, value):
		assert isinstance(value, NUMTYPE)

		if key == 0: self.w = int(value)
		elif key == 1: self.h = int(value)
		else: raise KeyError

	def __len__(self):
		return 2

	def __nonzero__(self):
		return self.w != 0 or self.h != 0

	def __add__(self, other):
		if isinstance(other, P):
			return R(other.x, other.y, self.w, self.h)
		elif isinstance(other, S):
			return S(self.w + other.w, self.h + other.h)
		raise TypeError

	def rand(self, wmin, wmax, hmin, hmax):
		self.w = random.randint(wmin, wmax)
		self.h = random.randint(hmin, hmax)




class R(object):
	x2 = property(lambda self: self.w-self.x)
	y2 = property(lambda self: self.h-self.y)
	p = property(lambda self: P(self.x, self.y))
	s = property(lambda self: S(self.w, self.h))

	def __init__(self, x=0, y=0, w=0, h=0):
		assert isinstance(x, NUMTYPE)
		assert isinstance(y, NUMTYPE)
		assert isinstance(w, NUMTYPE)
		assert isinstance(h, NUMTYPE)

		self.x = int(x)
		self.y = int(y)
		self.w = int(w)
		self.h = int(h)

	def __str__(self):
		return "R(%d,%d,%d,%d)" % (self.w, self.h, self.w, self.h)

	def __iter__(self):
		yield self.x
		yield self.y
		yield self.w
		yield self.h

	def __getitem__(self, key):
		if key == 0: return self.x
		elif key == 1: return self.y
		elif key == 2: return self.w
		elif key == 3: return self.h
		else: raise KeyError

	def __setitem__(self, key, value):
		assert isinstance(value, NUMTYPE)

		if key == 0: self.x = int(value)
		elif key == 1: self.y = int(value)
		elif key == 2: self.w = int(value)
		elif key == 3: self.h = int(value)
		else: raise KeyError

	def __len__(self):
		return 4

	def __nonzero__(self):
		return self.x != 0 or self.y != 0 or self.w != 0 or self.h != 0

	def __add__(self, other):
		if isinstance(other, P):
			return R(self.x + other.x, self.y + other.y, self.w, self.h)
		if isinstance(other, S):
			return R(self.x, self.y, self.w + other.w, self.h + other.h)
		if isinstance(other, R):
			return R(self.x + other.x, self.y + other.y, self.w + other.w, self.h + other.h)
		raise TypeError


class L(object):
	def __init__(self, min=0, max=0):
		assert isinstance(min, NUMTYPE)
		assert isinstance(max, NUMTYPE)

		self.min = int(min)
		self.max = int(max)

	def __str__(self):
		return "L(%d,%d)" % (self.min, self.max)

	def __iter__(self):
		yield self.min
		yield self.max

	def __getitem__(self, key):
		if key == 0: return self.min
		elif key == 1: return self.max
		else: raise KeyError

	def __setitem__(self, key, value):
		assert isinstance(value, NUMTYPE)

		if key == 0: self.min = int(value)
		elif key == 1: self.max = int(value)
		else: raise KeyError

	def __len__(self):
		return 2

	def __nonzero__(self):
		return self.min != 0 or self.max != 0

	def __add__(self, other):
		if isinstance(other, L):
			return L(self.min + other.min, self.max + other.max)
		raise TypeError

	def rand(self, amin, amax, bmin, bmax):
		self.min = random.randint(amin, amax)
		self.max = random.randint(bmin, bmax)

	def contains(self, other):
		if isinstance(other, P):
			return other.x >= self.min and other.x <= self.max and other.y >= self.min and other.y <= self.max
		elif isinstance(other, S):
			return other.w >= self.min and other.w <= self.max and other.h >= self.min and other.h <= self.max
		elif isinstance(other, R):
			return other.x >= self.min and other.x+other.w <= self.max and other.y >= self.min and other.y+other.h <= self.max
		raise TypeError


class Layout(object):
	def __init__(self, pos=P(0,0), off=S(0,0)):
		assert isinstance(pos, P)
		assert isinstance(off, S)

		self.pos = pos
		self.off = off

		self.it = self.__iter__()

	def __getitem__(self, key):
		assert isinstance(key, (int, long))

		if not self.off: return self.pos
		return P(self.pos.x+self.off.w*key, self.pos.y+self.off.h*key)

	def __iter__(self):
		x, y = self.pos
		w, h = self.off

		while True:
			yield P(x, y)
			x += w
			y += h

	def next(self):
		try: return self.it.next()
		except StopIteration: pass

		self.it = self.__iter__()
		return self.it.next()

