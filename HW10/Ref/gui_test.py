import tkinter


def initTKWindow():
    window = tkinter.Tk()
    window.title('字根分解')
    window.geometry('400x300')
    window.font()
    window.configure(background='white')
    return window


if __name__ == '__main__':
    window = initTKWindow()
    
    print(window.__dict__)
    exit()
    
    
    
    # 將元件分為 top/bottom 兩群並加入主視窗
    top_frame = tkinter.Frame(window)
    top_frame.pack()
    bottom_frame = tkinter.Frame(window)
    bottom_frame.pack(side=tkinter.BOTTOM)

    # 建立事件處理函式（event handler），透過元件 command 參數存取
    def echo_hello():
        print('hello world :)')

    # 以下為 top 群組
    left_button = tkinter.Button(top_frame, text='Red', fg='red')
    # 讓系統自動擺放元件，預設為由上而下（靠左）
    left_button.pack(side=tkinter.LEFT)

    middle_button = tkinter.Button(top_frame, text='Green', fg='green')
    middle_button.pack(side=tkinter.LEFT)

    right_button = tkinter.Button(top_frame, text='Blue', fg='blue')
    right_button.pack(side=tkinter.LEFT)

    # 以下為 bottom 群組
    # bottom_button 綁定 echo_hello 事件處理，點擊該按鈕會印出 hello world :)
    bottom_button = tkinter.Button(bottom_frame, text='Black', fg='black', command=echo_hello)
    # 讓系統自動擺放元件（靠下方）
    bottom_button.pack(side=tkinter.BOTTOM)

    # 運行主程式
    window.mainloop()