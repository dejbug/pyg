import pygame, pygame.font


class TextOut(object):
	def __init__(self, face="Courier New", size=12):
		self.font = pygame.font.SysFont(face, size)
		
	def __call__(self, surface, pos, text, color=None):
		c = color if color else pygame.Color("black")
		s = self.font.render(text, True, c)
		surface.blit(s, pos)


def drawText(surface, font, pos, text, c=None):
	s = font.render(text, True, c if c else pygame.Color("black"))
	surface.blit(s, pos)


