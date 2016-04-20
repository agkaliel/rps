"""Simple experiment runner for a Rock-Paper-Scissors Tournament.

Will have to import all the agent libraries, and then
"""
from rps_match import *
from agents import *
import os
from pandas import DataFrame
import pandas as pd
from itertools import combinations_with_replacement
import time

import agents # import default agent library
# import tournament agent libraries

# TODO: dynamically load agents
# specify the agents to actually run in the tournament
agents = [NashAgent, StubbornAgent, 
          MirrorAgent, CounterAgent, ScaredyAgent,
          BryanDualMarkovAgent1, BryanSelfMarkovAgent2,
          BryanMarkovAgent2, BryanSelfMarkovAgent1, BryanMarkovAgent1]



num_games = 1000000
time_limit = 36000 # ten minutes per match NOT IMPLEMENTED

# TODO: all the stuff to make this work
# TODO: figure out how to handle slow agents (remove from results? count as losses?)
# TODO: submit jobs 
# TODO: save results files for each pair with seed


def results_file_name(a1, a2):
    """
    Standardize filename construction for results files.
    
    Note that the order a1 a2 matters.
    """
    vs_str = "_vs_"
    return "results/{1}{0}{2}.txt".format(vs_str, a1, a2)

def extract_agent_names(filename):
    """
    Get the names of the participating agents from a results file name.
    Return as 2-element string tuple.
    Return an empty tuple if the filename is not formatted correctly
    """
    try:
        (root, ext) = os.path.splitext(filename)
        return root.split(vs_str)
    except:
        return ()

def check_for_results(a1, a2):
    """
    Return the path to the results file if it exists 
    None if there are no matches
    
    TODO: expand this so it can hold multiple results details
    and check for matching seed/num_trials
    """
    fn = results_file_name(a1, a2)
    if os.path.exists(fn):
        return fn
    fn = results_file_name(a2, a1)
    if os.path.exists(fn):
        return fn
    
    

def save_results(agent1, agent2, w1, w2, total_trials, seed):
    with open(results_file_name(agent1, agent2), 'a') as f:
        f.write("{0} {1} {2} {3}\n".format(w1, w2, total_trials, seed))
        return True

def load_results():
    """
    Read through the results directory to get all the completed matches.
    """
    results = {}
    for f in os.listdir("results"):
        (a1, a2) = extract_agent_name(f)
        # make sure we got some names
        if not a1:
            continue
        
        with open("results/"+f, 'r') as r:
            (w1, w2, total_trials, seed) = f.readline().split()
            results[f] = {'a1': a1,
                          'a2': a2,
                          'w1': w1,
                          'w2': w2,
                          'n': num_trials,
                          'seed': seed}
    return results

def run_all_agents(agents, redo=False, num_games=num_games):
    """
    For every pairing of agents (including vs itself), run a match of num_games. 
    If redo is False only run matches which do not already have results files.
    
    TODO: implement time limit
    """
    agents.sort(key=str)
    matches = combinations_with_replacement(agents, 2)
    
    seed = int(time.mktime(datetime.now().timetuple()))

    for (a1, a2) in matches:
        agent1 = a1()
        agent2 = a2()
        # TODO: this would be the place to submit jobs
        print("Setting up {} vs {}...".format(agent1, agent2), end='')
        # check if we need to run this match
        if not redo and check_for_results(agent1, agent2):
            print("already done")
            continue
        
        # TODO: this would be the place to time things
        # yup, we're good to go
        # set the seed
        random.seed(seed)
        (w1, w2) = runner(agent1, agent2, num_trials=num_games)

        print("{0}: {1:.1f}%, {2}: {3:.1f}%".format(agent1, 100.0*w1//num_games,
                                                agent2, 100.0*w2//num_games))
        if(save_results(agent1, agent2, w1, w2, num_games, seed)):
            print(" saved.")
        else:
            print("PROBLEM SAVING.")
        
        seed = random.getrandbits(8)
    print("DONE MATCHES")
        

def human_vs_bots(agents, num_games=15, seed=None):
    """
    Randomly select an opponent from the agents list and (without telling)
    set up a Command-Line Match with num_games rounds.
    """
    name = input("Enter your name: ")
    player1 = CommandLineAgent(name=name)
    print(name, "is Player 1")
    
    player2 = None
    while not player2:
        bot = input("Enter an opponent (empty for random): ")    
        if not bot:
            player2 = random.choice(agents)()
            print("Player 2 is a surprise!")
        else:
            poss = [a for a in agents if bot.lower() in a._name().lower()]
            if len(poss) == 0:
                print("Sorry, I did not recognize that bot.")
            elif len(poss) == 1:
                player2 = poss[0]()
                print(str(player2), "is Player 2")
            else:
                print("You need to be more specific. Did you mean:")
                for a in poss:
                    print(a._name())
        
    # set up match
    if seed is None:
        seed = int(time.mktime(datetime.now().timetuple()))

    random.seed(seed)

    (w1, w2) = runner(player1, player2, num_trials=num_games, verbose=False)
    winner = None
    if w1 > w2:
        winner = str(player1)
    elif w2 > w1:
        winner = name
    if winner:
        print("Tournament final: {}-{} with a win for {}".format(w1, w2, winner))
    else:
        print("Tournament ends with a {}-{} draw!".format(w1, w2))        
    
    if(save_results(player1, "CommandLine."+name, w1, w2, num_games, seed)):
        print("Recording for posterity!")
    else:
        print("Recording fail.")
     

if __name__ == "__main__":
    #run_all_agents(agents, redo=True)
    human_vs_bots(agents)