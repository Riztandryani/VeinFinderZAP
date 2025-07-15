import cv2


# capture from camera at location 0
cap = cv2.VideoCapture(1)
# set the width and height, and UNSUCCESSFULLY set the exposure time
cap.set(cv2.CAP_PROP_BRIGHTNESS, 150)
cap.set(cv2.CAP_PROP_CONTRAST, 200)
cap.set(cv2.CAP_PROP_SATURATION, 50)

while True:
    ret, img = cap.read()
    cv2.imshow("input", img)
    # cv2.imshow("thresholded", imgray*thresh2)

    k = cv2.waitKey(1)
    if k == ord('w'):
        break

cv2.destroyAllWindows()
cv2.VideoCapture(0).release()
