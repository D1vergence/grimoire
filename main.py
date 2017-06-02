import pygame
from pygame.locals import *
import random
import pickle
import copy
import os

import config
config.server_mode=True

rd = random.randint
from tool import *

import map
import unit
import effect
import ev
import server
import ctrl
import model


if __name__=='__main__':
    os.system('title 服务器')
    print('The server is on.')
    clock = pygame.time.Clock()
    
    while True:
        model.model_pool_bk=copy.copy(model.model_pool)
        model.model_pool=[]

        time_passed = clock.tick() / 1000
        if time_passed>0.03:
            time_passed=0.03 #保证刷新均匀
        time_log(time_passed)
        
        map.time_pass(time_passed)

        for i in unit.unit_pool:
            i.time_pass(time_passed)
        de(unit.unit_pool, lambda i: not i.iki)

        server.pickle_model = pickle.dumps(model.model_pool_bk)
