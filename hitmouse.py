import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance
import random
import winsound
import csv        
import os           
from datetime import datetime 

# 窗口与洞位配置 
WIN_W, WIN_H = 1000, 750  # 适配背景图比例

# 16个洞口 (中心x, 中心y, 地鼠大小)  background.jpg 实际洞位标定
HOLES = [
    (225, 294, 55),  (405, 295, 55),  (584, 295, 55),  (751, 295, 55),   
    (112, 380, 80),  (304, 380, 80),  (498, 380, 80),  (692, 379, 80),   (882, 379, 80),  
    (127, 496, 110), (372, 496, 110), (627, 497, 110), (868, 495, 110), 
    (166, 655, 150), (498, 656, 150), (830, 655, 150),                   
]

# 照片缓存
mole_photos = {}
golden_photos = {}


#界面
root=tk.Tk()
root.title("打地鼠")
root.geometry(f"{WIN_W}x{WIN_H}")

#加载背景图
try:
    bg_img = Image.open("background.jpg").resize((WIN_W, WIN_H))
    bg_photo = ImageTk.PhotoImage(bg_img)
except Exception as e:
    bg_photo = None
#全局变量
score=0
remaining_time=60
username='玩家1'
is_golden = False
combo = 0        
max_combo = 0    
mole_timer = None  

# 加载图片
img = Image.open('mole.png').convert('RGBA')
img_w, img_h = img.size


def crop_mole(image):
    #去掉地鼠图片底部的土堆，只保留从洞里钻出来的部分
    w, h = image.size
    return image.crop((0, 0, w, int(h * 0.58)))


photo = ImageTk.PhotoImage(crop_mole(img))

# 加载锤子图片
try:
    hammer_img = Image.open("锤子.png").resize((80, 80))
    hammer_photo = ImageTk.PhotoImage(hammer_img)
except:
    hammer_photo = None

# 基于原图生成金色地鼠（加饱和度 + 加亮度）
golden_img = ImageEnhance.Color(crop_mole(img)).enhance(2.5)
golden_img = ImageEnhance.Brightness(golden_img).enhance(1.2)
golden_photo = ImageTk.PhotoImage(golden_img)

#start--------------------------------
start_frame = tk.Frame(root, width=WIN_W, height=WIN_H)
start_frame.pack_propagate(False)
start_frame.pack()      

#标题
tk.Label(start_frame, text="⛏️ 打地鼠", font=("微软雅黑", 40, "bold")).pack(pady=100)

#名字
tk.Label(start_frame, text="玩家昵称：", font=("微软雅黑", 14)).pack(pady=5)
name_entry = tk.Entry(start_frame, font=("微软雅黑", 14), width=20)
name_entry.pack()

#选择时长
time_var = tk.IntVar(value=60)  # 默认选中60秒

tk.Radiobutton(start_frame, text="30秒", variable=time_var, value=30).pack()
tk.Radiobutton(start_frame, text="60秒", variable=time_var, value=60).pack()
tk.Radiobutton(start_frame, text="90秒", variable=time_var, value=90).pack() 


# 点击开始后
def start_game():
    global username, remaining_time, score
    # 1. 读取玩家输入
    username = name_entry.get().strip() or "匿名"
    remaining_time = int(time_var.get())
    score = 0

    # 2. 切换盒子：隐藏开始界面，显示游戏界面
    start_frame.pack_forget()
    game_frame.pack()

    #重置后续状态
    global combo, max_combo, mole_timer, is_golden, current_hole
    combo = 0
    max_combo = 0
    if mole_timer:
        root.after_cancel(mole_timer)
    mole_timer = None
    combo_label.config(text="")
    is_golden = False
    current_hole = 0

    # 初始化地鼠位置和大小
    photo_to_use = get_mole_photo(80, False)
    game_canvas.itemconfig(btn, image=photo_to_use)
    x, y, size = HOLES[current_hole]
    game_canvas.coords(btn, x, y - photo_to_use.height() // 2)
    game_canvas.tag_raise(btn)

    # 3. 初始化游戏
    update_label()
    timing()                    # 启动倒计时

tk.Button(start_frame, text="开始游戏", font=("微软雅黑", 14), 
          width=12, command=start_game).pack(pady=40)

#游戏界面--------------------------------
game_frame = tk.Frame(root, width=WIN_W, height=WIN_H)
game_frame.pack_propagate(False)

# 正确支持透明 PNG 叠加
game_canvas = tk.Canvas(game_frame, width=WIN_W, height=WIN_H, highlightthickness=0)
game_canvas.pack(fill="both", expand=True)
if bg_photo:
    game_canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    print("背景加载成功")
else:
    print("背景加载失败，文件可能不存在")

#label
label = tk.Label(game_frame, text="", bg="#a8e063")
combo_label = tk.Label(game_frame, text="", font=("微软雅黑", 16, "bold"), fg="red", bg="#a8e063")
combo_label.place(x=350, y=50)
label.place(x=300, y=10)



def update_label():
    label.config(text=f"玩家：{username} | 得分：{score} | 剩余时间：{remaining_time}")

#时间
def timing():
    global remaining_time
    if remaining_time>0:
        remaining_time-=1
        update_label()
        root.after(1000,timing)
    else:
        game_over()

def game_over():
    #切换到结束界面
    global mole_timer
    if mole_timer:
        root.after_cancel(mole_timer)#取消计时
        mole_timer = None
    game_frame.pack_forget()
    end_frame.pack()

    final_label.config(text=f"🎉 游戏结束！\n\n玩家：{username}\n最终得分：{score}")
    
    save_score()

    try:
        winsound.MessageBeep(winsound.MB_ICONHAND)  # 结束提示音（Windows）
    except:
        pass
    
#读取csv
def save_score():
    file_exists = os.path.exists("scores.csv")
    with open("scores.csv", "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        # 如果文件不存在，先写入表头
        if not file_exists:
            writer.writerow(["用户名", "得分", "设定时长", "最高连击", "日期"])
        writer.writerow([
        username,
        score,
        time_var.get(),
        max_combo,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

#排行榜
def show():
    #弹窗显示
    window = tk.Toplevel(root)           
    window.title("🏆 排行榜")
    window.geometry("500x600")
    window.resizable(False, False)

    # 标题
    tk.Label(window, text="🏆 排行榜 Top 10", font=("微软雅黑", 20, "bold")).pack(pady=15)
    #表头
    # 表格容器（
    table = tk.Frame(window)
    table.pack(fill="x", padx=20)

    # 列定义：(显示文字, 字符宽度)
    cols = [("排名", 6), ("玩家", 12), ("得分", 8), ("时长", 6), ("连击", 6), ("日期", 14)]

    # 表头
    for c, (text, width) in enumerate(cols):
        tk.Label(table, text=text, font=("微软雅黑", 11, "bold"),
                 width=width, anchor="center").grid(row=0, column=c, padx=2, pady=2)
    # 读取数据
    records = []
    if os.path.exists("scores.csv"):
        with open("scores.csv", "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)

    #排序
    records.sort(key=lambda x: int(x["得分"]), reverse=True)

    # 显示前10条
        # 显示前10条（和表头同一个 table，用 grid）
    if records:
        for i, rec in enumerate(records[:10], 1):
            vals = [
                str(i),
                rec["用户名"],
                rec["得分"],
                rec.get("设定时长", "-"),
                rec.get("最高连击", "-"),
                rec["日期"][:10]
            ]
            for c, v in enumerate(vals):
                tk.Label(table, text=v, font=("微软雅黑", 11),
                         width=cols[c][1], anchor="center").grid(row=i, column=c, padx=2, pady=2)
    else:
        tk.Label(window, text="暂无记录，快去游戏吧！", font=("微软雅黑", 12)).pack(pady=20)
    tk.Button(window, text="关闭", font=("微软雅黑", 12), command=window.destroy).pack(pady=15)


#地鼠逃跑了-----
def miss_mole():
    #地鼠逃跑，换下一个洞
    global combo, mole_timer, is_golden, current_hole
    combo = 0
    combo_label.config(text="")

    # 随机换洞
    current_hole = random.randint(0, len(HOLES) - 1)
    x, y, size = HOLES[current_hole]

    is_golden = random.random() < 0.1
    photo_to_use = get_mole_photo(size, is_golden)

    # 地鼠底部对齐洞口中心，模拟从洞里钻出来
    game_canvas.itemconfig(btn, image=photo_to_use)
    game_canvas.coords(btn, x, y - photo_to_use.height() // 2)
    game_canvas.tag_raise(btn)

    mole_timer = root.after(2000, miss_mole)

#照片缓存函数(辅助)
def get_mole_photo(size, golden=False):
    """按尺寸取缓存照片，没有就生成"""
    cache = golden_photos if golden else mole_photos
    if size not in cache:
        # 按比例缩放，并裁剪掉底部土堆
        resized = img.resize((size, int(size * 1.1)))
        cropped = crop_mole(resized)
        if golden:
            # 金色：加饱和度 + 亮度
            r = ImageEnhance.Color(cropped).enhance(2.5)
            r = ImageEnhance.Brightness(r).enhance(1.2)
            cache[size] = ImageTk.PhotoImage(r)
        else:
            cache[size] = ImageTk.PhotoImage(cropped)
    return cache[size]



#移动函数
def move():
    global score, is_golden, combo, max_combo, mole_timer, current_hole
    if remaining_time > 0:
        if mole_timer:
            root.after_cancel(mole_timer)

        # 计分
        points = 3 if is_golden else 1
        score += points
        combo += 1
        if combo > max_combo:
            max_combo = combo
        bonus = combo // 3
        score += bonus

        combo_label.config(text=f"🔥 {combo} 连击!" if combo >= 2 else "")
        update_label()

        # 随机选洞，根据地鼠大小调整照片
        current_hole = random.randint(0, len(HOLES) - 1)
        x, y, size = HOLES[current_hole]

        is_golden = random.random() < 0.1
        photo_to_use = get_mole_photo(size, is_golden)

        # 地鼠底部对齐洞口中心，模拟从洞里钻出来
        game_canvas.itemconfig(btn, image=photo_to_use)
        game_canvas.coords(btn, x, y - photo_to_use.height() // 2)
        game_canvas.tag_raise(btn)

        mole_timer = root.after(2000, miss_mole)

#创建地鼠（用画布图片实现透明底叠加）
btn = game_canvas.create_image(200, 200, image=photo, anchor="center")
game_canvas.tag_bind(btn, "<Button-1>", lambda e: move())


#结束界面------------------------------------------------
end_frame = tk.Frame(root, width=WIN_W, height=WIN_H)
end_frame.pack_propagate(False)

tk.Label(end_frame, text="⛏️ 打地鼠", font=("微软雅黑", 40, "bold")).pack(pady=80)

final_label = tk.Label(end_frame, text="", font=("微软雅黑", 24))
final_label.pack(pady=30)

def back_to_start():
    #返回开始界面，重置状态
    end_frame.pack_forget()
    start_frame.pack()

tk.Button(end_frame, text="再来一局", font=("微软雅黑", 14), 
          width=12, command=back_to_start).pack(pady=30)
tk.Button(end_frame, text="🏆 排行榜", font=("微软雅黑", 14), 
          width=12, command=show).pack(pady=10)
tk.Button(end_frame, text="退出游戏", font=("微软雅黑", 14), 
          width=12, command=root.destroy).pack(pady=10)


root.mainloop()

