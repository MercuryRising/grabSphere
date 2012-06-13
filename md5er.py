import md5

def filemd5(fp, block_size=128):
    has = md5.new()
    with open(fp, 'rb') as f:
        data = f.read(block_size)
        has.update(data)
    return has.hexdigest()

if __name__ == '__main__':
    a = filemd5('watchedFolders.py')
    print a

