import copy
import heapq


class Item:
    def __init__(self, weight: int, value: int, class_item: int, number = 0, state=0):
        self.weight = weight
        self.value = value
        self.class_item = class_item
        self.state = state
        self.ratio = float(self.value) / self.weight
        self.n = number

    def print_item_info(self):
        print(
            f"Weight:{self.weight}  Value:{self.value}  Class:{self.class_item}  Ratio:{self.ratio}  State:{self.state}")

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
            self.initial_item_list.append(Item(int(weight_list[i]), int(value_list[i]), int(class_list[i]), i))

class local_beam_search:
    def __init__(self, problem, k, times):
        self.problem = problem
        self.items = problem.initial_item_list
        self.capacity = problem.capacity
        self.k = k
        self.times = times
        solution = self.solution()
        temp = []
        for i in range(len(self.items)):
            temp.append(0)
        if solution:
            for i in range(len(solution)):
                temp[solution[i].n] = 1
            for i in range(len(temp)):
                print(temp[i], end=' ')
            print("\n")
            print(self.calc_items_value(solution))
        else:
            print("No solution")

    def calc_items_weight(self, items):
        total_weight = 0
        for i in range (len(items)):
            total_weight += items[i].weight
        return total_weight

    def calc_items_value(self, items):
        total_value = 0
        for i in range (len(items)):
            total_value += items[i].value
        return total_value

    def sort_items(self, items):
        for i in range(len(self.items)): #Sort list of item input
            for j in range(len(self.items) - i - 1):
                if self.items[j].value == self.items[j+1].value:
                    if self.items[j].weight > self.items[j+1].weight:
                        self.items[j], self.items[j+1] = self.items[j+1], self.items[j]
                else:
                    if self.items[j].value < self.items[j+1].value:
                        self.items[j], self.items[j + 1] = self.items[j + 1], self.items[j]
        return items

    def sort_list_items(self, list_items):
        for i in range(len(list_items)):
            for j in range (len(list_items)-i-1):
                if self.calc_items_value(list_items[j]) == self.calc_items_value(list_items[j+1]):
                    if self.calc_items_weight(list_items[j]) > self.calc_items_weight(list_items[j+1]):
                        list_items[j], list_items[j+1] = list_items[j+1], list_items[j]
                else:
                    if self.calc_items_value(list_items[j]) < self.calc_items_value(list_items[j+1]):
                        list_items[j], list_items[j + 1] = list_items[j + 1], list_items[j]
        return list_items

    def check_in_list(self, items, item):
        for i in range(len(items)):
            if item.n == items[i].n:
                return True
        return False

    def check_different_class(self, items):
        check = set()
        for i in range(len(items)):
            if items[i]:
                check.add(items[i].class_item)
        if len(check) == self.problem.number_of_class:
            return True
        return False

    def check_in_expanded(self, expanded, items):
        for i in range(len(expanded)):
            expanded[i] = self.sort_items(expanded[i])
            count = 0
            if len(items) == len(expanded[i]):
                items = self.sort_items(items)
                for j in range(len(items)):
                    if items[j].n == expanded[i][j].n:
                        count += 1
            if count == len(items):
                return True
        return False

    def find_pos_in_items(self, items, item):
        for i in range(len(items)):
            if items[i].n == item.n:
                return i
        return None

    def solution(self):
        frontier = []
        for i in range(len(self.items)):
            temp = []
            temp.append(self.items[i])
            frontier.append(temp)
        frontier = self.sort_list_items(frontier)
        beam = []
        self.items = self.sort_items(self.items)
        for i in range(self.k):
            beam.append(frontier[i])
        expanded = []
        for k in range(self.times):
            l = len(frontier)
            new_items = []
            for i in range(len(beam)):
                for j in range(self.find_pos_in_items(beam[i], beam[i][len(beam[i])-1])+1, len(self.items)):
                    new_items = copy.deepcopy(beam[i])
                    if self.check_in_list(beam[i], self.items[j]) == False:
                        new_items.append(self.items[j])
                        if self.check_in_expanded(expanded, new_items) == False:
                            if self.calc_items_weight(new_items) <= self.capacity:
                                frontier.append(new_items)
                            else:
                                continue
            frontier = self.sort_list_items(frontier)
            if len(frontier) == l:
                for i in range(self.k):
                    expanded.append(frontier.pop(0))
                    expanded.append(beam.pop(0))
                    beam.append(frontier[i])
            else:
                for i in range(self.k):
                    expanded.append(beam.pop(0))
                    beam.append(frontier[i])
        for i in range(len(expanded)):
            frontier.append(expanded[i])
        frontier = self.sort_list_items(frontier)
        for i in range(len(frontier)):
            if self.check_different_class(frontier[i]):
                return frontier[i]
        return None

if __name__ == '__main__':
    input_file_txt = "testcase2.txt"
    p = Problem(input_file_txt)
    search3 = local_beam_search(p, 2, 80)