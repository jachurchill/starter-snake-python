import bottle
import os
import random
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

from api import *

@bottle.route('/')
def static():
  return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
  return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
	data = bottle.request.json
	# TODO: Do things with data
	print(json.dumps(data))

	return StartResponse("#FF1493")


@bottle.post('/move')
def move():
	data = bottle.request.json
	current_pos = data['you']['body'][0]
	board = data['board']
	MAX_HEIGHT = board['height']
	MAX_WIDTH = board['width']

	current_grid = [[3 for x in range(MAX_WIDTH)] for y in range(MAX_HEIGHT)] 
	# for x in range(0, MAX_HEIGHT):
	# 	for y in range(0, MAX_HEIGHT):
	# 		current_grid[x][y] = 3

	foods = {}
	distances = []
	for food in board['food']:
		current_grid[food['y']][food['y']] = 2
		distance = abs(food['y'] - current_pos['y']) + abs(food['x'] - current_pos['x'])
		if food['x'] == 0 or food['x'] == MAX_WIDTH-1:
			distance += MAX_WIDTH
		if food['y'] == 0 or food['y'] == MAX_HEIGHT-1:
			distance += MAX_HEIGHT
		foods[distance] = (food['x'], food['y'])
		distances.append(distance)
	distances = sorted(distances, reverse=True)

	for snake in board['snakes']:
		y = snake['body'][0]['y']
		x = snake['body'][0]['x']
		if len(snake['body']) < len(data['you']['body']):
			if y < MAX_HEIGHT-1:
				current_grid[y+1][x] = 1
			if y > 0:
				current_grid[y-1][x] = 1
			if x < MAX_WIDTH-1:
				current_grid[y][x+1] = 1
			if x > 0:
				current_grid[y][x-1] = 1
		elif snake['body'][0] != data['you']['body'][0]:
			if y < MAX_HEIGHT-1:
				current_grid[y+1][x] = 10
			if y > 0:
				current_grid[y-1][x] = 10
			if x < MAX_WIDTH-1:
				current_grid[y][x+1] = 10
			if x > 0:
				current_grid[y][x-1] = 10
		for segment in snake['body']:
			current_grid[segment['y']][segment['x']] = 0

	for segment in data['you']['body']:
		current_grid[segment['y']][segment['x']] = 0

	current_grid[current_pos['y']][current_pos['x']] = 3
	print 'Current Grid: '
	for grid_row in current_grid:
		print grid_row
	grid = Grid(matrix=current_grid)
	start = grid.node(current_pos['x'], current_pos['y'])
	finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
	while distances:
		target = foods[distances.pop()]
		end = grid.node(target[0], target[1])
		path, runs = finder.find_path(start, end, grid)
		print(grid.grid_str(path=path, start=start, end=end))
		print 'Current Position: {0}'.format(current_pos)
		print 'Closest Food: {0}'.format(target)
		print 'Path: {0}'.format(path)
		if path and path[1][0] != current_pos['x']:
			direction = 'left' if path[1][0] < current_pos['x'] else 'right'
			break
		elif path and path[1][1] != current_pos['y']:
			direction = 'up' if path[1][1] < current_pos['y'] else 'down'
			break
	else:
		print 'Making Random Choice'
		directions = ['up', 'down', 'left', 'right']
		if current_pos['x'] == 0 or current_grid[y][x-1] == 0:
			directions.remove('left')
		if current_pos['x'] == MAX_WIDTH-1 or current_grid[y][x+1] == 0:
			directions.remove('right')
		if current_pos['y'] == 0 or current_grid[y-1][x] == 0:
			directions.remove('up')
		if current_pos['y'] == MAX_HEIGHT-1 or current_grid[y+1][x] == 0:
			directions.remove('down')
		direction = random.choice(directions)
	print 'Direction: {0}'.format(direction)
	return MoveResponse(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    # TODO: Any cleanup that needs to be done for this game based on the data
    print json.dumps(data)


@bottle.post('/ping')
def ping():
    return "Alive"


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=True)
