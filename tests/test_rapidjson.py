import ujson as json
import re
import html

fp = open('C:\\Users\\s\\Desktop\\file.txt', 'r', encoding='utf-8')
text = ''.join(fp.readlines())
fp.close()

text = html.unescape(text)
data = re.findall('(?<=defaultEvents\s\W\s)(.*)(?=\]\;)', text,
                   re.DOTALL | re.MULTILINE | re.VERBOSE | re.IGNORECASE)

data = ''.join(data) + ']'
for word in ["uid", "title", "start", "duration", "minutes", "className", "level", "price", "antenna_name", "antenna_id", "local", "status", "full"]:
    data = data.replace(word, f'"{word}"')
    #data = re.sub(r'{"minutes":"[0-9]{0,3}"}', "0", data)
data = data.replace('\n', '')
data = ','.join([d.strip() for d in data.split(',')])
data = '}'.join([d.strip() for d in data.split('}')])
data = '{'.join([d.strip() for d in data.split('{')])
data = data.replace(',]', ']')
print(data)

fp = open('C:\\Users\\s\\Desktop\\file1.txt', 'w')
fp.write(data)
fp.close()

print(type(json.loads(data)))

