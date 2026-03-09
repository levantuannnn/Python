class tango:
    def  __init__(self,name,age,birthday):
        self.name=name
        self.age=age
        self.birthday=birthday
    def Live(self):
        pass
    def hienthi(self): 
        return str(self.age) + " " + self.name + " " + str(self.birthday)
    def get(self):
        print("ao uoc no  khac gi nhau")

kh=tango("le van tuan",19,20)
print(kh.hienthi())