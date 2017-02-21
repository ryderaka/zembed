import json
import time
from .scraper.main import main
from .scraper.parser import Fetch
from .scraper.json import create_json
from .scraper.Image import Image_size
import logging
from threading import Thread
from pymongo import MongoClient

# fetching urls from file/set threading
url_threads = 100

# output files
input_file = 'urls.json'
# output_file = 'op_files/opfile.json'
err_file = 'op_files/log.log'
# err_urls = 'op_files/error_urls.txt'
# null_image = 'op_files/null_image_urls.json'
# time_urls = 'op_files/time_urls.json'
# status_error = 'op_files/status_error.txt'
# status404 = 'op_files/status404.json'

# mongo authentication
db_name = 'zembed'
collection_name = 'scrapper_op_100'
collection_status = 'scrapper_error_100'

user = 'zembed'
password = '$C}(38G>LTff5,pU'
mclient = MongoClient('mongodb://'+user+':'+password+'@localhost:45651/zembed')
# mclient = MongoClient('mongodb://'+user+':'+password+'@127.0.0.1')


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename=err_file,
                    filemode='a')


def call(url):
    allow_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/tiff',
                   'image/bmp']
    start = time.time()

    try:
        print(url)
        raw_data = Fetch(url, '').get_url_data()  # fetch url data
        end = time.time()
        if raw_data.headers['content-type'].split(';')[0] in ['text/html', 'text/html; charset=utf-8'] or raw_data.headers['content-type'] in allow_types:

            if Fetch(url, raw_data).get_header() and Fetch(url, raw_data).get_header()['status'] in [200, '200, 200 OK', '200 OK']:

                if Fetch(url,raw_data).get_header()['type'] in allow_types:
                    data = {
                        "url": url,
                        "image": Image_size().body_image_fetch(raw_data.url, []),
                        "time": time.time() - start
                    }
                else:
                    url_parsing = Fetch(raw_data.url, "").expand_url(url)  # URL parsing details
                    meta = main(url_parsing, raw_data)
                    if meta["image"] in [None, [], "", (None,), ('',)] or not meta["image"]:
                        meta["image"] = Image_size().body_image_fetch("https://logo.clearbit.com/"+url_parsing['provider_url']+"?s=300", [])

                    data = create_json(meta)
                    data["time"]["page_fetch"] = end - start
                    data["time"]["total_time"] += data["time"]["page_fetch"]
                    # print(data['image'])
                    # if data['image'] is None:
                        # with open(null_image, 'a') as image_file:
                        #     json.dump(data, image_file)
                        #     image_file.write('\n')
                    # elif data['time']['total_time'] > 5:
                    #     print(data['time']['total_time'])
                        # with open(time_urls, 'a') as time_file:
                        #     json.dump(data, time_file)
                        #     time_file.write('\n')

                # with open(output_file, 'a') as opfile:
                #     json.dump(data, opfile)
                #     opfile.write('\n')
                try:
                    client = mclient
                    db = client[db_name]
                    collection = db[collection_name]
                    collection.insert(data)
                except Exception as e:
                    print('failed ondata,', str(e))

            # elif Fetch(url, raw_data) and Fetch(url, raw_data).url_header() in [404, '404', ""]:
            elif raw_data[0].status_code if isinstance(raw_data, tuple) else raw_data.status_code in [404, '404', ""]:

                data = {
                    "url": url,
                    "time": time.time() - start,
                    "title": 'Error 404: Page not found',
                    "comment": 'Error 404'
                }
                # with open(status404, 'a') as not_found:
                #     json.dump(data, not_found)
                #     not_found.write('\n')
                try:
                    client = mclient
                    db = client[db_name]
                    collection = db[collection_status]
                    collection.insert(data)
                except Exception as e:
                    print('failed ondata,', str(e))


            else:
                data = {
                    "url": url,
                    "time": time.time() - start,
                    "title": Fetch(url,raw_data).url_header() if (Fetch(url,raw_data) and Fetch(url,raw_data).url_header()) else 'Unknown Error code',
                    "comment": 'Status Error'
                }

                # with open(status_error, 'a') as status:
                #     status.write(url)
                #     status.write('\n')

                try:
                    client = mclient
                    db = client[db_name]
                    collection = db[collection_status]
                    collection.insert(data)
                except Exception as e:
                    print('failed ondata,', str(e))


        else:
            data = {
                "url": url,
                "time": time.time() - start,
                "title": raw_data.headers['content-type'],
                "comment": 'Not suitable Webpage'
            }
            

            # with open(status_error, 'a') as status:
            #     status.write(url)
            #     status.write('\n')

            try:
                client = mclient
                db = client[db_name]
                collection = db[collection_status]
                collection.insert(data)
            except Exception as e:
                print('failed ondata,', str(e))


    except Exception as e:
        # with open(err_urls,'a') as err_url:
        #     err_url.write(url)
        #     err_url.write('\n')
        # with open(err_file,'a') as err:
        #     err.write('error in url:'+url)
        #     print(e,' error in url: ', url)
        #     err.write('\n')
        logging.info(url)
        logging.exception(e)

        data = {
            "url": url,
            "time": time.time() - start,
            "title": 'URL Error',
            "comment": 'URL Error'
        }
        try:
            client = mclient
            db = client[db_name]
            collection = db[collection_status]
            collection.insert(data)
        except Exception as e:
            print('failed ondata,', str(e))



with open("urls.json", 'r') as oip_urls:
    ip_urls = []
    oip_urls = json.load(oip_urls)
    for i in oip_urls:
        if i not in ip_urls:
            ip_urls.append(i)
    print(len(ip_urls))

    while ip_urls:
        total_threads = []
        if len(ip_urls) > url_threads:
            url_sublist = list(ip_urls[0:url_threads])
            del (ip_urls[0:url_threads])
        else:
            url_sublist = list(ip_urls)
            ip_urls.clear()
        for url in url_sublist:
            thread = Thread(target=call, args=(url,))
            thread.start()
            total_threads.append(thread)

        for thread in total_threads:
            thread.join()
        time.sleep(0)


