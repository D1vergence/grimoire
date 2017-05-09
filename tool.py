import random
from math import sin,cos
rd=random.randint

def void(x):
    return ''

def limit(x,a,b):
    if a>b:
        t=a;a=b;b=t;
    if x<a:
        return a
    if x>b:
        return b
    return x
    
class vec():
    def __init__(self,x,y):
        self.x=x
        self.y=y
    def mo(self):
        return (self.x**2+self.y**2)**0.5
    def normalize(self):    #规范化
        l=self.mo()
        if l==0 : return 
        self.x/=l
        self.y/=l
    def ran_dif(self,n,gauss=False):    #随机偏移
        if gauss:
            return vec(self.x+random.gauss(0,n),self.y+random.gauss(0,n))
        else:
            return vec(self.x+rd(-n,n),self.y+rd(-n,n))
    def adjust_angle(self,a):   #角度调整
        s,c=(sin(a),cos(a))
        return vec( c*self.x-s*self.y , s*self.x+c*self.y )
    def __mul__(self,n):
        if type(n)==int or type(n)==float:
            return vec(self.x*n,self.y*n)
        if type(n)==vec:
            return self.x*n.x+self.y*n.y
    def __add__(self,v2):
        return vec(self.x+v2[0],self.y+v2[1])
    def __sub__(self,v2):
        return vec(self.x-v2[0],self.y-v2[1])
    def __eq__(self,v2):
        return self.x==v2.x and self.y==v2.y
    def __getitem__(self, n):
        if n==0:
            return self.x
        if n==1:
            return self.y
        

def de(li,f):
    for i in range(len(li))[::-1]:
        if f(li[i]):
            li.pop(i)

class my_list(list):
    def __init__(self,owner):
        super().__init__()
        self.owner=owner
    def append(self,x):
        import effect,unit
        if isinstance(x,effect.effect):
            x.set_owner(self.owner)
        else:
            x.owner=self.owner
        list.append(self,x)
        if isinstance(x,effect.effect) or isinstance(x,unit.unit):
            x.birth()
    def __str__(self):
        return list.__str__(self)

a=[]
all_t=0
def time_log(t,server_mode=True):
    global all_t
    all_t+=t
    if len(a)<100:
        a.append(t)
    else:
        a[rd(0,99)]=t
    a[rd(0,len(a)-1)]=t
    if all_t>5:
        all_t-=5
        n=(1/(sum(a)/len(a)))
        print('平均更新次数/s: %d，'%n,'最慢更新用时: %.3f。'%max(a))
        if server_mode==n<80:
            print('------------------------------')
            print('-----------性能警告-----------')
            print('在过去的1秒内只更新了%d次，'%n,'最慢更新用时: %.3f。'%max(a))
            print('也许你的服务器不适合支持这个规模的游戏……')
            print('------------------------------')
            