#主要程式來源來自:https://www.youtube.com/c/MurtazasWorkshopRoboticsandAI/featured

#import serial
import argparse
import cv2
import time
import numpy as np
import math
import mediapipe as mp
from matplotlib import pyplot as plt
from queue import Queue
import socket

# server 設定
ip = "0.0.0.0" # 本機位置
port = 8080
server_address_family = (ip,port)       #伺服器地址族
server = socket.socket()
server.bind(server_address_family)
server.listen(2)


########## 手部追蹤偵測 #############
class handDetector():
    def __init__(self, mode=False, maxHands=1, modelComplexity=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.modelComplexity = modelComplexity
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplexity, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)
        '''
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        '''
        return img

    def findPosition(self, img, handNo=0, draw=True):

        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                lmList.append( [id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        return lmList


def main():
    
    pTime  = 0
    
    wCam, hCam = 640, 480
    cap1 = cv2.VideoCapture(0, cv2.CAP_DSHOW) #usb cam
    cap2 = cv2.VideoCapture(1, cv2.CAP_DSHOW) #內建
    if not cap1.isOpened() or not cap2.isOpened():
        print("Cannot open camera")
        exit()
    cap1.set(3, wCam) # 寬
    cap1.set(4, hCam) # 高
    cap2.set(3, wCam)
    cap2.set(4, hCam)

    detector1 = handDetector()
    detector2 = handDetector()

    # 手勢食指座標 
    act = Queue(maxsize=3) #-------------------------------------------------------------------->改範圍

    b = 23.5 # baseline
    f = 135 # 焦距
    d = 0.0 # 視差

    # socket 連接
    client,addr = server.accept()
    print("Connected by ", addr)
    print("Server sending test...")
    msg = "test"
    client.send(msg.encode('utf-8'))
    msg = client.recv(1024)
    print('recv: ' + msg.decode('utf-8'))

    try:
        while True:
            is_find = False
            success, img1 = cap1.read()
            success2, img2 = cap2.read()
            # 轉直向 水平翻轉
            img1 = cv2.rotate(img1, cv2.ROTATE_90_COUNTERCLOCKWISE)
            img1 = cv2.flip(img1, 1) 
            img2 = cv2.rotate(img2, cv2.ROTATE_90_COUNTERCLOCKWISE)
            img2 = cv2.flip(img2, 1) 
            # 以cap1偵測手部
            img1 = detector1.findHands(img1)
            lmList1 = detector1.findPosition(img1, draw=False)
            # 以cap2偵測手部
            img2 = detector2.findHands(img2)
            lmList2 = detector2.findPosition(img2, draw=False)
            #print(lmList)
            x1, y1 = 0, 0
            x2, y2 = 0, 0
            
            if len(lmList1) != 0 and len(lmList2) != 0:
                is_find = True
                x1, y1 = lmList1[8][1], lmList1[8][2]
                x2, y2 = lmList2[8][1], lmList2[8][2]
                print(x1, y1)

            cv2.circle(img1, (x1, y1), 5, (255, 0, 255), cv2.FILLED)
                #cv2.circle(img2, (x2, y2), 5, (0, 255, 255), cv2.FILLED)

            z = 0.0
            d = float(x1 - x2)
            if not d == 0.0:
                z = b*f/d # 深度
                print(int(z))


            #queue比較手勢
            if not act.empty() and not z == 0.0:
                move1 = act.get() # 3 frame之前的位置
                move2 = z # 現在的位置
                location_x = round(x1/wCam, 2) # 給介面的相對座標x
                location_y = round(y1/wCam, 2) # 給介面的相對座標y
                msg = str(location_x) + ' ' + str(location_y)
                if move1-move2 > 4.3 and move1-move2 < 30.0: # 點擊 #-----------------------------------------------> 改深度差
                    print("點擊")
                    # 傳送給介面
                    client.send(msg.encode('utf-8'))
                    print('send : ' + msg)
                    msg = client.recv(1024)
                    print('recv: ' + msg.decode('utf-8'))

            if act.full():
                tmp = act.get()
            if not z == 0.0:
                act.put(z)
            
                


            #print(dist)
            #計算每秒跑幾張
            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            #print(int(fps))
            cv2.putText(img1, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)

            #顯示畫面 
            cv2.imshow("HandDetector1", img1)
            #cv2.imshow("HandDetector2", img2)
                      
            #按q停止程式          
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        #ser.close()
        cap1.release()
        cap2.release()
        cv2.destroyAllWindows()
        server.close()
        client.close()
    

if __name__ == '__main__' :
    main()