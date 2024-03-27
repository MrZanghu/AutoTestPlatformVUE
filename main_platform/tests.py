class Preson():
    num= 10
    def __ini__(self,age,name):
        self.age= age
        self.name= name

    @classmethod
    def add_num(cls):
        cls.num+= 1

    def print(self):
        print(self.age,self.name,Preson.num)



p1= Preson()
p1.age= 11
p1.name= "test11"

p2= Preson()
p2.age= 22
p2.name= "test22"

Preson.add_num()
p1.print()
p2.print()