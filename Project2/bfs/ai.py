from copy import deepcopy
from typing import List

class Node:

    def __init__(self, score, cost, action, parent, snake_body):
        self.score = score
        self.cost = cost
        self.action = action
        self.parent = parent
        self.snake_body = snake_body
        self._children = []

    def add_child(self, node):
        self._children.append(node)

    def is_root(self):
        return self.parent is None

    def get_children(self):
        return deepcopy(self._children)

    def __str__(self):
        return f'{self.action, self.snake_body}'

    def __repr__(self):
        return str(self)


class Agent:
    def __init__(self, perceive_func=None, agent_id=None):
        self.perceive_func = perceive_func
        self.my_id = agent_id
        self.prev_action = ''
        self.win_score = 0
        self.food_score_multi = 0
        self.food_add_score = 0
        self.turning_cost = 0

    def act(self):
        sensor_data = self.perceive_func(self)

        agent_body = sensor_data['agent body']
        food_map = sensor_data['map']
        score = sensor_data['score']
        cost = sensor_data['cost']
        env = sensor_data['Current_Env']
        self.food_score_multi = env.state.foodScoreMulti
        self.food_add_score = env.state.foodAddScore
        self.win_score = env.state.winScore
        self.turning_cost = env.state.turningCost
        snake = env.state.agent_list[0]
        snake_shekam = snake.shekam
        prev_action = self.prev_action
        root = self.create_tree(food_map, score, cost, agent_body, 5, prev_action, snake_shekam, None)
        print('tree created')
        return self.get_best(root)

    def create_tree(self, food_map: List[List[int]], score: int, cost: int, agent_body: List[List[int]],
                    depth: int, prev_action: str, shekam, parent) -> Node:
        max_x, max_y = len(food_map), len(food_map[0])
        root = Node(score, cost, prev_action, parent, agent_body)
        if depth != 0:
            action_list = ['right','left','up','down']
            for action in action_list:
                flag = True
                head = agent_body[-1]
                tmp = (0, 0)
                if action == 'right':
                    tmp = (0, 1)
                elif action == 'left':
                    tmp = (0, -1)
                elif action == 'up':
                    tmp = (-1, 0)
                else:
                    tmp = (1, 0)
                new_head = [head[0] + tmp[0], head[1] + tmp[1]]
                if new_head[0] < 0 or new_head[0] == max_x or new_head[1] < 0 or new_head[1] == max_y:
                    flag = False
                if shekam != 0:
                    if new_head in agent_body:
                        flag = False
                else:
                    if new_head in agent_body[1:]:
                        flag = False
                if flag:
                    body, new_score, new_shekam = self._get_news(action, food_map, agent_body, score, prev_action,shekam)
                    child = self.create_tree(food_map, new_score, cost + 1, body, depth - 1, action, new_shekam, root)
                    root.add_child(child)
        return root

    def _get_news(self, action, food_map, agent_body, score, prev_action, shekam):
        head = agent_body[-1]
        tmp = (0,0)
        if action =='right':
            tmp = (0, 1)
        elif action =='left':
            tmp = (0, -1)
        elif action =='up':
            tmp = (-1, 0)
        else :
            tmp = (1, 0)
        new_head = [head[0] + tmp[0], head[1] + tmp[1]]
        new_body = deepcopy(agent_body)
        new_body.append(new_head)
        if shekam == 0:
            del new_body[0]
            if len(new_body) != 1:
                del new_body[0]
        new_shekam = shekam
        new_score = score
        if shekam == 0:
            if len(new_body) == 1:
                new_score = score + self.food_add_score + self.food_score_multi * food_map[new_head[0]][new_head[1]]
                new_shekam = food_map[new_head[0]][new_head[1]]
        else:
            new_shekam = shekam - 1
        if action != prev_action:
            new_score -= self.turning_cost
        return new_body, new_score, new_shekam

    def get_best(self, root: Node):
        queue = [root]
        max_score, best_move = -1, ''
        while len(queue) > 0:
            node = queue.pop(0)
            queue.extend(node.get_children())
            if node.score >= self.win_score:
                best_move = self._get_root_move(node)
                break
            if node.score > max_score:
                max_score = node.score
                best_move = self._get_root_move(node)
        if best_move != '':
            return best_move
        else:
            return 'down'
    def _get_root_move(self, node):
        if node.parent is None:
            return node.action
        if node.parent.is_root():
            return node.action
        return self._get_root_move(node.parent)
