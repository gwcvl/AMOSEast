import datetime
import os
import requests
import hashlib
import base64
import psycopg2
import urllib.request
import http.client
# import cv2
# import imageio

from urllib.parse import urlparse
from socket import timeout
from socket import error as SocketError

# from cv2 import VideoWriter, VideoWriter_fourcc, imread, resize


headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}

DATABASE_URL = os.environ['DATABASE_URL']
database = psycopg2.connect(DATABASE_URL, sslmode='require')


# md5 hash to give a hash to specific camera
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    # hexdigest is the string value of the hash
    return hash_md5.hexdigest()


def download_images():
    # connect to database and get list of cameras
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    sql = "SELECT * from cameras"
    cur.execute(sql)
    rows = cur.fetchall()

    # TODO: figure out threading
    for row in rows:

        try:

            myrequest = urllib.request.Request(row[2], None, headers)
            response = urllib.request.urlopen(myrequest, timeout=5)

            dt = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

            os.makedirs('static/images/%s' % (row[0]), exist_ok=True)
            f = open('static/images/%s/%s.jpg' % (row[0], dt), 'wb')
            filepath = ('%s/%s.jpg' % (row[0], dt))
            f.write(response.read())
            f.close()

            if(row[7] == md5('static/images/%s' % filepath)):
                print(
                    "Camera %s has not updated. Image was removed from path..." % (row[0]))
                os.remove('static/images/%s' % (filepath))

            else:
                print("Image from Camera %s is different. Saving image..." %
                      (row[0]))

                sql2 = "UPDATE cameras SET mhash=%s WHERE cameraid = %s"
                cur.execute(
                    sql2, (md5('static/images/%s' % filepath), row[0],))

                conn.commit()

                sql3 = "INSERT INTO images(filepath, curr_time, cameraid) VALUES(%s, %s, %s)"
                cur.execute(sql3, (filepath, dt, row[0]))
                conn.commit()

        except urllib.error.HTTPError as err:
            print(err)
        except urllib.error.URLError as err:
            print(err)
        except timeout:
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


download_images()