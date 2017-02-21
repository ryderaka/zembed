from io import BytesIO
# import logging
from PIL import Image
from threading import Thread
from .parser import Fetch


class Image_size:
    def __init__(self):
        self.allowed_types = ['image/jpeg', 'text/html', 'image/jpg', 'image/png', 'image/gif', 'image/webp',
                              'image/tiff', 'image/bmp', ""]
        self.threads = 4
        self.width = 200
        self.height = 200

    @staticmethod
    def colour(i):
        try:
            if i.mode == "RGB":
                h = i.histogram()
                return [int(sum(i * w for i, w in enumerate(h[256 * x: 256 * (x + 1)])) / sum(h[256 * x: 256 * (x + 1)])) for x
                        in range(3)]
            elif i.mode == "RGBA":
                h = i.histogram()
                result = [int(sum(i * w for i, w in enumerate(h[256 * x: 256 * (x + 1)])) / sum(h[256 * x: 256 * (x + 1)])) for x
                        in range(4)]
                result[3] = round((result[3]/255), 1)
                return result

            elif i.mode == "P":
                h = i.getpalette()
                return [int(sum(i * w for i, w in enumerate(h[256 * x: 256 * (x + 1)])) / sum(h[256 * x: 256 * (x + 1)])) for x
                        in range(3)]
        except Exception as e:
            print(e)

    def body_image_fetch(self, url, images_data=None):
        try:
            response = Fetch(url, "").get_url_data()
            header = Fetch(url, response).get_header()
            # print('header', header)

            if header["status"] in [200, '200, 200 OK', '200 OK'] and header["type"] in self.allowed_types:
                # print('after condition', header['status'])
                # print(response.content)
                image = Image.open(BytesIO(response.content))
                res = {
                       "height": image.size[0],
                       "mode": image.mode,
                       "width": image.size[1],
                       "mime": str(header["type"]),
                       "ratio": round((float((image.size[1] / image.size[0]) * 100)), 2),
                       "colors": Image_size.colour(image),
                       "size": image.size[0]*image.size[1] if header["length"] == 0 else header["length"],
                       "url": url
                }
                images_data.append(res)
                return res
        except Exception as e:
            print(e)

    def get_best_image(self, urls):
        try:
            # print(urls)
            while urls:
                images_data, final_image, total_threads = [], [], []
                if len(urls) > self.threads:
                    image_sublist = list(urls[0:self.threads])
                    del (urls[0:self.threads])
                else:
                    image_sublist = list(urls)
                    urls.clear()

                for url in image_sublist:
                    thread = Thread(target=self.body_image_fetch, args=(url, images_data))
                    total_threads.append(thread)
                    thread.start()

                for thread in total_threads:
                    thread.join()
                # print(images_data)
                for item in images_data:
                    if item['height'] >= self.height and item['width'] >= self.width:
                        final_image = item
                        self.height = item['height']
                        self.width = item['width']

                if final_image:
                    return [final_image]
        except Exception as e:
            print(e)
