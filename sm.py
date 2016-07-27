import pygame
import math

from lib import typ, com, trig, test, hex


SCREEN_SIZE = (640,300)
COLOR_BACKGROUND = (255,255,255)
EVENT_TIMER_1 = pygame.USEREVENT+1

# init
pygame.mixer.pre_init(44100, -16, 2, 512) # must come before pygame.init()!
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(10)
screen = pygame.display.set_mode(SCREEN_SIZE, pygame.DOUBLEBUF, 32)
pygame.display.set_caption("sm")
pygame.time.set_timer(EVENT_TIMER_1, 1000)


def Main():

	ht = [
		test.HexTest1(),
		test.HexTest2(),
	]
	hi = 1
	
	while True:
		event = pygame.event.wait()
		
		if event.type == pygame.QUIT:
			break
			
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				break
				
		elif event.type == pygame.MOUSEBUTTONDOWN:
		
			if event.button == 2:
				hi = (hi + 1) % len(ht)
				
			elif event.button == 4:
				hi = min(hi + 1, len(ht)-1)
				
			elif event.button == 5:
				hi = max(0, hi - 1)
				
		elif event.type == pygame.MOUSEMOTION:
			ht[hi].onMouseMotion(event.pos)
			
		elif event.type == EVENT_TIMER_1:
			pass
		
		screen.fill(COLOR_BACKGROUND)
		
		ht[hi].onDraw(screen)
		
		pygame.display.update()


if "__main__" == __name__:
	Main()
	
