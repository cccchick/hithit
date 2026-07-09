import tkinter as tk
from PIL import Image, ImageTk 
import random

#界面
root=tk.Tk()
root.title("打地鼠")
root.geometry("800x800")


#label
score=0
r_time=60
label=tk.Label(root,text=f"得分：{score},剩余时间：{r_time}")
label.pack()

#时间
def timing():
    global r_time
    if r_time>0:
        r_time-=1
        label.config(text=f"得分：{score},剩余时间：{r_time}")
        root.after(1000,timing)
    else:
        label.config(text=f"得分：{score},游戏结束,再接再厉！")
    
#移动函数
def move():
    global score
    if r_time>0:
        score+=1
        label.config(text=f"得分：{score},剩余时间：{r_time}")
                # 窗口尺寸
        win_w, win_h = 800, 800
        
        # 获取图片尺寸（原始像素）
        img_w, img_h = img.size
        
        # 顶部预留 60 像素给标签（经验值，可通过 label.winfo_height() 精确获取）
        top_safe = 60
        # 四周留 10 像素边距，防止贴边
        margin = 10
        
        # 计算地鼠左上角的合法随机范围
        x = random.randint(margin, win_w - img_w - margin)
        y = random.randint(top_safe, win_h - img_h - margin)
    
        btn.place(x=x, y=y)


#显示图像
img=Image.open('mole.png')
photo=ImageTk.PhotoImage(img)

#创建按键
btn=tk.Button(root,image=photo,relief=tk.FLAT,borderwidth=0,command=move)#去掉按钮的立体边框
btn.image=photo
btn.place(x=200,y=200)

timing()
root.mainloop()#应用程序的主窗口

