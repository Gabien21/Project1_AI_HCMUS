import heapq
import random
import itertools
import time
import tracemalloc
import copy
import winsound


class Item:
    def __init__(self, weight: int, value: int, class_item: int, number=0, state=0):
        self.weight = weight
        self.value = value
        self.class_item = class_item
        self.state = state
        self.ratio = float(self.value) / self.weight
        self.n = number

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
        self.weight_list = ""
        self.value_list = ""
        self.class_list = ""
        self.read_file()

    def read_file(self):
        file = open(self.input_file, "r")
        self.capacity = float(file.readline().strip("\n"))
        self.number_of_class = int(file.readline().strip("\n"))
        self.weight_list = file.readline().strip("\n").split(", ")
        self.value_list = file.readline().strip("\n").split(", ")
        self.class_list = file.readline().strip("\n").split(", ")
        file.close()
        self.number_of_item = len(self.weight_list)
        for i in range(self.number_of_item):
            self.initial_item_list.append(Item(int(self.weight_list[i]), int(
                self.value_list[i]), int(self.class_list[i]), i))

    def print_problem_info(self):
        print("Capacity:", self.capacity)
        print("Number of class:", self.number_of_class)
        print("Number of item:", self.number_of_item)
        print("Weight list: ", end="")
        for i in range(self.number_of_item):
            print(self.weight_list[i], end=" ")
        print()
        print("Value list: ", end="")
        for i in range(self.number_of_item):
            print(self.value_list[i], end=" ")
        print()
        print("Class list: ", end="")
        for i in range(self.number_of_item):
            print(self.class_list[i], end=" ")
        print()


# Thuat toan branch and bound
class BranchAndBound:
    def __init__(self, problem: Problem):
        self.problem = problem
        self.sorted_item_list: list[Item] = []
        self.class_oder: list[list[int]] = [[]
                                            for _ in range(problem.number_of_class)]
        self.get_sorted_item_list()

    # Sap xep cac Item theo thu tu giam dan cua ti le ratio = vale/weight
    def get_sorted_item_list(self):
        max_weight = max(self.problem.initial_item_list,
                         key=lambda item: item.weight).weight
        self.sorted_item_list = sorted(self.problem.initial_item_list, reverse=True,
                                       key=lambda item: (item.ratio, max_weight - item.weight))  # neu ti le ratio bang nhau thi sap xep Item giam dan theo weight
        # Lay ra danh sach vi tri cac Item cua tung class trong list da sap xep
        for i in range(self.problem.number_of_item):
            self.class_oder[self.sorted_item_list[i].class_item-1].append(i)

    # Tinh toan upperbound va cost cua 1 node va kiem tra xem 1 node co the pruned hay khong
    def check_node(self, node: Node, upper: int):
        if node.depth > -1:
            if node.res[-1] == 1:   # Neu ta chon vat dang xet
                node.current_weight += self.sorted_item_list[node.depth].weight
                node.current_value += self.sorted_item_list[node.depth].value
            # Neu weight cua node hien tai lon hon capacity thi prun node do
            if node.current_weight > self.problem.capacity:
                return False
        upper_bound = node.current_value
        weight = node.current_weight
        cost = upper_bound
        # Neu cac Item da xet (o do sau tu 0 den node.depth) chua xet day du tat ca cac class
        if len(node.active_class) < self.problem.number_of_class:
            tmp: list[int] = []  # list danh dau vi tri cua cac vat do chon
            # list danh dau cac class cua xet
            class_not_active = list(range(self.problem.number_of_class))
            for i in range(len(node.active_class)):
                class_not_active.remove(i)
            # Uu tien them Item cua cac class chua duoc xet truoc
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
            # Sau khi xet du cac class  ma van con du weight thi tiep tuc them cac Item
            # chua duoc xet theo thu tu trong sorted_item_list
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
        # Neu cac Item da xet (o do sau tu 0 den node.depth) da xet day du tat ca cac class
        else:
            # Them cac Item chua duoc xet theo thu tu trong sorted_item_list
            for i in range(node.depth + 1, self.problem.number_of_item):
                weight += self.sorted_item_list[i].weight
                if weight > self.problem.capacity:
                    weight -= self.sorted_item_list[i].weight
                    cost += (self.problem.capacity - weight) * \
                        self.sorted_item_list[i].ratio
                    break
                upper_bound += self.sorted_item_list[i].value
                cost = upper_bound
        # Luu lai cost va upper_bound o dang so am
        node.upper, node.cost = -upper_bound, -cost
        # Kiem tra xem abs(cost) < abs(upper) hay khong, neu co thi prun node do
        if -cost > upper:
            return False
        return True

    # Giai quyet bai toan bang thuat toan branch and bound
    def solve_problem(self):
        initial_state = Node(-1, 0, 0, [], [])
        upper = 100000
        self.check_node(initial_state, upper)
        upper = initial_state.upper
        # chua cac node theo thu tu giam dan cua cost
        my_queue: list[Node] = []
        max_val = 0  # Luu lai solution tot nhat
        max_item: list[int] = []    # Luu lai solution tot nhat
        heapq.heappush(my_queue, initial_state)
        while True:
            if len(my_queue) == 0:
                break
            curr: Node = heapq.heappop(my_queue)
            if curr.depth == self.problem.number_of_item - 1:   # Neu Node curr da xet xet tat ca cac vat
                # Neu node curr chon day du tat cac cac class va solution node curr dua ra
                # tot hon solution dang luu thi luu lai solution cua node curr
                if curr.current_value > max_val and len(curr.active_class) == self.problem.number_of_class:
                    max_val = curr.current_value
                    max_item = curr.res.copy()
                continue
            tmp1 = curr.res.copy()  # mang luu cac item da xet cua node curr
            tmp2 = curr.res.copy()  # mang luu cac item da xet cua node curr
            tmp3 = curr.active_class.copy()  # mang luu cac class da xet cua node curr
            tmp4 = curr.active_class.copy()  # mang luu cac class da xet cua node curr
            tmp1.append(1)  # xet chon vat o curr.depth + 1
            tmp2.append(0)  # xet khong chon vat o curr.depth + 1
            # xet xem class cua Item dang xet co duoc xet trong node curr hay chua,
            # Neu chua thi them vao cho node con lay item do
            if self.sorted_item_list[curr.depth + 1].class_item - 1 not in tmp3:
                tmp3.append(
                    self.sorted_item_list[curr.depth + 1].class_item - 1)
            node1 = Node(curr.depth + 1, curr.current_weight,
                         curr.current_value, tmp1, tmp3)  # Node con co lay Item
            node2 = Node(curr.depth + 1, curr.current_weight,
                         curr.current_value, tmp2, tmp4)  # Node con khong lay Item
            l: list[Node] = []  # Mang luu lai node con khong bi pruned
            if self.check_node(node1, upper):
                l.append(node1)
            if self.check_node(node2, upper):
                l.append(node2)
            for c in l:
                # Them cac node con khong bi pruned vao my_queue
                heapq.heappush(my_queue, c)
            for c in l:
                # Trong cac node con, neu co upper lon hon upper toan cuc thi luu lai upper toan cuc
                # Va prune di nhung node co cost > upper toan cuc vua thay doi do
                if c.upper < upper and len(c.active_class) == self.problem.number_of_class:
                    upper = c.upper
                    i = 0
                    while i < len(my_queue):
                        if my_queue[i].cost > upper and len(my_queue[i].active_class) == self.problem.number_of_class:
                            my_queue.pop(i)
                            continue
                        i += 1
            del curr
        if len(max_item) == 0:  # Neu mang solution ra ve rong thi bai toan khong co loi giai
            print("No solution!")
            return
        print(max_val)  # Nguoc lai tra ve solution
        for i in range(0, len(self.sorted_item_list)):
            self.sorted_item_list[i].state = max_item[i]
        return max_val

# Thuat toan Brute Force


class BruteForce:
    def __init__(self, problem: Problem):
        self.problem = problem
    # Ung voi moi lua chon , iem tra xem khoi luong cua cac vat duoc lay co lon hon khoi luong toi da ma tui co the chua duoc hay khong

    def isValid(self, choice) -> bool:
        temp = 0
        for i in range(len(choice)):
            if choice[i] == 1:
                temp += self.problem.initial_item_list[i].weight
            if temp > self.problem.capacity:
                return False
        return True
    # Tim gia tri cua tui ung voi cac vat duoc lua chon

    def findValue(self, choice) -> int:
        temp = 0
        for i in range(len(choice)):
            if choice[i] == 1:
                temp += self.problem.initial_item_list[i].value
        return temp
    # Kiem tra xem co du so luong class ung voi tung lua chon

    def checkEnoughClass(self, choice) -> bool:
        check = set()
        for i in range(len(choice)):
            if choice[i]:
                check.add(self.problem.initial_item_list[i].class_item)
        if len(check) == self.problem.number_of_class:
            return True
        return False
    # Tim gia tri cua tui ung voi cac vat duoc lua chon

    def findWeight(self, choice) -> int:
        temp = 0
        for i in range(len(choice)):
            if choice[i] == 1:
                temp += self.problem.initial_item_list[i].weight
        return temp

    def solve_problem(self):
        # Sinh ra tat ca cac truong hop lua chon voi moi vat co 2 trang thai la 1 ( duoc lua chon ) hay 2 ( khong duoc lua chon)
        gen = [[0, 1] for _ in range(self.problem.number_of_item)]
        choice_list = list(itertools.product(*gen))

        value = 0
        chosen = None
        weight = 0
        for choice in choice_list:
            # Ung voi moi lua chon , kiem tra so luong class va khoi luong cua cac vat duoc lay
            if self.checkEnoughClass(choice) and self.isValid(choice):
                temp = self.findValue(choice)
                if temp >= value:
                    value = temp
                    chosen = choice
                    weight = self.findWeight(choice)
        for i in range(self.problem.number_of_item):
            self.problem.initial_item_list[i].state = chosen[i]
        print(value)


class GeneticAlgorithm:
    def __init__(self, problem: Problem):
        self.problem = problem
        self.population = 1000 if problem.number_of_item < 100 else 5000
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
            population_list[i][self.N] = v + \
                10**len(temp) if w <= p.capacity else 0
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
            p.initial_item_list.clear()
            print("No solution!")


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
                self.problem.initial_item_list[i].state = temp[i]
            print(self.calc_items_value(solution))
        else:
            print("No solution")

    # Ham tinh tong khoi luong cua cac items trong danh sach
    def calc_items_weight(self, items):
        total_weight = 0
        for i in range(len(items)):
            total_weight += items[i].weight
        return total_weight

    # Ham tinh tong gia tri cua cac items trong danh sach
    def calc_items_value(self, items):
        total_value = 0
        for i in range(len(items)):
            total_value += items[i].value
        return total_value

    def sort_items(self, items):  # Ham sap xep cac item trong danh sach theo gia tri giam dan, neu cac item co cung gia tri thi sort theo khoi luong nho hon
        for i in range(len(self.items)):
            for j in range(len(self.items) - i - 1):
                if self.items[j].value == self.items[j+1].value:
                    if self.items[j].weight > self.items[j+1].weight:
                        self.items[j], self.items[j +
                                                  1] = self.items[j+1], self.items[j]
                else:
                    if self.items[j].value < self.items[j+1].value:
                        self.items[j], self.items[j +
                                                  1] = self.items[j + 1], self.items[j]
        return items

    # Ham sap xep cac list item trong danh sách các list itemsitems
    def sort_list_items(self, list_items):
        for i in range(len(list_items)):
            for j in range(len(list_items)-i-1):
                if self.calc_items_value(list_items[j]) == self.calc_items_value(list_items[j+1]):
                    if self.calc_items_weight(list_items[j]) > self.calc_items_weight(list_items[j+1]):
                        list_items[j], list_items[j +
                                                  1] = list_items[j+1], list_items[j]
                else:
                    if self.calc_items_value(list_items[j]) < self.calc_items_value(list_items[j+1]):
                        list_items[j], list_items[j +
                                                  1] = list_items[j + 1], list_items[j]
        return list_items

    # Kiem tra xem item da co trong danh sach hay chua
    def check_in_list(self, items, item):
        for i in range(len(items)):
            if item.n == items[i].n:
                return True
        return False

    # Kiem tra xem cac item trong danh sach co thoa dieu kien moi class co it nhat 1 vatkhongkhong
    def check_different_class(self, items):
        check = set()
        for i in range(len(items)):
            if items[i]:
                check.add(items[i].class_item)
        if len(check) == self.problem.number_of_class:
            return True
        return False

    # Kiem tra xem danh sach cac items co trong list expanded chuachua
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

    # Tim vi tri cua item trong danh sach items
    def find_pos_in_items(self, items, item):
        for i in range(len(items)):
            if items[i].n == item.n:
                return i
        return None

    def solution(self):
        frontier = []  # frontier la 1 danh sach ma moi phan tu cua no lai la danh sach cac items
        for i in range(len(self.items)):
            temp = []
            temp.append(self.items[i])
            frontier.append(temp)
        # Sap xep danh sach cac items
        frontier = self.sort_list_items(frontier)
        beam = []
        self.items = self.sort_items(self.items)  # Sap xep cac items
        for i in range(self.k):
            # Them b phan tu dau tien của frontier vao beam. Sau khi sort, cac phan tu dau tien cua beam cung la cac phan tu co gia tri nhatnhat
            beam.append(frontier[i])
        expanded = []  # Danh sach chua list cac items da duoc duyet
        for k in range(self.times):  # k chay tu 0 den so lan san xuat node moi
            l = len(frontier)
            new_items = []
            for i in range(len(beam)):
                # j chay tu vi tri cuoi cung cua phan tu den phan tu cuoi cung cua items
                for j in range(self.find_pos_in_items(beam[i], beam[i][len(beam[i])-1])+1, len(self.items)):
                    new_items = copy.deepcopy(beam[i])
                    # Kiem tra xem item[j] co trong list beam[i] chua
                    if self.check_in_list(beam[i], self.items[j]) == False:
                        # Luc nay new_items se chua beam[i] va items[j]
                        new_items.append(self.items[j])
                        # Kiem tra xem new_items co trong expanded chua
                        if self.check_in_expanded(expanded, new_items) == False:
                            # Kiem tra tong khoi luong cua new_items voi khoi luong gioi han
                            if self.calc_items_weight(new_items) <= self.capacity:
                                # Neu thoa dieu kien thi cho new_items vào frontier
                                frontier.append(new_items)
                            else:
                                continue
            frontier = self.sort_list_items(frontier)  # Sort lai frontier
            if len(frontier) == l:  # Kiem tra xem co node nao duoc mo rong khong, neu do dai cua frontier khong thay doi nghia la khong co node nao duoc san xuat
                for i in range(self.k):
                    # Chuyen node dau cua frontier vao expanded
                    expanded.append(frontier.pop(0))
                    # Chuyen node dau cua beam vao expanded
                    expanded.append(beam.pop(0))
                    # Tiep tuc xet nhung danh sach co gia tri lon nhat cua frontier
                    beam.append(frontier[i])
            else:  # Co node moi duoc san xuat
                for i in range(self.k):
                    # Chuyen node dau cua beam vao expanded
                    expanded.append(beam.pop(0))
                    # Tiep tuc xet nhung danh sach co gia tri lon nhat cua frontier
                    beam.append(frontier[i])
        for i in range(len(expanded)):
            # Them tat ca cac danh sach o trong expanded vao frontier de xet
            frontier.append(expanded[i])
        frontier = self.sort_list_items(frontier)
        for i in range(len(frontier)):
            # Kiem tra xem danh sach co thoa dieu kien moi class co it nhat 1 vat hay khong
            if self.check_different_class(frontier[i]):
                # Neu thoa thi tra ve danh sach do. Vi frontier da duoc sort nen danh sach nay là danh sach cac vat co tong gia tri lon nhat va thoa dieu kien
                return frontier[i]
        return None  # Neu sau k lan san xuat node moi khong co danh sach nao thoa dieu kien thi tra ve


def generate_test_case(capacity: int, number_of_class: int, number_of_item: int):
    test_file = "testcase12.txt"
    with open(test_file, 'w') as file:
        file.write(str(capacity)+"\n")
        file.write(str(number_of_class)+"\n")
        for k in range(number_of_item):
            if k == number_of_item-1:
                file.write(str(random.randint(1, 50)))
                file.write("\n")
            else:
                file.write(str(random.randint(1, 50)) + ", ")

        for k in range(number_of_item):
            if k == number_of_item-1:
                file.write(str(random.randint(1, 100)))
                file.write("\n")
            else:
                file.write(str(random.randint(1, 100)) + ", ")
        for k in range(number_of_item):
            if k == number_of_item-1:
                file.write(str(random.randint(1, number_of_class)))
            else:
                file.write(str(random.randint(1, number_of_class)) + ", ")


if __name__ == '__main__':
    input_file_txt = "INPUT_2.txt"
    p = Problem(input_file_txt)
    p.print_problem_info()
    while True:
        print(
            "______________________________________________________________________________")
        print(
            "1/Brute Force\n2/Branch And Bound\n3/Local Beam\n4/Genetic Algorithm\n5/Stop")
        option = int(input(
            "Enter your choice: "))
        s = ""
        start = time.time()
        tracemalloc.start()
        if option == 5:
            print("Thank you for watching <3")
            break
        elif option == 2:
            search = BranchAndBound(p)
            search.solve_problem()
        elif option == 1:
            tracemalloc.start()
            search = BruteForce(p)
            search.solve_problem()
        elif option == 3:
            tracemalloc.start()
            search = local_beam_search(p, 2, 10)
        elif option == 4:
            tracemalloc.start()
            search = GeneticAlgorithm(p)
            search.solve_problem()
        end = time.time()
        for i in range(len(p.initial_item_list)):
            if len(p.initial_item_list) - 1 == i:
                s += str(p.initial_item_list[i].state)
            else:
                s += str(p.initial_item_list[i].state) + ", "
        print(s)
        print("Time: ", (end - start) * 1000, "ms")
        print("Memory: ", tracemalloc.get_tracemalloc_memory() / 1024, "KB")
        tracemalloc.stop()
