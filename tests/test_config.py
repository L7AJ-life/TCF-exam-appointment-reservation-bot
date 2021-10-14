import ujson as json


def read_json_file(file_name: str) -> None:
    try:
        fp = open(file_name, 'r')
        config = json.load(fp)
        fp.close()

        print(json.dumps(config))
    except Exception as e:
        print(f'exception: {e}')


read_json_file('C:\\Users\\s\\Desktop\\config.txt')