import random
from enum import IntEnum
from contextlib import suppress


verbs = {(0, 1): "covered by",
         (0, 2): "smashes",
         (1, 0): "covers",
         (1, 2): "cut by",
         (2, 0): "smashed by",
         (2, 1): "cuts"}


def score(a1, a2, verbose=False):
    """
    Return the score for a rock-paper-scissors game.
    If verbose, display a message
    
    >>> score(Action.r, Action.r)
    0
    >>> score(Action.r, Action.r, verbose=True)
    ROCK ties ROCK: No win!
    0
    >>> score(Action.p, Action.r, True)
    PAPER covers ROCK: Player 1 wins!
    1
    >>> score(Action.s, Action.r, True)
    SCISSORS smashed by ROCK: Player 2 wins!
    -1
    >>> score(0, 1)
    -1
    """
    result = 0
    if a1 == a2:
        if verbose:
            print("{} ties {}: No win!".format(a1.name, a2.name))
        return result

    # if parity is the same, lower value wins
    if a1 % 2 == a2 % 2:
        result = 1 if a1 < a2 else -1
    else:     # if parity is different, higher value wins
        result = 1 if a1 > a2 else -1
        
    if verbose:
        winner = 1 if result > 0 else 2
        print("{} {} {}: Player {} wins!".format(a1.name,
                                                 verbs[(a1, a2)],
                                                 a2.name, 
                                                 winner))
    return result
          


class Action(IntEnum):
    ROCK = 0
    PAPER = 1
    SCISSORS = 2
    # aliases
    r = 0
    p = 1
    s = 2
    R = 0
    P = 1
    S = 2
    rock = 0
    paper = 1
    scissors = 2

class RPSAgent():
    """
    Interface for a generic Rock-Paper-Scissors agent.
    """
    
    def __init__(self):
        """
        Whatever setup you might need to do for a match, do here.
        """
        pass
    
    def act(self):
        """
        And however you might want to act, do it here.
        Must return an Action.
        """
        return Action.r
    
    def react(self, response):
        """
        And respond however you would like to the action taken by 
        the other player. Nothing returned.
        """
        pass
    
    def __str__(self):
        """
        Return a nicely formatted name
        """
        return self.__class__.__name__
    
    @classmethod
    def _name(cls):
        """
        Convenience for logging
        """
        return cls.__name__
          
    
class MyAgent(RPSAgent):
    def __init__(self):
        """
        Whatever setup you might need to do for a match, do here.
        """

        #The number of recent moves to store in memory
        self.memory = 100
        #The recent moves the opponent has made
        self.oppRecent = []
        #The recent moves I have made
        self.myRecent = []
        #The "mode" that we are currently in
        self.mode = "nash"
        pass
    
    def act(self):
        """
        And however you might want to act, do it here.
        Must return an Action.
        """
        action = Action.r #set rock as the defaul action
        self.checkScaredy()
        self.checkStubborn()
        self.checkSelfCounter()
        self.checkMirror()
        self.checkCounter()

        if len(self.myRecent) > 1:
        #any time no action is set, rock is returned

            if self.mode == "counter":
                if self.myRecent[-1] == Action.s:
                    action = Action.p
                elif self.myRecent[-1] == Action.r:
                    action = Action.s

            elif self.mode == "selfCounter":
                if self.oppRecent[-1] == Action.s:
                    action = Action.p
                elif self.oppRecent[-1] == Action.r:
                    action = Action.s

            elif self.mode == 'stubborn':
                if self.oppRecent[-1] == Action.r:
                    action = Action.p
                elif self.oppRecent[-1] == Action.p:
                    action = Action.s

            elif self.mode == 'mirror':
                if len(self.myRecent) > 0:
                    if self.myRecent[-1] == Action.r:
                        action = Action.p
                    elif self.myRecent[-1] == Action.p:
                        action = Action.s

            elif self.mode == 'scaredy':
                prevResult = self.beats(self.oppRecent[-1], self.myRecent[-1])
                if prevResult: #if we just lost
                    if self.oppRecent[-1] == Action.p:
                        action = Action.s
                    elif self.oppRecent[-1] == Action.r:
                        action = Action.p
                else: #if we just won
                    if self.oppRecent[-1] == Action.s:
                        action = Action.p
                    elif self.oppRecent[-1] == Action.r:
                        action = Action.s

            else: #We are playing a Nash Agent, or oppRecent is not filled yet
                mostCommon = self.mostCommon() #get the most common action from oppRecent
                if mostCommon == Action.p:
                    action = Action.s
                elif mostCommon == Action.r:
                    action = Action.p

        self.myRecent.append(action)
        if len(self.myRecent) > self.memory:
            self.myRecent.pop(0)
        return action

    #returns the most common action in oppRecent
    def mostCommon(self):
        count = [0,0,0]
        for move in self.oppRecent:
            if move == Action.r:
                count[0] = count[0] + 1
            if move == Action.p:
                count[1] = count[1] + 1
            if move == Action.s:
                count[2] = count[2] + 1
        biggest = count.index(max(count))
        if biggest == 0:
            return Action.r
        elif biggest == 1:
            return Action.p
        else:
            return Action.s
    
    def checkStubborn(self):
        if len(self.oppRecent) >= self.memory:
            stubborn = True
            first = self.oppRecent[0]
            for i in range(1,len(self.oppRecent)):
                if first != self.oppRecent[i]:
                    stubborn = False
            if stubborn == True:
                self.mode = "stubborn"


    def checkSelfCounter(self):
        if len(self.oppRecent) >= self.memory:
            selfCounter = True
            for i in range(len(self.oppRecent)-1):
                if self.beats(self.oppRecent[i+1], self.oppRecent[i]) == False:
                    selfCounter = False
            if selfCounter:
                self.mode = "selfCounter"

    def checkMirror(self):
        if len(self.oppRecent) >= self.memory:
            mirror = True
            for i in range(1, len(self.oppRecent)):
                if self.oppRecent[i] != self.myRecent[i-1]:
                    mirror = False
            if mirror:
                self.mode = "mirror"

    def checkCounter(self):
        if len(self.oppRecent) >= self.memory:
            counter = True
            for i in range(len(self.oppRecent)-1):
                if self.beats(self.oppRecent[i+1], self.myRecent[i]) == False:
                    counter = False
            if counter:
                self.mode = "counter"

    def checkScaredy(self):
        if len(self.oppRecent) >= self.memory:
            scaredy = True
            for i in range(len(self.oppRecent)-1):
                prevResult = self.beats(self.oppRecent[i], self.myRecent[i])
                if prevResult:
                    if self.oppRecent[i+1] != self.oppRecent[i]:
                        scaredy = False
                else:
                    if self.oppRecent[i+1] == self.oppRecent[i]:
                        scaredy = False
            if scaredy:
                self.mode = "scaredy"


    def beats(self, first, second):
        if first == Action.r and second == Action.s:
            return True
        elif first == Action.s and second == Action.p:
            return True
        elif first == Action.p and second == Action.r:
            return True
        else:
            return False

    def react(self, response):
        """
        And respond however you would like to the action taken by 
        the other player. Nothing returned.
        """
        self.oppRecent.append(response)
        if len(self.oppRecent) > self.memory:
            self.oppRecent.pop(0)
        pass
    
    def __str__(self):
        """
        Return a nicely formatted name
        """
        return self.__class__.__name__   

class CommandLineAgent(RPSAgent):
    """
    Allows humans to play in the bot tournaments. Prompts user for action 
    selection at each round. Does not cheat.
    """
    def __init__(self, actions="[r]ock, [p]aper, [s]cissors", name=None):
        self.actions = actions
        self.name = name
        self.choice = None
        pass

        
    def act(self):
        choice = None
        while choice is None:
            choice = input("Select action {}: ".format(self.actions))
            try:
                choice = Action[choice]
            except KeyError:
                # one last try
                with suppress(ValueError):
                    choice = Action(int(choice))
                    self.choice = choice
                    return choice
                
                # okay, this is not a choice
                print("{} is not a valid action".format(choice))
                choice = None
        self.choice = choice
        return choice
    
    def react(self, response):
        score(self.choice, response, verbose=True)

    
class StubbornAgent(RPSAgent):
    """
    Choose an action at the start and stick to it.
    """
    def __init__(self, action=None):
        if action is None:
            action = random.choice(list(Action))
        self.action = action
            
    def act(self):
        return self.action

    
class NashAgent(RPSAgent):
    """
    Uniformly randomly choose an action each time, ignoring
    opponent actions.
    """
    def __init__(self):
        self.actions = list(Action)
    
    def act(self):
        return random.choice(self.actions)
        

class MirrorAgent(RPSAgent):
    """
    Randomly choose your first action, then always choose the action
    the opponent chose last time
    """
    def __init__(self):
        self.action = random.choice(list(Action))
        
    def act(self):
        return self.action

    def react(self, response):
        self.action = response


class ScaredyAgent(RPSAgent):
    """
    Randomly chooses a first action, then keep doing it as long as it wins, otherwise 
    randomly switch to one of the other two.
    """
    def __init__(self):
        self.action = random.choice(list(Action))
    
    def act(self):
        return self.action
    
    def react(self, response):
        result = score(self.action, response)

        # if we won, keep doing the same thing.
        if result > 0:
            return
        # otherwise we need to choose a new action
        options = list(Action)
        
        # if we tied, randomly choose from everything
        if result == 0:
            self.action = random.choice(options)
        else: # choose anything but what you just did
            options.remove(self.action)
            self.action = random.choice(options)
            
        

class CounterAgent(RPSAgent):
    """
    Randomly choose your first action, then always choose the next action
    that would have beaten the opponent's last action
    """
    def __init__(self):
        self.action = random.choice(list(Action))
        
    def act(self):
        return self.action
    
    def react(self, response):
        action = (response + 1) % len(Action)
        self.action = Action(action)
        
class SelfCounterAgent(RPSAgent):
    """
    Randomly choose your first action, then always choose the next action
    that would have beaten your last action
    """
    def __init__(self):
        self.action = random.choice(list(Action))
        
    def act(self):
        return self.action
    
    def react(self, response):
        response = (self.action + 1) % len(Action)
        self.action = Action(response)
    
  
##########################################
## STUDENT AGENTS
##########################################

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    print("Done tests")
    