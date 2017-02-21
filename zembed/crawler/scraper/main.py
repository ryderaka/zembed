# import re
import time
from .Image import Image_size
from .scraphead import Scrape
# from .json import create_json
# from .scraper.main import main


def main(input_url, data):
    try:
        start = time.time()

        scrape_obj = Scrape(input_url, data)

        meta = scrape_obj.get_meta()
        meta_time = time.time() - start
        start2 = time.time()
        # print(meta)
        if meta is None or "image" not in meta or meta["image"] in [None, [], "", (None,), ('',)]:
            # if meta is None or "image" not in meta or meta["image"] is None:
            parse_image_urls = scrape_obj.parse_image_urls()            # all image URLs
            meta["parse_image_urls_time"] = time.time() - start2
            start3 = time.time()
            image_data = Image_size().get_best_image(urls=parse_image_urls)
            meta["image"] = image_data
            meta["image_data"] = time.time() - start3

        meta["url"] = input_url,
        meta["video"] = meta["video"] if "image" in meta.keys() else "",
        # print(meta['video'])
        meta["image"] = meta["image"] if "image" in meta.keys() else "",
        meta["time"] = {
            "get_meta_time": meta_time - meta['mitime'] if "mitime" in meta.keys() else meta_time,
            "meta_image_time": meta['mitime'] if "mitime" in meta.keys() else "",
            "image_data": meta["image_data"] if "image_data" in meta.keys() else "",
            "parse_image_urls_time": meta["parse_image_urls_time"] if "parse_image_urls_time" in meta.keys() else "",
            "total_time": time.time() - start,
        }
        meta["poster"] = "" if meta["video"] in ["", None, (None,), ('',), []] else meta["image"]
        return meta
    except Exception as e:
        print(e)
