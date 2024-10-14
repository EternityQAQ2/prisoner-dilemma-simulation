import numpy as np
import matplotlib.pyplot as plt
import random
import tkinter as tk
from tkinter import ttk


# Created By Linxi
# 2024
# prisoner's dilemma simulation
# 定义玩家类
class Player:
    def __init__(self, x, y, aspiration):
        self.x = x
        self.y = y
        self.strategy = 'C' if random.random() < 0.5 else 'B'  # 初始策略随机
        self.strategyM = 'M' if random.random() < 0.5 else 'S'  # M MOVE S STILL
        self.aspiration = aspiration  # 用户设置的期望收益
        self.bto_move_prob = 0.5  # BTO移动策略的初始概率 移动概率
        self.bto_game_prob = 0.5  # BTO博弈策略的初始概率 合作概率

    def decide_move(self, move_strategy):
        # 决定是否移动，依据选择的策略
        if move_strategy == 'BTO':
            return random.random() < self.bto_move_prob  # BTO选择移动的概率
        else:
            return random.random() < 0.5  # Random 随机移动

    def decide_strategy(self, game_strategy):
        # 决定是合作还是背叛，依据选择的策略
        if game_strategy == 'BTO':
            return 'C' if random.random() < self.bto_game_prob else 'B'  # BTO策略的合作/背叛
        else:
            return random.choice(['C', 'B'])  # 随机策略选择



# 初始化世界
def init_world(size, num_people, aspiration):
    world = [[None for _ in range(size)] for _ in range(size)]
    people = []
    for _ in range(num_people):
        while True:
            x, y = random.randint(0, size - 1), random.randint(0, size - 1)
            if world[x][y] is None:  # 确保一个位置只有一个人
                player = Player(x, y, aspiration)
                world[x][y] = player
                people.append(player)
                break
    return world, people


# 获取周围邻居
def get_neighbors(world, x, y, mode='four'):
    neighbors = []
    if mode == 'four':
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    else:
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in directions:
        nx, ny = (x + dx) % size, (y + dy) % size  # 四边相连
        if world[nx][ny] is not None:
            neighbors.append(world[nx][ny])
    return neighbors


# 计算某个
def calculate_payoff(player, neighbors, b_param):
    if not neighbors:
        return 0  # 没有邻居，收益为0

    c_count = sum(1 for n in neighbors if n.strategy == 'C')#  周围选择合作的人数
    if player.strategy == 'C':
        return c_count * 1  # 合作收益
        # 如果有人选B 自己没有收益，便不计算
    else:
        b_count = len(neighbors) - c_count#  周围选择背叛的人数
        return c_count * (1 + b_param) + b_count * b_param  # 背叛收益


# 进行一次博弈
def play_game(world, people, b_param, game_strategy, comparison_method):
    for player in people:
        neighbors = get_neighbors(world, player.x, player.y, comparison_method)
        payoff = calculate_payoff(player, neighbors, b_param)

        # BTO策略调整：根据本次收益与预期收益比较，调整移动和博弈策略的概率
        if payoff > player.aspiration:
            # 如果大于收益
            if player.strategy == 'C':
                player.bto_game_prob = min(player.bto_game_prob + 0.1, 1.0)
            if player.strategyM == 'M':
                player.bto_move_prob = min(player.bto_move_prob + 0.1, 1.0)
        else:
            if player.strategy == 'C':
                player.bto_game_prob = max(player.bto_game_prob - 0.1, 0.0)
            if player.strategyM == 'M':
                player.bto_move_prob = max(player.bto_move_prob - 0.1, 0.0)


        # 更新策略（合作或背叛）
        player.strategy = player.decide_strategy(game_strategy)


# 移动玩家
def move_players(world, people, size, move_strategy):
    new_world = [[None for _ in range(size)] for _ in range(size)]
    for player in people:
        if player.decide_move(move_strategy):
            while True:
                x, y = random.randint(0, size - 1), random.randint(0, size - 1)
                if new_world[x][y] is None:
                    new_world[x][y] = player
                    player.x, player.y = x, y
                    break
        else:
            new_world[player.x][player.y] = player
    return new_world


# 显示世界状态并保存为PNG
def display_world(world, iteration, save_all, show_all, save_png=False):
    img = np.zeros((size, size, 3))
    for i in range(size):
        for j in range(size):
            if world[i][j] is not None:
                if world[i][j].strategy == 'C':
                    img[i, j] = [0, 1, 0]  # 绿色表示合作
                else:
                    img[i, j] = [1, 0, 0]  # 红色表示背叛
    if save_png:
        if save_all:
            plt.imshow(img)
            plt.title(f'Iteration {iteration}')
            plt.axis('off')
            plt.savefig(f'game_result_iteration_{iteration}.png')
        elif iteration == times:  # 仅保存最后一张
            plt.imshow(img)
            plt.title(f'Iteration {iteration}')
            plt.axis('off')
            plt.savefig(f'final_game_result.png')

    if show_all or iteration == times:  # 选择是否显示每次迭代
        plt.imshow(img)
        plt.title(f'Iteration {iteration}')
        plt.axis('off')
        plt.show()


# 主程序运行逻辑
def run_simulation():
    global size, density, times, b_param, comparison_method, move_strategy, game_strategy, save_all, aspiration, show_all

    size = int(size_entry.get())  # 获取网格大小
    density = float(density_entry.get())  # 获取人口密度
    times = int(times_entry.get())  # 获取博弈次数
    b_param = float(b_param_entry.get())  # 获取收益参数b
    aspiration = float(aspiration_entry.get())  # 获取期望收益
    comparison_method = comparison_method_var.get()  # 获取比较方法（四格或八格）
    move_strategy = move_strategy_var.get()  # 获取移动策略
    game_strategy = game_strategy_var.get()  # 获取博弈策略
    save_all = save_all_var.get() == '1'  # 判断是否保存所有迭代的图片
    show_all = show_all_var.get() == '1'  # 判断是否显示每次迭代

    num_people = int(size * size * density)
    world, people = init_world(size, num_people, aspiration)

    for t in range(times):
        play_game(world, people, b_param, game_strategy, comparison_method)
        world = move_players(world, people, size, move_strategy)
        display_world(world, t + 1, save_all, show_all, save_png=True)


# 创建GUI窗口
root = tk.Tk()
root.title("Prisoner's Dilemma Simulation")

# 创建输入参数框
ttk.Label(root, text="Grid Size (50 default):").grid(row=0, column=0)
size_entry = ttk.Entry(root)
size_entry.grid(row=0, column=1)
size_entry.insert(0, "50")

ttk.Label(root, text="Population Density (0.5 default):").grid(row=1, column=0)
density_entry = ttk.Entry(root)
density_entry.grid(row=1, column=1)
density_entry.insert(0, "0.5")

ttk.Label(root, text="Game Iterations (10 default):").grid(row=2, column=0)
times_entry = ttk.Entry(root)
times_entry.grid(row=2, column=1)
times_entry.insert(0, "10")

ttk.Label(root, text="Betrayal Gain Parameter b (0.5 default):").grid(row=3, column=0)
b_param_entry = ttk.Entry(root)
b_param_entry.grid(row=3, column=1)
b_param_entry.insert(0, "0.5")

ttk.Label(root, text="Aspiration (1.0 default):").grid(row=4, column=0)
aspiration_entry = ttk.Entry(root)
aspiration_entry.grid(row=4, column=1)
aspiration_entry.insert(0, "1.0")

# 添加比较对象选择（四格或八格）
ttk.Label(root, text="Comparison Method:").grid(row=5, column=0)
comparison_method_var = tk.StringVar()
comparison_menu = ttk.Combobox(root, textvariable=comparison_method_var)
comparison_menu['values'] = ('four', 'eight')
comparison_menu.grid(row=5, column=1)
comparison_menu.current(0)

# 添加移动策略选择
ttk.Label(root, text="Move Strategy:").grid(row=6, column=0)
move_strategy_var = tk.StringVar()
move_strategy_menu = ttk.Combobox(root, textvariable=move_strategy_var)
move_strategy_menu['values'] = ('Random', 'BTO')
move_strategy_menu.grid(row=6, column=1)
move_strategy_menu.current(0)

# 添加博弈策略选择
ttk.Label(root, text="Game Strategy:").grid(row=7, column=0)
game_strategy_var = tk.StringVar()
game_strategy_menu = ttk.Combobox(root, textvariable=game_strategy_var)
game_strategy_menu['values'] = ('Random', 'BTO')
game_strategy_menu.grid(row=7, column=1)
game_strategy_menu.current(0)

# 添加保存图片选项（保存全部或只保存最后一张）
ttk.Label(root, text="Save All Iterations (1 for Yes, 0 for No):").grid(row=8, column=0)
save_all_var = tk.StringVar()
save_all_menu = ttk.Combobox(root, textvariable=save_all_var)
save_all_menu['values'] = ('0', '1')
save_all_menu.grid(row=8, column=1)
save_all_menu.current(0)

# 添加显示所有迭代图片的选项
ttk.Label(root, text="Show All Iterations (1 for Yes, 0 for No):").grid(row=9, column=0)
show_all_var = tk.StringVar()
show_all_menu = ttk.Combobox(root, textvariable=show_all_var)
show_all_menu['values'] = ('0', '1')
show_all_menu.grid(row=9, column=1)
show_all_menu.current(0)

# 创建运行按钮
run_button = ttk.Button(root, text="Run Simulation", command=run_simulation)
run_button.grid(row=10, column=0, columnspan=2)

# 启动GUI
root.mainloop()
