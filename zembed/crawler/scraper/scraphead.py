import time
import re
from urllib.parse import urlparse
from ..embed.code import embed_video
from .Image import Image_size


def search(pattern, string):
    _search = re.search(pattern=re.compile(pattern, re.I), string=string)
    return _search


class Scrape:
    def __init__(self, url, data):
        self.base_url = url["provider_url"]
        self.url = url
        self.raw_data = data.text.replace("\n", "")
        self.head = "<head([\S\D]+)</head>"
        self.meta_regex = "<meta(?:\s+)?([^=]+)=(?:\'|\")([^\"\']+)(?:\'|\")(?:(?:\s+)?([^=/>]+)=(?:\'|\")([^\"\']+)(?:\'|\"))?(?:(?:\s+)?([^=>/]+)=(?:\'|\")([^\"]+)(?:\'|\"))?(?:[^>]+)?>"
        # self.meta_regex = "<meta(?:\s+)?([^=]+)=\"([^\"]+)\"(?:(?:\s+)?([^=/>]+)=\"([^\"]+)\")?(?:(?:\s+)?([^=>/]+)=\"([^\"]+)\")?(?:[^>]+)?>"
        self.title_regex = "<title>([^>]+)<\/title>"
        self.body = "<body([\S\D]+)(<\/body ?>)?"
        self.image_regex = "<(?:img|IMG)[^\>]+(?:src|SRC)\s*=\s*(?:\'|\"|)([^\'\"]+\.(?:(?=jpe?g|gif|png|tiff|bmp|jpg)|(?=JPE?G|GIF|PNG|TIFF|BMP))[^\'\" ]+)(?:\'|\"|)(?:[^\>]+)?>"

    def correct_url(self, url):
        try:
            if url:
                # print(url,self.base_url)
                if url.startswith("//"):
                    # print(url)
                    # print(self.url)
                    return self.url["scheme"] + ":" + url.rstrip("\">")
                elif url.startswith("http"):
                    return url
                elif url.startswith(".."):
                    return self.base_url + url.split('..')[1]
                elif url.startswith("/"):
                    return self.base_url + url
                else:
                    _url = urlparse(self.url["origin"])
                    path = "/".join(_url.path.split('/')[1:-1])
                    return _url.scheme + "://" + _url.netloc + "/" + path + "/" + url
        except Exception as e:
            print(e)

    def parse_image_urls(self):                             # fetch all image URLs from body tag
        try:
            img_urls, comp_url = [], []
            string = search(self.body, self.raw_data)
            if string:
                img_urls.extend(re.findall(self.image_regex, string.group(1)))
                for url in set(img_urls):
                    comp_url.append(self.correct_url(url))
            # print(comp_url)
            return comp_url
        except Exception as e:
            print(e)

    def get_meta(self):
        try:
            result, res = {}, {}
            response = []
            metas = re.findall(self.meta_regex, self.raw_data)
            for meta in metas:
                if " content" in meta and " property" in meta:
                    res.update({meta[meta.index(" property") + 1]: meta[meta.index(" content") + 1]})
                elif "content" in meta and "property" in meta:
                    res.update({meta[meta.index("property") + 1]: meta[meta.index("content") + 1]})
                elif "content" in meta and "name" in meta:
                    res.update({meta[meta.index("name") + 1]: meta[meta.index("content") + 1]})
                elif " content" in meta and " name" in meta:
                    res.update({meta[meta.index(" name") + 1]: meta[meta.index(" content") + 1]})
            key = res.keys()

            if "og:title" in key:
                result["title"] = res["og:title"]
            elif "twitter:title" in key:
                result["title"] = res["twitter:title"]
            elif search(self.title_regex, self.raw_data):
                result["title"] = search(self.title_regex, self.raw_data).group(1)
            else:
                result["title"] = ""

            if "og:description" in key:
                result["description"] = res["og:description"]
            elif "twitter:description" in key:
                result["description"] = res["twitter:description"]
            elif "description" in key:
                result["description"] = res["description"]
            else:
                result["description"] = ""

            if "og:video" in key:
                video = embed_video(res["og:video"])
                result["video"] = video
            elif "og:video:url" in key:
                video = embed_video(res["og:video:url"])
                result["video"] = video
            elif "og:video:secure_url" in key:
                video = embed_video(res["og:video:secure_url"])
                result["video"] = video
            else:
                result["video"] = ""
            if "og:audio" in key:
                result["audio"] = res["og:audio"]
            elif "og:audio:url" in key:
                result["audio"] = res["og:audio:url"]
            else:
                result["audio"] = ""
            if "author" in key:
                result["author"] = res["author"]
            elif "twitter:author" in key:
                result["author"] = res["twitter:author"]
            else:
                result["author"] = ""
            if "article:author" in key:
                result["author_url"] = res["article:author"]
            else:
                result["author_url"] = ""
            if "code" in key:
                result["code"] = res["code"]
            else:
                result["code"] = ""
            try:
                if "og:image" in key:
                    s_time = time.time()
                    image = Image_size().body_image_fetch(self.correct_url(res["og:image"]), [])
                    result['mitime'] = time.time() - s_time
                    result["image"] = image
                elif "twitter:image" in key:
                    s_time = time.time()
                    image = Image_size().body_image_fetch(self.correct_url(res["twitter:image"]), [])
                    result['mitime'] = time.time() - s_time
                    result["image"] = image
                elif "twitter:image:src" in key:
                    s_time = time.time()
                    image = Image_size().body_image_fetch(self.correct_url(res["twitter:image:src"]), [])
                    result['mitime'] = time.time() - s_time
                    result["image"] = image
                else:
                    result["image"] = ""

            except Exception as e:
                print(e)
            return result
        except Exception as e:
            print(e)
