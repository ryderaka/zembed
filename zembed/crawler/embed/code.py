from ..scraper.parser import Fetch
import re


def embed_video(url):
    try:
        provider_name = (Fetch(url, "").expand_url(url))['provider_name']
        if provider_name in ["youtu", "youtube"]:
            yid = url.split('/')[-1]
            if '?' in yid:
                yid = yid.split('?')[0]
            return '<iframe width="560" height="315" src="https://www.youtube.com/embed/"'+yid+'" frameborder="0" allowfullscreen></iframe>'

        elif provider_name == "vmeo":
            vid = url.split('/')[-1]
            vid = re.search(r'^(clip_id)?(\d+)', vid)
            return vid.group(1)

        else:
            return url
    except Exception as e:
        print(e)
