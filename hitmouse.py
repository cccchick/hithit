import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance
import random
import winsound
import csv
import os
from datetime import datetime


#图片处理辅助函数 
def make_white_transparent(img, threshold=35):
    """将图片中的白色背景转为透明

    Args:
        img: PIL Image 对象
        threshold: 与纯白色的距离阈值，越小越严格（推荐 30-50）
    """
    img = img.convert("RGBA")
    datas = img.getdata()
    white = (255, 255, 255)
    new_data = []
    transparent_count = 0

    for item in datas:
        # 计算与纯白色的欧氏距离
        distance = ((item[0] - white[0])**2 +
                    (item[1] - white[1])**2 +
                    (item[2] - white[2])**2) ** 0.5
        if distance < threshold:
            new_data.append((255, 255, 255, 0))
            transparent_count += 1
        else:
            new_data.append(item)

    img.putdata(new_data)
    print(f"去白底完成：共 {len(datas)} 像素，转为透明 {transparent_count} 像素")
    return img


# 窗口与洞位配置 
WIN_W, WIN_H = 1000, 750  # 适配背景图比例

# 16个洞口 (中心x, 中心y, 地鼠大小) —— 根据 background.jpg 实际洞位标定
HOLES = [
    (225, 294, 55),  (405, 295, 55),  (584, 295, 55),  (751, 295, 55),   # 第1行（远，小）
    (112, 380, 80),  (304, 380, 80),  (498, 380, 80),  (692, 379, 80),   (882, 379, 80),  # 第2行
    (127, 496, 110), (372, 496, 110), (627, 497, 110), (868, 495, 110),  # 第3行
    (166, 655, 150), (498, 656, 150), (830, 655, 150),                   # 第4行（近，大）
]

# 照片缓存（每种尺寸只生成一次，避免闪烁）
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
    print(f"背景加载失败: {e}")
    bg_photo = None
#全局变量
score=0
remaining_time=60
username='玩家1'
is_golden = False
combo = 0
max_combo = 0
mole_timer = None

# 全局变量（新增）
HAMMER_SIZE = 100
HIT_DELAY = 200
hammer_photo = None
hammer_id = None
hit_photos = {}
is_hit_state = False

# 加载图片
img = Image.open('mole.png').convert('RGBA')
img_w, img_h = img.size


def crop_mole(image):
    """去掉地鼠图片底部的土堆，只保留从洞里钻出来的部分"""
    w, h = image.size
    return image.crop((0, 0, w, int(h * 0.58)))


photo = ImageTk.PhotoImage(crop_mole(img))
# 基于原图生成金色地鼠（加饱和度 + 加亮度）
golden_img = ImageEnhance.Color(crop_mole(img)).enhance(2.5)
golden_img = ImageEnhance.Brightness(golden_img).enhance(1.2)
golden_photo = ImageTk.PhotoImage(golden_img)

# ========== 新增：加载锤子 ==========
try:
    hammer_raw = Image.open("锤子.png")
    hammer_raw = make_white_transparent(hammer_raw)
    w, h = hammer_raw.size
    hammer_img = hammer_raw.resize((int(w * HAMMER_SIZE / h), HAMMER_SIZE), Image.Resampling.LANCZOS)
    hammer_photo = ImageTk.PhotoImage(hammer_img)
except Exception as e:
    print(f"锤子加载失败: {e}")
    hammer_photo = None


# ========== 新增：生成被打地鼠的缓存 ==========
def get_hit_photo(size):
    """获取对应尺寸的‘被打晕’地鼠"""
    if size not in hit_photos:
        try:
            hit_raw = Image.open("hitmole.png")
            hit_raw = make_white_transparent(hit_raw)
            hit_resized = hit_raw.resize((size, int(size * 1.1)))
            hit_cropped = crop_mole(hit_resized)
            hit_photos[size] = ImageTk.PhotoImage(hit_cropped)
        except Exception:
            hit_photos[size] = get_mole_photo(size, False)
    return hit_photos[size]

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
    global combo, max_combo, mole_timer, is_golden, current_hole, is_hit_state
    combo = 0
    max_combo = 0
    if mole_timer:
        root.after_cancel(mole_timer)
    mole_timer = None
    combo_label.config(text="")
    is_golden = False
    current_hole = 0
    is_hit_state = False

    # --- 新增：隐藏系统鼠标，显示锤子 ---
    game_canvas.config(cursor="none")
    if hammer_id:
        game_canvas.coords(hammer_id, WIN_W // 2, WIN_H // 2)
        game_canvas.itemconfig(hammer_id, state='normal')

    # 初始化第一只地鼠
    spawn_mole()

    # 3. 初始化游戏
    update_label()
    timing()                    # 启动倒计时

tk.Button(start_frame, text="开始游戏", font=("微软雅黑", 14),
          width=12, command=start_game).pack(pady=40)

#游戏界面--------------------------------
game_frame = tk.Frame(root, width=WIN_W, height=WIN_H)
game_frame.pack_propagate(False)

# 使用画布显示背景图和地鼠，才能正确支持透明 PNG 叠加
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
    global mole_timer, is_hit_state
    if mole_timer:
        root.after_cancel(mole_timer)#取消计时
        mole_timer = None

    # --- 新增：恢复系统鼠标，隐藏锤子 ---
    game_canvas.config(cursor="")
    if hammer_id:
        game_canvas.itemconfig(hammer_id, state='hidden')
    is_hit_state = False

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
    """地鼠逃跑，重置连击，生成下一只"""
    global combo, is_hit_state

    # 如果正处于“被打中”的动画播放中，不用处理
    if is_hit_state:
        return

    combo = 0
    combo_label.config(text="")

    # 直接调用生成下一只，逻辑统一
    spawn_mole()

#照片缓存函数
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


# 飘字效果 
def show_floating_text(x, y, text):
    text_id = game_canvas.create_text(
        x, y, text=text,
        font=("微软雅黑", 20, "bold"),
        fill="yellow"
    )

    def float_up(step=0):
        if step < 10:
            game_canvas.move(text_id, 0, -2)
            root.after(30, float_up, step + 1)
        else:
            game_canvas.delete(text_id)

    float_up()


# 屏幕震动 
def shake_canvas():
    
    def do_shake(step=0):
        dx = 3 if step % 2 == 0 else -3
        game_canvas.move("all", dx, 0)
        if step < 5:
            root.after(30, do_shake, step + 1)
        else:
            # 最后一步把画布移回平衡位置
            if step % 2 == 0:
                game_canvas.move("all", -dx, 0)
    do_shake()


# 鼠标点击判定
def on_canvas_click(event):
    global is_hit_state

    # 如果已经显示“被打中”的图了，点击无效，防止连点刷分
    if is_hit_state or remaining_time <= 0:
        return

    # 检测鼠标周围 10x10 区域内所有重叠的 Canvas 对象
    # 即使锤子在最上层，地鼠只要在该区域内就能被识别
    overlapped = game_canvas.find_overlapping(event.x - 5, event.y - 5,
                                               event.x + 5, event.y + 5)
    if btn in overlapped:
        hit_mole()


#  新增：打击反馈逻辑 
def hit_mole():
    global score, combo, max_combo, is_hit_state, mole_timer, current_hole

    # 1. 取消原来的“逃跑计时器”
    if mole_timer:
        root.after_cancel(mole_timer)

    # 2. 计分
    points = 3 if is_golden else 1
    score += points
    combo += 1
    if combo > max_combo:
        max_combo = combo
    bonus = combo // 3
    score += bonus

    combo_label.config(text=f"🔥 {combo} 连击!" if combo >= 2 else "")
    update_label()

    # 3. 显示“被打晕”的图片
    x, y, size = HOLES[current_hole]
    hit_photo = get_hit_photo(size)
    game_canvas.itemconfig(btn, image=hit_photo)

    # 飘字 + 屏幕震动 
    total_points = points + bonus
    show_floating_text(x, y - 50, f"+{total_points}")
    if is_golden:
        shake_canvas()

    # 4. 进入“停顿状态”，防止重复点击
    is_hit_state = True

    # 5. 延时后生成下一只地鼠
    root.after(HIT_DELAY, spawn_mole)


# 生成新地鼠逻辑 
def spawn_mole():
    global is_hit_state, mole_timer, is_golden, current_hole

    # 恢复可点击状态
    is_hit_state = False

    # 随机选洞
    current_hole = random.randint(0, len(HOLES) - 1)
    x, y, size = HOLES[current_hole]
    is_golden = random.random() < 0.1

    # 换回普通地鼠或金地鼠图
    photo_to_use = get_mole_photo(size, is_golden)
    game_canvas.itemconfig(btn, image=photo_to_use)
    game_canvas.coords(btn, x, y - photo_to_use.height() // 2)
    game_canvas.tag_raise(btn)

    # 启动逃跑计时器（随时间推进逐渐加速，任意时长开局都是 2000ms，最快 600ms）
    total_time = int(time_var.get())
    if total_time > 0:
        stay_time = max(600, int(remaining_time / total_time * 1400 + 600))
    else:
        stay_time = 2000
    mole_timer = root.after(stay_time, miss_mole)

#创建地鼠（用画布图片实现透明底叠加）
btn = game_canvas.create_image(200, 200, image=photo, anchor="center")

# 事件绑定
# 1. 绑定整个画布的点击事件（代替原来的 tag_bind）
game_canvas.bind("<Button-1>", on_canvas_click)

# 2. 锤子跟随逻辑
def move_hammer(event):
    if hammer_id:
        # 让锤子稍微偏右下一点，像握在手里
        game_canvas.coords(hammer_id, event.x + 20, event.y + 20)
        game_canvas.tag_raise(hammer_id)

game_canvas.bind("<Motion>", move_hammer)

# 创建锤子对象（初始隐藏）
if hammer_photo:
    hammer_id = game_canvas.create_image(-100, -100, image=hammer_photo, anchor="center", state='hidden')
else:
    hammer_id = None


#结束界面------------------------------------------------
end_frame = tk.Frame(root, width=WIN_W, height=WIN_H)
end_frame.pack_propagate(False)

tk.Label(end_frame, text="⛏️ 打地鼠", font=("微软雅黑", 40, "bold")).pack(pady=80)

final_label = tk.Label(end_frame, text="", font=("微软雅黑", 24))
final_label.pack(pady=30)

def back_to_start():
    #返回开始界面，重置状态
    global is_hit_state
    end_frame.pack_forget()
    start_frame.pack()

    # --- 新增：恢复系统鼠标，隐藏锤子 ---
    game_canvas.config(cursor="")
    if hammer_id:
        game_canvas.itemconfig(hammer_id, state='hidden')
    is_hit_state = False

tk.Button(end_frame, text="再来一局", font=("微软雅黑", 14),
          width=12, command=back_to_start).pack(pady=30)
tk.Button(end_frame, text="🏆 排行榜", font=("微软雅黑", 14),
          width=12, command=show).pack(pady=10)
tk.Button(end_frame, text="退出游戏", font=("微软雅黑", 14),
          width=12, command=root.destroy).pack(pady=10)


root.mainloop()
