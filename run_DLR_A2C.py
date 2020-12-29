from stable_baselines3 import A2C
import gym_interceptor


def run_a2c(env_id):
    model = A2C("MlpPolicy", env_id, seed=0, policy_kwargs=dict(net_arch=[16]), verbose=1, create_eval_env=True)
    model.learn(total_timesteps=1000, eval_freq=500)


if __name__ == '__main__':
    run_a2c(env_id='interceptor-v0')