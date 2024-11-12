import matplotlib.pyplot as plt
import random
import copy
from matplotlib.animation import FuncAnimation
import numpy as np
import mycolor
from matplotlib.patches import Rectangle
import japanize_matplotlib

# rankは数字高い方が上
s_rank_list = [1, 2, 3, 4, 5]
c_rank_list = [0, 1, 2, 3, 4, 5, 6] 

num_students = 200
num_companies = 7
c_limit = 30
day_limit = 400

HITO_SIYA_LEVEL = 16.0 # 👁️
SEKKATI = 0.2
YASASISA = 0.1 # 人回避の重み

WIDTH = 500
HEIGHT = 500

goal_list = [[20, 400], [80, 400], [160, 400], [220, 400], [300, 400], [390, 400], [460, 400]]

colors = mycolor.CrandomList(num_companies)

class Simulation:
    def __init__(self):  # 初期化
        self.students = [Student(s, "normal") for s in range(num_students)]  # 学生の初期化
        self.companies = [Company(c) for c in range(num_companies)]  # 会社の初期化
        self.day = 0
        self.fcounter = 0 # フレーム調整用
        self.s_doing = list(range(num_students))  # 就活中学生idリスト
        self.c_recruiting = list(range(num_companies))  # 募集中会社idリスト
        self.result = {}  # s_id: c_id

        self.width = WIDTH
        self.height = HEIGHT

        self.c_adress = {} # 会社所在地
    
    def update(self):
        if self.day > 180 and self.day % 30 != 0:
            self.updating()
        self.day += 1
        print(f"Day: {self.day}")
    
    def updating(self):  # フレームの更新処理
        # time.sleep(2.0)
        resume = {}  # 履歴書
        # while self.day < day_limit:
        

       
        # 2. 応募
        s_to_c = {}
        
        for s in self.students:
            if s.id not in self.s_doing:  # 終了学生の除外
                continue
            c_applyable = copy.deepcopy(self.c_recruiting)
            s_to_c[s.id] = [c_applyable.pop(random.randrange(len(c_applyable))) for _ in range(min(s.onetime, len(c_applyable)))]
            resume[s.id] = s.rank

        # 3. 応募処理
        naitei_mail = {}
        oinori_mail = {}
        yuukasyoukenhoukokusyo = {}  # 有価証券報告書
        for c in self.companies:
            yuukasyoukenhoukokusyo[c.id] = c.rank
            self.c_adress[c.id] = c.position
            if c.id not in self.c_recruiting:  # 締め切った企業の除外
                continue
            c.process(s_to_c, resume, naitei_mail, oinori_mail)
        # print(naitei_mail)

        # 4. 結果通知
        for s in self.students:
            s_naiteisaki = []
            for c_id, s_list in naitei_mail.items():
                if s.id in s_list:
                    s_naiteisaki.append(c_id)
            s.decide_offer(s_naiteisaki, yuukasyoukenhoukokusyo, self.result, self.c_adress)
        
        # 5. 内定受領処理
        for s_id, c_id in self.result.items():
            if s_id in self.s_doing:  # 学生が就活中の場合
                for c in self.companies:
                    if c.id == c_id:  # 企業に通知
                        c.naitei_member.append(s_id)
                        if len(c.naitei_member) >= c_limit:
                            if c.id in self.c_recruiting:
                                self.c_recruiting.remove(c.id)  # 募集締め切り
                # 内定を受けた学生を就活中リストから削除
                self.s_doing.remove(s_id)
        for student in self.students:
            student.update(self.students)
        

        # for c in self.companies:
        #     print(f"-- id: {c.id} --\n{c.naitei_member}")

    def animate(self):
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)


        for c in self.companies:
            ax.plot(c.position[0], c.position[1], 'b*', markersize=10)
            ax.text(c.position[0], c.position[1] + 80, f"らんく: {c.rank}", ha='center', color='blue')
            

        scatter = ax.scatter([], [], c=[])
        texts = [ax.text(student.position[0], student.position[1], str(student.rank), ha='center') for student in self.students]
        texts2 = [ax.text(c.position[0], c.position[1] + 60, str(len(c.naitei_member)), ha='center') for c in self.companies]
        text3 = ax.text(250, 480, str(self.day), ha='center')

        def update(frame):
            self.update()
            scatter.set_offsets(np.array([student.position for student in self.students]))
            scatter.set_color([student.color for student in self.students])

            for i, student in enumerate(self.students):
                texts[i].set_position((student.position[0], student.position[1]))
                texts[i].set_text(str(student.rank))

            for i, c in enumerate(self.companies):
                texts2[i].set_position((c.position[0], c.position[1] + 60))
                texts2[i].set_text(str(len(c.naitei_member)) + "/" + str(c_limit))
            
            text3.set_text(str(self.day))

        anim = FuncAnimation(fig, update, frames=day_limit, interval=100, blit=False)
        plt.show()
    
        
class Student:
    def __init__(self, id, s_type):
        self.id = id
        self.rank = s_rank_list[id % len(s_rank_list)]
        self.type = s_type
        self.naiteisaki = []
        self.x = self.id
        self.y = self.rank * 20
        self.color = colors[self.rank]
        self.position = np.array([random.uniform(10, WIDTH-10), float((7-self.rank)*6)])

        self.goal = np.zeros(2)
        self.max_speed = self.rank * 2
        self.velocity = np.zeros(2)

        self.hitosiya = HITO_SIYA_LEVEL

        if self.type == "normal":
            self.start_day = 180
            self.cycle = 30
            self.onetime = 3  # 一度に応募する会社

    def __str__(self):
        return f"id: {self.id}, rank: {self.rank}"
    
    def decide_offer(self, naiteisaki, yuukasyoukenhoukokusyo, result, c_adress):
        # 内定処理
        naiteisaki = [c for c in naiteisaki if yuukasyoukenhoukokusyo[c] >= self.rank]
        if not naiteisaki:
            return
        kakutei = naiteisaki[random.randrange(len(naiteisaki))]
        result[self.id] = kakutei
        self.naiteisaki.append(kakutei)
        self.goal = np.array(c_adress[kakutei])

    def update(self, students):
        if np.array_equal(self.goal, [0, 0]):
            return
        sekkati_level_velocity = (self.goal - self.position)

        human_avoid_power = self.impact_avoid(students)
        if np.linalg.norm(sekkati_level_velocity) > 0:
            sekkati_level_velocity = sekkati_level_velocity / np.linalg.norm(sekkati_level_velocity) * self.max_speed

            self.velocity += (sekkati_level_velocity - self.velocity) * SEKKATI + human_avoid_power * YASASISA
        
        if np.linalg.norm(self.velocity) > self.max_speed:
            self.velocity = self.velocity / np.linalg.norm(self.velocity) * self.max_speed

        self.position += self.velocity
        

    def impact_avoid(self, students):
        human_avoid_power = np.zeros(2) # 初期化

        # -- 他人と回避 --
        for other in students:
            if other != self: # 自分じゃない
                diff = self.position - other.position
                dist = np.linalg.norm(diff)
                if 0 < dist < self.hitosiya:
                    human_avoid_power += diff / dist * (self.hitosiya - dist) # 他人が近いほど強く回避

        return human_avoid_power
class Company:
    def __init__(self, id):
        self.id = id  # 会社ID
        self.rank = c_rank_list[id % len(c_rank_list)]
        self.naitei_member = []  # 内定者リスト
        self.position = np.array(goal_list[self.rank])

    # 応募の処理
    def process(self, s_to_c, resume, naitei_mail, oinori_mail):
        s_applied = []  # 応募者
        s_success = []  # 当選者
        s_failed = []  # 不合格者
        
        for s_id, c_list in s_to_c.items():
            if self.id in c_list:  # 応募リストに企業IDがある場合、応募者として追加
                s_applied.append(s_id)

        # 絞り込み
        while len(s_applied) > c_limit - len(self.naitei_member):
            s_failed.append(s_applied.pop(random.randrange(len(s_applied))))
        
        # 内定処理
        for s in s_applied:
            if resume[s] > self.rank:  # 学生が優秀
                if random.uniform(0.0, 1.0) >= 0.1:
                    s_success.append(s)
                else:
                    s_failed.append(s)
            elif resume[s] == self.rank:  # 妥当
                if random.uniform(0.0, 1.0) >= 0.4:
                    s_success.append(s)
                else:
                    s_failed.append(s)
            else:  # 採用ミス
                if random.uniform(0.0, 1.0) >= 0.9:
                    s_success.append(s)
                else:
                    s_failed.append(s)

        naitei_mail[self.id] = s_success
        oinori_mail[self.id] = s_failed

sim = Simulation()


sim.animate()