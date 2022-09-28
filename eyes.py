from ctypes import sizeof
import cv2
import cv2.ximgproc
import numpy as np
import time
import stereoconfig
from matplotlib import pyplot as plt


# 預處理
def preprocess(img1, img2):
    # 彩色圖->灰度圖
    im1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    im2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # 直方圖均衡
    im1 = cv2.equalizeHist(im1)
    im2 = cv2.equalizeHist(im2)

    return im1, im2


# 消除畸變
def undistortion(image, camera_matrix, dist_coeff):
    undistortion_image = cv2.undistort(image, camera_matrix, dist_coeff)

    return undistortion_image



# 獲取畸變校正和立體校正的映射變換矩陣、重投影矩陣
# @param：config是一個類，存儲着雙目標定的參數:config = stereoconfig.stereoCamera()
def getRectifyTransform(height, width, config):
    # 讀取內參和外參
    left_K = config.cam_matrix_left
    right_K = config.cam_matrix_right
    left_distortion = config.distortion_l
    right_distortion = config.distortion_r
    R = config.R
    T = config.T

    # 計算校正變換
    if type(height) != 'int' or type(width) != 'int':
        height = int(height)
        width = int(width)
    R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(left_K, left_distortion, right_K, right_distortion, (width, height), R, T, alpha= 0)

    map1x, map1y = cv2.initUndistortRectifyMap(left_K, left_distortion, R1, P1, (width, height), cv2.CV_32FC1)
    map2x, map2y = cv2.initUndistortRectifyMap(right_K, right_distortion, R2, P2, (width, height), cv2.CV_32FC1)

    return map1x, map1y, map2x, map2y, Q



# 畸變校正和立體校正
def rectifyImage(image1, image2, map1x, map1y, map2x, map2y):
    rectifyed_img1 = cv2.remap(image1, map1x, map1y, cv2.INTER_AREA)
    rectifyed_img2 = cv2.remap(image2, map2x, map2y, cv2.INTER_AREA)

    return rectifyed_img1, rectifyed_img2



# 立體校正檢驗----畫線
def draw_line(image1, image2):
    # 建立輸出圖像
    height = max(image1.shape[0], image2.shape[0])
    width = image1.shape[1] + image2.shape[1]

    output = np.zeros((height, width,3), dtype=np.uint8)
    output[0:image1.shape[0], 0:image1.shape[1]] = image1
    output[0:image2.shape[0], image1.shape[1]:] = image2

    for k in range(15):
        cv2.line(output, (0, 50 * (k+1)), (2 * width, 50* (k+1)), (0, 255, 0), thickness=2, lineType=cv2.LINE_AA)  #直線間隔：100

    return output



# 視差計算
def disparity_SGBM(left_image, right_image, down_scale= False):
    # SGBM匹配參數設置
    if left_image.ndim == 2:
        img_channels = 1
    else:
        img_channels = 3
    blockSize = 3
    param = {'minDisparity' : 0,
             'numDisparities': 128,
             'blockSize' : blockSize,
             'P1' : 8 * img_channels * blockSize ** 2,
             'P2' : 32 * img_channels * blockSize ** 2,
             'disp12MaxDiff' : 1,
             'preFilterCap' : 63,
             'uniquenessRatio' : 15,
             'speckleWindowSize' : 400,
             'speckleRange' : 2,
             'mode' : cv2.STEREO_SGBM_MODE_SGBM_3WAY
             }


    # 構建SGBM對象
    sgbm = cv2.StereoSGBM_create(**param)


    # 計算視差圖
    if down_scale == False:
        disparity_left = sgbm.compute(left_image, right_image)
        disparity_right = sgbm.compute(right_image, left_image)
    else:
        left_image_down = cv2.pyrDown(left_image)
        right_image_down = cv2.pyrDown(right_image)
        disparity_left = sgbm.compute(left_image_down, right_image_down)
        disparity_right = sgbm.compute(right_image_down, left_image_down)

    return disparity_left



# 計算視差與3D座標（左攝像機下）
def computeDispAndPoints(iml_rec, imr_rec, Q):
    # 計算視差
    rectify1, rectify2 = preprocess(iml_rec, imr_rec)  # 預處理
    disparity_left = disparity_SGBM(rectify1, rectify2, down_scale= True)
    disp_left = np.divide(disparity_left.astype(np.float32), 16.0)

    # 恢復3D座標
    points_3d = cv2.reprojectImageTo3D(disp_left, Q)

    return disp_left, points_3d
    

# 計算目標框視差--模板匹配
# 假定：所標選的框內所有點具有相同的視差或深度
def disparity_box(left_img, right_img, xmin, ymin, xmax, ymax):
    # 模板
    template = left_img[ymin:ymax, xmin:xmax]

    # 搜索圖
    height = right_img.shape[0]
    yi = ymin - 10
    yu = ymax + 10
    if yi < 0: yi = 0
    if yu > height: yu = height
    search = right_img[yi:yu, :]

    # 模板匹配
    res = cv2.matchTemplate(search, template, cv2.TM_CCOEFF_NORMED)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(res)
    h = ymax - ymin
    w = xmax - xmin
    lu = (maxLoc[0], maxLoc[1] + yi)   # 左上角座標（注意:取maxLoc還是minLoc取決於所選擇的相似度量）
    rb = (maxLoc[0] + w, maxLoc[1] + yi + h)   # 右下角座標

    # 視差計算
    disparity = abs(maxLoc[0] - xmin)

    return disparity, lu, rb


def main():
    wCam, hCam = 640, 480   
    cap1 = cv2.VideoCapture(1, cv2.CAP_DSHOW) #usb cam
    cap2 = cv2.VideoCapture(0) #內建
    if not cap1.isOpened() or not cap2.isOpened():
        print("Cannot open camera")
        exit()
    cap1.set(3, wCam)
    cap1.set(4, hCam)
    cap2.set(3, wCam)
    cap2.set(4, hCam)
    
    try:
        while True:
            success, img1 = cap1.read()
            success2, img2 = cap2.read()
            # 左右水平翻轉
            img1 = cv2.flip(img1, 1) 
            img2 = cv2.flip(img2, 1) 
            '''
            config = stereoconfig.stereoCamera()
            map1x, map1y, map2x, map2y, Q = getRectifyTransform(hCam, wCam, config)
            rect_img1, rect_img2 = rectifyImage(img1, img2, map1x, map1y, map2x, map2y)
            out = draw_line(img1, img2)
            disp_left, points_3d = computeDispAndPoints(img1, img2, Q)
            '''
            #顯示畫面
            out = draw_line(img1, img2)
            cv2.imshow("out", out)
            #cv2.imshow("disparity", disp_left)
            #print(np.size(points_3d))
            
            # disparity range tuning

            window_size = 3
            min_disp = 0
            num_disp = 320 - min_disp

            stereo = cv2.StereoSGBM_create(
                minDisparity=0,
                numDisparities=240,  # max_disp has to be dividable by 16 f. E. HH 192, 256
                blockSize=3,
                P1=8 * 3 * window_size ** 2,
                # wsize default 3; 5; 7 for SGBM reduced size image; 15 for SGBM full size image (1300px and above); 5 Works nicely
                P2=32 * 3 * window_size ** 2,
                disp12MaxDiff=1,
                uniquenessRatio=15,
                speckleWindowSize=0,
                speckleRange=2,
                preFilterCap=63,
                mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
            )
            disparity = stereo.compute(img1, img2).astype(np.float32) / 16.0
            plt.imshow(disparity, 'gray')
            plt.show()

            #按q停止程式          
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        #ser.close()
        cap1.release()
        cap2.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()