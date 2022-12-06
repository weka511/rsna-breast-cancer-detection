TYPE   = 'train_images'
HEADERS = ['10106','10122']

def download(name):
    parts = name.split('/')
    if parts[0].startswith(TYPE) and parts[1] in HEADERS:
        print (name)


with open('../data/files.txt') as f:
    for line in f:
        name = line.split()[0]
        if name.endswith('dcm'):
            download(name)

