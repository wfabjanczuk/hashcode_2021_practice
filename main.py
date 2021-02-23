from tqdm import tqdm


class IO:
    def __init__(self, input_file_name):
        self.pizza_count = 0
        self.team_count_dict = {"2": 0, "3": 0, "4": 0}

        self.pizza_list = []
        self.sorted_pizza_list = []
        self.all_ingredients = set()

        self.team_dict = {}
        self.full_teams_count = 0

        self.input_path_prefix = './input/'
        self.output_path_prefix = './output/'
        self.input_file_name = input_file_name
        self.read_input()

    def read_input(self):
        with open(self.input_path_prefix + self.input_file_name) as file:
            header_line = file.readline()
            self.pizza_count, two_teams, three_teams, four_teams = [int(i) for i in header_line.strip().split()]
            self.initialize_pizza_list(file)

            self.team_count_dict = {"2": two_teams, "3": three_teams, "4": four_teams}
            self.initialize_team_dicts(self.team_count_dict)

    def initialize_pizza_list(self, input_file):
        for pizza_id, line in enumerate(input_file.readlines()):
            ingredients = line.strip().split(' ')

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
        self.assign_reusable_pizzas_to_leftover_teams()

    def distance_from_mean(self, pizza):
        return (len(pizza["ingredients"]) - len(self.all_ingredients) / 2.0) ** 2

    def assign_pizzas_by_best_points_possible(self):
        all_teams_count = sum(self.team_count_dict.values())
        while self.full_teams_count < all_teams_count:

            filled_before = self.full_teams_count

            print(self.assign_pizzas_by_best_points_possible.__name__)
            for _ in tqdm(range(len(self.sorted_pizza_list))):

                best_pizza = self.sorted_pizza_list.pop()
                best_team = self.find_best_team_for_pizza(best_pizza, 10000)
                if best_team is None:
                    break
                else:
                    self.add_pizza_to_team(best_pizza, best_team)

            self.sorted_pizza_list = sorted(
                self.sorted_pizza_list + self.get_reusable_pizzas(),
                key=self.distance_from_mean,
                reverse=True
            )

            if self.full_teams_count == filled_before or len(self.sorted_pizza_list) == 0:
                break

    def find_best_team_for_pizza(self, pizza, team_loop_limit):
        best_score = None
        best_team = None

        team_loop_id = 0
        for pizza_count in self.team_dict:
            for team in self.team_dict[pizza_count]:
                if len(team["pizzas"]) < team["max_pizzas"]:
                    score = self.get_team_pizza_score(team, pizza)

                    if best_score is None or score > best_score:
                        best_score = score
                        best_team = team

                if team_loop_id > team_loop_limit:
                    return best_team
                team_loop_id += 1

        return best_team

    @staticmethod
    def get_team_pizza_score(team, pizza):
        current_ingredients = {ingredient for pizza in team["pizzas"] for ingredient in pizza["ingredients"]}

        new_score = len(current_ingredients.union(pizza["ingredients"])) ** 2
        common_ingredients_squared = (len(current_ingredients) + len(pizza["ingredients"])) / 2.0

        return new_score - common_ingredients_squared

    def get_reusable_pizzas(self):
        reusable_pizzas = []

        for pizza_count in self.team_dict:
            for team in self.team_dict[pizza_count]:
                if team["max_pizzas"] != len(team["pizzas"]):
                    reusable_pizzas += team["pizzas"]
                    self.team_dict[pizza_count][team["id"]]["pizzas"] = []

        return reusable_pizzas

    def assign_reusable_pizzas_to_leftover_teams(self):
        if len(self.sorted_pizza_list) == 0:
            return

        leftover_teams = self.get_leftover_teams()

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

    def get_leftover_teams(self):
        leftover_teams = []

        for pizza_count in reversed(self.team_count_dict.keys()):
            for team in self.team_dict[pizza_count]:
                if team["max_pizzas"] != len(team["pizzas"]):
                    leftover_teams.append(team)

        return leftover_teams

    def assign_best_pizza_to_team(self, team, pizza_loop_limit):
        best_score = None
        best_pizza_loop_id = None

        for pizza_loop_id, pizza in enumerate(self.sorted_pizza_list):
            score = self.get_team_pizza_score(team, pizza)

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
        print()
