import tkinter as tk
from PIL import Image, ImageTk 
import random
import winsound
import csv        
import os           
from datetime import datetime 

#界面
root=tk.Tk()
root.title("打地鼠")
root.geometry("800x800")

#全局变量
score=0
remaining_time=60
username='玩家1'

# 加载图片
img = Image.open('mole.png')
img_w, img_h = img.size
photo = ImageTk.PhotoImage(img)

#start--------------------------------
start_frame=tk.Frame(root,width=800,height=800)
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
    
    # 3. 初始化游戏
    update_label()
    timing()                    # 启动倒计时

tk.Button(start_frame, text="开始游戏", font=("微软雅黑", 14), 
          width=12, command=start_game).pack(pady=40)

#游戏界面--------------------------------
game_frame = tk.Frame(root, width=800, height=800)
game_frame.pack_propagate(False)

#label
label = tk.Label(game_frame, text="")
label.pack()

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
            writer.writerow(["用户名", "得分", "设定时长", "日期"])
        # 写入本次数据
        writer.writerow([
            username,
            score,
            time_var.get(), 
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
    header = tk.Frame(window)
    header.pack(fill="x", padx=20)
    for text, width in [("排名", 6), ("玩家", 12), ("得分", 8), ("时长", 6), ("日期", 14)]:
        tk.Label(header, text=text, font=("微软雅黑", 11, "bold"), width=width).pack(side="left")

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
    if records:
        for i, rec in enumerate(records[:10], 1):
            row_frame = tk.Frame(window)
            row_frame.pack(fill="x", padx=20, pady=2)
            vals = [
                str(i),
                rec["用户名"],
                rec["得分"],
                rec.get("设定时长", "-"),
                rec["日期"][:10]  
            ]
            widths = [6, 12, 8, 6, 14]
            for v, w in zip(vals, widths):
                tk.Label(row_frame, text=v, font=("微软雅黑", 11), width=w).pack(side="left")
    else:
        tk.Label(window, text="暂无记录，快去游戏吧！", font=("微软雅黑", 12)).pack(pady=20)

    tk.Button(window, text="关闭", font=("微软雅黑", 12), command=window.destroy).pack(pady=15)


#移动函数
def move():
    global score
    if remaining_time > 0:
        score += 1
        update_label()
        
        x = random.randint(10, 800 - img_w - 10)
        y = random.randint(80, 800 - img_h - 10)
        
        btn.place(x=x, y=y)



#创建按键
btn = tk.Button(game_frame, image=photo, relief=tk.FLAT, borderwidth=0, command=move)
btn.image = photo
btn.place(x=200, y=200)


#结束界面------------------------------------------------
end_frame = tk.Frame(root, width=800, height=800)
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

