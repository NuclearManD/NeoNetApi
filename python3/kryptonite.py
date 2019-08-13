from netcrypt import decrypt1, encrypt1, shortstrhash
import os

class CryptFS:
    def __init__(self, password, location="."):
        self.location = os.path.realpath(location)+'/'
        if type(password)==str:
            password=password.encode()
        self.key=password

        if not os.path.isdir(self.location):
            os.makedirs(self.location)
            self.filenames = []
        else:
            self.filenames = self.read("@filenames")
            if self.filenames==-1:
                self.filenames = []
            else:
                self.filenames = eval(self.filenames)
    def read(self, fn):
        nfn=shortstrhash(fn+self.key.decode())+".enc"
        p=os.path.join(self.location, nfn)
        if not os.path.isfile(p):
            return -1

        f=open(p,'rb')
        return decrypt1(f.read(), self.key+fn.encode())
    def write(self, fn, data):
        nfn=shortstrhash(fn+self.key.decode())+".enc"
        p=os.path.join(self.location, nfn)

        f=open(p,'wb')
        f.write(encrypt1(data, self.key+fn.encode()))
        f.close()

        if not fn in self.filenames and fn!="@filenames":
            self.filenames.append(fn)
            self.write("@filenames",repr(self.filenames))
    def cpin(self, src, dst):
        f = open(src, 'rb')
        data = f.read()
        f.close()

        self.write(dst, data)
    def cpout(self, src, dst):
        data = self.read(src)
        f=open(dst,'wb')
        f.write(data)
        f.close()

