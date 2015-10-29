import pygame
pygame.mixer.init()
pygame.mixer.music.load("Left.wav")
pygame.mixer.music.play()
while pygame.mixer.music.get_busy() == True:
    continue
pygame.mixer.music.load("Right.wav")
pygame.mixer.music.play()
while pygame.mixer.music.get_busy() == True:
    continue
pygame.mixer.music.load("Stop.wav")
pygame.mixer.music.play()
while pygame.mixer.music.get_busy() == True:
    continue
pygame.mixer.music.load("Move.wav")
pygame.mixer.music.play()
while pygame.mixer.music.get_busy() == True:
    continue