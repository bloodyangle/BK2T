
def isIn(source,target):
    count = 0
    for index in source:
        if index in target:
            count += 1
            if count <= len(source):
                return True
            return False