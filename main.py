class Solver:
    def __init__(self, file_name):
        self.pizza_count, self.t_2, self.t_3, self.t_4 = [0, 0, 0, 0]
        self.pizza_list = []
        self.team_dict = {}

        self.input_path_prefix = './input/'
        self.read_file(file_name)

    def read_file(self, file_name):
        with open(self.input_path_prefix + file_name) as file:
            header_line = file.readline()
            self.pizza_count, self.t_2, self.t_3, self.t_4 = [int(i) for i in header_line.strip().split()]

            pizza_id = 0
            for line in file.readlines():
                ingredients = line.strip().split(', ')
                pizza = {
                    "id": pizza_id,
                    "ingredients": ingredients,
                    "ingredients_count": len(ingredients),
                    "assigned_team": None
                }

                self.pizza_list.append(pizza)
                pizza_id += 1

            self.team_dict = {
                "2": [{"id": i, "pizzas": [], "points": 0} for i in range(self.t_2)],
                "3": [{"id": i, "pizzas": [], "points": 0} for i in range(self.t_3)],
                "4": [{"id": i, "pizzas": [], "points": 0} for i in range(self.t_4)]
            }

    def solve(self):
        print('gg')


if __name__ == '__main__':
    Solver('a_example').solve()
