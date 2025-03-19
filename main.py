import numpy as np
import matplotlib.pyplot as plt
import random
import tkinter as tk
from tkinter import ttk

# ================================
#      Created by Linxi (改进)
#        囚徒困境模拟器
# ================================

class Player:
    def __init__(self, x, y, aspiration):
        self.x = x
        self.y = y
        # 初始策略：合作(C) / 背叛(B)
        self.strategy = 'C' if random.random() < 0.5 else 'B'
        # 初始移动方式：移动(M) / 不动(S)
        self.strategyM = 'M' if random.random() < 0.2 else 'S'
        
        # 记录该玩家本轮的收益
        self.payoff = 0
        
        # 期望收益 (LEBO 策略会用到)
        self.aspiration = aspiration

        # 针对 LEBO 学习方法：记录合作/移动的概率，初始都设为 0.5
        self.prob_cooperate = 0.5  # (C/B) 的概率
        self.prob_move = 0.5      # (M/S) 的概率

    def decide_strategy(self, game_strategy, neighbors, comparison_method):
        """
        根据游戏策略确定本轮玩家要使用的博弈策略 (C/B)。
        - Random: 随机选择合作或背叛
        - BTO:    模仿收益最高邻居的策略
        - MAJ:    模仿邻居中出现最多的策略
        - LEBO:   基于自身收益与期望比较，对本轮采用的策略做概率更新后，再决定下一轮策略
        """
        if game_strategy == 'Random':
            return random.choice(['C', 'B'])

        elif game_strategy == 'BTO':
            if not neighbors:
                return self.strategy
            # 寻找收益最高的邻居并模仿其策略
            best_neighbor = max(neighbors, key=lambda n: n.payoff)
            return best_neighbor.strategy

        elif game_strategy == 'MAJ':
            if not neighbors:
                return self.strategy
            # 统计邻居中 C 和 B 的数量
            c_count = sum(1 for n in neighbors if n.strategy == 'C')
            b_count = len(neighbors) - c_count
            if c_count > b_count:
                return 'C'
            elif b_count > c_count:
                return 'B'
            else:
                # 平局则随机
                return random.choice(['C', 'B'])

        elif game_strategy == 'LEBO':
            # 若 payoff > aspiration，根据当前策略调整合作概率 prob_cooperate
            if self.payoff > self.aspiration:
                if self.strategy == 'C':
                    # 本轮用的是 C 且收益较好 -> 提高合作概率
                    self.prob_cooperate = min(1.0, self.prob_cooperate + 0.1)
                else:
                    # 本轮用的是 B 且收益较好 -> 降低合作概率
                    self.prob_cooperate = max(0.0, self.prob_cooperate - 0.1)
            else:
                # payoff <= aspiration
                if self.strategy == 'C':
                    # 本轮用的是 C 且收益不理想 -> 降低合作概率
                    self.prob_cooperate = max(0.0, self.prob_cooperate - 0.1)
                else:
                    # 本轮用的是 B 且收益不理想 -> 提高合作概率
                    self.prob_cooperate = min(1.0, self.prob_cooperate + 0.1)

            # 最终根据更新后的概率决定新的策略
            return 'C' if random.random() < self.prob_cooperate else 'B'

        else:
            # 其他情况保持原策略
            return self.strategy

    def decide_move(self, move_strategy, neighbors, comparison_method):
        """
        根据移动策略决定本轮是否要移动 (返回 True/False)，并更新 self.strategyM。
        - Random: 随机移动
        - BTO:    模仿收益最高邻居的移动决策
        - MAJ:    模仿邻居中出现最多的移动决策
        - LEBO:   基于自身收益与期望比较，对本轮采用的移动方式做概率更新后，再决定下一轮是否移动
        """
        if move_strategy == 'Random':
            choice = random.random() < 0.5
            self.strategyM = 'M' if choice else 'S'
            return choice

        elif move_strategy == 'BTO':
            if not neighbors:
                return (self.strategyM == 'M')
            # 找到收益最高的邻居并模仿其移动方式
            best_neighbor = max(neighbors, key=lambda n: n.payoff)
            self.strategyM = best_neighbor.strategyM
            return (self.strategyM == 'M')

        elif move_strategy == 'MAJ':
            if not neighbors:
                return (self.strategyM == 'M')
            # 统计邻居中 M 和 S 的数量
            m_count = sum(1 for n in neighbors if n.strategyM == 'M')
            s_count = len(neighbors) - m_count
            if m_count > s_count:
                self.strategyM = 'M'
            elif s_count > m_count:
                self.strategyM = 'S'
            else:
                # 平局则随机
                self.strategyM = random.choice(['M', 'S'])
            return (self.strategyM == 'M')

        elif move_strategy == 'LEBO':
            # 若 payoff > aspiration，根据当前移动方式调整移动概率 prob_move
            if self.payoff > self.aspiration:
                if self.strategyM == 'M':
                    self.prob_move = min(1.0, self.prob_move + 0.1)
                else:
                    self.prob_move = max(0.0, self.prob_move - 0.1)
            else:
                # payoff <= aspiration
                if self.strategyM == 'M':
                    self.prob_move = max(0.0, self.prob_move - 0.1)
                else:
                    self.prob_move = min(1.0, self.prob_move + 0.1)

            choice = (random.random() < self.prob_move)
            self.strategyM = 'M' if choice else 'S'
            return choice

        else:
            self.strategyM = 'S'
            return False


# ------------ 初始化世界 ------------
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

# ------------ 获取邻居 ------------
def get_neighbors(world, x, y, mode='four'):
    """
    mode='four'  -> 上下左右 (von Neumann neighborhood)
    mode='eight' -> 周围八格（含对角线，Moore neighborhood）
    """
    size = len(world)
    neighbors = []
    if mode == 'four':
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    else:
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),           (0, 1),
                      (1, -1),  (1, 0),  (1, 1)]

    for dx, dy in directions:
        nx, ny = (x + dx) % size, (y + dy) % size  # 边界循环
        if world[nx][ny] is not None:
            neighbors.append(world[nx][ny])
    return neighbors

# ------------ 计算单个玩家收益 ------------
def calculate_payoff(player, neighbors, b_param):
    """
    囚徒困境的简化模型：
      - 如果玩家是合作(C)，对方也合作则玩家+1，若对方背叛则玩家+0
      - 如果玩家是背叛(B)，对方合作则玩家+(1+b_param)，对方背叛则玩家+b_param
    由于与所有邻居分别博弈，收益相加
    """
    if not neighbors:
        return 0  # 没有邻居，收益为0

    payoff = 0
    for n in neighbors:
        if player.strategy == 'C':
            if n.strategy == 'C':
                payoff += 1.7 # 合作收益略高于b
            else:
                payoff += 0
        else:
            # player.strategy == 'B'
            if n.strategy == 'C':
                payoff += (1 + b_param)
            else:
                payoff += b_param
    return payoff

# ------------ 进行一轮博弈 (计算收益 & 更新策略) ------------
def play_game(world, people, b_param, game_strategy, comparison_method):
    """
    1) 计算每个玩家的收益
    2) 更新他们的博弈策略 (C/B)
    """
    for player in people:
        neighbors = get_neighbors(world, player.x, player.y, mode=comparison_method)
        player.payoff = calculate_payoff(player, neighbors, b_param)

    for player in people:
        neighbors = get_neighbors(world, player.x, player.y, mode=comparison_method)
        player.strategy = player.decide_strategy(game_strategy, neighbors, comparison_method)

# ------------ 移动玩家位置 ------------
def move_players(world, people, size, move_strategy, comparison_method):
    """
    根据移动策略，决定是否离开当前位置。如果移动，则随机找一个空位落脚。
    """
    new_world = [[None for _ in range(size)] for _ in range(size)]
    for player in people:
        neighbors = get_neighbors(world, player.x, player.y, mode=comparison_method)
        want_move = player.decide_move(move_strategy, neighbors, comparison_method)

        if want_move:
            # 随机找个空位
            while True:
                x, y = random.randint(0, size - 1), random.randint(0, size - 1)
                if new_world[x][y] is None:
                    new_world[x][y] = player
                    player.x, player.y = x, y
                    break
        else:
            new_world[player.x][player.y] = player
    return new_world

# ------------ 显示世界状态 + 保存PNG ------------
def display_world(world, iteration, save_all, show_all, save_png=False):
    size = len(world)
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
            plt.close()
        else:
            # 只在最后一次保存 (见主循环外)
            pass
    
    if show_all:
        plt.imshow(img)
        plt.title(f'Iteration {iteration}')
        plt.axis('off')
        plt.show()

# ------------ 主程序运行 ------------
def run_simulation():
    global size, density, times, b_param, comparison_method, move_strategy, game_strategy
    global save_all, aspiration, show_all

    size = int(size_entry.get())            # 网格大小
    density = float(density_entry.get())    # 人口密度
    times = int(times_entry.get())          # 迭代次数
    b_param = float(b_param_entry.get())    # 背叛收益参数 b
    aspiration = float(aspiration_entry.get())  # 期望收益(LEBO方法中用到)
    
    comparison_method = comparison_method_var.get()  # 邻居比较方式 (four/eight)
    move_strategy = move_strategy_var.get()          # 移动策略 (Random/BTO/MAJ/LEBO)
    game_strategy = game_strategy_var.get()          # 博弈策略 (Random/BTO/MAJ/LEBO)
    
    save_all = save_all_var.get() == '1'             # 是否保存所有迭代图
    show_all = show_all_var.get() == '1'             # 是否显示所有迭代图

    num_people = int(size * size * density)
    world, people = init_world(size, num_people, aspiration)

    # 用于记录日志
    iteration_log = []
    chances = 1
    # 打开日志文件（写模式），每次运行都会覆盖之前内容
    with open("iteration_log.txt", "w", encoding="utf-8") as log_file:
        log_file.write("===== Simulation iteration logs =====\n")
        log_file.flush()  # 强制刷新
        for t in range(times):
            # 1) 博弈并更新策略
            play_game(world, people, b_param, game_strategy, comparison_method)
            # 2) 移动
            world = move_players(world, people, size, move_strategy, comparison_method)
            # 3) 显示 & 保存
            display_world(world, t + 1, save_all, show_all, save_png=True)

            # 记录日志：统计合作/背叛/移动/不动人数
            c_count = sum(1 for p in people if p.strategy == 'C')
            b_count = sum(1 for p in people if p.strategy == 'B')
            m_count = sum(1 for p in people if p.strategyM == 'M')
            s_count = sum(1 for p in people if p.strategyM == 'S')
            
            # if(m_count == 0 and chances ==1):
            #     #迭代结束
            #     print(f"迭代终止次数:{t}")
            #     chances = 0

        
            iteration_log.append((t+1, c_count, b_count, m_count, s_count))

            # 写入日志文件 & 控制台输出
            log_line = (f"Iteration {t+1} -> Cooperators: {c_count}, "
                        f"Betrayers: {b_count}, Movers: {m_count}, Still: {s_count}")
            print(log_line)
            log_file.write(log_line + "\n")

        # 如果只保存最后一张，则在这里保存
        if not save_all:
            display_world(world, times, save_all=False, show_all=True, save_png=True)
            plt.savefig("final_game_result.png")
            plt.close()

        # 写入最终日志
        log_file.write("\nSimulation finished. Final log data:\n")
        print("\nSimulation finished. Final log data:")
        for entry in iteration_log:
            summary_line = (f"Iteration {entry[0]}: "
                            f"C={entry[1]}, B={entry[2]}, M={entry[3]}, S={entry[4]}")
            print(summary_line)
            log_file.write(summary_line + "\n")


# ------------ 创建GUI ------------
root = tk.Tk()
root.title("Prisoner's Dilemma Simulation (Modified)")

# -- 参数输入区域 --
ttk.Label(root, text="Grid Size (50 default):").grid(row=0, column=0)
size_entry = ttk.Entry(root)
size_entry.grid(row=0, column=1)
size_entry.insert(0, "100")

ttk.Label(root, text="Population Density (0.5 default):").grid(row=1, column=0)
density_entry = ttk.Entry(root)
density_entry.grid(row=1, column=1)
density_entry.insert(0, "0.5")

ttk.Label(root, text="Game Iterations (1000 default):").grid(row=2, column=0)
times_entry = ttk.Entry(root)
times_entry.grid(row=2, column=1)
times_entry.insert(0, "1000")

ttk.Label(root, text="Betrayal Gain Parameter b (0.5 default):").grid(row=3, column=0)
b_param_entry = ttk.Entry(root)
b_param_entry.grid(row=3, column=1)
b_param_entry.insert(0, "0.5")

ttk.Label(root, text="Aspiration (1.0 default):").grid(row=4, column=0)
aspiration_entry = ttk.Entry(root)
aspiration_entry.grid(row=4, column=1)
aspiration_entry.insert(0, "7.0")

# 比较方式
ttk.Label(root, text="Comparison Method:").grid(row=5, column=0)
comparison_method_var = tk.StringVar()
comparison_menu = ttk.Combobox(root, textvariable=comparison_method_var)
comparison_menu['values'] = ('four', 'eight')
comparison_menu.grid(row=5, column=1)
comparison_menu.current(0)

# 移动策略
ttk.Label(root, text="Move Strategy:").grid(row=6, column=0)
move_strategy_var = tk.StringVar()
move_strategy_menu = ttk.Combobox(root, textvariable=move_strategy_var)
move_strategy_menu['values'] = ('Random', 'BTO', 'MAJ', 'LEBO')
move_strategy_menu.grid(row=6, column=1)
move_strategy_menu.current(3)

# 博弈策略
ttk.Label(root, text="Game Strategy:").grid(row=7, column=0)
game_strategy_var = tk.StringVar()
game_strategy_menu = ttk.Combobox(root, textvariable=game_strategy_var)
game_strategy_menu['values'] = ('Random', 'BTO', 'MAJ', 'LEBO')
game_strategy_menu.grid(row=7, column=1)
game_strategy_menu.current(3)

# 是否保存所有迭代图
ttk.Label(root, text="Save All Iterations (1 for Yes, 0 for No):").grid(row=8, column=0)
save_all_var = tk.StringVar()
save_all_menu = ttk.Combobox(root, textvariable=save_all_var)
save_all_menu['values'] = ('0', '1')
save_all_menu.grid(row=8, column=1)
save_all_menu.current(0)

# 是否显示所有迭代图
ttk.Label(root, text="Show All Iterations (1 for Yes, 0 for No):").grid(row=9, column=0)
show_all_var = tk.StringVar()
show_all_menu = ttk.Combobox(root, textvariable=show_all_var)
show_all_menu['values'] = ('0', '1')
show_all_menu.grid(row=9, column=1)
show_all_menu.current(0)

# -- 运行按钮 --
run_button = ttk.Button(root, text="Run Simulation", command=run_simulation)
run_button.grid(row=10, column=0, columnspan=2)

root.mainloop()
