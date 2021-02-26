from tqdm import tqdm


class IO:
    def __init__(self, input_file_name):
        self.pizza_count = 0
        self.team_count_dict = {"4": 0, "3": 0, "2": 0}

        self.pizza_list = []
        self.sorted_pizza_list = []
        self.all_ingredients = set()
        self.all_ingredients_count = 0

        self.team_dict = {}
        self.full_teams_count = 0
        self.all_teams_count = 0

        self.input_path_prefix = './input/'
        self.output_path_prefix = './output/'
        self.input_file_name = input_file_name
        self.read_input()

    def read_input(self):
        with open(self.input_path_prefix + self.input_file_name) as file:
            header_line = file.readline()
            self.pizza_count, two_teams, three_teams, four_teams = [int(i) for i in header_line.strip().split()]
            self.initialize_pizza_list(file)
            self.all_ingredients_count = len(self.all_ingredients)

            self.team_count_dict = {"4": four_teams, "3": three_teams, "2": two_teams}
            self.initialize_team_dicts(self.team_count_dict)
            self.all_teams_count = sum(self.team_count_dict.values())

    def initialize_pizza_list(self, input_file):
        for pizza_id, line in enumerate(input_file.readlines()):
            ingredients = line.strip().split(' ')[1:]

            self.pizza_list.append({
                "id": pizza_id,
                "ingredients": ingredients
            })
            self.all_ingredients = self.all_ingredients.union(set(ingredients))

    def initialize_team_dicts(self, team_count_dict):
        team_objects = map(
            lambda pizza_count: self.get_empty_team_list(pizza_count),
            team_count_dict.keys()
        )
        self.team_dict = dict(zip(team_count_dict.keys(), team_objects))

    def get_empty_team_list(self, pizza_count):
        return [
            {
                "id": team_id,
                "pizzas": [],
                "max_pizzas": int(pizza_count)
            }
            for team_id in range(self.team_count_dict[pizza_count])
        ]

    def write_output(self):
        with open(self.output_path_prefix + self.input_file_name, 'w+') as file:
            file.write(str(self.full_teams_count))

            for count in self.team_dict:
                for team in self.team_dict[count]:
                    if team["max_pizzas"] == len(team["pizzas"]):
                        line = "\n" + str(team["max_pizzas"]) + " "
                        line += " ".join([str(pizza["id"]) for pizza in team["pizzas"]])
                        file.write(line)


class Solver(IO):
    def solve(self):
        self.fill_teams_with_pizzas()
        self.write_output()

    def fill_teams_with_pizzas(self):
        self.sorted_pizza_list = sorted(self.pizza_list, key=self.distance_from_mean, reverse=True)
        self.assign_pizzas_by_best_points_possible()
        self.assign_reusable_pizzas_to_leftover_teams(True)

        if self.input_file_name == 'a_example':
            self.assign_reusable_pizzas_to_leftover_teams(False)

    def distance_from_mean(self, pizza):
        return (len(pizza["ingredients"]) - self.all_ingredients_count / 2.0) ** 2

    def assign_pizzas_by_best_points_possible(self):
        self.add_first_pizza(6)

        while self.full_teams_count < self.all_teams_count:

            filled_before = self.full_teams_count

            print(self.assign_pizzas_by_best_points_possible.__name__)
            for _ in tqdm(range(len(self.sorted_pizza_list))):
                if len(self.sorted_pizza_list) == 0:
                    break

                best_pizza = self.sorted_pizza_list.pop()
                best_team = self.find_best_team_for_pizza(best_pizza, 10000)
                if best_team is None:
                    break
                else:
                    self.add_pizza_to_team(best_pizza, best_team)
                    if self.is_team_full(best_team):
                        self.add_first_pizza(1)

            self.sorted_pizza_list = sorted(
                self.sorted_pizza_list + self.get_reusable_pizzas(),
                key=self.distance_from_mean,
                reverse=True
            )

            if self.full_teams_count == filled_before or len(self.sorted_pizza_list) == 0:
                break

    def add_first_pizza(self, suggested_insertions):
        max_insertions = self.get_max_insertions(suggested_insertions)
        insertions = 0

        while insertions < max_insertions:
            if len(self.sorted_pizza_list) == 0:
                break

            pizza = self.sorted_pizza_list.pop()
            team = self.find_empty_team(10000)

            if team is None:
                self.sorted_pizza_list.append(pizza)
                return

            self.add_pizza_to_team(pizza, team)
            insertions += 1

    def find_empty_team(self, team_loop_limit):
        team_loop_id = 0
        for pizza_count in self.team_dict:
            for team in self.team_dict[pizza_count]:
                if len(team["pizzas"]) == 0:
                    return team
                if team_loop_id > team_loop_limit:
                    return None
                team_loop_id += 1
        return None

    def get_max_insertions(self, suggested_insertions):
        return min(suggested_insertions, int(self.all_teams_count / 5 + 1))

    def find_best_team_for_pizza(self, pizza, team_loop_limit):
        best_score = None
        best_team = None

        team_loop_id = 0
        for pizza_count in self.team_dict:
            for team in self.team_dict[pizza_count]:
                if len(team["pizzas"]) < team["max_pizzas"]:
                    score = self.get_team_pizza_adaptive_score(team, pizza)

                    if best_score is None or score > best_score:
                        best_score = score
                        best_team = team

                if team_loop_id > team_loop_limit:
                    return best_team
                team_loop_id += 1

        return best_team

    def get_team_pizza_adaptive_score(self, team, pizza):
        current_ingredients = self.get_team_ingredients(team)
        new_score = len(current_ingredients.union(pizza["ingredients"])) ** 2

        return new_score / (len(team["pizzas"]) + 1)

    @staticmethod
    def get_team_ingredients(team):
        return {ingredient for pizza in team["pizzas"] for ingredient in pizza["ingredients"]}

    def get_reusable_pizzas(self):
        reusable_pizzas = []

        for pizza_count in self.team_dict:
            for team in self.team_dict[pizza_count]:
                if team["max_pizzas"] != len(team["pizzas"]):
                    reusable_pizzas += team["pizzas"]
                    self.team_dict[pizza_count][team["id"]]["pizzas"] = []

        return reusable_pizzas

    def assign_reusable_pizzas_to_leftover_teams(self, ascending):
        self.sorted_pizza_list = sorted(
            self.sorted_pizza_list + self.get_reusable_pizzas(),
            key=self.distance_from_mean,
            reverse=False
        )
        if len(self.sorted_pizza_list) == 0:
            return

        leftover_teams = self.get_leftover_teams(ascending)

        print(self.assign_reusable_pizzas_to_leftover_teams.__name__)
        for _ in tqdm(range(len(leftover_teams))):
            filled_before = self.full_teams_count

            team = leftover_teams.pop()
            while len(self.sorted_pizza_list):
                self.assign_best_pizza_to_team(team, 10000)
                if self.is_team_full(team):
                    break

            if self.full_teams_count == filled_before:
                break

    def get_leftover_teams(self, ascending):
        leftover_teams = []

        if ascending is True:
            team_count_keys = reversed(self.team_count_dict.keys())
        else:
            team_count_keys = self.team_count_dict.keys()

        for pizza_count in team_count_keys:
            for team in self.team_dict[pizza_count]:
                if team["max_pizzas"] != len(team["pizzas"]):
                    leftover_teams.append(team)

        return leftover_teams

    def assign_best_pizza_to_team(self, team, pizza_loop_limit):
        best_score = None
        best_pizza_loop_id = None

        for pizza_loop_id, pizza in enumerate(self.sorted_pizza_list):
            score = self.get_team_pizza_adaptive_score(team, pizza)

            if best_score is None or score > best_score:
                best_score = score
                best_pizza_loop_id = pizza_loop_id

            if pizza_loop_id > pizza_loop_limit:
                break

        best_pizza = self.sorted_pizza_list.pop(best_pizza_loop_id)
        self.add_pizza_to_team(best_pizza, team)

    def add_pizza_to_team(self, pizza, team):
        self.team_dict[str(team["max_pizzas"])][team["id"]]["pizzas"].append(pizza)

        if self.is_team_full(team):
            self.full_teams_count += 1

    @staticmethod
    def is_team_full(team):
        return len(team["pizzas"]) == team["max_pizzas"]


class SolverWithOptimization(Solver):
    def fill_teams_with_pizzas(self):
        super().fill_teams_with_pizzas()
        self.optimize_selection()

    optimization_runs_dict = {
        'a_example': 3,
        'b_little_bit_of_everything.in': 10,
        'c_many_ingredients.in': 10,
        'd_many_pizzas.in': 5,
        'e_many_teams.in': 5
    }

    optimization_team_loop_limit_dict = {
        'a_example': 1000,
        'b_little_bit_of_everything.in': 1000,
        'c_many_ingredients.in': 100,
        'd_many_pizzas.in': 100,
        'e_many_teams.in': 100
    }

    def optimize_selection(self):
        run_count = self.get_optimization_runs()
        for run_id in range(run_count):
            print(self.optimize_selection.__name__ + ", run=" + str(run_id + 1) + "/" + str(run_count))
            for pizza_count in self.team_count_dict.keys():
                for team_id in tqdm(range(len(self.team_dict[pizza_count]))):
                    team = self.team_dict[pizza_count][team_id]
                    if self.is_team_full(team):
                        self.find_pizza_swap(team, self.get_optimization_loop_limit())

    def get_optimization_runs(self):
        return self.optimization_runs_dict[self.input_file_name]

    def get_optimization_loop_limit(self):
        return self.optimization_team_loop_limit_dict[self.input_file_name]

    def find_pizza_swap(self, team, team_loop_limit):
        team_loop_id = 0
        for pizza_count in self.team_count_dict.keys():
            if int(pizza_count) == team["max_pizzas"]:
                min_i = team["id"] + 1
            else:
                min_i = 0

            for i in range(min_i, len(self.team_dict[pizza_count])):
                next_team = self.team_dict[pizza_count][i]
                if self.is_team_full(next_team) and self.make_pizza_swap(team, next_team):
                    return
                team_loop_id += 1

                if team_loop_id > team_loop_limit:
                    return

    def make_pizza_swap(self, team1, team2):
        default_score = self.get_team_score(team1) + self.get_team_score(team2)

        best_swap_score = None
        pizza_id1_for_swap = None
        pizza_id2_for_swap = None

        for pizza_id1 in range(len(team1["pizzas"])):
            for pizza_id2 in range(pizza_id1, len(team2["pizzas"])):
                swap_score = self.get_swap_score(pizza_id1, pizza_id2, team1, team2)

                if swap_score > default_score:
                    best_swap_score = swap_score
                    pizza_id1_for_swap = pizza_id1
                    pizza_id2_for_swap = pizza_id2

        if best_swap_score is None:
            return False

        pizza1 = team1["pizzas"][pizza_id1_for_swap]
        pizza2 = team2["pizzas"][pizza_id2_for_swap]

        self.team_dict[str(team1["max_pizzas"])][team1["id"]]["pizzas"][pizza_id1_for_swap] = pizza2
        self.team_dict[str(team2["max_pizzas"])][team2["id"]]["pizzas"][pizza_id2_for_swap] = pizza1

        return True

    def get_team_score(self, team):
        ingredients = self.get_team_ingredients(team)
        return len(ingredients) ** 2

    def get_swap_score(self, pizza_id1, pizza_id2, team1, team2):
        team1_copy = {"pizzas": team1["pizzas"].copy()}
        team2_copy = {"pizzas": team2["pizzas"].copy()}

        team1_copy["pizzas"][pizza_id1] = team2["pizzas"][pizza_id2]
        team2_copy["pizzas"][pizza_id2] = team1["pizzas"][pizza_id1]

        return self.get_team_score(team1_copy) + self.get_team_score(team2_copy)


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
        SolverWithOptimization(file_name).solve()
        print()
