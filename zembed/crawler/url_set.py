import json


with open ('urls.json','r') as ip:
	file = json.load(ip)
	new_urls = []
	for i in (file):
		if i in new_urls:
			continue
		else:
			new_urls.append(i)
	print((new_urls))

with open('new_urls.txt','a') as nip:
	for i in new_urls:
		nip.write(i)
