import random
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from io import BytesIO
from django.conf import settings
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GPAXF.settings")# project_name 项目名称
django.setup()



class ValidCodeImg:
    def __init__(self, width= 150, height= 30, code_count= 4 ,
                 font_size= 30, point_count= 100,
                 line_count= 5,img_format= 'png'):
        '''
        可以生成一个经过降噪后的随机验证码的图片
        :param width: 图片宽度 单位px
        :param height: 图片高度 单位px
        :param code_count: 验证码个数
        :param font_size: 字体大小
        :param point_count: 噪点个数
        :param line_count: 划线个数
        :param img_format: 图片格式
        :return 生成的图片的bytes类型的data
        '''
        self.width= width
        self.height= height
        self.code_count= code_count
        self.font_size= font_size
        self.point_count= point_count
        self.line_count= line_count
        self.img_format= img_format

    def get_random_color(self):
        '''获取一个随机颜色(r,g,b)，分别给画布、字符、干扰项使用'''
        c1= random.randint(128, 255)
        c2= random.randint(128, 255)
        c3= random.randint(128, 255)
        c4= random.randint(0, 80)
        c5= random.randint(0, 80)
        c6= random.randint(0, 80)
        c7= random.randint(0, 255)
        c8= random.randint(0, 255)
        c9= random.randint(0, 255)
        return [(c1, c2, c3),(c4,c5,c6),(c7,c8,c9)]

    def get_random_str(self):
        '''获取一个随机字符串'''
        random_num= str(random.randint(0, 9))
        random_low_chr= chr(random.randint(97, 122))
        random_upper_chr= chr(random.randint(65, 90))
        random_char= random.choice([random_num, random_low_chr, random_upper_chr])
        return random_char

    def getValidCodeImg(self):
        image= Image.new('RGB', (self.width, self.height), self.get_random_color()[0])
        # 获取一个Image对象，参数分别是RGB模式。宽150，高30，随机颜色
        draw= ImageDraw.Draw(image)
        # 获取一个画笔对象，将图片对象传过去

        font= ImageFont.truetype(settings.FONT_PATH,size= self.font_size)
        # settings文件中的路径导入

        temp= []
        for i in range(self.code_count):
            # 获取4个随机字符串
            random_char= self.get_random_str()
            draw.text((10+ i * 30, 0), random_char, self.get_random_color()[1], font= font)
            # 在图片上一次写入得到的随机字符串,参数是：定位，字符串，颜色，字体
            temp.append(random_char)
        valid_str= "".join(temp)
        # 保存随机字符，以供验证用户输入的验证码是否正确时使用

        for i in range(self.line_count):
            '''随机位置、随机颜色画干扰线'''
            x1= random.randint(0, self.width)
            x2= random.randint(0, self.width)
            y1= random.randint(0, self.height)
            y2= random.randint(0, self.height)
            draw.line((x1, y1, x2, y2), fill= self.get_random_color()[2],width= 1)

        for i in range(self.point_count):
            '''随机位置、随机颜色画干扰点'''
            draw.point([random.randint(0, self.width),
                        random.randint(0, self.height)],
                       fill= self.get_random_color()[2])

        fp= BytesIO()
        image.save(fp, self.img_format)
        # 存到内存中
        return fp, valid_str



if __name__ == '__main__':
    img= ValidCodeImg()
    fp, verify_code= img.getValidCodeImg()
    f= open("validCode.png","wb")
    f.write(fp.getvalue())
    print(verify_code)