import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
from keras.layers import *
from livelossplot import PlotLossesKerasTF
from PIL import Image, ImageOps
import numpy as np
import warnings
import glob


def preprocess(im_data_path, custom_class, size, is_split=True):

    classes = ['maybe', 'you', custom_class]  # if custom class is a list, use + to append
    x = []
    y = []

    for i, v in enumerate(classes):
        print(im_data_path + '/' + v + '*.png')
        files = glob.glob(im_data_path + '/' + v + '*.png')
        print('Num. of files found for the class <' + v + '>: ' + str(len(files)))

        for f in files:
            image = Image.open(f)
            image = ImageOps.fit(image, size, Image.ANTIALIAS)
            image_array = np.asarray(image)
            image_array = image_array[:, :, :3]
            image_array = (image_array.astype(np.float32) / 127.0) - 1
            x.append(image_array)
            y.append(i)
    x = np.array(x)
    y = np.array(y)
    print('x:', x.shape)
    print('y:', y.shape)

    if is_split:
        from sklearn.model_selection import train_test_split
        x_train, x_test, y_train, y_test = train_test_split(x, keras.utils.to_categorical(y),
                                                            test_size=0.2, random_state=1)
        return [x_train, x_test, y_train, y_test]
    else:
        # shuffle
        perm = np.random.permutation(len(y))
        x = x[perm]
        y = y[perm]
        return [x, y]


def CNN_train(data, is_split, num_layers, lr, verbose, num_epochs, model_name):
    print('TF version: ', print(tf.__version__))
    print('GPU: ', tf.config.list_physical_devices('GPU'))

    if is_split:
        x_train, x_test, y_train, y_test = data[0], data[1], data[2], data[3]
        print(x_train.shape)
        print(y_train.shape)
        print(x_test.shape)
        print(y_test.shape)
    else:
        x_train, y_train = data[0], data[1]
    activation = keras.layers.LeakyReLU()
    opt = keras.optimizers.Adam(learning_rate=lr)

    I = Input(shape=(x_train.shape[1], x_train.shape[2], x_train.shape[3]))

    x = Conv2D(256, kernel_size=(3, 3), padding='same', activation=activation)(I)
    x = MaxPooling2D((2, 2))(x)

    for i in range(num_layers-1):
        x = Conv2D(256, kernel_size=(3, 3), padding='same', activation=activation)(x)
        x = MaxPooling2D((2, 2))(x)

    x = Flatten()(x)
    x = Dense(256, activation=activation)(x)
    x = Dropout(0.5)(x)
    x = Dense(128, activation=activation)(x)

    O = Dense(y_train.shape[-1], activation='softmax')(x)

    model = keras.Model(inputs=I, outputs=O)
    model.compile(optimizer=opt, loss='categorical_crossentropy')
    if is_split:
        history = model.fit(x_train, y_train, validation_data=(x_test, y_test), batch_size=8, verbose=verbose,
                            epochs=num_epochs, callbacks=[PlotLossesKerasTF()])
    else:
        history = model.fit(x_train, y_train, batch_size=8, verbose=verbose,
                            epochs=num_epochs, callbacks=[PlotLossesKerasTF()])
    model.save(model_name)

    return model, history


def prediction(model_path, size):
    warnings.filterwarnings("ignore")

    # Load the model
    model = load_model(model_path)

    # Create the array of the right shape to feed into the keras model
    # The 'length' or number of images you can put into the array is
    # determined by the first position in the shape tuple, in this case 1.
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    # Replace this with the path to your image
    image = Image.open('data/raw_data_Raw_0_py.png')

    # resize the image to a 224x224 with the same strategy as in TM2:
    # resizing the image to be at least 224x224 and then cropping from the center
    image = ImageOps.fit(image, size, Image.ANTIALIAS)
    # image = image.resize(size)

    # turn the image into a numpy array
    image_array = np.asarray(image)
    image_array = image_array[:, :, :3]
    # print(image_array.shape)
    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    # Load the image into the array
    data[0] = normalized_image_array

    # run the inference
    predicted = model.predict(data)
    # print(prediction)
    return predicted
