import logging
import numpy as np
from mjrl.utils.get_environment import get_environment
from mjrl.utils import tensor_utils
logging.disable(logging.CRITICAL)


# Single core rollout to sample trajectories
# =======================================================
def do_rollout(N,
    policy,
    T=1e6,
    env=None,
    env_name=None,
    base_seed=None):
    """
    params:
    N               : number of trajectories
    policy          : policy to be used to sample the data
    T               : maximum length of trajectory
    env             : env object to sample from
    env_name        : name of env to be sampled from 
                      (one of env or env_name must be specified)
    base_seed       : seed for environment
    """

    if env_name is None and env is None:
        print("No environment specified! Error will be raised")
    if env is None: env = get_environment(env_name)
    if base_seed is not None: env.set_seed(base_seed)
    T = min(T, env.horizon)

    paths = []

    for ep in range(N):

        # Set seed (can be different for env and numpy)
        # Setting seed at a trajectory level ensures compatibility between different number of cores
        if base_seed is not None:
            seed = base_seed + ep
            env.set_seed(seed)
            np.random.seed(seed)
        else:
            np.random.seed()

        observations=[]
        actions=[]
        rewards=[]
        agent_infos = []
        env_infos = []

        o = env.reset()
        done = False
        t = 0

        while t < T and done != True:
            a, agent_info = policy.get_action(o)
            next_o, r, done, env_info = env.step(a)
            observations.append(o)
            actions.append(a)
            rewards.append(r)
            agent_infos.append(agent_info)
            env_infos.append(env_info)
            o = next_o
            t += 1

        path = dict(
            observations=np.array(observations),
            actions=np.array(actions),
            rewards=np.array(rewards),
            agent_infos=tensor_utils.stack_tensor_dict_list(agent_infos),
            env_infos=tensor_utils.stack_tensor_dict_list(env_infos),
            terminated=done
        )

        paths.append(path)

    del(env) # flush RAM
    return paths

def do_rollout_star(args_list):
    return do_rollout(*args_list)
