import cv2
from PIL import Image
from pprint import pprint
ind = 0
def upscale(mas):

    return mas
def draw(mas):
    global ind
    ind+=1
    f = open(f'{ind}.txt', 'w')
    for i in mas:
        s = ''
        for j in i:
            if j:
                s+='#'
            else:
                s+='.'
        s+='\n'
        f.write(s)
def average(mas):
    print(len(mas[0]), len(mas))
def isLetter(x, y, w, h, img):
    ans = []
    for yaxis in range(y, y + h):
        s = []
        for xaxis in range(x, x+w):
            if img[yaxis][xaxis] == 255:
                s.append(0)
            else:
                s.append(1)
#todo здесь проверка нейронкой буков

        ans.append(s)
    draw(ans)
    return True
def filter_box(mas):
    cop = mas[:]
    for x, y, w, h, massa in mas:
        for xt, yt, wt, ht, massat in mas:

            if [ x, y, w, h, massa] != [xt, yt, wt, ht, massat] and xt <= x <= xt + wt and yt <= y <= yt + ht:
                cop.remove([x, y, w, h, massa])
                break
    return cop

def get_letters(index, flag):

    #коррекция размера изображениия
    img_src = f"{index}.png"
    src = cv2.imread(img_src)
    im = Image.open(img_src)
    scale_percent = 100
    width = int(src.shape[1] * scale_percent / 100)
    height = int(src.shape[0] * scale_percent / 100)
    dsize = (width, height)
    img = cv2.resize(src, dsize)

    #фильтр
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)

    th2 = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,199,10)


    cv2.imshow("2", gray)
    cv2.imshow("1", th2)
    cv2.waitKey(0)

    #контуры
    contours, hierarchy = cv2.findContours(th2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    output = img.copy()
    output2 = img.copy()

    #todo добавть удаление поле рамок текста
    #центрировать изображение (учет коэффицента площади контура)!
    #avg = [[cv2.boundingRect(contour)[0], cv2.boundingRect(contour)[1], cv2.boundingRect(contour)[2], cv2.boundingRect(contour)[3]] for idx, contour in enumerate(contours)]
    #len_avg = len(avg)
    #a, b = int(sum([i[0]+i[2]/2 for i in avg])/len_avg), int(sum([i[1]+i[3]/2 for i in avg])/len_avg)
    #cv2.circle(output, (a,  b), 2, (0, 0, 255), 3)

    #среднее значение площади контура
    sqw = [cv2.boundingRect(contour)[2]*cv2.boundingRect(contour)[3] for idx, contour in enumerate(contours)]
    awg = sum(sqw)/len(sqw)
    awg = awg*0.08
    minim = 2000
    xyarray = []
    #рисование конткров + распознавание букв
    idd = 0
    for idx, contour in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)
        if hierarchy[0][idx][3] == 0:
            xyarray.append([x, y, w, h, w*h])
    #pprint(xyarray)# filter
    #xyarray = filter_box(xyarray)
    minim = min(mas for x, y, w, h, mas in xyarray)
    count2 = 0
    copxy = xyarray[:]

    for x, y, w, h, mass in xyarray:
        # x, y - верхниий левый угол
        cv2.rectangle(output2, (x, y), (x + w, y + h), (100, 2, 2), 1)

    cv2.imshow("Output2", output2)
    #cv2.waitKey(0)


    delmas = []
    #print(minim)
    for x, y, w, h, mass in xyarray:
        if w*h - minim < 30:
            print(x, y, w*h)
            count = 0
            delmas.append([x, y, w, h, mass])
            for xt, yt, wt, ht, masst in xyarray:
                if [x, y, w, h, mass] != [xt, yt, wt, ht, masst] and y + h + 20 >= yt and xt <= x+w//2 <= xt + wt:
                    print(x, y, xt, yt, count)
                    copxy[count] = [xyarray[count][0], xyarray[count2][1], xyarray[count][2], xyarray[count][3] + xyarray[count2][3] + 6, (xyarray[count][3] + xyarray[count2][3] + 6)*xyarray[count][2]]
                    break
                count +=1

        count2 += 1
    #print(delmas)
    #print(copxy[46], copxy[47])
    #print(xyarray[46], xyarray[47])
    for val in delmas:
        try:
            copxy.remove(val)
        except:
            continue
    xyarray = copxy[:]

    for x, y, w, h, mass in xyarray:
        # x, y - верхниий левый угол
        #print(x, y, w* h)
        cv2.rectangle(output, (x, y), (x + w, y + h), (100, 2, 2), 1)

        if flag:
            im_crop = im.crop((x, y, x + w, y + h))
            im_crop.save(f'{img_src[:-4]}-{idd}.png', quality=95)
            idd += 1

        #if awg>w*h:
        #    print(w*h)
        #if hierarchy[0][idx][3] == 0:
        #    # and awg<w*h:
        #    # and isLetter(x, y, w, h, th2):
        #    cv2.rectangle(output, (x, y), (x + w, y + h), (100, 2, 2), 1)
        #    im_crop = im.crop((x, y, x+w, y+h))
        #    im_crop.save(f'{img_src[:-4]}-{idd}.jpg', quality=95)
        #    idd += 1

    #вывод
    cv2.imshow("Output", output)
    cv2.imshow('23e', th2)
    cv2.waitKey(0)
    #print(minim, contours)
get_letters('text', False)

#for i in range(1, 10):
#    get_letters(i)