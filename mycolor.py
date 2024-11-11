import random

color_list = [
    "skyblue", 
    "Cyan", # シアン
    "MediumAquamarine", # ミディアム・アクアマリン
    "Darkturquoise", # ダーク・ターコイズ
    "DarkOliveGreen",
    "Limegreen", # ライムグリーン
    "HotPink",
    "Indigo",
    "DarkSlateBlue", # ダーク・スレート・ブルー
    "DarkSlateGray", # ダーク・スレート・グレー
    "CornflowerBlue", # コーン・フラワー・ブルー
    "AntiqueWhite",
    "DarkSalmon",
    "Tomato", # 🍅
    "LightSalmon",
    "MediumPurple",
    "Mediumvioletred", # ミディアム・バイオレット・レッド
    "PaleVioletRed", # ペール・バイオレット・レッド
    "#9e76b4", # アメシスト
    "Rosybrown", # ロージー・ブラウン
    "DarkMagenta" # ダーク・マゼンタ
    ]

# ランダムカラー
def Crandom():
    random_color = color_list[random.randint(0,len(color_list)-1)]
    return random_color

# ランダムカラーリスト
def CrandomList(number):
    use_colors = []
    for n in range(number):
        random_color = color_list[random.randint(0,len(color_list)-1)]
        use_colors.append(random_color)
    return use_colors