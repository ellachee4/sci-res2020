# read all_pieces and all_pieces_targets from files

import numpy as np
import pickle
import tensorflow as tf
from sklearn.model_selection import KFold
from keras.utils import np_utils
from keras.metrics import Precision, Recall, TrueNegatives, TruePositives, FalseNegatives, FalsePositives
from keras.models import Sequential
from keras.layers import Dense, Flatten, Dropout, Conv1D, MaxPooling1D, Reshape, GlobalAveragePooling1D
from keras.utils import to_categorical
from keras.callbacks import ModelCheckpoint, EarlyStopping

all_pieces_file = open('all_pieces.pkl', mode='rb')
all_pieces = pickle.load(all_pieces_file)
all_pieces_file.close()
print('Got',len(all_pieces),'pieces')

all_pieces_targets_file = open('all_pieces_targets.pkl', mode='rb')
all_pieces_targets = pickle.load(all_pieces_targets_file)
all_pieces_targets_file.close()
print('Got',len(all_pieces_targets),'pieces targets')

# remove pieces with no data (not sure why we had them to start with)
i = len(all_pieces) - 1
while i >= 0:
    if len(all_pieces[i]) == 0:
        del all_pieces[i]
        del all_pieces_targets[i]
    i -= 1
print(len(all_pieces), 'remaining pieces')

# 5-fold cross validation to get train and test sets
kfold = KFold(n_splits=5, shuffle=True)
for train_set, test_set in kfold.split(all_pieces, all_pieces_targets):
    # train set 1
    train_set_pieces_raw = [all_pieces[i] for i in train_set]
    #input - train set 1 MLII signal only        
    train_set_pieces_arr = np.array([[s[0] for s in piece] for piece in train_set_pieces_raw])
    train_set_pieces = train_set_pieces_arr.reshape(train_set_pieces_arr.shape[0], train_set_pieces_arr.shape[1], 1)
    print('train_set_pieces shape: ', train_set_pieces.shape)

    # output - train set target labels
    train_set_targets = np.array([all_pieces_targets[i] for i in train_set])
    print('train_set_targets shape: ', train_set_targets.shape)

    # one-hot encoding of train_set_targets
    # train_set_targets_one_hot = np_utils.to_categorical(train_set_targets, 2)
    # print('New train_set_targets shape: ', train_set_targets_one_hot.shape)

    # test set 1
    test_set_pieces_raw = [all_pieces[i] for i in test_set]
    # input - test set 1 MLII signal only
    test_set_pieces_arr = np.array([[s[0] for s in piece] for piece in test_set_pieces_raw])
    test_set_pieces = test_set_pieces_arr.reshape(test_set_pieces_arr.shape[0], test_set_pieces_arr.shape[1], 1)
    print('test_set_pieces shape: ', test_set_pieces.shape)

    # output - test set target labels
    test_set_targets = np.array([all_pieces_targets[i] for i in test_set])
    print('test_set_targets shape: ', test_set_targets.shape)

    # one-hot encoding of test_set_targets
    # test_set_targets_one_hot = np_utils.to_categorical(test_set_targets, 2)
    # print('New test_set_targets shape: ', test_set_targets_one_hot.shape)

    # 1D CNN to identify AFIB or not AFIB
    filters = 50
    kernel_size = 36
    model_1 = Sequential()
    model_1.add(Conv1D(filters=filters, kernel_size=kernel_size, activation='relu', input_shape=(10800, 1)))
    model_1.add(Conv1D(filters, kernel_size, activation='relu'))
    # added 4 Conv1D layers
    # model_1.add(Conv1D(filters, kernel_size, activation='relu'))
    # model_1.add(Conv1D(filters, kernel_size, activation='relu')) 
    # model_1.add(Conv1D(filters, kernel_size, activation='relu'))
    # model_1.add(Conv1D(filters, kernel_size, activation='relu'))
    model_1.add(MaxPooling1D(3))
    model_1.add(Conv1D(filters, kernel_size, activation='relu'))
    model_1.add(Conv1D(filters, kernel_size, activation='relu'))
    # added 4 Conv1D layers
    # model_1.add(Conv1D(filters, kernel_size, activation='relu'))
    # model_1.add(Conv1D(filters, kernel_size, activation='relu'))
    # model_1.add(Conv1D(filters, kernel_size, activation='relu'))
    # model_1.add(Conv1D(filters, kernel_size, activation='relu'))
    model_1.add(GlobalAveragePooling1D())
    model_1.add(Dropout(0.5))
    model_1.add(Dense(activation='sigmoid', units=1))
    print(model_1.summary())

    callbacks_list = [
    #    ModelCheckpoint(
    #        filepath='best_model.{epoch:02d}-{val_loss:.2f}.h5',
    #        monitor='val_loss', save_best_only=True),
        EarlyStopping(monitor='accuracy', patience=2)
    ]
    model_1.compile(loss='binary_crossentropy',
                    optimizer='adam', metrics=['accuracy', Precision(), Recall(), TrueNegatives(), TruePositives(), FalseNegatives(), FalsePositives(), 'AUC'])

    history = model_1.fit(train_set_pieces,
                        train_set_targets,
                        batch_size=24,
                        epochs=20,
                        callbacks=callbacks_list,
                        validation_split=0,
                        verbose=2)
    print('Training metrics:', history.history)

    results = model_1.evaluate(
        test_set_pieces, test_set_targets, verbose=2, sample_weight=None, return_dict=False)
    print('Test metrics:', results)