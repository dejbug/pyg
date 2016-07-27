import pygame
import collections


Point = collections.namedtuple("Point", "x y")
Rect = pygame.Rect


def enumerateGridCells(cols, rows):
	for row in xrange(rows):
		for col in xrange(cols):
			yield (col, row)


class GridList(object):
	def __init__(self, cols, rows):
		self.cols, self.rows = cols, rows
		self.data = []
		
	def __iter__(self):
		return self.data.__iter__()
		
	def __getitem__(self, index):
		return self.data[index]
		
	def append(self, obj):
		self.data.append(obj)
		
	def geti(self, index):
		return self.data[index]
		
	def get(self, col, row):
		index = self.cell2index(col, row)
		return self.data[index]
		
	def cell2index(self, col, row):
		return row * self.cols + col
		
	def index2cell(self, index):
		return (index % self.cols, index / self.cols)
		
