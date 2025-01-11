from stable_baselines3 import PPO, A2C, DQN
from sb3_contrib import RecurrentPPO, QRDQN, ARS
import os

# from SB_Crypto_env import CryptoEnv
from HeliAttack2_ENV import HeliAttackEnv
    
# Global consts for training
SAVE_MODEL = True
TIMESTEPS = 100000

# Naming Convention
# "Model_Timeframe_data source_SHAPE_Reward Function_added observations_#itteration"
model_name = "PPO_HeliAttack2_8"
models_dir = f"models/{model_name}"
logdir = "logs"


if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(logdir):
    os.makedirs(logdir)

# Create the environment
env = HeliAttackEnv()

# Required before you can step the environment
#env.reset()

# Models
model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=logdir)
# model = RecurrentPPO("MlpLstmPolicy", env, verbose=1, tensorboard_log=logdir)

# Timesteps
model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name= model_name)
model.save(f"{models_dir}/{model_name}")

env.close()

#tensorboard --logdir=logs