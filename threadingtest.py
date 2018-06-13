import datetime
import os
import requests
import hashlib
import base64
import psycopg2
import gevent
import urllib.request
import http.client
# import cv2
# import imageio

from gevent import monkey
from gevent import socket
from gevent.pool import Pool

from urllib.parse import urlparse
from socket import timeout
from socket import error as SocketError

monkey.patch_socket()
pool = Pool(10)
finished = 0
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    # hexdigest is the string value of the hash
    return hash_md5.hexdigest()


query = "SELECT * from cameras"
cur.execute(query)
cameras = cur.fetchall()

camera_urls = []
for camera in cameras:
    camera_urls.append([camera[0], camera[2], camera[7]])


def download_file(index, url, mhash):
    global finished
    print('starting %s' % url)
    try:
        data = urllib.request.urlopen(url, timeout=5)

        dt = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        data = data.read()
        filename = os.path.basename(dt)
        filepath = '%s/%s_%s.jpg' % (index, index, filename)

        os.makedirs('static/images/%s' % index, exist_ok=True)
        f = open('static/images/%s/%s_%s.jpg' % (index, index, filename), 'wb')
        f.write(data)
        f.close()
        if(mhash == md5('static/images/%s' % filepath)):
            print(
                "Camera %s has not updated. Image was removed from path..." % (index))
            os.remove('static/images/%s' % (filepath))
        else:
            print("Image from Camera %s is different. Saving image..." % (index))
            hash_update = "UPDATE cameras SET mhash=%s WHERE cameraid = %s"
            cur.execute(
                hash_update, (md5('static/images/%s' % filepath), index,))

            conn.commit()

            insert_image_table = "INSERT INTO images(filepath, curr_time, cameraid) VALUES(%s, %s, %s)"
            cur.execute(insert_image_table, (filepath, dt, index))
            conn.commit()

    except urllib.error.HTTPError as err:
        print(err)
    except urllib.error.URLError as err:
        print(err)
    except timeout as err:
        print(err)
    except http.client.HTTPException as err:
        print(err)
    except http.client.IncompleteRead as err:
        print(err)
    except http.client.ImproperConnectionState as err:
        print(err)
    except http.client.RemoteDisconnected as err:
        print(err)
    except ConnectionResetError as err:
        print(err)
    except SocketError as err:
        print(err)



# with gevent.Timeout(10000000, False):
# for x in range(10, 10 + N):
jobs = [pool.spawn(download_file, index, url, mhash)
        for index, url, mhash in camera_urls]
# pool.map(jobs)

print('Downloaded images')
