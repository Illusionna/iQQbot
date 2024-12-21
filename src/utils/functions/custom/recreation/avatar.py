# /get_image 获取图片
# https://**i.pximg.net**
# https://q1.qlogo.cn/g?b=qq&nk=3516515029&s=640

import os
import re
import time
import random
import requests
from PIL import Image, ImageDraw
from ....tools.inherit import Function, Run
from ....tools.send import send_message


class Chop(Function, Run):
    invoke = '/斩'
    permission = 1
    description = '指令 + 用户'

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{Chop.invoke} ', '', 1)
        if text != Chop.invoke:
            who = Chop.__parse(text)
            if who:
                try:
                    os.makedirs('./cache/avatar-result', exist_ok=True)
                    if who.isdigit():
                        if os.path.exists(f'./cache/avatar-result/avatar-result-{who}.png'):
                            path = os.path.abspath(f'./cache/avatar-result/avatar-result-{who}.png')
                            send_message(f'[CQ:image,file={path}]', self.params['config']['socket'], data)
                        else:
                            Chop.__download(f'https://q1.qlogo.cn/g?b=qq&nk={who}&s=140', who)
                            Chop.__circle(f'./cache/avatar-result/avatar-{who}.jpg', who)
                            Chop.__split_circle_image(f'./cache/avatar-result/avatar-circle-{who}.png', f'./cache/avatar-result/avatar-result-{who}.png')
                            path = os.path.abspath(f'./cache/avatar-result/avatar-result-{who}.png')
                            send_message(f'[CQ:image,file={path}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        if os.path.exists(f'./cache/avatar-result/avatar-result-{tmp}.png'):
                            path = os.path.abspath(f'./cache/avatar-result/avatar-result-{tmp}.png')
                            send_message(f'[CQ:image,file={path}]', self.params['config']['socket'], data)
                        else:
                            Chop.__download(f'https://q1.qlogo.cn/g?b=qq&nk={tmp}&s=140', tmp)
                            Chop.__circle(f'./cache/avatar-result/avatar-{tmp}.jpg', tmp)
                            Chop.__split_circle_image(f'./cache/avatar-result/avatar-circle-{tmp}.png', f'./cache/avatar-result/avatar-result-{tmp}.png')
                            path = os.path.abspath(f'./cache/avatar-result/avatar-result-{tmp}.png')
                            send_message(f'[CQ:image,file={path}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)
        else:
            send_message('大家好好相处嘛 ( ´థ౪థ）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None

    @staticmethod
    def __circle(local_path: str, avatar: str) -> None:
        image = Image.open(local_path)
        circle_image = Image.new('RGBA', image.size)
        draw = ImageDraw.Draw(circle_image)
        draw.ellipse([(0, 0), image.size], fill=(255, 255, 255))
        result = Image.new('RGBA', image.size)
        result.paste(image, mask=circle_image)
        result.save(f'./cache/avatar-result/avatar-circle-{avatar}.png')

    @staticmethod
    def __download(url: str, avatar: str) -> None:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            with open(f'./cache/avatar-result/avatar-{avatar}.jpg', 'wb') as f:
                f.write(response.content)
        else:
            pass

    @staticmethod
    def __split_circle_image(image_path, output_path, offset=5, separation=20) -> None:
        original = Image.open(image_path).convert('RGBA')
        width, height = original.size
        radius = min(width, height) // 2
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, width, height), fill=255)
        circle = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        circle.paste(original, (0, 0), mask)
        left_half = circle.crop((0, 0, radius - offset, height))
        right_half = circle.crop((radius + offset, 0, width, height))
        canvas_width = left_half.width + right_half.width + separation
        canvas_height = height
        canvas = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
        canvas.paste(left_half, (0, 0))
        canvas.paste(right_half, (left_half.width + separation, 0))
        canvas = canvas.rotate(30, expand=False)
        canvas.save(output_path)


class DrawTool:
    """
    Meme-with-QQavatar: 作者“怕瓦落地”
    """
    def __init__(self):
        self.basePath = os.path.dirname(os.path.realpath(__file__))
        self.drawPath = os.path.join(self.basePath, "draw")
        self.resultDirPath = os.path.join(os.getcwd(), 'cache', "avatar-result")
        if not os.path.exists(self.resultDirPath):
            os.mkdir(self.resultDirPath)
        self.avatarDirPath = os.path.join(os.getcwd(), 'cache', 'avatar')
        if not os.path.exists(self.avatarDirPath):
            os.mkdir(self.avatarDirPath)

    # 返回一个数组，里面是每个结果图片的本地绝对路径
    def wantDraw(self, text):

        # 返回头像，size 格式应为 (width, height)，默认裁剪为圆的
        def getAvatar(text, size, needClipToCircle: bool = True):
            if text.isdigit():
                theQQ = int(text)
            else:
                beginIndex = text.find("[@")
                endIndex = text.find("]")
                if beginIndex != -1 and endIndex != -1 and beginIndex + 2 < endIndex and text[beginIndex + 2:endIndex].isdigit():
                    theQQ = int(text[beginIndex + 2:endIndex])
                else:
                    return None

            url = "http://q1.qlogo.cn/g?b=qq&nk={}&s=640".format(theQQ)
            r = requests.get(url)
            if r.status_code != 200:
                return None
            avatarPath = os.path.join(self.avatarDirPath, "{}.jpg".format(theQQ))
            with open(avatarPath, "wb") as f:
                f.write(r.content)
            avatar = Image.open(avatarPath)
            avatar = avatar.resize(size)
            avatar = avatar.convert("RGBA")
            if needClipToCircle:
                circle = Image.new('L', avatar.size, 0)  # 创建一个黑色正方形画布
                draw = ImageDraw.Draw(circle)
                draw.ellipse((0, 0, avatar.size[0], avatar.size[1]), fill=255)  # 画一个白色圆形
                avatar.putalpha(circle)  # 白色区域透明可见，黑色区域不可见
            return avatar

        if text.startswith("丢"):
            avatar = getAvatar(text[1:], (300, 300))
            if avatar is None:
                return None
            throw = Image.open(os.path.join(self.drawPath, "丢.jpg"))
            throw = throw.resize((512, 512))
            theAvatar = avatar.resize((100, 100))
            throw.paste(theAvatar, (30, 200), theAvatar.split()[3])
            resultPath = os.path.join(self.resultDirPath, "{}.jpg".format(time.time()))
            throw.save(resultPath)
            # 另一个 丢
            throwPath = os.path.join(self.drawPath, "throw")
            throwImages = []
            for i in range(0, 8):
                backImage = Image.open(os.path.join(throwPath, "throw_{}.png".format(i + 1)))
                if i + 1 == 1:
                    theAvatar = avatar.resize((34, 34))
                    backImage.paste(theAvatar, (108, 35), theAvatar.split()[3])
                elif i + 1 == 2:
                    theAvatar = avatar.resize((34, 34))
                    backImage.paste(theAvatar, (122, 34), theAvatar.split()[3])
                elif i + 1 == 3:
                    theAvatar = avatar.resize((19, 19))
                    backImage.paste(theAvatar, (143, 41), theAvatar.split()[3])
                elif i + 1 == 4:
                    theAvatar = avatar.resize((126, 126))
                    backImage.paste(theAvatar, (17, 128), theAvatar.split()[3])
                elif i + 1 == 5:
                    theAvatar = avatar.resize((190, 190))
                    backImage.paste(theAvatar, (-53, 199), theAvatar.split()[3])
                    theAvatar = avatar.resize((39, 39))
                    backImage.paste(theAvatar, (287, 67), theAvatar.split()[3])
                elif i + 1 == 6:
                    theAvatar = avatar.resize((37, 37))
                    backImage.paste(theAvatar, (276, 69), theAvatar.split()[3])
                elif i + 1 == 7:
                    theAvatar = avatar.resize((38, 38))
                    backImage.paste(theAvatar, (258, 30), theAvatar.split()[3])
                elif i + 1 == 8:
                    theAvatar = avatar.resize((180, 180))
                    backImage.paste(theAvatar, (-53, 219), theAvatar.split()[3])
                throwImages.append(backImage)
            resultPath2 = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            throwImages[0].save(resultPath2, format="GIF", append_images=throwImages[1:], save_all=True, duration=100, loop=0)
            # 第三个 丢
            throwPath = os.path.join(self.drawPath, "throw-2")
            throwImages = []
            theAvatar = avatar.resize((84, 84))
            positions = [(199, 32), (114, -1), (22, 30), (0, 46), (100, -1), (195, 29)]
            for i in range(0, 6):
                backImage = Image.open(os.path.join(throwPath, "throw_{}.png".format(i + 1)))
                backImage.paste(theAvatar, positions[i], theAvatar.split()[3])
                throwImages.append(backImage)
            resultPath3 = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            throwImages[0].save(resultPath3, format="GIF", append_images=throwImages[1:], save_all=True, duration=100, loop=0)
            return [resultPath, resultPath2, resultPath3]
        elif text.startswith("仰望大佬"):
            avatar = getAvatar(text[4:], (100, 100))
            if avatar is None:
                return None
            admire = Image.open(os.path.join(self.drawPath, "仰望大佬.jpg"))
            admire = admire.resize((1080, 1080))
            admire.paste(avatar, (395, 460), avatar.split()[3])
            admire.paste(avatar, (606, 442), avatar.split()[3])
            resultPath = os.path.join(self.resultDirPath, "{}.jpg".format(time.time()))
            admire.save(resultPath)
            return [resultPath]
        elif text.startswith("打拳"):
            avatar = getAvatar(text[2:], (73, 73))
            if avatar is None:
                return None
            boxingPath = os.path.join(self.drawPath, "boxing")
            boxingImages = []
            positions = [(6, 25), (12, 20), (17, 13), (21, 8), (27, 4), (32, 7), (37, 12), (41, 17), (42, 19), (34, 13), (25, 8), (17, 5), (11, 5), (7, 10), (6, 18), (5, 23)]
            for i in range(0, 16):
                frontImage = Image.open(os.path.join(boxingPath, "boxing_{}.png".format(i + 1)))
                img = Image.new("RGBA", frontImage.size, (255, 255, 255))  # 白底
                img.paste(avatar, positions[i], avatar.split()[3])  # 加上圆头像
                img.paste(frontImage, (0, 0), frontImage.split()[3])  # 加上拳头
                boxingImages.append(img)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            boxingImages[0].save(resultPath, format="GIF", append_images=boxingImages[1:], save_all=True, duration=40, loop=0)
            return [resultPath]
        elif text.startswith("打"):
            avatar = getAvatar(text[1:], (300, 300))
            if avatar is None:
                return None
            hitPath = os.path.join(self.drawPath, "hit")
            hitImages = []
            positions = [(161, 121), (173, 124), (208, 166)]
            sizes = [(75, 75), (68, 68), (52, 52)]
            for i in range(0, 3):
                backImage = Image.open(os.path.join(hitPath, "hit_{}.png".format(i + 1)))
                theAvatar = avatar.resize(sizes[i])
                backImage.paste(theAvatar, positions[i], theAvatar.split()[3])
                hitImages.append(backImage)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            hitImages[0].save(resultPath, format="GIF", append_images=hitImages[1:], save_all=True, duration=100, loop=0)
            # 另一个 打
            avatar = avatar.resize((27, 27))
            hitPath = os.path.join(self.drawPath, "hit-2")
            hitImages = []
            for i in range(0, 6):
                backImage = Image.open(os.path.join(hitPath, "hit_{}.png".format(i + 1)))
                if (i + 1) % 2 == 1:
                    backImage.paste(avatar, (66, 58), avatar.split()[3])
                else:
                    backImage.paste(avatar, (72, 62), avatar.split()[3])
                hitImages.append(backImage)
            resultPath2 = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            hitImages[0].save(resultPath2, format="GIF", append_images=hitImages[1:], save_all=True, duration=100, loop=0)
            return [resultPath, resultPath2]
        elif text.startswith("摸头"):
            avatar = getAvatar(text[2:], (30, 30))
            if avatar is None:
                return None
            touchPath = os.path.join(self.drawPath, "touchHead")
            touchImages = []
            positions = [(50, 50), (52, 50), (54, 50), (56, 50), (58, 50)]
            sizes = [(80, 80), (70, 75), (60, 70), (50, 65), (80, 80)]
            for i in range(0, 5):
                img = Image.new("RGBA", (160, 160), (255, 255, 255))  # 白底
                frontImage = Image.open(os.path.join(touchPath, "touchHead_{}.bmp".format(i + 1)))
                frontImage = frontImage.convert("RGBA")
                theAvatar = avatar.resize(sizes[i])
                img.paste(theAvatar, positions[i], theAvatar.split()[3])  # 加上头像
                img.paste(frontImage, (0, 0), frontImage.split()[3])  # 加上手
                touchImages.append(img)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            touchImages[0].save(resultPath, format="GIF", append_images=touchImages[1:], save_all=True, duration=60, loop=0)
            return [resultPath]
        elif text.startswith("摸鱼"):
            # 静止的摸鱼图
            avatar = getAvatar(text[2:], (287, 287))
            if avatar is None:
                return None
            frontImage = Image.open(os.path.join(self.drawPath, "摸鱼.png"))
            fish = Image.new("RGBA", frontImage.size, (255, 255, 255))  # 白底
            fish.paste(avatar, (14, 11), avatar.split()[3])  # 加上头像
            fish.paste(frontImage, (0, 0), frontImage.split()[3])  # 加上鱼
            resultPath = os.path.join(self.resultDirPath, "{}.png".format(time.time()))
            fish.save(resultPath)
            # 摸鱼动图
            avatar = avatar.resize((144, 144))
            touchFishPath = os.path.join(self.drawPath, "touchFish")
            touchFishImages = []
            for i in range(0, 6):
                frontImage = Image.open(os.path.join(touchFishPath, "touchFish_{}.png".format(i + 1)))
                img = Image.new("RGBA", frontImage.size, (255, 255, 255))
                img.paste(avatar, (78, 77), avatar.split()[3])
                img.paste(frontImage, (0, 0), frontImage.split()[3])
                touchFishImages.append(img)
            resultPath2 = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            touchFishImages[0].save(resultPath2, format="GIF", append_images=touchFishImages[1:], save_all=True, duration=130, loop=0)
            return [resultPath, resultPath2]
        elif text.startswith("摸"):
            avatar = getAvatar(text[1:], (30, 30))
            if avatar is None:
                return None
            touchPath = os.path.join(self.drawPath, "touch")
            touchImages = []
            for i in range(0, 4):
                frontImage = Image.open(os.path.join(touchPath, "touch_{}.png".format(i + 1)))
                img = Image.new("RGBA", frontImage.size, (255, 255, 255))  # 白底
                img.paste(avatar, (11, 45), avatar.split()[3])  # 加上圆头像
                img.paste(frontImage, (0, 0), frontImage.split()[3])  # 加上人
                touchImages.append(img)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            touchImages[0].save(resultPath, format="GIF", append_images=touchImages[1:], save_all=True, duration=60, loop=0)
            return [resultPath]
        elif text.startswith("敲"):
            avatar = getAvatar(text[1:], (75, 75))
            if avatar is None:
                return None
            knockPath = os.path.join(self.drawPath, "knock")
            knockImages = []
            knockImages.append(Image.open(os.path.join(knockPath, "knock_1.png")))
            knockImages.append(Image.open(os.path.join(knockPath, "knock_2.png")))
            knockImages[0].paste(avatar, (25, 95), avatar.split()[3])
            avatar = avatar.resize((70, 70))
            knockImages[1].paste(avatar, (25, 95), avatar.split()[3])
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            knockImages[0].save(resultPath, format="GIF", append_images=knockImages[1:], save_all=True, duration=80, loop=0)
            # 另一个 敲
            avatar = avatar.resize((25, 25))
            knockPath = os.path.join(self.drawPath, "knock-2")
            knockImages = []
            for i in range(0, 3):
                backImage = Image.open(os.path.join(knockPath, "knock_{}.png".format(i + 1)))
                backImage.paste(avatar, (63, 57), avatar.split()[3])
                knockImages.append(backImage)
            resultPath2 = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            knockImages[0].save(resultPath2, format="GIF", append_images=knockImages[1:], save_all=True, duration=200, loop=0)
            return [resultPath, resultPath2]
        elif text.startswith("赞"):
            avatar = getAvatar(text[1:], (70, 70))
            if avatar is None:
                return None
            praisePath = os.path.join(self.drawPath, "praise")
            praiseImages = []
            for i in range(0, 6):
                backImage = Image.open(os.path.join(praisePath, "praise_{}.png".format(i + 1)))
                if i > 2:
                    backImage.paste(avatar, (200, 10), avatar.split()[3])
                praiseImages.append(backImage)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            praiseImages[0].save(resultPath, format="GIF", append_images=praiseImages[1:], save_all=True, duration=200, loop=0)
            return [resultPath]
        elif text.startswith("旋转"):
            avatar = getAvatar(text[2:], (146, 146))
            if avatar is None:
                return None
            whirlPath = os.path.join(self.drawPath, "whirl")
            whirlImages = []
            for i in range(0, 30):
                backImage = Image.open(os.path.join(whirlPath, "whirl_{}.png".format(i + 1)))
                theAvatar = avatar.rotate(-12 * i)  # 头像旋转
                backImage.paste(theAvatar, (43, 17), theAvatar.split()[3])
                whirlImages.append(backImage)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            whirlImages[0].save(resultPath, format="GIF", append_images=whirlImages[1:], save_all=True, duration=50, loop=0)
            return [resultPath]
        elif text.startswith("吃"):
            avatar = getAvatar(text[1:], (290, 290))
            if avatar is None:
                return None
            frontImage = Image.open(os.path.join(self.drawPath, "eat.png"))
            eat = Image.new("RGBA", frontImage.size, (255, 255, 255))  # 白底
            eat.paste(avatar, (86, 155), avatar.split()[3])  # 加上头像
            eat.paste(frontImage, (0, 0), frontImage.split()[3])  # 加上鲨鱼
            resultPath = os.path.join(self.resultDirPath, "{}.png".format(time.time()))
            eat.save(resultPath)
            # 另一个 吃
            eat = Image.open(os.path.join(self.drawPath, "eat-2.jpg"))
            theAvatar = avatar.resize((158, 152))
            eat.paste(theAvatar, (179, 172), theAvatar.split()[3])
            resultPath2 = os.path.join(self.resultDirPath, "{}.jpg".format(time.time()))
            eat.save(resultPath2)
            return [resultPath, resultPath2]
        elif text.startswith("吞"):
            avatar = getAvatar(text[1:], (300, 300))
            if avatar is None:
                return None
            swallowPath = os.path.join(self.drawPath, "swallow")
            swallowImages = []
            for i in range(0, 31):
                frontImage = Image.open(os.path.join(swallowPath, "swallow_{}.png".format(i + 1)))
                backImage = Image.new("RGBA", frontImage.size, (255, 255, 255))  # 白底
                # 加上头像
                if i + 1 <= 5:
                    theAvatar = avatar.resize((82, 82))
                    backImage.paste(theAvatar, (0, 174), theAvatar.split()[3])
                elif i + 1 == 6:
                    theAvatar = avatar.resize((82, 83))
                    backImage.paste(theAvatar, (12, 160), theAvatar.split()[3])
                elif i + 1 == 7:
                    theAvatar = avatar.resize((81, 83))
                    backImage.paste(theAvatar, (19, 152), theAvatar.split()[3])
                elif i + 1 == 8:
                    theAvatar = avatar.resize((81, 83))
                    backImage.paste(theAvatar, (23, 148), theAvatar.split()[3])
                elif i + 1 == 9:
                    theAvatar = avatar.resize((81, 83))
                    backImage.paste(theAvatar, (26, 145), theAvatar.split()[3])
                elif i + 1 == 10:
                    theAvatar = avatar.resize((80, 83))
                    backImage.paste(theAvatar, (32, 140), theAvatar.split()[3])
                elif i + 1 == 11:
                    theAvatar = avatar.resize((82, 83))
                    backImage.paste(theAvatar, (37, 136), theAvatar.split()[3])
                elif i + 1 == 12:
                    theAvatar = avatar.resize((81, 84))
                    backImage.paste(theAvatar, (42, 131), theAvatar.split()[3])
                elif i + 1 == 13:
                    theAvatar = avatar.resize((82, 83))
                    backImage.paste(theAvatar, (49, 127), theAvatar.split()[3])
                elif i + 1 == 14:
                    theAvatar = avatar.resize((82, 82))
                    backImage.paste(theAvatar, (70, 126), theAvatar.split()[3])
                elif i + 1 == 15:
                    theAvatar = avatar.resize((79, 80))
                    backImage.paste(theAvatar, (88, 128), theAvatar.split()[3])
                elif i + 1 == 16:
                    theAvatar = avatar.resize((80, 79))
                    backImage.paste(theAvatar, (-30, 210), theAvatar.split()[3])
                elif i + 1 == 17:
                    theAvatar = avatar.resize((76, 77))
                    backImage.paste(theAvatar, (-19, 207), theAvatar.split()[3])
                elif i + 1 == 18:
                    theAvatar = avatar.resize((74, 75))
                    backImage.paste(theAvatar, (-14, 200), theAvatar.split()[3])
                elif i + 1 == 19:
                    theAvatar = avatar.resize((81, 82))
                    backImage.paste(theAvatar, (-10, 188), theAvatar.split()[3])
                elif i + 1 == 20:
                    theAvatar = avatar.resize((82, 84))
                    backImage.paste(theAvatar, (-7, 179), theAvatar.split()[3])
                elif i + 1 == 21:
                    theAvatar = avatar.resize((81, 83))
                    backImage.paste(theAvatar, (-3, 170), theAvatar.split()[3])
                elif i + 1 == 22:
                    theAvatar = avatar.resize((82, 82))
                    backImage.paste(theAvatar, (-3, 175), theAvatar.split()[3])
                elif i + 1 == 23:
                    theAvatar = avatar.resize((82, 82))
                    backImage.paste(theAvatar, (-1, 174), theAvatar.split()[3])
                elif i + 1 >= 24:
                    theAvatar = avatar.resize((82, 82))
                    backImage.paste(theAvatar, (0, 174), theAvatar.split()[3])
                backImage.paste(frontImage, (0, 0), frontImage.split()[3])  # 加上可莉
                swallowImages.append(backImage)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            swallowImages[0].save(resultPath, format="GIF", append_images=swallowImages[1:], save_all=True, duration=50, loop=0)
            return [resultPath]
        elif text.startswith("咬"):
            avatar = getAvatar(text[1:], (96, 97))
            if avatar is None:
                return None
            bitePath = os.path.join(self.drawPath, "bite")
            biteImages = []
            positions = [(108, 234), (108, 237)]
            sizes = [(98, 101), (96, 100)]
            for i in range(0, 2):
                frontImage = Image.open(os.path.join(bitePath, "bite_{}.png".format(i + 1)))
                img = Image.new("RGBA", frontImage.size, (255, 255, 255))
                theAvatar = avatar.resize(sizes[i])
                img.paste(theAvatar, positions[i], theAvatar.split()[3])
                img.paste(frontImage, (0, 0), frontImage.split()[3])
                biteImages.append(img)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            biteImages[0].save(resultPath, format="GIF", append_images=biteImages[1:], save_all=True, duration=100, loop=0)
            return [resultPath]
        elif text.startswith("快逃"):
            avatar = getAvatar(text[2:], (100, 100))
            if avatar is None:
                return None
            escapePath = os.path.join(self.drawPath, "escape")
            escapeImages = []
            positions = [(112, 95), (112, 95), (93, 87), (82, 67), (82, 76), (85, 75), (85, 75), (85, 75)]
            sizes = [(86, 86), (86, 86), (100, 100), (104, 104), (103, 103), (103, 103), (103, 103), (103, 103)]
            for i in range(0, 8):
                frontImage = Image.open(os.path.join(escapePath, "escape_{}.png".format(i + 1)))
                img = Image.new("RGBA", frontImage.size, (255, 255, 255))
                theAvatar = avatar.resize(sizes[i])
                img.paste(theAvatar, positions[i], theAvatar.split()[3])
                img.paste(frontImage, (0, 0), frontImage.split()[3])
                escapeImages.append(img)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            escapeImages[0].save(resultPath, format="GIF", append_images=escapeImages[1:], save_all=True, duration=150, loop=0)
            return [resultPath]
        elif text.startswith("色色"):
            avatar = getAvatar(text[2:], (103, 103))
            if avatar is None:
                return None
            eroticPath = os.path.join(self.drawPath, "erotic")
            eroticImages = []
            positions = [(14, 36), (-12, 18), (38, 28), (4, 9), (50, 42), (18, 1), (-4, 3), (51, 20), (2, 26), (44, 40), (12, 5), (50, 30), (3, 35), (53, 2), (8, 23), (8, 22), (57, 12), (-3, 13), (-8, 7), (-14, 28), (41, 43), (26, 9)]
            for i in range(0, 22):
                frontImage = Image.open(os.path.join(eroticPath, "erotic_{}.png".format(i + 1)))
                img = Image.new("RGBA", frontImage.size, (255, 255, 255))  # 白底
                img.paste(avatar, positions[i], avatar.split()[3])  # 加上头像
                img.paste(frontImage, (0, 0), frontImage.split()[3])  # 加上色色牌子
                eroticImages.append(img)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            eroticImages[0].save(resultPath, format="GIF", append_images=eroticImages[1:], save_all=True, duration=100, loop=0)
            return [resultPath]
        elif text.startswith("舔"):
            avatar = getAvatar(text[1:], (44, 44))
            if avatar is None:
                return None
            lickPath = os.path.join(self.drawPath, "lick")
            lickImages = []
            for i in range(0, 2):
                backImage = Image.open(os.path.join(lickPath, "lick_{}.png".format(i + 1)))
                backImage.paste(avatar, (10, 138), avatar.split()[3])
                lickImages.append(backImage)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            lickImages[0].save(resultPath, format="GIF", append_images=lickImages[1:], save_all=True, duration=100, loop=0)
            return [resultPath]
        elif text.startswith("拍"):
            avatar = getAvatar(text[1:], (29, 29))
            if avatar is None:
                return None
            patPath = os.path.join(self.drawPath, "pat")
            patImages = []
            positions = [(2, 45), (2, 65)]
            for i in range(0, 2):
                backImage = Image.open(os.path.join(patPath, "pat_{}.png".format(i + 1)))
                backImage.paste(avatar, positions[i], avatar.split()[3])
                patImages.append(backImage)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            patImages[0].save(resultPath, format="GIF", append_images=patImages[1:], save_all=True, duration=100, loop=0)
            return [resultPath]
        elif text.startswith("爬"):
            avatar = getAvatar(text[1:], (83, 83))
            if avatar is None:
                return None
            path = os.path.join(self.drawPath, "爬")
            # 随机找一张 爬 图片
            filelist = os.listdir(path)
            index = random.randint(0, len(filelist) - 1)
            creep = Image.open(os.path.join(path, filelist[index]))
            creep = creep.resize((500, 500))
            creep.paste(avatar, (0, 415), avatar.split()[3])
            resultPath = os.path.join(self.resultDirPath, "{}.jpg".format(time.time()))
            creep.save(resultPath)
            return [resultPath]
        elif text.startswith("推"):
            avatar = getAvatar(text[1:], (279, 279))
            if avatar is None:
                return None
            pushPath = os.path.join(self.drawPath, "push")
            pushImages = []
            for i in range(0, 16):
                backImage = Image.open(os.path.join(pushPath, "push_{}.png".format(i + 1)))
                theAvatar = avatar.rotate(-22.5 * i)  # 头像旋转
                backImage.paste(theAvatar, (384, 152), theAvatar.split()[3])  # 加上头像
                pushImages.append(backImage)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            pushImages[0].save(resultPath, format="GIF", append_images=pushImages[1:], save_all=True, duration=100, loop=0)
            return [resultPath]
        elif text.startswith("踢"):
            avatar = getAvatar(text[1:], (74, 74))
            if avatar is None:
                return None
            kickPath = os.path.join(self.drawPath, "kick")
            kickImages = []
            positions = [(58, 137), (57, 118), (56, 100), (53, 114), (51, 127), (49, 140), (48, 113), (48, 86), (48, 58), (49, 98), (51, 137), (52, 177), (53, 170), (56, 182), (59, 154)]
            for i in range(0, 15):
                backImage = Image.open(os.path.join(kickPath, "kick_{}.png".format(i + 1)))
                theAvatar = avatar.rotate(-24 * i)  # 头像旋转
                backImage.paste(theAvatar, positions[i], theAvatar.split()[3])  # 加上头像
                kickImages.append(backImage)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            kickImages[0].save(resultPath, format="GIF", append_images=kickImages[1:], save_all=True, duration=100, loop=0)
            return [resultPath]
        elif text.startswith("捂脸"):
            avatar = getAvatar(text[2:], (419, 419))
            if avatar is None:
                return None
            frontImage = Image.open(os.path.join(self.drawPath, "捂脸.png"))
            facepalm = Image.new("RGBA", frontImage.size, (255, 255, 255))  # 白底
            facepalm.paste(avatar, (46, 0), avatar.split()[3])  # 加上头像
            facepalm.paste(frontImage, (0, 0), frontImage.split()[3])  # 加上手
            resultPath = os.path.join(self.resultDirPath, "{}.png".format(time.time()))
            facepalm.save(resultPath)
            return [resultPath]
        elif text.startswith("踩"):
            avatar = getAvatar(text[1:], (300, 300))
            if avatar is None:
                return None
            treadPath = os.path.join(self.drawPath, "tread")
            treadImages = []
            for i in range(0, 5):
                frontImage = Image.open(os.path.join(treadPath, "tread_{}.png".format(i + 1)))
                backImage = Image.new("RGBA", frontImage.size, (255, 255, 255))
                if i + 1 == 1 or i + 1 == 2:
                    theAvatar = avatar.resize((103, 65))
                    theAvatar = theAvatar.rotate(-26, expand=True)
                    # 扩展后实际大小为(123, 105)
                    backImage.paste(theAvatar, (31, 188), theAvatar.split()[3])
                elif i + 1 == 3:
                    theAvatar = avatar.resize((90, 71))
                    theAvatar = theAvatar.rotate(-14)
                    backImage.paste(theAvatar, (51, 209), theAvatar.split()[3])
                elif i + 1 == 4:
                    theAvatar = avatar.resize((85, 76))
                    theAvatar = theAvatar.rotate(-7)
                    backImage.paste(theAvatar, (52, 203), theAvatar.split()[3])
                elif i + 1 == 5:
                    theAvatar = avatar.resize((88, 82))
                    theAvatar = theAvatar.rotate(-7)
                    backImage.paste(theAvatar, (49, 198), theAvatar.split()[3])
                backImage.paste(frontImage, (0, 0), frontImage.split()[3])
                treadImages.append(backImage)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            treadImages[0].save(resultPath, format="GIF", append_images=treadImages[1:], save_all=True, duration=70, loop=0)
            return [resultPath]
        elif text.startswith("脆弱"):
            avatar = getAvatar(text[2:], (73, 73))
            if avatar is None:
                return None
            frontImage = Image.open(os.path.join(self.drawPath, "脆弱.png"))
            fragile = Image.new("RGBA", frontImage.size, (255, 255, 255))
            fragile.paste(avatar, (45, 62), avatar.split()[3])
            fragile.paste(frontImage, (0, 0), frontImage.split()[3])
            resultPath = os.path.join(self.resultDirPath, "{}.png".format(time.time()))
            fragile.save(resultPath)
            return [resultPath]
        elif text.startswith("吸"):
            avatar = getAvatar(text[1:], (300, 300))
            if avatar is None:
                return None
            inhalePath = os.path.join(self.drawPath, "inhale")
            inhaleImages = []
            positions = [(65, 88), (61, 89), (60, 112), (70, 142), (68, 151), (70, 129), (73, 141), (69, 145), (70, 154), (68, 119), (64, 115), (64, 99)]
            sizes = [(162, 151), (167, 146), (165, 120), (151, 90), (151, 84), (149, 109), (145, 94), (151, 89), (149, 76), (152, 118), (160, 121), (161, 140)]
            for i in range(0, 12):
                frontImage = Image.open(os.path.join(inhalePath, "inhale_{}.png".format(i + 1)))
                img = Image.new("RGBA", frontImage.size, (255, 255, 255))
                theAvatar = avatar.resize(sizes[i])
                img.paste(theAvatar, positions[i], theAvatar.split()[3])
                img.paste(frontImage, (0, 0), frontImage.split()[3])
                inhaleImages.append(img)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            inhaleImages[0].save(resultPath, format="GIF", append_images=inhaleImages[1:], save_all=True, duration=60, loop=0)
            return [resultPath]
        elif text.startswith("好玩"):
            avatar = getAvatar(text[2:], (90, 90))
            if avatar is None:
                return None
            frontImage = Image.open(os.path.join(self.drawPath, "interesting.png"))
            interesting = Image.new("RGBA", frontImage.size, (255, 255, 255))
            interesting.paste(avatar, (321, 172), avatar.split()[3])
            interesting.paste(frontImage, (0, 0), frontImage.split()[3])
            resultPath = os.path.join(self.resultDirPath, "{}.png".format(time.time()))
            interesting.save(resultPath)
            return [resultPath]
        elif text.startswith("贴贴"):
            avatar = getAvatar(text[2:], (300, 300))
            if avatar is None:
                return None
            snugglePath = os.path.join(self.drawPath, "snuggle")
            snuggleImages = []
            positions = [(77, 257), (82, 271), (82, 271), (81, 261), (64, 243)]
            sizes = [(174, 183), (175, 169), (175, 169), (175, 178), (194, 193)]
            for i in range(0, 5):
                frontImage = Image.open(os.path.join(snugglePath, "snuggle_{}.png".format(i + 1)))
                img = Image.new("RGBA", frontImage.size, (255, 255, 255))
                theAvatar = avatar.resize(sizes[i])
                img.paste(theAvatar, positions[i], theAvatar.split()[3])
                img.paste(frontImage, (0, 0), frontImage.split()[3])
                snuggleImages.append(img)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            snuggleImages[0].save(resultPath, format="GIF", append_images=snuggleImages[1:], save_all=True, duration=110, loop=0)
            return [resultPath]
        elif text.startswith("弹"):
            avatar = getAvatar(text[1:], (100, 100))
            if avatar is None:
                return None
            bouncePath = os.path.join(self.drawPath, "bounce")
            bounceImages = []
            positions = [(103, 51), (103, 46), (101, 10), (101, 27), (103, 46)]
            sizes = [(35, 35), (35, 35), (39, 35), (38, 37), (35, 35)]
            for i in range(0, 5):
                frontImage = Image.open(os.path.join(bouncePath, "bounce_{}.png".format(i + 1)))
                img = Image.new("RGBA", frontImage.size, (255, 255, 255))
                theAvatar = avatar.resize(sizes[i])
                img.paste(theAvatar, positions[i], theAvatar.split()[3])
                img.paste(frontImage, (0, 0), frontImage.split()[3])
                bounceImages.append(img)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            bounceImages[0].save(resultPath, format="GIF", append_images=bounceImages[1:], save_all=True, duration=70, loop=0)
            return [resultPath]
        elif text.startswith("致电"):
            avatar = getAvatar(text[2:], (90, 90))
            if avatar is None:
                return None
            call = Image.open(os.path.join(self.drawPath, "call.jpg"))
            call.paste(avatar, (156, 50), avatar.split()[3])
            resultPath = os.path.join(self.resultDirPath, "{}.jpg".format(time.time()))
            call.save(resultPath)
            return [resultPath]
        elif text.startswith("需要"):
            avatar = getAvatar(text[2:], (113, 113), needClipToCircle=False)
            if avatar is None:
                return None
            frontImage = Image.open(os.path.join(self.drawPath, "need.png"))
            need = Image.new("RGBA", frontImage.size, (255, 255, 255))
            need.paste(avatar, (328, 232), avatar.split()[3])
            need.paste(frontImage, (0, 0), frontImage.split()[3])
            resultPath = os.path.join(self.resultDirPath, "{}.png".format(time.time()))
            need.save(resultPath)
            return [resultPath]
        elif text.startswith("扭"):
            avatar = getAvatar(text[1:], (33, 32))
            if avatar is None:
                return None
            twistPath = os.path.join(self.drawPath, "twist")
            twistImages = []
            for i in range(0, 5):
                backImage = Image.open(os.path.join(twistPath, "twist_{}.png".format(i + 1)))
                img = Image.new("RGBA", backImage.size, (255, 255, 255))
                img.paste(backImage, (0, 0), backImage.split()[3])
                img.paste(avatar, (12, 3), avatar.split()[3])
                twistImages.append(img)
            resultPath = os.path.join(self.resultDirPath, "{}.gif".format(time.time()))
            twistImages[0].save(resultPath, format="GIF", append_images=twistImages[1:], save_all=True, duration=40, loop=0)
            return [resultPath]
        elif text.startswith("看到"):
            avatar = getAvatar(text[2:], (176, 176))
            if avatar is None:
                return None
            sight = Image.open(os.path.join(self.drawPath, "sight.jpg"))
            sight.paste(avatar, (610, 160), avatar.split()[3])
            resultPath = os.path.join(self.resultDirPath, "{}.jpg".format(time.time()))
            sight.save(resultPath)
            return [resultPath]
        return None


class 丢(Function, Run):
    invoke = '/丢'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{丢.invoke} ', '', 1)
        if text != 丢.invoke:
            who = 丢.__parse(text)
            if who:
                try:
                    tool = DrawTool()
                    if who.isdigit():
                        result = tool.wantDraw(f'丢{who}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        result = tool.wantDraw(f'丢{tmp}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None


class 爬(Function, Run):
    invoke = '/爬'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{爬.invoke} ', '', 1)
        if text != 爬.invoke:
            who = 爬.__parse(text)
            if who:
                try:
                    tool = DrawTool()
                    if who.isdigit():
                        result = tool.wantDraw(f'爬[@{who}]')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        result = tool.wantDraw(f'爬[@{tmp}]')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None


class 咬(Function, Run):
    invoke = '/咬'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{咬.invoke} ', '', 1)
        if text != 咬.invoke:
            who = 咬.__parse(text)
            if who:
                try:
                    tool = DrawTool()
                    if who.isdigit():
                        result = tool.wantDraw(f'咬[@{who}]')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        result = tool.wantDraw(f'咬[@{tmp}]')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None


class 弹(Function, Run):
    invoke = '/弹'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{弹.invoke} ', '', 1)
        if text != 弹.invoke:
            who = 弹.__parse(text)
            if who:
                try:
                    tool = DrawTool()
                    if who.isdigit():
                        result = tool.wantDraw(f'弹{who}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        result = tool.wantDraw(f'弹{tmp}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None


class 逃(Function, Run):
    invoke = '/逃'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{逃.invoke} ', '', 1)
        if text != 逃.invoke:
            who = 逃.__parse(text)
            if who:
                try:
                    tool = DrawTool()
                    if who.isdigit():
                        result = tool.wantDraw(f'快逃[@{who}]')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        result = tool.wantDraw(f'快逃[@{tmp}]')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None


class 打(Function, Run):
    invoke = '/打'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{打.invoke} ', '', 1)
        if text != 打.invoke:
            who = 打.__parse(text)
            if who:
                try:
                    tool = DrawTool()
                    if who.isdigit():
                        result = tool.wantDraw(f'打{who}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        result = tool.wantDraw(f'打{tmp}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None


class 吸(Function, Run):
    invoke = '/吸吸'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{吸.invoke} ', '', 1)
        if text != 吸.invoke:
            who = 吸.__parse(text)
            if who:
                try:
                    tool = DrawTool()
                    if who.isdigit():
                        result = tool.wantDraw(f'吸{who}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        result = tool.wantDraw(f'吸{tmp}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None


class 踢(Function, Run):
    invoke = '/踢踢'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{踢.invoke} ', '', 1)
        if text != 踢.invoke:
            who = 踢.__parse(text)
            if who:
                try:
                    tool = DrawTool()
                    if who.isdigit():
                        result = tool.wantDraw(f'踢[@{who}]')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        result = tool.wantDraw(f'踢[@{tmp}]')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None


class 推(Function, Run):
    invoke = '/推'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{推.invoke} ', '', 1)
        if text != 推.invoke:
            who = 推.__parse(text)
            if who:
                try:
                    tool = DrawTool()
                    if who.isdigit():
                        result = tool.wantDraw(f'推[@{who}]')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        result = tool.wantDraw(f'推[@{tmp}]')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None


class 贴(Function, Run):
    invoke = '/贴贴'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{贴.invoke} ', '', 1)
        if text != 贴.invoke:
            who = 贴.__parse(text)
            if who:
                try:
                    tool = DrawTool()
                    if who.isdigit():
                        result = tool.wantDraw(f'贴贴{who}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        result = tool.wantDraw(f'贴贴{tmp}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None


class 吞(Function, Run):
    invoke = '/吞'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{吞.invoke} ', '', 1)
        if text != 吞.invoke:
            who = 吞.__parse(text)
            if who:
                try:
                    tool = DrawTool()
                    if who.isdigit():
                        result = tool.wantDraw(f'吞{who}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        result = tool.wantDraw(f'吞{tmp}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None


class 踩(Function, Run):
    invoke = '/踩踩'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{踩.invoke} ', '', 1)
        if text != 踩.invoke:
            who = 踩.__parse(text)
            if who:
                try:
                    tool = DrawTool()
                    if who.isdigit():
                        result = tool.wantDraw(f'踩[@{who}]')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        result = tool.wantDraw(f'踩[@{tmp}]')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None


class 猫(Function, Run):
    invoke = '/猫猫'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{猫.invoke} ', '', 1)
        if text != 猫.invoke:
            who = 猫.__parse(text)
            if who:
                try:
                    tool = DrawTool()
                    if who.isdigit():
                        result = tool.wantDraw(f'旋转{who}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        result = tool.wantDraw(f'旋转{tmp}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None


class 慕(Function, Run):
    invoke = '/xm'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{慕.invoke} ', '', 1)
        if text != 慕.invoke:
            who = 慕.__parse(text)
            if who:
                try:
                    tool = DrawTool()
                    if who.isdigit():
                        result = tool.wantDraw(f'仰望大佬{who}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        result = tool.wantDraw(f'仰望大佬{tmp}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None


class 喊(Function, Run):
    invoke = '/致电'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{喊.invoke} ', '', 1)
        if text != 喊.invoke:
            who = 喊.__parse(text)
            if who:
                try:
                    tool = DrawTool()
                    if who.isdigit():
                        result = tool.wantDraw(f'致电{who}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        result = tool.wantDraw(f'致电{tmp}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None


class 吃(Function, Run):
    invoke = '/我要吃'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{吃.invoke} ', '', 1)
        if text != 吃.invoke:
            who = 吃.__parse(text)
            if who:
                try:
                    tool = DrawTool()
                    if who.isdigit():
                        result = tool.wantDraw(f'吃{who}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        result = tool.wantDraw(f'吃{tmp}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None


class 找(Function, Run):
    invoke = '/找'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{找.invoke} ', '', 1)
        if text != 找.invoke:
            who = 找.__parse(text)
            if who:
                try:
                    tool = DrawTool()
                    if who.isdigit():
                        result = tool.wantDraw(f'需要{who}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                    else:
                        tmp = who[who.find('qq='):]
                        tmp = tmp[:tmp.find(',')].replace('qq=', '')
                        result = tool.wantDraw(f'需要{tmp}')
                        if result is not None:
                            send_message(f'[CQ:image,file={random.choice(result)}]', self.params['config']['socket'], data)
                except:
                    pass
            else:
                send_message('格式不正确 ：）', self.params['config']['socket'], data)

    @staticmethod
    def __parse(s: str) -> str | None:
        s = s.strip()
        number_match = re.search(r'^\d+$', s)
        bracket_match = re.search(r'^\[.*?\]$', s)
        if number_match:
            return number_match.group()
        elif bracket_match:
            return bracket_match.group()
        else:
            return None