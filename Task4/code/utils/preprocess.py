import numpy as np
import h5py
from tqdm import tqdm

f1 = h5py.File("../data_after/train" + "_dataset.hdf5", "w")
train_path = '../data_before/' + 'train' + '/'
f2 = h5py.File("../data_after/test" + "_dataset.hdf5", "w")
test_path = '../data_before/' + 'test' + '/'


def preprocess(path, f):
    for label in tqdm(range(21)):
        grp = f.create_group(str(label), "w")
        for i in tqdm(range(1, 101)):
            image = np.zeros([4, 128, 128])
            _data = np.loadtxt(path + str(label) + '/' + str(i) + '.txt')
            min_time = (int)(_data[0, 0])
            max_time = (int)(_data[-1, 0])
            for j in range(len(_data)):
                if _data[j, 3] == 1:
                    image[0, (int)(_data[j, 1]), (int)(_data[j, 2])] += 1
                    image[2, (int)(_data[j, 1]), (int)(_data[j, 2])] = (
                        _data[j, 0]-min_time) / (max_time - min_time)
                else:
                    image[1, (int)(_data[j, 1]), (int)(_data[j, 2])] += 1
                    image[3, (int)(_data[j, 1]), (int)(_data[j, 2])] = (
                        _data[j, 0]-min_time) / (max_time - min_time)
            grp.create_dataset(name=str(i), data=image)


print("making the train set")
preprocess(train_path, f1)
print("making the test set")
preprocess(test_path, f2)

f1.close()
f2.close()
