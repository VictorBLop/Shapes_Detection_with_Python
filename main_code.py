1
2 import time
3 import random as rng
4 import cv2 as cv
5 import numpy as np
6 import math
7
8 #Iniciamos la camara
9 captura = cv.VideoCapture(1)
10
11 #Establecemos el rango de colores que vamos a detectar
12 #En este caso de verde oscuro a verde-azulado claro
13 sensivity=15
14 yellow=30
15 rojo_bajos_0 = np.array([0, 100, 100], dtype=np.uint8)
16 rojo_altos_0 = np.array([sensivity, 255, 255], dtype=np.uint8)
17 rojo_bajos_1 = np.array([180-sensivity, 100, 100], dtype=np.uint8)
18 rojo_altos_1 = np.array([180, 255, 255], dtype=np.uint8)
19
20 azul_bajos = np.array([100, 65, 75], dtype=np.uint8)
21 azul_altos = np.array([130, 255, 255], dtype=np.uint8)
22
23 blanco_bajos = np.array([0, 0, 255-sensivity], dtype=np.uint8)
24 blanco_altos = np.array([180, sensivity, 255], dtype=np.uint8)
25
26 amarillo_bajos = np.array([yellow-sensivity, 100, 255], dtype=np.uint8)
27 amarillo_altos = np.array([yellow+sensivity, 100, 255], dtype=np.uint8)
28
29 null=np.array([0, 0, 0], dtype=np.uint8)
30 #Crear un kernel de '1' de 3x3
31 kernel = np.ones((3,3),np.uint8)
32
33 def detection(color_low,color_high,color_low_plus,
color_high_plus,color,imagen):
34 #Crear una mascara con solo los pixeles dentro del rango de verdes
35 mask = cv.inRange(hsv, color_low, color_high)
36
37 if color_low_plus[0]!=0 or color_low_plus[1]!=0 or color_low_plus[2]!=0:
38 mask2=cv.inRange(hsv, color_low_plus, color_high_plus)
39 mask=cv.bitwise_or(mask,mask2)
40
41 #Se aplica la transformacion: Opening
42 trans1 = cv.morphologyEx(mask,cv.MORPH_OPEN,kernel)
43 trans2 = cv.morphologyEx(trans1,cv.MORPH_CLOSE,kernel)
44 #trans3 = cv.morphologyEx(mask,cv.MORPH_HITMISS,kernel)
45
46 src=trans2
47 # Find contours
48 contours, hierarchy = cv.findContours(src, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
49 # Get the moments
50 mu = [None]*len(contours)
51 v = [0]*len(contours)
52 for i in range(len(contours)):
53 mu[i] = cv.moments(contours[i])
54 if mu[i]['m00']>3000 and mu[i]['m00']<75000:
55 v[i]=1
56
57 # Get the mass centers
58 mc = [None]*len(contours)
59 for i in range(len(contours)):
60 # add 1e-5 to avoid division by zero
61 if v[i]==1:
62 mc[i] = (mu[i]['m10'] / (mu[i]['m00'] + 1e-5), mu[i]['m01'] / (mu[i]['m00'] +
1e-5))
63
64 # Draw contours
65 drawing = np.zeros((len(src), len(src[0]), 3), dtype=np.uint8)
66 drawing=imagen
67 for i in range(len(contours)):
68 if v[i]==1:
69 cv.drawContours(drawing, contours, i, (255,0,255), 1)
70
71 # Approximate contours to polygons + get bounding rects and circles
72 contours_poly = [None]*len(contours)
73 boundRect = [None]*len(contours)
74 minEllipse = [None]*len(contours)
75 minRect = [None]*len(contours)
76 N=15
77 for i,cin enumerate(contours):
78 contours_poly[i] = cv.approxPolyDP(c, 0.03*cv.arcLength(c,True), True)
79 boundRect[i] = cv.boundingRect(contours_poly[i])
80 if v[i]==1:
81 if c.shape[0]>5:
82 minEllipse[i] = cv.fitEllipse(c)
83 minRect[i] = cv.minAreaRect(c)
84 area_ellipse=minEllipse[i][1][0]*minEllipse[i][1][1]
85 area_rect=minRect[i][1][0]*minRect[i][1][1]
86 if math.fabs(area_ellipse-area_rect)<150 and
math.fabs(minEllipse[i][0][0]-minRect[i][0][0])<3 and
math.fabs(minEllipse[i][0][1]-minRect[i][0][1])<3:
87 v[i]=2
88 print("CIRCULO SIGNAL")
89 cv.ellipse(drawing, minEllipse[i], (0,255,0), 2)
90
91 if v[i]==1:
92 if len(contours_poly[i])==3 and (color==(255,255,0) or color==(0,0,255) or
color==(255,255,255)):
93 print("TRIANGULO")
94
lato1=(contours_poly[i][0][0][0]-contours_poly[i][1][0][0])*(contours_poly
[i][0][0][0]-contours_poly[i][1][0][0])+(contours_poly[i][0][0][1]-contour
s_poly[i][1][0][1])*(contours_poly[i][0][0][1]-contours_poly[i][1][0][1])
95
lato2=(contours_poly[i][1][0][0]-contours_poly[i][2][0][0])*(contours_poly
[i][1][0][0]-contours_poly[i][2][0][0])+(contours_poly[i][1][0][1]-contour
s_poly[i][2][0][1])*(contours_poly[i][1][0][1]-contours_poly[i][2][0][1])
96
lato3=(contours_poly[i][2][0][0]-contours_poly[i][0][0][0])*(contours_poly
[i][2][0][0]-contours_poly[i][0][0][0])+(contours_poly[i][2][0][1]-contour
s_poly[i][0][0][1])*(contours_poly[i][2][0][1]-contours_poly[i][0][0][1])
97 dif=10000
98 #print("lati:",lato1,lato2,lato3)
99 if math.fabs(lato1-lato2)<dif or math.fabs(lato2-lato3)<dif or
math.fabs(lato3-lato1)<dif:
100 v[i]=3
101 print("TRIANGULO SIGNAL")
102 cv.drawContours(drawing, contours_poly, i, (0,255,0), 2)
103 elif len(contours_poly[i])==4 and (color==(255,255,0) or color==(255,0,0) or
color==(255,255,255)):
104 print("CUADRADO")
105
lato1=(contours_poly[i][0][0][0]-contours_poly[i][1][0][0])*(contours_poly
[i][0][0][0]-contours_poly[i][1][0][0])+(contours_poly[i][0][0][1]-contour
s_poly[i][1][0][1])*(contours_poly[i][0][0][1]-contours_poly[i][1][0][1])
106
lato2=(contours_poly[i][1][0][0]-contours_poly[i][2][0][0])*(contours_poly
[i][1][0][0]-contours_poly[i][2][0][0])+(contours_poly[i][1][0][1]-contour
s_poly[i][2][0][1])*(contours_poly[i][1][0][1]-contours_poly[i][2][0][1])
107
lato3=(contours_poly[i][2][0][0]-contours_poly[i][3][0][0])*(contours_poly
[i][2][0][0]-contours_poly[i][3][0][0])+(contours_poly[i][2][0][1]-contour
s_poly[i][3][0][1])*(contours_poly[i][2][0][1]-contours_poly[i][3][0][1])
108
lato4=(contours_poly[i][3][0][0]-contours_poly[i][0][0][0])*(contours_poly
[i][3][0][0]-contours_poly[i][0][0][0])+(contours_poly[i][3][0][1]-contour
s_poly[i][0][0][1])*(contours_poly[i][3][0][1]-contours_poly[i][0][0][1])
109 dif=10000
110 #print("lati:",lato1,lato2,lato3,lato4)
111 if math.fabs(lato1-lato3)<dif and math.fabs(lato2-lato4)<dif:
112 v[i]=4
113 print("CUADRADO SIGNAL")
114 cv.drawContours(drawing, contours_poly, i, (0,255,0), 2)
115 elif len(contours_poly[i])==8 and color==(0,0,255):
116 print("OCTOGONO")
117
lato1=(contours_poly[i][0][0][0]-contours_poly[i][1][0][0])*(contours_poly
[i][0][0][0]-contours_poly[i][1][0][0])+(contours_poly[i][0][0][1]-contour
s_poly[i][1][0][1])*(contours_poly[i][0][0][1]-contours_poly[i][1][0][1])
118
lato2=(contours_poly[i][1][0][0]-contours_poly[i][2][0][0])*(contours_poly
[i][1][0][0]-contours_poly[i][2][0][0])+(contours_poly[i][1][0][1]-contour
s_poly[i][2][0][1])*(contours_poly[i][1][0][1]-contours_poly[i][2][0][1])
119
lato3=(contours_poly[i][2][0][0]-contours_poly[i][3][0][0])*(contours_poly
[i][2][0][0]-contours_poly[i][3][0][0])+(contours_poly[i][2][0][1]-contour
s_poly[i][3][0][1])*(contours_poly[i][2][0][1]-contours_poly[i][3][0][1])
120
lato4=(contours_poly[i][3][0][0]-contours_poly[i][4][0][0])*(contours_poly
[i][3][0][0]-contours_poly[i][4][0][0])+(contours_poly[i][3][0][1]-contour
s_poly[i][4][0][1])*(contours_poly[i][3][0][1]-contours_poly[i][4][0][1])
121
lato5=(contours_poly[i][4][0][0]-contours_poly[i][5][0][0])*(contours_poly
[i][4][0][0]-contours_poly[i][5][0][0])+(contours_poly[i][4][0][1]-contour
s_poly[i][5][0][1])*(contours_poly[i][4][0][1]-contours_poly[i][5][0][1])
122
lato6=(contours_poly[i][5][0][0]-contours_poly[i][6][0][0])*(contours_poly
[i][5][0][0]-contours_poly[i][6][0][0])+(contours_poly[i][5][0][1]-contour
s_poly[i][6][0][1])*(contours_poly[i][5][0][1]-contours_poly[i][6][0][1])
123
lato7=(contours_poly[i][6][0][0]-contours_poly[i][7][0][0])*(contours_poly
[i][6][0][0]-contours_poly[i][7][0][0])+(contours_poly[i][6][0][1]-contour
s_poly[i][7][0][1])*(contours_poly[i][6][0][1]-contours_poly[i][7][0][1])
124
lato8=(contours_poly[i][7][0][0]-contours_poly[i][0][0][0])*(contours_poly
[i][7][0][0]-contours_poly[i][0][0][0])+(contours_poly[i][7][0][1]-contour
s_poly[i][0][0][1])*(contours_poly[i][7][0][1]-contours_poly[i][0][0][1])
125 dif=10000
126 if math.fabs(lato1-lato5)<dif and math.fabs(lato2-lato6)<dif and
math.fabs(lato3-lato7)<dif and math.fabs(lato4-lato8)<dif:
127 v[i]=5
128 print("OCTOGONO SIGNAL")
129 cv.drawContours(drawing, contours_poly, i, (0,255,0), 2)
130
131
132 for i in range(len(contours)):
133 if v[i]>1:
134 j=0
135 aux=0
136 while aux==0 and j<len(contours):
137 if v[j]>1:
138 if i!=j and mc[i][0]>boundRect[j][0] and
mc[i][0]<boundRect[j][0]+boundRect[j][2] and mc[i][1]>boundRect[j][1]
andmc[i][1]<boundRect[j][1]+boundRect[j][3]:
139 if boundRect[i][2]*boundRect[i][3] >boundRect[j][2]*boundRect[j][3]:
140 v[j]=1
141 else:
142 v[i]=1
143 aux=1
144 j+=1
145
146 for i in range(len(contours)):
147 if v[i]>1:
148 cv.circle(drawing, (int(mc[i][0]), int(mc[i][1])), 3, (0,255,0), -1)
149 cv.rectangle(drawing, (int(boundRect[i][0]), int(boundRect[i][1])), \
150 (int(boundRect[i][0]+boundRect[i][2]), int(boundRect[i][1]+boundRect[i][3])),
(125,125,0), 1)
151
152 return drawing,src;
153
154 while(1):
155 #Capturamos una imagen y la convertimos de RGB -> HSV
156 #_, imagen = captura.read()
157 imagen=cv.imread('signal1.jpg',cv.IMREAD_COLOR)
158 hsv = cv.cvtColor(imagen, cv.COLOR_BGR2HSV)
159
160 draw1,src1=detection(azul_bajos,azul_altos,null,null,(255,0,0),imagen)
161 draw2,src2=detection(rojo_bajos_0,rojo_altos_0,rojo_bajos_1,rojo_altos_1,(0,0,255),draw1)
162 draw3,src3=detection(blanco_bajos,blanco_altos,null,null,(255,255,255),draw2)
163 draw4,src4=detection(amarillo_bajos,amarillo_altos,null,null,(255,255,0),draw3)
164
165 draw=draw4
166 src=src1+src2+src3+src4
167
168 # Show in a window
169 cv.imshow('mask',src)
170 cv.imshow('Contours', draw)
171
172 #tecla = cv.waitKey(5) & 0xFF
173 #time.sleep(2)
174 #if tecla == 27:
175 # break
176 while(1):
177 tecla = cv.waitKey(5) &0xFF
178 if tecla == 27:
179 break
180
181 cv.destroyAllWindows()
