
fff=dict()

class fh(object):
    def __init__(self,i):
        self.f=open("/mnt/c/tmp/"+str(i)+".tmp","w")
        #self.f=open("c:/tmp/"+str(i)+".tmp","w")
    def write(self,line):
        self.f.write(line)
    def close(self,):
        self.f.close()
for i in range(5000):
    fff[i]=fh(i)
for i in range(200):
    for j in range(5000):
        fff[j].write(str(i)+"aa"+str(j)+"\n")
for i in range(1000):
    fff[i].close()   
    
'''
sub system中python3的IO不如win下python的IO
'''
 