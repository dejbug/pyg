
import pygame
import collections, math, re, os.path

import lib.pyg
from lib.geom import P,S,R,L


def Drawable(cls):
	def draw(self, surface=None):
		if None == surface:
			surface = pygame.display.get_surface()

		self.onDraw(surface)

	def onDraw(self, surface):
		raise NotImplementedError

	if not hasattr(cls, "draw"):
		setattr(cls, "draw", draw)

	if not hasattr(cls, "onDraw"):
		setattr(cls, "onDraw", onDraw)

	return cls


@Drawable
class TextBox(object):
	def __init__(self, px=24, pos=P(10,10), span=P(30,5), drawGrid=True, drawBorder=True,
		text=""):
		self.text = text
		self.px = px # character height in pixels
		self.pos = pos
		self.span = span
		self.border = 1
		self.cellcount = self.span.x * self.span.y
		self.drawGrid = drawGrid
		self.drawBorder = drawBorder

		self.font = pygame.font.SysFont("Courier New", self.px)

		self.cs = S(*self.font.size("X"))
		self.cs.h = self.font.get_linesize()

		self.size = S(self.span.x * self.cs.w, self.span.y * self.cs.h)
		self.rect = self.pos + (self.size + S(1,1))

		self.fg = pygame.Color("black")
		self.bg = pygame.Color("white")
		self.gc = pygame.Color("light grey")

	def onDraw(self, surf):
		if self.drawGrid:
			x, y = self.pos
			for i in xrange(self.span.x+1):
				pygame.draw.aaline(surf, self.gc, (x,y), (x,y+self.size.h))
				x += self.cs.w

			x, y = self.pos
			for i in xrange(self.span.y+1):
				pygame.draw.aaline(surf, self.gc, (x,y), (x+self.size.w,y))
				y += self.cs.h
		
		elif self.drawBorder:
			pygame.draw.rect(surf, self.gc, self.rect, self.border)


		x, y = self.pos
		b, e = 0, self.span.x
		
		for i in xrange(self.span.y):
			line = self.text[b:e]
			if not len(line): break
			
			img = self.font.render(line, True, self.fg)
			surf.blit(img, (x,y))
			
			b = e
			e += self.span.x
			y += self.cs.h


@lib.pyg.UserEvent
class MyAppEvent(object): pass


class MyApp(lib.pyg.App):
	def __init__(self):
		lib.pyg.App.__init__(self, pos=(20,50), size=(600,300))

		#self.setTimer("update", 1000)

		self.box = TextBox(px=18)
		self.box.text = "Hello, TextBox! " * 7

	def onDraw(self):
		self.box.draw()

	def onTimer(self, name, event):
		if name == "update":
			pass

	def onEvent(self, event):
		lib.pyg.App.onEvent(self, event)

		if event.type == MyAppEvent.TYPE:
			pass

		elif event.type == pygame.locals.KEYDOWN:
			if event.key == pygame.locals.K_F2:
				pass


if "__main__" == __name__:
	MyApp().run()

