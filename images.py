import argparse
import os
import random
import sys
import tempfile

from os import walk
from os.path import join, exists, basename, splitext
from zipfile import ZipFile
from pathlib import Path

# supported file extensions
image_extensions = ['.jpg', '.png', '.bmp', '.gif']
zip_extensions = ['.zip']

# keep created TemporaryDirectory objects here to prevent it from deletion (will be deleted after program exit)
zip_extract_temp_paths = []

class ImageList:
    def __init__(self):
        self.img_list = []
        self.cur_img_index = 0
        self.cur_image_path = ''

        self.timer_paused = False
        self.max_timer_value = 60
        self.cur_timer = 0
        self.total_time_spent = 0

        self.window_width = 0
        self.window_height = 0

    def getImagePath(self):
        return self.cur_image_path

    def getWindowWidth(self):
        return self.window_width

    def getWindowHeight(self):
        return self.window_height

    def getIndexOfPrevImageInSameFolder(self):

        # search from current index till the beginning of list
        for i in reversed(range(0, self.cur_img_index - 1)):
            if self.img_list[self.cur_img_index].same_folder(self.img_list[i]):
                return i

        # search from the end of the list till current index
        for i in reversed(range(self.cur_img_index + 1, len(self.img_list))):
            if self.img_list[self.cur_img_index].same_folder(self.img_list[i]):
                return i

        return self.cur_img_index + 1

    def getIndexOfNextImageInSameFolder(self):

        # search from current index till the end of list
        for i in range(self.cur_img_index + 1, len(self.img_list)):
            if self.img_list[self.cur_img_index].same_folder(self.img_list[i]):
                return i

        # search from begin of list till current index
        for i in range(0, self.cur_img_index - 1):
            if self.img_list[self.cur_img_index].same_folder(self.img_list[i]):
                return i

        return self.cur_img_index + 1

    def load(self):
        # command line arguments
        parser = argparse.ArgumentParser(description='Gesture drawing helper for artists.')

        parser.add_argument('-path', metavar='path', default='', nargs='+',
                            help='Paths to the images directory (current directory by default). You can specify many '
                                 'directories')

        parser.add_argument('-zip-path', metavar='zip_path', default='',
                            help='Path to the directory with zip files contains images. The one random zip file selected,'
                                 ' then all it images will be shown in random order')

        parser.add_argument('-zip-path-random', metavar='zip_path_random', default='',
                            help='Path to the directory with zip files contains images. All zip files selected,'
                                 ' then all images from all these files will be shown in random order')

        parser.add_argument('-zip-file', metavar='zip_file', default='', nargs='+',
                            help='Zip files with images. You can specify many files.')

        parser.add_argument('-timeout', dest='timeout', type=int, default=60,
                            help='Timeout in seconds (60 by default)')

        parser.add_argument('-width', dest='width', type=int, default=600,
                            help='Window width in pixels (600 by default)')

        parser.add_argument('-height', dest='height', type=int, default=800,
                            help='Window height in pixels (800 by default)')

        args = parser.parse_args()
        print(args)

        if args.zip_file:

            # extract the zip files to temp directories and return list of images inside them
            self.img_list = findAllSupportedZipFiles(self, args.zip_file)

        elif args.zip_path:

            if not args.zip_path or not exists(args.zip_path):
                print('Directory {} not found'.format(args.zip_path))
                sys.exit(-1)

            # if zip-path defined - use it to find archives
            zip_files_list = findAllSupportedFiles([args.zip_path], zip_extensions)

            if len(zip_files_list) == 0:
                print('No supported archives found in directory {}'.format(args.zip_path))
                sys.exit(-1)

            # now peek one random archive file and extract it to the temp directory
            self.img_list = findAllSupportedZipFiles(self, [random.choice(zip_files_list)])

        elif args.zip_path_random:

            if not args.zip_path_random or not exists(args.zip_path_random):
                print('Directory {} not found'.format(args.zip_path_random))
                sys.exit(-1)

            # if zip-path defined - use it to find archives
            zip_files_list = findAllSupportedFiles([args.zip_path_random], zip_extensions)

            if len(zip_files_list) == 0:
                print('No supported archives found in directory {}'.format(args.zip_path))
                sys.exit(-1)

            self.img_list = findAllSupportedZipFilesRandom(self, zip_files_list)

        else:
            # use specified path or current directory to find all supported images
            self.img_list = toImgList(self, findAllSupportedFiles(args.path if args.path else [os.getcwd()], image_extensions))

        if len(self.img_list) == 0:
            print('No supported images found')
            sys.exit(-1)

        # shuffle images
        random.shuffle(self.img_list)

        print('{} images found'.format(len(self.img_list)))

        self.max_timer_value = args.timeout

        self.window_width = args.width
        self.window_height = args.height

    def append_img(self, img):
        self.img_list.append(img)

    def update_list(self):
        if (self.cur_img_index + 1) >= len(self.img_list):
            return

        # make copy
        img_list_copy = self.img_list[(self.cur_img_index + 1):]

        # shuffle it
        random.shuffle(img_list_copy)

        # return temporary list to the back of the list
        self.img_list[(self.cur_img_index + 1):] = img_list_copy

    def getCurTimer(self, decrement=True):

        if self.timer_paused:
            return 'PAUSE'

        if decrement:
            self.cur_timer -= 1

        if self.cur_timer <= 0:
            self.change(1)

            # we must return expired to actually change image
            # when we go back in this function to change timer value
            return 'expired'

        return '{:02d}:{:02d}'.format(int(self.cur_timer / 60), int(self.cur_timer % 60))

    def getCurTimerColor(self):

        if self.timer_paused:
            return 'gray'

        if self.cur_timer <= 5:
            return 'red'

        return 'white'

    def pause(self):
        if self.timer_paused:
            self.timer_paused = False
            print('Unpaused ... ')
        else:
            self.timer_paused = True
            print('Paused ... ')

    def change(self, direction):

        # if it's not the first run - save and print some stats
        if self.cur_image_path != '':
            self.total_time_spent += (self.max_timer_value - max(self.cur_timer, 0))
            print('Image {0} took {1} second(s).'.format(self.cur_img_index, self.max_timer_value - self.cur_timer))

        self.cur_timer = self.max_timer_value

        # unpause if was paused
        if self.timer_paused:
            self.pause()

        # set label default color
        # timeImgLabel.config(foreground=timer_foreground_color)

        # next image index
        if direction == 2:
            # next image in same folder as current image
            self.cur_img_index = self.getIndexOfNextImageInSameFolder()
        elif direction == -2:
            # prev image in same folder as current image
            self.cur_img_index = self.getIndexOfPrevImageInSameFolder()
        else:
            self.cur_img_index += direction

        if self.cur_img_index == len(self.img_list):
            self.cur_img_index = 0
        elif self.cur_img_index < 0:
            self.cur_img_index = len(self.img_list) - 1

        self.cur_image_path = self.img_list[self.cur_img_index].get_path()

        # timeImgLabel.config(image=cur_photo)

        # imgFileNameLabel.config(text=img_list[cur_img_index].get_path(), wraplength=cur_window_width)

    def excludeFolder(self):

        print('Exclude folder/archive: {0}'.format(self.img_list[self.cur_img_index].get_folder()))

        self.img_list = [item for item in self.img_list if not self.img_list[self.cur_img_index].same_folder(item)]

        print('{0} images left, current {1}'.format(len(self.img_list), self.cur_img_index))

        self.change(1)


class ImagePath:
    """Path to image"""

    def __init__(self, par, img_path):
        # ptr to ImageList
        self.parent = par

        self.img_path = img_path

    def get_path(self):
        return self.img_path

    def get_folder(self):
        return Path(self.img_path).parent

    def same_folder(self, other):
        return self.get_folder() == other.get_folder()


class ImagePathInZip(ImagePath):
    """Path to the zip with image in it + image file stored in this zip file
    If img_path empty - read image list from zip"""

    def __init__(self, par, zip_path, img_path, temp_path):
        super().__init__(par, img_path)

        # path to archive
        self.zip_path = zip_path

        # one temporary directory for all zip archive
        self.temp_path = temp_path

        # if image was opened from archive - keep path to it here
        self.real_path_to_img = ''

    def get_folder(self):
        return self.zip_path

    def get_path(self):
        global cur_img_index

        if len(self.real_path_to_img) != 0:
            return self.real_path_to_img

        with ZipFile(self.zip_path, 'r') as zipObj:

            # if img_path empty - read all images from zip
            if not self.img_path or self.img_path == '':
                # create temp directory
                temp_path = tempfile.TemporaryDirectory(prefix=splitext(basename(self.zip_path))[0] + '_')

                # save temp path object in global list
                zip_extract_temp_paths.append(temp_path)

                for img_file in zipObj.namelist():
                    if is_file_valid(img_file, image_extensions):
                        if not self.img_path or self.img_path == '':
                            # set image in current element
                            self.img_path = img_file
                            self.temp_path = temp_path.name
                        else:
                            # add other images in list
                            self.parent.append_img(ImagePathInZip(self.parent, self.zip_path, img_file, temp_path.name))

                # shuffle images which go next in list to keep Next/Prev button working (more or less)
                self.parent.update_list()

            if not self.img_path or self.img_path == '':
                # zip without images - don't know what to do
                return ''

            # extract files into temp directory
            zipObj.extract(self.img_path, self.temp_path)

            # save path to temp directory in list
            self.real_path_to_img = join(self.temp_path, self.img_path)

            return self.real_path_to_img


def is_file_valid(file_name, extensions):
    return any(x in str.lower(file_name) for x in extensions)


def findAllSupportedFiles(path_list, extensions):
    files_list = []

    for path in path_list:
        if not path or not exists(path):
            continue

        for dirpath, dirs, files in walk(path):
            for name in files:
                if is_file_valid(name, extensions):
                    files_list.append(join(dirpath, name))

    return files_list


def toImgList(par, path_list):
    temp_img_list = []

    for path in path_list:
        temp_img_list.append(ImagePath(par, path))

    return temp_img_list


def findAllSupportedZipFiles(par, zip_file_list):
    temp_path_names = []
    for zip_file in zip_file_list:
        if not zip_file or not exists(zip_file):
            print('File {} not found'.format(zip_file))

        with ZipFile(zip_file, 'r') as zipObj:
            # create temp directory
            temp_path = tempfile.TemporaryDirectory()

            # extract files into temp directory
            zipObj.extractall(temp_path.name)

            # save temp path object in global list
            zip_extract_temp_paths.append(temp_path)

            # save path to temp directory in list
            temp_path_names.append(temp_path.name)

    return toImgList(par, findAllSupportedFiles(temp_path_names, image_extensions))


def findAllSupportedZipFilesRandom(par, zip_file_list):
    temp_list = []

    for zip_file in zip_file_list:
        if not zip_file or not exists(zip_file):
            print('File {} not found'.format(zip_file))

        print('File {} found'.format(zip_file))

        temp_list.append(ImagePathInZip(par, zip_file, '', ''))

    return temp_list
