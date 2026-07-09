import tkinter as tk
from PIL import Image, ImageTk 
import random
import winsound

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
    
    try:
        winsound.MessageBeep(winsound.MB_ICONHAND)  # 结束提示音（Windows）
    except:
        pass
    
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
tk.Button(end_frame, text="退出游戏", font=("微软雅黑", 14), 
          width=12, command=root.destroy).pack(pady=10)

root.mainloop()

