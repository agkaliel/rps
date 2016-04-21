import random

def changeStates(state):
	if state == 0:
		return random.randint(0,1)
	if state == 1:
		return random.randint(0,2)
	if state == 2:
		return 0


if __name__ == "__main__":
	counter = [0,0,0]
	state = 0
	for i in range(1000000):
		state = changeStates(state)	
		counter[state] = counter[state] + 1
	print(counter)
	print([x / sum(counter) for x in counter])



