import gymnasium as gym
import numpy as np
from gymnasium import spaces
import keyboard
# from collections import deque
# import keras

import csv

# Convert Observation space into floats
# Return as np array
# def str_to_float(data_list):
#     return np.array([float(i) for i in data_list])

WIDTH = 563
HEIGHT = 378

class CryptoEnv(gym.Env):
    """Custom Environment that follows gym interface."""

    def __init__(self):
        super().__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(3)
        # Example for using image as input (channel-first; channel-last also works):
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(3, WIDTH, HEIGHT), dtype=np.uint8)
        
    # ACTIONS
    # 0 - Left
    # 1 - Right
    # 2 - Jump
    # 3 - Duck
    # 4 - Mouse Left
    # 5 - Mouse Right
    def step(self, action):
        info = {}
        
        
        return self.observation, self.reward, self.done, self.truncated, info

    def reset(self, seed=None, options=None):
        info = {}
        

        return self.observation, info

    # Close File
    def close(self):
        self.file.close()