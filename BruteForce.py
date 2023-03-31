import itertools


class Item:
    def __init__(self, weight: int, value: int, class_value: int):
        self.weight = weight
        self.value = value
        self.class_value = class_value

    def print(self):
        print("Weight of item :", self.weight)
        print("Value of item :", self.value)
        print("Class of item :", self.class_value)


class Problem:
    def __init__(self, inputfile):
        self.input_file = inputfile
        self.item_list: list[Item] = []
        self.capacity = 0
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
            self.item_list.append(Item(int(weight_list[i]), int(value_list[i]), int(class_list[i])))


class BruteForce:
    def __init__(self, problem: Problem):
        self.problem = problem

    def isValid(self, choice) -> bool:
        temp = 0
        for i in range(len(choice)):
            if choice[i] == 1:
                temp += self.problem.item_list[i].weight
            if temp > self.problem.capacity: return False
        return True

    def findValue(self, choice) -> int:
        temp = 0
        for i in range(len(choice)):
            if choice[i] == 1:
                temp += self.problem.item_list[i].value
        return temp

    def checkEnoughClass(self, choice) -> bool:
        check = set()
        for i in range(len(choice)):
            if choice[i]:
                check.add(self.problem.item_list[i].class_value)
        if len(check) == self.problem.number_of_class: return True
        return False

    def findWeight(self, choice) -> int:
        temp = 0
        for i in range(len(choice)):
            if choice[i] == 1:
                temp += self.problem.item_list[i].weight
        return temp

    def solve(self):
        gen = [[0, 1] for _ in range(self.problem.number_of_item)]
        choice_list = list(itertools.product(*gen))

        value = 0
        chosen = None
        weight = 0
        for choice in choice_list:
            if self.checkEnoughClass(choice) and self.isValid(choice):
                temp = self.findValue(choice)
                if temp >= value:
                    value = temp
                    chosen = choice
                    weight = self.findWeight(choice)
        return value, chosen, weight


if __name__ == "__main__":
    input_file =input("Input the name of file :")
    p = Problem(input_file)

    search1 = BruteForce(p)
    val, sol, wei = search1.solve()
    print(val)
    print(sol)
