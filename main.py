from tqdm import tqdm


class Solver:
    def __init__(self, file_name):
        self.pizza_count, self.t_2, self.t_3, self.t_4 = [0, 0, 0, 0]
        self.teams_count = 0
        self.pizza_list = []
        self.sorted_pizza_list = []
        self.merged_pizza_list = []
        self.team_dict = {}
        self.all_ingredients = set()

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
            self.teams_count = self.t_2 + self.t_3 + self.t_4

            pizza_id = 0
            for line in file.readlines():
                ingredients = line.strip().split(' ')
                ingredients_count = int(ingredients.pop(0))
                self.all_ingredients = self.all_ingredients.union(set(ingredients))

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
                    "list": self.get_empty_team_list(2, self.t_2)
                },
                "3": {
                    "first_free_id": 0,
                    "list": self.get_empty_team_list(3, self.t_3)
                },
                "4": {
                    "first_free_id": 0,
                    "list": self.get_empty_team_list(4, self.t_4)
                }
            }

    @staticmethod
    def get_empty_team_list(max_pizzas, count):
        return [{"id": i, "pizzas": [], "max_pizzas": max_pizzas, "points": 0} for i in range(count)]

    def solve(self):
        self.sorted_pizza_list = sorted(self.pizza_list, key=self.distance_from_mean, reverse=True)

        while self.filled_teams_count < self.teams_count:
            filled_before = self.filled_teams_count

            print("Assigning pizzas everywhere by best points possible")
            for _ in tqdm(range(len(self.sorted_pizza_list))):
                best_pizza = self.sorted_pizza_list.pop()
                best_team = self.add_pizza_to_best_team(best_pizza)

                if best_team is None:
                    break

            self.sorted_pizza_list += sorted(self.get_reusable_pizzas(), key=self.distance_from_mean, reverse=True)
            if len(self.sorted_pizza_list) == 0:
                break

            filled_after = self.filled_teams_count

            if filled_after == filled_before:
                break

        if len(self.sorted_pizza_list) == 0:
            return

        leftover_teams = self.get_leftover_teams()

        print("Assigning reusable pizzas to leftover teams")
        for _ in tqdm(range(len(leftover_teams))):
            filled_before = self.filled_teams_count

            current_team = leftover_teams.pop()
            while len(self.sorted_pizza_list):
                result = self.assign_best_pizza_to_team(current_team)

                if result is False:
                    break

            filled_after = self.filled_teams_count

            if filled_after == filled_before:
                break

        self.print_result()

    def distance_from_mean(self, pizza):
        return (pizza["ingredients_count"] - len(self.all_ingredients) / 2.0) ** 2

    def add_pizza_to_best_team(self, best_pizza):
        best_score = None
        best_team_id = None
        best_count = None

        loop_id = 0
        for count in self.team_dict:
            team_id = 0
            for team in self.team_dict[count]["list"]:
                if len(team["pizzas"]) < team["max_pizzas"]:
                    score = self.get_score(team, best_pizza)

                    if best_score is None or score > best_score:
                        best_score = score
                        best_team_id = team_id
                        best_count = count

                team_id += 1
                loop_id += 1

                if loop_id > 10000:
                    break

            if loop_id > 10000:
                break

        if best_team_id is not None:
            self.team_dict[best_count]["list"][best_team_id]["pizzas"].append(best_pizza)

            current_team = self.team_dict[best_count]["list"][best_team_id]
            if len(current_team["pizzas"]) == current_team["max_pizzas"]:
                self.filled_teams_count += 1
            return True
        else:
            return False

    @staticmethod
    def get_score(team, pizza):
        current_ingredients = {
            i for p in team["pizzas"] for i in p["ingredients"]
        }

        return len(current_ingredients.union(pizza["ingredients"])) ** 2 - (
                len(current_ingredients) + pizza["ingredients_count"]) / 2.0

    def print_result(self):
        with open(self.output_path_prefix + self.file_name, 'w+') as file:
            file.write(str(self.filled_teams_count) + "\n")

            for count in self.team_dict:
                for team in self.team_dict[count]["list"]:
                    if team["max_pizzas"] == len(team["pizzas"]):
                        line = str(team["max_pizzas"]) + " " + " ".join([str(p["id"]) for p in team["pizzas"]])
                        file.write(line + "\n")

    def get_reusable_pizzas(self):
        reusable_pizzas = []

        for count in self.team_dict:
            for team in self.team_dict[count]["list"]:
                if team["max_pizzas"] != len(team["pizzas"]):
                    reusable_pizzas += team["pizzas"]
                    self.team_dict[count]["list"][team["id"]]["pizzas"] = []

        return reusable_pizzas

    def get_leftover_teams(self):
        leftover_teams = []

        for count in ["4", "3", "2"]:
            for team in self.team_dict[count]["list"]:
                if team["max_pizzas"] != len(team["pizzas"]):
                    leftover_teams.append(team)

        return leftover_teams

    def assign_best_pizza_to_team(self, current_team):
        if not len(self.sorted_pizza_list):
            return False

        max_score = None
        best_loop_id = None
        loop_id = 0

        for possible_pizza in self.sorted_pizza_list:
            score = self.get_score(current_team, possible_pizza)

            if max_score is None or score > max_score:
                max_score = score
                best_loop_id = loop_id

            loop_id += 1

        best_pizza = self.sorted_pizza_list.pop(best_loop_id)
        return self.add_pizza_to_team(best_pizza, current_team)

    def add_pizza_to_team(self, pizza, team):
        self.team_dict[str(team["max_pizzas"])]["list"][team["id"]]["pizzas"].append(pizza)
        updated_team = self.team_dict[str(team["max_pizzas"])]["list"][team["id"]]

        if len(updated_team["pizzas"]) == updated_team["max_pizzas"]:
            self.filled_teams_count += 1
            return False

        return True


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
