import tkinter as tk
from PIL import Image, ImageTk 
import random

#界面
root=tk.Tk()
root.title("打地鼠")
root.geometry("800x800")

#label
score=0
label=tk.Label(root,text=f"得分：{score}")
label.pack()

#移动函数
def move():
    global score
    score+=1
    label.config(text=f"得分：{score}")
    x=random.randint(0,350)
    y=random.randint(0,350)
    btn.place(x=x,y=y)
    print(f'移动到（{x},{y}）')

#显示图像
img=Image.open('mole.png')
photo=ImageTk.PhotoImage(img)

#创建按键
btn=tk.Button(root,image=photo,relief=tk.FLAT,borderwidth=0,command=move)#去掉按钮的立体边框
btn.image=photo
btn.place(x=200,y=200)


root.mainloop()#应用程序的主窗口

