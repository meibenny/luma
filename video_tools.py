import cv2

def grab_first_frame(filename):
    print(filename)
    #cap = cv2.VideoCapture(filename)
    #_, frame = cap.read()
    #_, frame = cap.read()
    #b,g,r = cv2.split(frame)
    #recolored_frame = cv2.merge((r,g,b))

    cap = cv2.VideoCapture(filename)
    _, frame = cap.read()
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

    return cv2image