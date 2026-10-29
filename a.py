import cv2import matplotlib.pyplot
import matplotlib.pyplot as plt

image_color = cv2.imread("img/bernie-almanzar.png")
img_rgb = cv2.cvtColor(image_color, cv2.COLOR_BGR2RGB)

fig, axes = plt.subplot(2,2,figsize=(5,5))

axes[0,0].imshow(img_rgb)
axes[0,0].set_title('Fig 1 -LOCO')

axes[0,1].imshow(img_rgb)
axes[0,1].set_title('Fig 2-LOC1')
axes[0,1].axis("off")

image_color =
axes[0,1].imshow(img_rgb)
axes[0,1].set_title('Fig 2-LOC1')
axes[0,1].axis("off")

axes[0,1].imshow(img_rgb)
axes[0,1].set_title('Fig 2-LOC1')
axes[0,1].axis("off")