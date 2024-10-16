import cv2
from rect_detect import *
import polars as pl
import time
import imutils

def hacky_nut(roi):
    conts, _ = cv2.findContours(
        edge_detect(roi),
        cv2.RETR_CCOMP,
        cv2.CHAIN_APPROX_SIMPLE
    )
    if len(conts) < 2:
        return

    for cont in conts:
       p = cv2.arcLength(cont, True)
       poly = cv2.approxPolyDP(cont, p*0.03, True)
       if len(poly) >= 4:
           yield cv2.boundingRect(poly)
    return

stream = cv2.VideoCapture("./test-assets/tr.mp4")
SCALE_FACTOR = 0.06

OBJECTS = [
]

AREA_MAP = [

]

def search_item(area):
    for i, o in enumerate(AREA_MAP):
        if o[0][0] < area < o[0][1]:
            return (o[1], i)
    return ("Unknown", -1)

qty = [[0], [0], [0]]

def main_loop():
    last_item = "Unknown"
    print("Hit 'a' to Add Item to DB, q to quit")
    while True:
        ret, image = stream.read()
        if not ret:
            break

        # cv2.imshow("kek", image)
        # cv2.waitKey(16)
        # continue

        # cv2.imwrite("baddi-test.png", image);
        # break

        dimg = imutils.resize(image, width=960)
        rimage = imutils.resize(image, width=640)
        rimage = rimage[10:430, 40:500]
        # dimg = rimage.copy()

        # cv2.imshow("kek2", rimage)
        # cv2.waitKey(16)
        # continue

        x, y, w, h = max(
            filter(
                lambda o: o != None and 100 < o[3]*o[2] < 200000,
                hacky_nut(rimage)
            ),
            key = lambda o: o[2] * o[3],
            default = (None, None, None, None)
        )

        if x != None:
            rs = (round(w*SCALE_FACTOR, 2), round(h*SCALE_FACTOR, 2))
            o, idx = search_item(rs[0]*rs[1])
            x = int((x+40)*1.5)
            y = int((y+10)*1.5)
            w = int(w*1.5)
            h = int(h*1.5)
            if idx != -1:
                last_item = (o, idx)


            cv2.rectangle(dimg, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(dimg, f"(w, h)={rs}cm", (x - x//4, y), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(dimg, o, (x, y+h+10), cv2.FONT_HERSHEY_PLAIN, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow("kek", dimg)
        k = cv2.waitKey(11)
        if k == ord('a') and x != None:
            qty[last_item[1]][0] += 1
            print("Added to DB")
        if k == ord('q'):
            break

try:
    main_loop()
except KeyboardInterrupt:
    pass

cv2.destroyAllWindows()

df = pl.DataFrame(qty)
print(df)

df.write_csv("data.txt")
