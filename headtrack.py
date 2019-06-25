import pygame
import numpy as np
import sys
import os
from freenect import sync_get_depth as get_depth # get_depth returns an array of 2 elements; [1] array of pixels, and [2] a timestamp
from keras.models import Sequential
from keras.layers import Conv2D, BatchNormalization, Dense, Input

# supress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# config
NFRAMES = 100 # number of frames per observation (@30fps, ~3 sec)
NMONITORS = 3 # number of monitors being used
NRESOLUTION = 2048 # number of depth 'pixels'

def record_observation():
    print("\trecording...")
    # record the user looking at something

    frames = []
    for i in range(NFRAMES):
        frames.append(get_depth()[0].tolist())

    print("\tdone")
    return frames # returns regular array

def collect_data():
    # collect data of the user looking at the monitor
    x_train_arr = []
    y_train_arr = []

    # monitor 1
    #input("look at the top left monitor, press any key when ready")
    x_train_arr.append(record_observation())
    y_train_arr.append(np.full(NFRAMES, 1).tolist()) # create array with all ones
    """
    # monitor 2
    input("look at the bottom left monitor, press any key when ready")
    x_train_arr.append(record_observation())
    y_train_arr.append(np.full(NFRAMES, 2).tolist()) # create array with all twos

    # monitor 3
    input("look at the right monitor, press any key when ready")
    x_train_arr.append(record_observation())
    y_train_arr.append(np.full(NFRAMES, 3).tolist()) # create array with all threes

    # no monitors
    input("look away from the monitors, press any key when ready")
    x_train_arr.append(record_observation())
    y_train_arr.append(np.full(NFRAMES, 0).tolist()) # create array with all zeros
    """
    # flatten and convert to numpy arrays
    x_train = np.asarray(x_train_arr)
    y_train = np.asarray(y_train_arr)
    x_train = x_train.flatten()
    y_train = y_train.flatten()

    return (x_train, y_train)
    
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

# shuffle the data
indices = np.arange(len(y))
np.random.shuffle(indices)
x = x[indices]
y = y[indices]

# randomly seperate 10% as validation data
split_at = len(x) - len(x) // 10
(x_train, x_val) = x[:split_at], x[split_at:]
(y_train, y_val) = y[:split_at], y[split_at:]

# print some neat details
print('Training Data:')
print(x_train.shape)
print(y_train.shape)

print('Validation Data:')
print(x_val.shape)
print(y_val.shape)

# create the model
model = Sequential()
# TODO try adding 'Input' layer
model.add(Conv2D(64, activation='relu', kernel_size=3, input_shape=(640, 480, 1))) # 64 'nodes'
model.add(Dense(4)) # 3 monitors + no monitor

# compile
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# train
BATCH_SIZE = 24
EPOCHS = 5
model.fit(x_train, y_train, batch_size=BATCH_SIZE, epochs=EPOCHS, validation_data=(x_val, y_val))
model.save('trackv1.model')

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
