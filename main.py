import pyxel
import random
import copy
import time

# rankは数字高い方が上
s_rank_list = [1, 2, 3, 4, 5]
c_rank_list = [0, 1, 2, 3, 4, 5, 6] 

num_students = 200
num_companies = 7
c_limit = 30
day_limit = 400

class App:
    def __init__(self):  # 初期化
        pyxel.init(160, 120, fps=10)
        pyxel.load("resource.pyxres")  # リソース読み込み
        self.students = [Student(s, "normal") for s in range(num_students)]  # 学生の初期化
        self.companies = [Company(c) for c in range(num_companies)]  # 会社の初期化
        self.day = 0
        self.fcounter = 0 # フレーム調整用
        self.s_doing = list(range(num_students))  # 就活中学生idリスト
        self.c_recruiting = list(range(num_companies))  # 募集中会社idリスト
        self.result = {}  # s_id: c_id

        while self.day < day_limit:
            pyxel.run(self.update, self.draw)  # アプリケーションの実行
        # pyxel.quit()


    def update(self):
        if self.fcounter % 200 == 0:
            self.updating()
        self.fcounter += 1
        time.sleep(3.0)

    def updating(self):  # フレームの更新処理
        # time.sleep(2.0)
        resume = {}  # 履歴書
        while self.day < day_limit:
            print(f"Day: {self.day}")

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
                if c.id not in self.c_recruiting:  # 締め切った企業の除外
                    continue
                c.process(s_to_c, resume, naitei_mail, oinori_mail)

            # 4. 結果通知
            for s in self.students:
                s_naiteisaki = []
                for c_id, s_list in naitei_mail.items():
                    if s.id in s_list:
                        s_naiteisaki.append(c_id)
                s.decide_offer(s_naiteisaki, yuukasyoukenhoukokusyo, self.result)
            
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

            self.day += 1

        for c in self.companies:
            print(f"-- id: {c.id} --\n{c.naitei_member}")
        
        pyxel.quit()


    def draw(self):  # 描画処理
        time.sleep(2.0)
        pyxel.cls(0)
        for student in self.students:
            student.draw()
        for company in self.companies:
            company.draw()

class Student:
    def __init__(self, id, s_type):
        self.id = id
        self.rank = s_rank_list[id % len(s_rank_list)]
        self.type = s_type
        self.naiteisaki = []
        self.x = self.id
        self.y = self.rank * 20
        
        if self.type == "normal":
            self.start_day = 180
            self.cycle = 30
            self.onetime = 3  # 一度に応募する会社

    def __str__(self):
        return f"id: {self.id}, rank: {self.rank}"
    
    def decide_offer(self, naiteisaki, yuukasyoukenhoukokusyo, result):
        # 内定処理
        naiteisaki = [c for c in naiteisaki if yuukasyoukenhoukokusyo[c] >= self.rank]
        if not naiteisaki:
            return
        kakutei = naiteisaki[random.randrange(len(naiteisaki))]
        result[self.id] = kakutei
        self.naiteisaki.append(kakutei)

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 7, 0, 15, 7, 0)

class Company:
    def __init__(self, id):
        self.id = id  # 会社ID
        self.rank = c_rank_list[id % len(c_rank_list)]
        self.naitei_member = []  # 内定者リスト

    def draw(self):
        pyxel.blt(10 + 15 * (self.id + 1), 10, 0, 0, 0, 7, 7, 0)

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

App()
