import cv2
import matplotlib.pyplot as plt

imageColor = cv2.imread("img/bernie-almanzar.png")

cv2.imshow("Mostrando a imagem", imageColor)

cv2.waitKey(0)
cv2.destroyAllWindows()

img_rgb = cv2.imread(imageColor, cv2.COLOR_BGR2RGB)

plt.imshow(img_rgb)
plt.title("Mostrando a imagem")
plt.axis("off")
plt.show()
