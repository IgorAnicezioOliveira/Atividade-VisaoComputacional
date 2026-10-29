import cv2

cap = cv2.VideoCapture("videos/dog.mp4")

while(True):
    _, frame =cap.read()
    cv2.imshow("Video do dog/", frame)

    if cv2.waitKey(20) & 0xFF == ord('d'):
        break

cap.release()
cv2.destroyAllWindows()
