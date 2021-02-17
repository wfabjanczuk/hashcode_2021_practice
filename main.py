from tqdm import tqdm


class Solver:
    def __init__(self, file_name):
        self.pizza_count, self.t_2, self.t_3, self.t_4 = [0, 0, 0, 0]
        self.pizza_list = []
        self.sorted_pizza_list = []
        self.team_dict = {}

        self.current_team_id = None
        self.current_count = None
        self.filled_teams_count = 0
        self.is_start = True
        self.can_work = True

        self.input_path_prefix = './input/'
        self.output_path_prefix = './output/'
        self.file_name = file_name
        self.read_file()

    def read_file(self):
        with open(self.input_path_prefix + self.file_name) as file:
            header_line = file.readline()
            self.pizza_count, self.t_2, self.t_3, self.t_4 = [int(i) for i in header_line.strip().split()]

            pizza_id = 0
            for line in file.readlines():
                ingredients = line.strip().split(' ')
                ingredients_count = int(ingredients.pop(0))

                pizza = {
                    "id": pizza_id,
                    "ingredients": ingredients,
                    "ingredients_count": ingredients_count,
                    "assigned_team": None
                }

                self.pizza_list.append(pizza)
                pizza_id += 1

            self.team_dict = {
                "2": {
                    "first_free_id": 0,
                    "list": [{"id": i, "pizzas": [], "max_pizzas": 2, "points": 0} for i in range(self.t_2)]
                },
                "3": {
                    "first_free_id": 0,
                    "list": [{"id": i, "pizzas": [], "max_pizzas": 3, "points": 0} for i in range(self.t_3)]
                },
                "4": {
                    "first_free_id": 0,
                    "list": [{"id": i, "pizzas": [], "max_pizzas": 4, "points": 0} for i in range(self.t_4)]
                }
            }

    def solve(self):
        self.sorted_pizza_list = sorted(self.pizza_list, key=lambda item: item["ingredients_count"], reverse=True)

        for _ in tqdm(range(self.pizza_count)):
            if not self.can_work:
                break
            self.assign_a_pizza()

        self.print_result()

    def assign_a_pizza(self):
        if self.is_current_team_filled():
            self.current_team_id = self.get_best_team_id()

        if self.current_team_id is None:
            self.can_work = False
            return

        best_pizza = self.get_best_pizza()

        if best_pizza is None:
            self.can_work = False
            return

        self.add_pizza_to_current_team(best_pizza)
        if self.is_current_team_filled():
            self.filled_teams_count += 1

    def is_current_team_filled(self):
        if self.is_start:
            self.is_start = False
            return True

        current_team = self.get_current_team()
        return len(current_team["pizzas"]) >= current_team["max_pizzas"]

    def get_current_team(self):
        return self.team_dict[self.current_count]["list"][self.current_team_id]

    def add_pizza_to_current_team(self, pizza):
        self.team_dict[self.current_count]["list"][self.current_team_id]["pizzas"].append(pizza)

    # bigger team => possibly more ingredients and higher square
    def get_best_team_id(self):
        counts = ["4", "3", "2"]

        for count in counts:

            is_pizza_count_enough = int(count) <= len(self.sorted_pizza_list)
            is_any_team_left = self.team_dict[count]["first_free_id"] < len(self.team_dict[count]["list"])

            if is_pizza_count_enough and is_any_team_left:
                self.current_team_id = self.team_dict[count]["first_free_id"]
                self.current_count = count

                self.team_dict[count]["first_free_id"] += 1
                return self.current_team_id

        return None

    def get_best_pizza(self):
        if not len(self.sorted_pizza_list):
            return None

        current_team = self.get_current_team()
        current_ingredients = set()

        for assigned_pizza in current_team["pizzas"]:
            current_ingredients.union(set(assigned_pizza["ingredients"]))

        max_income = 0
        best_loop_id = None
        loop_id = 0

        for possible_pizza in self.sorted_pizza_list:
            new_ingredients = set(possible_pizza["ingredients"]).difference(current_ingredients)

            if len(new_ingredients) > max_income:
                max_income = len(new_ingredients)
                best_loop_id = loop_id

            loop_id += 1
            if loop_id > 10000:
                break

        if best_loop_id is None:
            return self.sorted_pizza_list.pop()
        else:
            return self.sorted_pizza_list.pop(best_loop_id)

    def print_result(self):
        with open(self.output_path_prefix + self.file_name, 'w+') as file:
            file.write(str(self.filled_teams_count) + "\n")

            for count in self.team_dict:
                for team in self.team_dict[count]["list"]:
                    if team["max_pizzas"] == len(team["pizzas"]):
                        line = str(team["max_pizzas"]) + " " + " ".join([str(p["id"]) for p in team["pizzas"]])
                        file.write(line + "\n")


if __name__ == '__main__':
    file_name_list = [
        'a_example',
        'b_little_bit_of_everything.in',
        'c_many_ingredients.in',
        'd_many_pizzas.in',
        'e_many_teams.in'
    ]

    for file_name in file_name_list:
        print(file_name + " progress:")
        Solver(file_name).solve()
