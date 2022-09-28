from multiprocessing import Event
import threading
import tkinter as tk
import socket
import time

#socket 設置
ip = socket.gethostbyname(socket.gethostname()) #本機
port = 8080

server_address_family = (ip,port)       #伺服器地址族

s = socket.socket()
s.connect(server_address_family)
#msg = client.recv(5120)


class App(object):
    def __init__(self):
        self.root =tk.Tk()
        self.pos = [0, 0] #x, y
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.canvas=tk.Canvas(self.root,height=self.screen_height-100,width=self.screen_width-100)
        self.canvas.pack()
        self.root.attributes('-fullscreen', True)
        self.value=tk.StringVar()

        #按鍵設置
        btn_x, btn_y = 0.1, 0.2
        btn_txt = [["1", "2", "3", "取消"], ["4", "5", "6", "更正"], ["7", "8", "9", "確認"]]
        w = 0.2-0.01
        h = 0.18

        #背景
        self.frame=tk.Frame(self.root,bg="#000000") 
        self.frame.place(relwidth=1,relheight=1,relx=0,rely=0)

        self.input = tk.Label(self.frame, textvariable=self.value, font=("Arial", 50), bg="white", anchor="e")
        self.input.place(relwidth=0.8, relheight=0.14, relx=0.1, rely=0.05)

        #按鈕位置
        self.label_1 = tk.Label(self.frame, text="1", font=("Arial", 50), width=5, height=3, bg="white")
        self.label_1.place(relwidth=w, relheight=h, relx=0.1, rely=0.2)
        self.label_2 = tk.Label(self.frame, text="2", font=("Arial", 50), width=5, height=3, bg="white")
        self.label_2.place(relwidth=w, relheight=h, relx=0.3, rely=0.2)
        self.label_3 = tk.Label(self.frame, text="3", font=("Arial", 50), width=5, height=3, bg="white")
        self.label_3.place(relwidth=w, relheight=h, relx=0.5, rely=0.2)
        self.label_cancel = tk.Label(self.frame, text="取消", font=("Arial", 50), width=5, height=3, bg="white")
        self.label_cancel.place(relwidth=w, relheight=h, relx=0.7, rely=0.2)

        self.label_4 = tk.Label(self.frame, text="4", font=("Arial", 50), width=5, height=3, bg="white")
        self.label_4.place(relwidth=w, relheight=h, relx=0.1, rely=0.4)
        self.label_5 = tk.Label(self.frame, text="5", font=("Arial", 50), width=5, height=3, bg="white")
        self.label_5.place(relwidth=w, relheight=h, relx=0.3, rely=0.4)
        self.label_6 = tk.Label(self.frame, text="6", font=("Arial", 50), width=5, height=3, bg="white")
        self.label_6.place(relwidth=w, relheight=h, relx=0.5, rely=0.4)
        self.label_clear = tk.Label(self.frame, text="更正", font=("Arial", 50), width=5, height=3, bg="white")
        self.label_clear.place(relwidth=w, relheight=h, relx=0.7, rely=0.4)

        self.label_7 = tk.Label(self.frame, text="7", font=("Arial", 50), width=5, height=3, bg="white")
        self.label_7.place(relwidth=w, relheight=h, relx=0.1, rely=0.6)
        self.label_8 = tk.Label(self.frame, text="8", font=("Arial", 50), width=5, height=3, bg="white")
        self.label_8.place(relwidth=w, relheight=h, relx=0.3, rely=0.6)
        self.label_9 = tk.Label(self.frame, text="9", font=("Arial", 50), width=5, height=3, bg="white")
        self.label_9.place(relwidth=w, relheight=h, relx=0.5, rely=0.6)
        self.label_enter = tk.Label(self.frame, text="確認", font=("Arial", 50), width=5, height=3, bg="white")
        self.label_enter.place(relwidth=w, relheight=h, relx=0.7, rely=0.6)

        self.label_0 = tk.Label(self.frame, text="0", font=("Arial", 50), width=3, height=3, bg="white")
        self.label_0.place(relwidth=w, relheight=h, relx=0.3, rely=0.8)

        '''
        for i in range(0, 3):
            for j in range(0, 4):
                self.label = tk.Label(self.frame, text=btn_txt[i][j], font=("Arial", 50), width=5, height=3, bg="white")
                self.label.place(relwidth=w, relheight=h, relx=btn_x, rely=btn_y)
                btn_x += 0.2
            btn_x = 0.1
            btn_y += 0.2
        self.label = tk.Label(self.frame, text="0", font=("Arial", 50), width=3, height=3, bg="white")
        self.label.place(relwidth=w, relheight=h, relx=0.3, rely=btn_y)
        btn_y = 0.2
        '''

        # 啟動一個不斷接收改變資料的thread
        t = threading.Thread(target=self.update_input)
        t.start()
    

    #判斷點擊位置
    def click_button(self, pos):
        btn = ''
        # 1 4 7
        if pos[0] >= 0.1 and pos[0] <= 0.28:
            if pos[1] >=0.2 and pos[1] <=0.39: # 1
                btn = '1'
                self.label_1['bg'] = "gray"
                time.sleep(0.2)
                self.label_1['bg'] = "white"
            if pos[1] >=0.4 and pos[1] <=0.59: # 4
                btn = '4'
                self.label_4['bg'] = "gray"
                time.sleep(0.2)
                self.label_4['bg'] = "white"
            if pos[1] >=0.6 and pos[1] <=0.79: # 7
                btn = '7'
                self.label_7['bg'] = "gray"
                time.sleep(0.2)
                self.label_7['bg'] = "white"
            
        # 2 5 8
        if pos[0] >= 0.3 and pos[0] <= 0.48:
            if pos[1] >=0.2 and pos[1] <=0.39: # 2
                btn = '2'
                self.label_2['bg'] = "gray"
                time.sleep(0.2)
                self.label_2['bg'] = "white"
            if pos[1] >=0.4 and pos[1] <=0.59: # 5
                btn = '5'
                self.label_5['bg'] = "gray"
                time.sleep(0.2)
                self.label_5['bg'] = "white"
            if pos[1] >=0.6 and pos[1] <=0.79: # 8
                btn = '8'
                self.label_8['bg'] = "gray"
                time.sleep(0.2)
                self.label_8['bg'] = "white"
            if pos[1] >=0.8 and pos[1] <=0.99: # 0
                btn = '0'
                self.label_0['bg'] = "gray"
                time.sleep(0.2)
                self.label_0['bg'] = "white"

        # 3 6 9
        if pos[0] >= 0.5 and pos[0] <= 0.68:
            if pos[1] >=0.2 and pos[1] <=0.39: # 3
                btn = '3'
                self.label_3['bg'] = "gray"
                time.sleep(0.2)
                self.label_3['bg'] = "white"
            if pos[1] >=0.4 and pos[1] <=0.59: # 6
                btn = '6'
                self.label_6['bg'] = "gray"
                time.sleep(0.2)
                self.label_6['bg'] = "white"
            if pos[1] >=0.6 and pos[1] <=0.79: # 9
                btn = '9'
                self.label_9['bg'] = "gray"
                time.sleep(0.2)
                self.label_9['bg'] = "white"

        # else
        if pos[0] >= 0.7 and pos[0] <= 0.88:
            if pos[1] >=0.2 and pos[1] <=0.39: # 取消
                btn = 'ca'
                self.label_cancel['bg'] = "gray"
                time.sleep(0.2)
                self.label_cancel['bg'] = "white"
            if pos[1] >=0.4 and pos[1] <=0.59: # 更正
                btn = 'cl'
                self.label_clear['bg'] = "gray"
                time.sleep(0.2)
                self.label_clear['bg'] = "white"
            if pos[1] >=0.6 and pos[1] <=0.79: # 確定
                btn = 'en'
                self.label_enter['bg'] = "gray"
                time.sleep(0.2)
                self.label_enter['bg'] = "white"

        return btn

    #socket 不斷接收資料

    #更新顯示
    def update_input(self):
        while True:
            msg = None
            msg = s.recv(1024)
            if msg:
                msg = msg.decode('utf-8')
                str1 = msg.split(' ')
                pos = [float(str1[0]), float(str1[1])]
                print(pos)
                print('recv: ' + msg)
                msg = "Get"
                s.send(msg.encode('utf-8'))
                print('send: ' + msg)

                # 取得按鈕
                btn = self.click_button(pos)

                if btn == 'ca': # 取消
                    # 清空value
                    self.value.set('')
                elif btn == 'cl': # 更正
                    # 取到前一位
                    tmp = self.value.get()
                    if len(tmp) > 0:
                        self.value.set(tmp[:-1])
                elif btn == 'en': # 確認
                    #輸出到cmd 並清空
                    print("----------------------")
                    print("Enter: " + self.value.get())
                    print("----------------------")
                    self.value.set('')
                else:
                    self.value.set(self.value.get() + btn)
                #self.tmp += 10
                msg = None
        
    
    #執行
    def run(self):
        self.root.mainloop()



if __name__=='__main__':
    msg = s.recv(1024)
    print('recv: ' + msg.decode('utf-8'))
    msg = "Get"
    s.send(msg.encode('utf-8'))
    print('send: ' + msg)

    if msg:
        App().run()

    print ("close client socket")
    s.close()




