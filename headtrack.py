import pygame
import numpy as np
import sys
import os
from freenect import sync_get_depth as get_depth # get_depth returns an array of 2 elements; [1] array of pixels, and [2] a timestamp
from keras.models import Sequential
from keras.layers import Conv2D, BatchNormalization, Dense, MaxPooling2D, Flatten
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
import cv2
import matplotlib.pyplot as plt

# supress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# config
NFRAMES = 100 # number of frames per observation (@30fps)
NMONITORS = 3 # number of monitors being used
NRESOLUTION = 2325 # max depth (unsure if this is the absolute max)
DEPTH_CAP = 1000
# NRESOLUTION used to be 2048
# TODO CONSIDER capping the NRESOLUTION in the future to be only in the depth range of your body

def record_observation():
    print("\trecording...")
    # record the user looking at something

    frames = []
    for i in range(NFRAMES):
        frame = get_depth()[0][0] # get current frame from connect
        frame = cv2.resize(frame, dsize=(28, 28), interpolation=cv2.INTER_CUBIC) # resize the image to be 32x32
        frame = frame/NRESOLUTION # scale each depth between 0-1

        # verify that its less than max
        maxVal = np.max(frame)
        if(maxVal>=1):
            print(f"Found Max: {maxVal}")

        frames.append(frame.tolist())

    print("\tdone")
    return np.asarray(frames)

def collect_data():
    # collect data of the user looking at the monitor
    y_train_arr = []

    # monitor 1
    input("look at the top left monitor, press any key when ready")
    x_train = record_observation()
    y_train_arr.append(np.full(NFRAMES, 1).tolist()) # create array with all ones
    os.system('play /data/Music/tada.wav')
    # play sound to signify done collecting
    
    # monitor 2
    input("look at the bottom left monitor, press any key when ready")
    x_train = np.concatenate([x_train, record_observation()])
    y_train_arr.append(np.full(NFRAMES, 2).tolist()) # create array with all twos
    os.system('play /data/Music/tada.wav')

    # monitor 3
    input("look at the right monitor, press any key when ready")
    x_train = np.concatenate([x_train, record_observation()])
    y_train_arr.append(np.full(NFRAMES, 3).tolist()) # create array with all threes
    os.system('play /data/Music/tada.wav')

    # no monitors
    input("look away from the monitors, press any key when ready")
    x_train = np.concatenate([x_train, record_observation()])
    y_train_arr.append(np.full(NFRAMES, 0).tolist()) # create array with all zeros
    os.system('play /data/Music/tada.wav')
    
    # convert to numpy arrays, and flatten
    y_train = np.asarray(y_train_arr)
    y_train = y_train.flatten()

    # turn the array into a matrix (one-hot encoding)
    y_train = to_categorical(y_train)

    return (np.asarray(x_train.tolist()), np.asarray(y_train))
    
def make_gamma():
    """
    Create a gamma table
    """
    npf = float(NRESOLUTION)
    _gamma = np.empty((NRESOLUTION, 3), dtype=np.uint16)

    for i in range(NRESOLUTION):
        v = i / npf
        v = pow(v, 3) * 6
        pval = int(v * 6 * 256)
        lb = pval & 0xff
        pval >>= 8
        if pval == 0:
            a = np.array([255, 255 - lb, 255 - lb], dtype=np.uint8)
        elif pval == 1:
            a = np.array([255, lb, 0], dtype=np.uint8)
        elif pval == 2:
            a = np.array([255 - lb, lb, 0], dtype=np.uint8)
        elif pval == 3:
            a = np.array([255 - lb, 255, 0], dtype=np.uint8)
        elif pval == 4:
            a = np.array([0, 255 - lb, 255], dtype=np.uint8)
        elif pval == 5:
            a = np.array([0, 0, 255 - lb], dtype=np.uint8)
        else:
            a = np.array([0, 0, 0], dtype=np.uint8)

        _gamma[i] = a
    return _gamma

# TODO remove
gamma = make_gamma()

# start the phases
(x, y) = collect_data()

print('Raw Data:')
print(x.shape)
print(y.shape)
x = x.reshape([-1, 28, 28, 1])# reshape x_train

# create validation and training set
x_train, x_val, y_train, y_val = train_test_split(x, y, random_state=7, test_size=0.2)

# print some neat details
print('Training Data:')
print(x_train.shape)
print(y_train.shape)

print('Validation Data:')
print(x_val.shape)
print(y_val.shape)

# create the model
model = Sequential()
# filters are also called kernels, so... filters is number of segments to take of picture, and kernal_size is the size of the filter
model.add(Conv2D(filters=32, kernel_size=(3,3), activation='relu', input_shape=(28, 28, 1)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dense(4, activation='softmax')) # 3 monitors + no monitor

# sanity check: x_train should be an array of pixels

# compile
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# train
#cbk_early_stopping = EarlyStopping(monitor='val_acc', mode='max')
#model.fit(x_train, y_train, epochs=100, validation_data=(x_val, y_val), callbacks=[cbk_early_stopping])
model.fit(x_train, y_train, epochs=100, validation_data=(x_val, y_val))

# save
model.save('trackv2.model')

# show the cam
if __name__ == "__main__":
    fpsClock = pygame.time.Clock()
    FPS = 30 # kinect only outputs 30 fps
    disp_size = (640, 480)
    pygame.init()
    screen = pygame.display.set_mode(disp_size)
    font = pygame.font.Font(pygame.font.get_default_font(), 32) # provide your own font 
    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                sys.exit()
        fps_text = "FPS: {0:.2f}".format(fpsClock.get_fps())

        # get sensor data
        depth = np.rot90(get_depth()[0]) # get the depth readings from the camera

        # show the camera
        pixels = gamma[depth] # the colour pixels are the depth readings overlayed onto the gamma table
        temp_surface = pygame.Surface(disp_size)
        pygame.surfarray.blit_array(temp_surface, pixels)
        pygame.transform.scale(temp_surface, disp_size, screen)
        screen.blit(font.render(fps_text, 1, (255, 255, 255)), (30, 30))
        pygame.display.flip()
        fpsClock.tick(FPS)
