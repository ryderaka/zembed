import requests
from re import search


class Fetch:
    def __init__(self, url, data):
        self.url = url
        self.url_data = data

    def expand_url(self, base_url):
        try:
            tld = ['com', 'org', 'net', 'int', 'edu', 'gov', 'mil', 'arpa']
            urlregex = "(((?:http|ftp)s?):\/\/(?:www)?\.?(([^\.]+)\.([^\/\.]+)\.?([^\/\.]+)?\.?([^\/\.]+)?\.?([^\/\.]+)?))(?:.+)?"

            url_data = search(urlregex, self.url)
            dot_count = (url_data.group(3).count("."))
            if dot_count == 1:
                provider_name = url_data.group(4)
            elif dot_count == 2:               # if the last word of url is of length 2
                provider_name = url_data.group(5) if len(url_data.group(5)) != 2 and url_data.group(5) not in tld else url_data.group(4)
            elif dot_count == 3:
                provider_name = url_data.group(5)
            elif dot_count == 4:
                provider_name = url_data.group(6)
            return {
                "scheme": url_data.group(2),
                "url": base_url,
                "origin": self.url,
                "provider": self.url.split('/')[2],
                "provider_name": provider_name,
                "provider_url":  url_data.group(1)
            }
        except Exception as e:
            print(e)

    def get_url_data(self):
        response = ""
        try:
            if not self.url is None:
                try:
                    response = requests.get(
                        self.url,
                        allow_redirects=True,
                        headers={
                            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                          "Chrome/55.0.2883.87 Safari/537.36"
                        }, verify=False, timeout=5
                    )
                except Exception as e:
                     print(e)
            return response
        except Exception as e:
            print(e)

    def get_header(self):
        # try:
        header = ""
        if self.url_data:
            head = self.url_data.headers
            if 'status' in head and head['status'] == 'BYPASS':
                head['status'] = '200'
            header = {
                "status": int(head['status'].replace(',', ' ').split(' ')[0]) if 'status' in head.keys() else self.url_data.status_code,
                "type": head["content-type"].split(';')[0] if "content-type" in head.keys() else "",
                "length": head["content-length"] if "content-length" in head.keys() else 0,
            }
        else:
            header = {
                "status": "",
                "type": "",
                "length": "",
            }
        return header
        # except Exception as e:
        #     print(e)


'''
    def url_header(self):
        head = requests.get(self.url, verify=False)
        # print('url_header head', head)
        return head[0].status_code if isinstance(head, tuple) else head.status_code
'''

