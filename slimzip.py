from PIL import Image
from zipfile import ZipFile
from glob import glob
import os
import shutil
from threading import Thread
from ctypes import windll, wintypes, byref

def modify_ctime(path, ctime):
    #https://stackoverflow.com/questions/4996405/how-do-i-change-the-file-creation-date-of-a-windows-file
    # Arbitrary example of a file and a date
    filepath = path
    epoch = ctime

    # Convert Unix timestamp to Windows FileTime using some magic numbers
    # See documentation: https://support.microsoft.com/en-us/help/167296
    timestamp = int((epoch * 10000000) + 116444736000000000)
    ctime = wintypes.FILETIME(timestamp & 0xFFFFFFFF, timestamp >> 32)

    # Call Win32 API to modify the file creation date
    handle = windll.kernel32.CreateFileW(filepath, 256, 0, None, 3, 128, None)
    windll.kernel32.SetFileTime(handle, byref(ctime), None, None)
    windll.kernel32.CloseHandle(handle)

def gen_chunk(images, n):
    return [images[i::n] for i in range(n)]

def image_thread(images):
    for image in images:
        print(image)
        imObj = Image.open(image)
        imObj.save(os.path.splitext(image)[0] + '.webp')
        os.remove(image)

zip_files = glob('*/*.zip')
print(zip_files)
index = 0
number_of_threads = 4

for zip_file in zip_files:
    print(zip_file)
    index = index + 1
    temp = 'temp/' + str(index)
    file_time = (os.stat(zip_file).st_atime, os.stat(zip_file).st_mtime)
    ctime = os.stat(zip_file).st_ctime
    shutil.unpack_archive(zip_file, temp, 'zip')

    images = glob(temp + '/*.??g')
    images_chunk = gen_chunk(images,number_of_threads)
    print(images_chunk)

    threads = []
    for i in range(number_of_threads):
        threads.append(Thread(target=image_thread, args=(images_chunk[i],)))

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    os.remove(zip_file)

    shutil.make_archive(os.path.splitext(zip_file)[0], 'zip', temp)

    shutil.rmtree(temp)
    os.utime(zip_file, file_time)
    modify_ctime(zip_file,ctime)

    # os.remove('temp')


# im1 = Image.open('04.png').convert('RGB')
#
# im1.save('04.jpg')
# im1.save('04.webp', method=6)