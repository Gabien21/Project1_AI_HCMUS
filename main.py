import heapq
import random


class Item:
    def __init__(self, weight: int, value: int, class_item: int, state=0):
        self.weight = weight
        self.value = value
        self.class_item = class_item
        self.state = state
        self.ratio = float(self.value) / self.weight

    def print_item_info(self):
        print(
            f"Weight:{self.weight}  Value:{self.value}  Class:{self.class_item}  Ratio:{self.ratio}  State:{self.state}")

    def __lt__(self, other):
        if self.ratio == other.ratio:
            return self.weight < other.weight
        return self.ratio > other.ratio


class Node:
    def __init__(self, d: int, w: int, v: int, res: list[int], cl: list[int]):
        self.current_weight = w
        self.current_value = v
        self.upper = 0
        self.cost = 0
        self.depth = d
        self.active_class = cl
        self.res = res

    def __lt__(self, other):
        return self.cost < other.cost


class Problem:
    def __init__(self, input_file):
        self.input_file = input_file
        self.initial_item_list: list[Item] = []
        self.capacity: int = 0
        self.number_of_class = 0
        self.number_of_item = 0
        self.read_file()

    def read_file(self):
        file = open(self.input_file, "r")
        self.capacity = float(file.readline().strip("\n"))
        self.number_of_class = int(file.readline().strip("\n"))
        weight_list = file.readline().strip("\n").split(", ")
        value_list = file.readline().strip("\n").split(", ")
        class_list = file.readline().strip("\n").split(", ")
        self.number_of_item = len(weight_list)
        for i in range(self.number_of_item):
            self.initial_item_list.append(
                Item(int(weight_list[i]), int(value_list[i]), int(class_list[i])))


class BranchAndBound:
    def __init__(self, problem: Problem):
        self.problem = problem
        self.sorted_item_list: list[Item] = []
        self.class_oder: list[list[int]] = [[]
                                            for _ in range(problem.number_of_class)]
        self.get_sorted_item_list()
        '''
                for i in range(problem.number_of_item):
            print(i, end=" ")
            self.sorted_item_list[i].print_item_info()
        for i in range(problem.number_of_class):
            print("Class:", i + 1, ":", self.class_oder[i])
        '''

    def get_sorted_item_list(self):
        max_weight = max(self.problem.initial_item_list,
                         key=lambda item: item.weight).weight
        self.sorted_item_list = sorted(self.problem.initial_item_list, reverse=True,
                                       key=lambda item: (item.ratio, max_weight - item.weight))
        for i in range(self.problem.number_of_item):
            self.class_oder[self.sorted_item_list[i].class_item-1].append(i)

        '''
        res = 0
                for i in range(self.problem.number_of_class):
            min = 100
            for j in self.class_oder[i]:
                if self.sorted_item_list[j].weight < min:
                    min = self.sorted_item_list[j].weight
            res += min
        print(res)
        '''

    def upper_bound_and_cost_cal(self, node: Node):
        if node.current_weight > self.problem.capacity:
            node.current_weight -= self.sorted_item_list[node.depth].weight
            node.current_value -= self.sorted_item_list[node.depth].value
        upper_bound = node.current_value
        weight = node.current_weight
        cost = upper_bound
        for i in range(node.depth+1, self.problem.number_of_item):
            weight += self.sorted_item_list[i].weight
            if weight > self.problem.capacity:
                cost = upper_bound
                if i == 0:
                    return 100, 100
                weight -= self.sorted_item_list[i].weight
                cost += (self.problem.capacity-weight) * \
                    self.sorted_item_list[i].ratio
                break
            upper_bound += self.sorted_item_list[i].value
            cost = upper_bound
        return -upper_bound, -cost

    def check_node_2(self, node: Node, upper: int):
        if node.res[-1] == 1:
            node.current_weight += self.sorted_item_list[node.depth].weight
            node.current_value += self.sorted_item_list[node.depth].value
        if node.current_weight > self.problem.capacity:
            return False
        upper_bound = node.current_value
        weight = node.current_weight
        cost = upper_bound
        for i in range(node.depth + 1, self.problem.number_of_item):
            weight += self.sorted_item_list[i].weight
            if weight > self.problem.capacity:
                weight -= self.sorted_item_list[i].weight
                cost += (self.problem.capacity - weight) * \
                    self.sorted_item_list[i].ratio
                break
            upper_bound += self.sorted_item_list[i].value
            cost = upper_bound
        node.upper, node.cost = -upper_bound, -cost
        if -cost > upper:
            return False
        return True

    def check_node(self, node: Node, upper: int):
        if node.depth > -1:
            if node.res[-1] == 1:
                node.current_weight += self.sorted_item_list[node.depth].weight
                node.current_value += self.sorted_item_list[node.depth].value
            if node.current_weight > self.problem.capacity:
                return False
        upper_bound = node.current_value
        weight = node.current_weight
        cost = upper_bound
        tmp: list[int] = []
        if len(node.active_class) < self.problem.number_of_class:
            class_not_active = list(range(self.problem.number_of_class))
            for i in range(len(node.active_class)):
                class_not_active.remove(i)
            for i in range(node.depth+1, self.problem.number_of_item):
                if len(class_not_active) == 0:
                    break
                if self.sorted_item_list[i].class_item - 1 in class_not_active:
                    weight += self.sorted_item_list[i].weight
                    if weight > self.problem.capacity:
                        weight -= self.sorted_item_list[i].weight
                        cost += (self.problem.capacity - weight) * \
                            self.sorted_item_list[i].ratio
                        break
                    upper_bound += self.sorted_item_list[i].value
                    cost = upper_bound
                    class_not_active.remove(
                        self.sorted_item_list[i].class_item - 1)
                    tmp.append(i)
            if weight < self.problem.capacity:
                for i in range(node.depth + 1, self.problem.number_of_item):
                    if i in tmp:
                        continue
                    weight += self.sorted_item_list[i].weight
                    if weight > self.problem.capacity:
                        weight -= self.sorted_item_list[i].weight
                        cost += (self.problem.capacity - weight) * \
                            self.sorted_item_list[i].ratio
                        break
                    upper_bound += self.sorted_item_list[i].value
                    cost = upper_bound
        else:
            for i in range(node.depth + 1, self.problem.number_of_item):
                weight += self.sorted_item_list[i].weight
                if weight > self.problem.capacity:
                    weight -= self.sorted_item_list[i].weight
                    cost += (self.problem.capacity - weight) * \
                        self.sorted_item_list[i].ratio
                    break
                upper_bound += self.sorted_item_list[i].value
                cost = upper_bound
        node.upper, node.cost = -upper_bound, -cost
        if -cost > upper:
            return False
        return True

    def solve_problem(self):
        initial_state = Node(-1, 0, 0, [], [])
        upper = 100
        self.check_node(initial_state, upper)
        upper = initial_state.upper
        my_queue: list[Node] = []
        max_val = 0
        max_item: list[int] = []
        heapq.heappush(my_queue, initial_state)
        k = 0
        while True:
            k += 1
            if len(my_queue) == 0:
                break
            curr: Node = heapq.heappop(my_queue)
            if curr.depth == self.problem.number_of_item - 1:
                if curr.current_value > max_val and len(curr.active_class) == self.problem.number_of_class:
                    max_val = curr.current_value
                    max_item = curr.res.copy()
                continue
            tmp1 = curr.res.copy()
            tmp2 = curr.res.copy()
            tmp3 = curr.active_class.copy()
            tmp4 = curr.active_class.copy()
            tmp1.append(1)
            if self.sorted_item_list[curr.depth + 1].class_item - 1 not in tmp3:
                tmp3.append(
                    self.sorted_item_list[curr.depth + 1].class_item - 1)
            tmp2.append(0)
            node1 = Node(curr.depth + 1, curr.current_weight,
                         curr.current_value, tmp1, tmp3)
            node2 = Node(curr.depth + 1, curr.current_weight,
                         curr.current_value, tmp2, tmp4)
            l: list[Node] = []
            if self.check_node(node1, upper):
                l.append(node1)
            if self.check_node(node2, upper):
                l.append(node2)
            for c in l:
                heapq.heappush(my_queue, c)
            for c in l:
                if c.upper < upper and len(c.active_class) == self.problem.number_of_class:
                    upper = c.upper
                    i = 0
                    while i < len(my_queue):
                        if my_queue[i].cost > upper and len(my_queue[i].active_class) == self.problem.number_of_class:
                            my_queue.pop(i)
                            continue
                        i += 1
            del curr
        if len(max_item) == 0:
            print("No solution!")
            return
        print(max_val)
        # res = 0
        for i in range(0, len(self.sorted_item_list)):
            self.sorted_item_list[i].state = max_item[i]
            # if max_item[i] == 1:
            # res += self.sorted_item_list[i].weight
        # print(res)


class GeneticAlgorithm:
    def __init__(self, problem: Problem):
        self.problem = problem
        self.population = 1000
        self.N = problem.number_of_item

    def random_population(self):
        generation_list = []
        for _ in range(self.population):
            gene = []
            for _ in range(self.N):
                gene.append(random.randint(0, 1))
            # last element save fitness value
            gene.append(0)
            generation_list.append(gene)
        return generation_list

    def fitness(self, population_list):
        for i in range(len(population_list)):
            w = 0
            v = 0
            temp = set()
            for j in range(self.N):
                if population_list[i][j]:
                    w += p.initial_item_list[j].weight
                    v += p.initial_item_list[j].value
                    temp.add(p.initial_item_list[j].class_item)
            population_list[i][self.N] = v if w <= p.capacity else 0
            population_list[i][self.N] += 10**len(temp)
        return sorted(population_list, key=lambda x: x[self.N], reverse=True)

    def cross_over(self, generation_list):
        for i in range(0, len(generation_list), 2):
            slice = random.randint(1, self.N-2)
            new1 = generation_list[i][:slice] + generation_list[i+1][slice:]
            new2 = generation_list[i+1][:slice] + generation_list[i][slice:]
            new1[self.N] = 0
            new2[self.N] = 0
            generation_list.append(new1)
            generation_list.append(new2)
        return generation_list

    def mutation(self, generation_list, population):
        muted_list = []
        for _ in range(population//2):
            new_rand = random.randint(population//2, population-1)
            if new_rand not in muted_list:
                muted_list.append(new_rand)
                generation_list[new_rand][random.randint(
                    0, self.N-1)] = random.randint(0, 1)
        return generation_list

    def solve_problem(self):
        current_generation = self.random_population()
        current_generation = self.fitness(current_generation)
        temp = current_generation[0][self.N]
        cnt = 0
        while cnt < 100:
            current_generation = current_generation[0:self.population//2]
            new_generation = self.cross_over(current_generation)
            new_generation = self.mutation(new_generation, self.population)
            current_generation = new_generation
            current_generation = self.fitness(current_generation)
            if current_generation[0][self.N] != temp:
                temp = current_generation[0][self.N]
                cnt = 0
            else:
                cnt += 1

        # print solution
        ans = 0
        for i in range(self.N):
            item = p.initial_item_list[i]
            item.state = current_generation[0][i]
            if current_generation[0][i]:
                ans += item.value
        if current_generation[0][self.N]-10**self.problem.number_of_class == ans:
            print(ans)
        else:
            print("No solution!")


if __name__ == '__main__':
    input_file_txt = "testcase1.txt"
    # input_file_txt = "input1.txt"
    p = Problem(input_file_txt)
    opt = int(input(
        "Enter number to choose algorithms: "))

    if (opt == 1):
        search = BranchAndBound(p)
        search.get_sorted_item_list()
        n = Node(1, 2, 10, [1, 1], [])
    # elif (opt == 2):
    #     solution =
    # elif (opt == 3):
    #     solution =
    elif (opt == 4):
        search = GeneticAlgorithm(p)
    s = ""
    search.solve_problem()

    for i in range(len(p.initial_item_list)):
        if len(p.initial_item_list) - 1 == i:
            s += str(p.initial_item_list[i].state)
        else:
            s += str(p.initial_item_list[i].state) + ", "
    print(s)
