# -*- coding: utf-8 -*-
# @Time    : 2020/3/15 11:46
# @Author  : FanZY
# @FileName: 20200315_1146_backup.py
# @Software: PyCharm
# @GitHub ：https://github.com/FanBB2333

import pygame  # 引入最重要的pygame库
import sys  # 用于结束进程的sys库
import random  # 用于随机产生散弹大招子弹的random库
import math  # 简单数学运算

pygame.init()        # pygame主模块初始化
pygame.mixer.init()  # pygame声音混合器模块初始化
# -------------载入所需音效及图片-------------
pygame.mixer.music.load(r'E\bgm.wav')
pygame.mixer.music.set_volume(0.05)      # 设置音量
# pygame.mixer.music.play(-1)
sound_boom = pygame.mixer.Sound(r'E\boom.wav')      # 导入爆炸声音
sound_boom.set_volume(0.01)                         # 设置爆炸音量
sound_shoot = pygame.mixer.Sound(r'E\shoot.wav')    # 导入发射子弹声音
sound_shoot.set_volume(0.01)                        # 设置发射子弹音量
img_background = pygame.image.load(r'E\background.png')
img_shot = pygame.image.load(r'E\shot.gif')
img_tank1 = pygame.image.load(r'E\tank1.png')
img_tank2 = pygame.image.load(r'E\tank2.png')
img_icon = pygame.image.load(r'E\icon.gif')
img_super_bullet = pygame.image.load(r'E\bullet_super.png')

# --------------载入完毕--------------
size = [width, height] = [img_background.get_rect()[2], img_background.get_rect()[3]]  # 根据背景图片大小设置屏幕长宽
screen = pygame.display.set_mode(size)  # 创建新的窗口
pygame.display.set_caption('坦克大战2020全新重制版')  # 起一个响亮的名字
pygame.display.set_icon(img_icon)  # 用喜欢的图片作为图标

# 设置初始坐标
position_tank1 = [360, 5]
position_tank2 = [360, 595]
rect_tank1 = img_tank1.get_rect()  # 得到坦克1的外接矩形
rect_tank2 = img_tank2.get_rect()  # 得到坦克2的外接矩形
rect_tank1 = rect_tank1.move(position_tank1)  # 坦克1位置初始化
rect_tank2 = rect_tank2.move(position_tank2)  # 坦克2位置初始化
fpsclock = pygame.time.Clock()  # 引入fpsclock来控制帧速率
# 创建速度相关变量
delta_speed = 0.5  # 设置加速度
delta_angle = 5  # 设置角加速度
angle_1 = 90  # 设定初始角度，使得两个坦克针锋相对,这里是模型旋转的角度
angle_2 = angle_NPC = -90   # 注意！速度的角度计算方法和图片旋转的角度计算方法得到的角度恰巧是相反数
real_speed_1 = real_speed_2 = 0  # real_speed用于存储坦克速率(只有大小)
real_speed_NPC = 3  # 设置PVE时的NPC坦克(即坦克2)的速率
proj_speed_1 = [0, 0]
proj_speed_2 = [0, 0]   # 用列表分别存储速度在x，y的投影
bullet_speed = 20
score_1 = score_2 = 0   # 初始化两方分数
multishot_1 = multishot_2 = 0   # 初始化两方大招个数
choice = 0              # 创建变量记录选择的模式变量，默认为0,改为1为PVE，改为2为PVP
# 预设颜色RGB值，用于渲染字体
BLACK = 0, 0, 0
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
BLUE_ZJU = 0, 63, 136  # 求是蓝
RED_ZJU = 176, 31, 36  # 创新红
ORANGE_Tank1 = 255, 127, 39  # 两个坦克的颜色均为Photoshop中吸管提取出来的原始数据
BLUE_Tank2 = 0, 168, 243


# -------------------------------数据初始化结束-------------------------------


def speed_proj_update():
    """由速度投影来更新双方坦克速度
    """
    global proj_speed_1, proj_speed_2, real_speed_1, real_speed_2
    proj_speed_1[0] = real_speed_1 * math.cos(angle_1 / 180 * math.pi)
    proj_speed_1[1] = real_speed_1 * math.sin(angle_1 / 180 * math.pi)
    proj_speed_2[0] = real_speed_2 * math.cos(angle_2 / 180 * math.pi)
    proj_speed_2[1] = real_speed_2 * math.sin(angle_2 / 180 * math.pi)


def is_out():
    """防止坦克出界
    """
    global rect_tank1, rect_tank2
    if rect_tank1[0] < 0:  # 防止水平方向出左边界
        rect_tank1[0] = 0
    if rect_tank1[1] < 0:  # 防止竖直方向出上边界
        rect_tank1[1] = 0
    if rect_tank1[0] > 720:  # 防止水平方向出右边界
        rect_tank1[0] = 720
    if rect_tank1[1] > 600:  # 防止竖直方向出下边界
        rect_tank1[1] = 600
    if rect_tank2[0] < 0:  # 防止水平方向出左边界
        rect_tank2[0] = 0
    if rect_tank2[1] < 0:  # 防止竖直方向出上边界
        rect_tank2[1] = 0
    if rect_tank2[0] > 720:  # 防止水平方向出右边界
        rect_tank2[0] = 720
    if rect_tank2[1] > 600:  # 防止竖直方向出下边界
        rect_tank2[1] = 600


def is_boom():
    """检测两个坦克是否相距太近，即boom并显示游戏平局
    """
    global tank1_rotate_rect, tank2_rotate_rect, if_running, score_1, score_2, rect_tank1, rect_tank2, real_speed_1, real_speed_2
    global direction_1_ad,direction_1_ws ,direction_2_lr ,direction_2_ud, multishot_1, multishot_2
    # 先根据两个坦克的rect得到两个坦克的中心位置
    x1 = tank1_rotate_rect[0] + 40
    y1 = tank1_rotate_rect[1] + 40
    x2 = tank2_rotate_rect[0] + 40
    y2 = tank2_rotate_rect[1] + 40
    distance = dist(x1, y1, x2, y2)  # 求出两个坦克的中心距离
    if distance < 40:
        even_score_font = pygame.font.SysFont('georgia', 40)  # 渲染平局标题
        img_even_score = even_score_font.render('Even Score!, Press SPACE to play again', True, BLUE)
        score1_font = pygame.font.SysFont('timesnewroman', 50)  # 渲染平局得分
        img_score1 = score1_font.render('Team 1 : %d' % score_1, True, ORANGE_Tank1)
        score_2_font = pygame.font.SysFont('timesnewroman', 50)  # 渲染平局得分
        img_score2 = score_2_font.render('Team 2 : %d' % score_2, True, BLUE_Tank2)
        if_running = False  # 视为不再循环，用于后方跳出循环的判断
        screen.fill(BLACK)
        # 绘制死亡后界面
        screen.blit(img_even_score, [80, 100])  # 打出平局标题
        screen.blit(img_score1, [200, 300])  # 分别打出两方分数
        screen.blit(img_score2, [200, 500])
        pygame.display.update()  # 刷新屏幕，使得分数和标题显示出来
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                    if event.key == pygame.K_SPACE:  # 如果按下空格键则视为重新开一局，数据清零
                        if_running = True
                        score_1 = score_2 = 0  # 两方分数清零
                        rect_tank1[0] = 360  # 两个坦克位置回归
                        rect_tank1[1] = 0
                        rect_tank2[0] = 360
                        rect_tank2[1] = 595
                        real_speed_2 = real_speed_1 = 0  # 双方速度清零
                        direction_1_ad = direction_1_ws = direction_2_lr = direction_2_ud = 0   # 双方速度大小与方向指向变量置零
                        multishot_1 = multishot_2 = 0    # 双方大招数量置零
                        break
            if if_running:  # 两层循环，需要逐层判断，此时可跳出循环
                break


def is_minimized():
    """判断是否最小化来确定是否需要暂停程序
    """
    if_break = 0  # 设置变量以判断是否跳出循环
    if pygame.display.get_active():  # 若没有检测到最小化则直接pass
        pass
    else:  # 若检测到最小化则进入“else”
        pause_font = pygame.font.SysFont('georgia', 60)
        img_pause = pause_font.render('Press "P" to continue......', True, RED_ZJU)  # 生成并渲染字体
        screen.fill(BLUE_ZJU)  # 将屏幕背景填充为单色BLUE_ZJU
        screen.blit(img_pause, [40, 300])  # 将提示文字绘制在屏幕上
        print('The window had been minimized,press letter P to continue......')  # 在终端窗口中提示，因为此时最小化后看不到屏幕内容
        pygame.display.update()  # 重新刷新屏幕
        while True:  # 进入循环以暂停
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:  # 若按下p键则变量设置为1并手动跳出循环
                        if_break = 1
                        break
            if if_break:  # 此时需要跳出上一层循环，也需要通过变量判断
                break



def dist(x1, y1, x2, y2):
    """函数：求两点间距离
    """
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


class Shot_1:
    """创建坦克1射出的子弹类，下面坦克2的子弹存储方式类似
    """

    def __init__(self, angle_1):
        self.img = pygame.transform.rotate(img_shot, -angle_1 - 90)  # 旋转子弹至子弹与坦克炮口平行
        self.x = rect_tank1[0] + 40 + 40 * math.cos(angle_1 / 180 * math.pi)  # 纠正子弹的位置至炮口
        self.y = rect_tank1[1] + 40 + 40 * math.sin(angle_1 / 180 * math.pi)
        self.speed_x = bullet_speed * math.cos(angle_1 / 180 * math.pi)  # 根据当前坦克的角度决定子弹的速度方向
        self.speed_y = bullet_speed * math.sin(angle_1 / 180 * math.pi)

    def is_hit(self):
        """判断是否击中敌人的子弹类中的方法
        """
        global rect_tank2, score_1,real_speed_2,angle_2
        # 判断子弹是否击中敌人，判定范围为敌人中心为圆心，40像素为半径的圆，注：此时未开启自身伤害
        if dist(self.x, self.y, rect_tank2[0] + 40, rect_tank2[1] + 40) < 40:
            shot_1.remove(self)  # 若击中另一个坦克，从列表中移除子弹
            sound_boom.play()  # 播放击中音效
            score_1 += 1  # 击中后分数对方分数加一
            rect_tank2[0] = 360  # 炸到后立即返回重生点
            rect_tank2[1] = 595
            real_speed_2 = 0     # 炸到后返回重生点速度变为0
            angle_2 = -90        # 返回重生点后角度复原为出生角度


# 用一个列表记录坦克1射出的子弹
shot_1 = []


def show_shot_1():
    """刷新并绘制子弹的位置
    """
    for s in shot_1:
        screen.blit(s.img, (s.x, s.y))  # 将子弹图片绘制到窗口中
        s.is_hit()  # 判断并删除击中的子弹
        s.x += s.speed_x  # 若子弹未击中，则每次刷新时更新坐标
        s.y += s.speed_y
        # 删除出界的子弹
        if (s.x < 0) or (s.y < 0) or (s.x > 800) or (s.y > 680):
            shot_1.remove(s)


class Shot_2:
    """创建坦克2射出的子弹类，与坦克1的子弹类似
    """
    def __init__(self, angle_2):
        self.img = pygame.transform.rotate(img_shot, -angle_2 - 90)
        # 此处由于两个坦克的模型略有区别，在确定炮口位置的时候数据略有区别
        self.x = rect_tank2[0] + 40 + 60 * math.cos(angle_2 / 180 * math.pi)
        self.y = rect_tank2[1] + 40 + 60 * math.sin(angle_2 / 180 * math.pi)
        self.speed_x = bullet_speed * math.cos(angle_2 / 180 * math.pi)
        self.speed_y = bullet_speed * math.sin(angle_2 / 180 * math.pi)

    def is_hit(self):
        global rect_tank1, score_2,real_speed_1,angle_1
        if dist(self.x, self.y, rect_tank1[0] + 40, rect_tank1[1] + 40) < 40:
            shot_2.remove(self)
            sound_boom.play()
            score_2 += 1
            rect_tank1[0] = 360  # 炸到后立即返回重生点
            rect_tank1[1] = 0
            real_speed_1 = 0  # 炸到后返回重生点速度变为0
            angle_1 = 90  # 返回重生点后角度复原为出生角度

# 用一个列表记录坦克2射出的子弹
shot_2 = []


def show_shot_2():
    for s in shot_2:
        screen.blit(s.img, (s.x, s.y))
        s.is_hit()
        s.x += s.speed_x
        s.y += s.speed_y
        if (s.x < 0) or (s.y < 0) or (s.x > 800) or (s.y > 680):
            shot_2.remove(s)

# -------------------子弹数据记录完成-------------------


def speed_change():
    """此函数根据当前的坦克角度和绝对速度大小计算并赋值x，y坐标轴分量速度
    """
    global proj_speed_1, proj_speed_2, real_speed_1, real_speed_2
    # 根据angle_1和angle_2的大小来向坐标轴投影。注：因为rect类的move方法在应用时传入数据需为整数
    proj_speed_1[0] = math.floor(real_speed_1 * math.cos(angle_1 / 180 * math.pi))
    proj_speed_1[1] = math.floor(real_speed_1 * math.sin(angle_1 / 180 * math.pi))
    proj_speed_2[0] = math.floor(real_speed_2 * math.cos(angle_2 / 180 * math.pi))
    proj_speed_2[1] = math.floor(real_speed_2 * math.sin(angle_2 / 180 * math.pi))

# 分别将两个坦克的速度大小与方向指向变量置0
direction_1_ad = direction_1_ws = direction_2_lr = direction_2_ud = 0

def event_response_key():
    """响应键盘按下与抬起事件
    """
    global if_running, rect_tank2, rect_tank1, proj_speed_1, proj_speed_2,multishot_1,multishot_2
    global real_speed_1, real_speed_2, delta_speed, delta_angle, angle_1, angle_2
    global direction_1_ad,direction_1_ws,direction_2_lr,direction_2_ud
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 检测到QUIT的事件，直接退出
            if_running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()  # 如果按下esc键则直接退出
                sys.exit()
            if event.key == pygame.K_RIGHT:
                direction_2_lr = 1          # 当按下“左”方向键时坦克2的速度方向指向变量设置为1，即向左转
            if event.key == pygame.K_LEFT:
                direction_2_lr = -1         # 当按下“右”方向键时坦克2的速度方向指向变量设置为-1，即向右转
            if event.key == pygame.K_UP:
                direction_2_ud = 1          # 当按下“上”方向键时坦克2的速度大小指向变量设置为1，即向前加速
            if event.key == pygame.K_DOWN:
                direction_2_ud = -1         # 当按下“下”方向键时坦克2的速度大小指向变量设置为-1，即向前减速（向后加速）
            if event.key == pygame.K_d:
                direction_1_ad = 1          # 当按下“d”键时坦克1的速度方向指向变量设置为1，即向右转
            if event.key == pygame.K_a:
                direction_1_ad = -1         # 当按下“a”键时坦克1的速度方向指向变量设置为-1，即向左转
            if event.key == pygame.K_w:
                direction_1_ws = 1          # 当按下“w”方向键时坦克1的速度大小指向变量设置为1，即向前加速
            if event.key == pygame.K_s:
                direction_1_ws = -1         # 当按下“s”方向键时坦克1的速度大小指向变量设置为-1，即向前减速（向后加速）
            if event.key == pygame.K_g:
                shot_1.append(Shot_1(angle_1))  # 按下g键发射子弹，即向子弹的列表里加入一个实例化后的子弹元素
                sound_shoot.play()  # 同时播放发射子弹的声音
            if event.key == pygame.K_SLASH:
                shot_2.append(Shot_2(angle_2))
                sound_shoot.play()
            if event.key == pygame.K_f:  # 按下f键,若散弹大招还有余量，则控制坦克1同时发射3枚夹角30°的散弹
                if multishot_1 > 0:
                    multishot_1 -= 1     # 大招数量使用后减一
                    shot_1.append(Shot_1(angle_1))
                    shot_1.append(Shot_1(angle_1 + 30))
                    shot_1.append(Shot_1(angle_1 - 30))
                    sound_shoot.play()
            if event.key == pygame.K_PERIOD:  # 按下.(英文句号)键,若散弹大招还有余量，则控制坦克2同时发射3枚夹角30°的散弹
                if multishot_2 > 0:
                    multishot_2 -= 1     # 大招数量使用后减一
                    shot_2.append(Shot_2(angle_2))
                    shot_2.append(Shot_2(angle_2 + 30))
                    shot_2.append(Shot_2(angle_2 - 30))
                    sound_shoot.play()

        # 检测是否抬起按键，如果按键已经抬起来则将对应的速度增量置零，即不再改变速度
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                direction_2_lr = 0              # 坦克2不再向右转弯
            if event.key == pygame.K_LEFT:
                direction_2_lr = 0              # 坦克2不再向左转弯
            if event.key == pygame.K_UP:
                direction_2_ud = 0              # 坦克2不再加速
            if event.key == pygame.K_DOWN:
                direction_2_ud = 0              # 坦克2不再减速
            if event.key == pygame.K_d:
                direction_1_ad = 0              # 坦克1不再向右转弯
            if event.key == pygame.K_a:
                direction_1_ad = 0              # 坦克1不再向左转弯
            if event.key == pygame.K_w:
                direction_1_ws = 0              # 坦克1不再加速
            if event.key == pygame.K_s:
                direction_1_ws = 0              # 坦克1不再减速

def speed_num_and_angle_update():
    """根据键盘输入的速度方向来调节速度，由于每次主循环都会调用此函数，于是实现了速度的连续变化
    """
    global real_speed_1,real_speed_2,angle_1,angle_2
    real_speed_1 += direction_1_ws * delta_speed        # 给坦克1的速度进行变化
    real_speed_2 += direction_2_ud * delta_speed        # 给坦克2的速度进行变化
    angle_1 += direction_1_ad * delta_angle             # 给坦克1的角度进行变化
    angle_2 += direction_2_lr * delta_angle             # 给坦克2的角度进行变化


def mouse_action():
    """响应鼠标事件，用于初次进入游戏时选择游戏模式是PVE还是PVP
    """
    global choice
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()  # 如果按下esc键则直接退出
                sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
            mouse_react = pygame.mouse.get_pressed()  # 获取鼠标产生点击的键是哪一个
            mouse_direction = pygame.mouse.get_pos()  # 获取鼠标位置到列表里
            if mouse_react[0]:  # 判断，即如果单击左键，再判断单击时位置
                # 判断鼠标再哪一个矩形范围里，同时要求choice未被赋值，即第一次判断
                # 也可直接手动改变choice的数值来手动切换游戏模式，手动改变时便不会进入此循环，提高了效率
                if (250 < mouse_direction[0] < 550) and (200 < mouse_direction[1] < 300) and (not choice):
                    choice = 1  # 选择1表示PVE模式，即与低智商NPC对战
                if (250 < mouse_direction[0] < 550) and (400 < mouse_direction[1] < 500) and (not choice):
                    choice = 2  # 选择2表示PVP模式，即与朋友对战


def angle_npc():
    """控制NPC自动追踪的函数
    """
    global angle_NPC, rect_tank2, rect_tank1, angle_2
    center_tank2_x = rect_tank2[0] + 40  # 获取玩家坦克的中心位置，以便之后判断旋转角度
    center_tank2_y = rect_tank2[1] + 40
    center_tank1_x = rect_tank1[0] + 40  # 获取NPC坦克的中心位置，以便之后判断旋转角度
    center_tank1_y = rect_tank1[1] + 40
    distance = dist(center_tank1_x, center_tank1_y, center_tank2_x, center_tank2_y)

    angle_NPC = math.acos((center_tank2_x - center_tank1_x) / distance) / math.pi * 180 + 180   # 这个+180度是图像先要矫正到初始方向
    if center_tank1_y > center_tank2_y:
        angle_NPC = 360 - angle_NPC          # 由于arccos函数的值域为0到180°，故计算优角的时候应该用360度减去算出来的角度

multi_count = 0     # 幕布上的大招buff数目，开始时没有，该变量最大为1，即最多同时出现一个大招buff供坦克食用
buff_x = buff_y = 1000
def multishot_create():
    global count,tank1_rotate_rect, tank2_rotate_rect,multi_count,buff_x,buff_y
    x1 = tank1_rotate_rect[0] + 40
    y1 = tank1_rotate_rect[1] + 40
    x2 = tank2_rotate_rect[0] + 40
    y2 = tank2_rotate_rect[1] + 40
    screen.blit(img_super_bullet, [buff_x, buff_y])  # 如果随机产生的位置符合要求，则buff计数加一，并绘制buff图片
    if count % 100 == 0 and multi_count == 0:
        buff_x = random.randint(0, width - 80)
        buff_y = random.randint(0, height - 80)
        if dist(x1,y1,buff_x+40,buff_y+40) < 60 or dist(x2,y2,buff_x+40,buff_y+40) < 60:
            multishot_create()                                  # 如果产生的随机buff距离任一坦克太近，都会重新产生
        else:
            # screen.blit(img_super_bullet,[buff_x,buff_y])       # 如果随机产生的位置符合要求，则buff计数加一，并绘制buff图片
            multi_count += 1


def multishot_eat():
    global count,tank1_rotate_rect, tank2_rotate_rect,multi_count,buff_x,buff_y,multishot_1,multishot_2
    x1 = tank1_rotate_rect[0] + 40
    y1 = tank1_rotate_rect[1] + 40
    x2 = tank2_rotate_rect[0] + 40
    y2 = tank2_rotate_rect[1] + 40
    if dist(x1,y1,buff_x+40,buff_y+40) < 60:
        multi_count -= 1
        multishot_1 += 1
        buff_x = buff_y = 1000
    if dist(x2, y2, buff_x+40, buff_y+40) < 60:
        multi_count -= 1
        multishot_2 += 1
        buff_x = buff_y = 1000


def draw_score_1():
    """在屏幕上显示出tank1的得分
    """
    global score_1
    score1_font = pygame.font.SysFont('timesnewroman', 30)  # 渲染字体
    img_score1 = score1_font.render('Team 1 : %d' % score_1, True, ORANGE_Tank1)  # 用与坦克1一样的颜色
    screen.blit(img_score1, [5, 5])  # 将得分放在左上角


def draw_score_2():
    """在屏幕上显示出tank2的得分
    """
    global score_2
    score2_font = pygame.font.SysFont('timesnewroman', 30)  # 渲染字体
    img_score2 = score2_font.render('Team 2 : %d' % score_2, True, BLUE_Tank2)  # 用与坦克2一样的颜色
    screen.blit(img_score2, [650, 640])  # 将得分放在右下角

def draw_multishot_1():
    """在屏幕上显示出tank1的大招数量
    """
    global multishot_1
    multishot_1_font = pygame.font.SysFont('timesnewroman', 30)
    img_multishot_1 = multishot_1_font.render('Multi left :%d' % multishot_1,True, ORANGE_Tank1)
    screen.blit(img_multishot_1,[5,35])


def draw_multishot_2():
    """在屏幕上显示出tank2的大招数量
    """
    global multishot_2
    multishot_2_font = pygame.font.SysFont('timesnewroman', 30)
    img_multishot_2 = multishot_2_font.render('Multi left :%d' % multishot_2,True, BLUE_Tank2)
    screen.blit(img_multishot_2,[650,610])

# ------------------------------结束函数与类的定义------------------------------


while True:
    """进入选择PVE或是PVP模式的交互界面，作为图形化的交互界面
    """
    screen.blit(img_background, (0, 0))
    pygame.draw.rect(screen, BLUE, [250, 200, 300, 100], 10)  # 绘制选择框矩形
    pygame.draw.rect(screen, BLUE, [250, 400, 300, 100], 10)
    p1_font = pygame.font.SysFont('georgia', 44)  # 在选择框矩形里写上选项：1 Player
    img_p1 = p1_font.render('1 Player', True, RED_ZJU)  # 渲染字体
    screen.blit(img_p1, [320, 230])
    p2_font = pygame.font.SysFont('georgia', 44)  # 在选择框矩形里写上选项：2 Player
    img_p2 = p2_font.render('2 Player', True, RED_ZJU)  # 渲染字体
    screen.blit(img_p2, [320, 430])
    title_font = pygame.font.SysFont('tahoma', 80)  # 尝试一种新字体tahoma，用于渲染标题字体
    img_title = p1_font.render('Tank Battle', True, RED_ZJU)
    screen.blit(img_title, [300, 40])
    mouse_action()
    if choice:  # 如果已经做出了选择，就退出循环，进入相应的游戏
        break
    pygame.display.update()

count = 0       # 设置变量用于记录游戏主界面循环的次数，以此判断NPC发射导弹的间隔

# ---------------------------PVE模式---------------------------
if choice == 1:
    if_running = True           # 变量用于判断是否需要终止游戏
    while if_running:
        fpsclock.tick(30)       # 设置屏幕刷新率，可以用此参数更改NPC子弹发射速率和坦克移动速率
        screen.blit(img_background, (0, 0))     # 预先用题中给的壁纸填充背景
        angle_npc()
        angle_2 = angle_NPC
        real_speed_2 = real_speed_NPC
        event_response_key()     # 响应键盘事件
        speed_num_and_angle_update()    # 根据键盘事件的响应来更新速度
        speed_proj_update()       # 重新计算玩家所控制的坦克1的速度
        # 移动一个始终竖直水平并与坦克中心时时刻刻重合的坦克框，为了之后能够确定中心位置
        # 若无此操作，因坦克图像不是圆形，故在旋转的时候不能做到精准绕中心旋转，会有偏差
        rect_tank1 = rect_tank1.move(proj_speed_1)
        rect_tank2 = rect_tank2.move(proj_speed_2)
        # 将原坦克图像根据角度需要进行旋转，保存为旋转后的坦克图像
        img_real_tank1 = pygame.transform.rotate(img_tank1, -angle_1)
        img_real_tank2 = pygame.transform.rotate(img_tank2, -angle_2)
        # 重新选取旋转中心，使得坦克在旋转的时候绕真正的图片中心
        tank1_rotate_rect = img_real_tank1.get_rect(center=rect_tank1.center)
        tank2_rotate_rect = img_real_tank2.get_rect(center=rect_tank2.center)
        # 移动旋转后的坦克框
        tank1_rotate_rect = tank1_rotate_rect.move(proj_speed_1)
        tank2_rotate_rect = tank2_rotate_rect.move(proj_speed_2)
        # 将旋转后的坦克图像绘制到旋转后的坦克框中
        screen.blit(img_real_tank1, tank1_rotate_rect)
        screen.blit(img_real_tank2, tank2_rotate_rect)
        count += 1              # 用于记录循环的次数，来控制发射子弹的频率
        if count % 40 == 0:     # 屏幕每刷新40次则发射一枚导弹
            shot_2.append(Shot_2(angle_2))
            sound_shoot.play()
        if count % 200 == 0:    # 每刷新200次放一个散弹大招
            shot_2.append(Shot_2(angle_2 + 60))     # 大招增加两个与原子弹夹角为60度的子弹
            shot_2.append(Shot_2(angle_2 - 60))
            sound_shoot.play()
        is_out()            # 判断是否出界
        is_boom()           # 判断是否相撞而爆炸
        is_minimized()      # 判断窗口是否最小化而暂停游戏
        show_shot_1()       # 展示坦克1的子弹
        show_shot_2()       # 展示坦克2的子弹
        draw_score_1()      # 绘制坦克1的分数
        draw_score_2()      # 绘制坦克1的分数
        draw_multishot_1()  # 绘制坦克1的可用大招数目
        multishot_create()  # 刷新大招buff图片
        multishot_eat()     # 判定是否吃到大招buff
        pygame.display.update()     # 屏幕刷新
# ---------------------------PVE模式代码结束---------------------------

screen.blit(img_background, (0, 0))  # 重新填充背景色，覆盖选择选项，准备绘画游戏画面

# ------------------------------双人模式------------------------------
if choice == 2:
    if_running = True
    while if_running:
        fpsclock.tick(30)       # 设置屏幕刷新率，可以用此参数更改NPC子弹发射速率和坦克移动速率
        screen.blit(img_background, (0, 0))     # 预先用题中给的壁纸填充背景
        event_response_key()  # 响应键盘事件
        speed_num_and_angle_update()    # 根据键盘事件的响应来更新速度
        speed_proj_update()    # 重新计算坦克速度
        # 移动一个始终竖直水平并与坦克中心时时刻刻重合的坦克框，为了之后能够确定中心位置
        # 若无此操作，因坦克图像不是圆形，故在旋转的时候不能做到精准绕中心旋转，会有偏差
        rect_tank1 = rect_tank1.move(proj_speed_1)
        rect_tank2 = rect_tank2.move(proj_speed_2)
        # 将原坦克图像根据角度需要进行旋转，保存为旋转后的坦克图像
        img_real_tank1 = pygame.transform.rotate(img_tank1, -angle_1)
        img_real_tank2 = pygame.transform.rotate(img_tank2, -angle_2)
        # 重新选取旋转中心，使得坦克在旋转的时候绕真正的图片中心
        tank1_rotate_rect = img_real_tank1.get_rect(center=rect_tank1.center)
        tank2_rotate_rect = img_real_tank2.get_rect(center=rect_tank2.center)
        # 移动旋转后的坦克框
        tank1_rotate_rect = tank1_rotate_rect.move(proj_speed_1)
        tank2_rotate_rect = tank2_rotate_rect.move(proj_speed_2)
        # 将旋转后的坦克图像绘制到旋转后的坦克框中
        screen.blit(img_real_tank1, tank1_rotate_rect)
        screen.blit(img_real_tank2, tank2_rotate_rect)
        is_out()  # 判断是否出界
        is_boom()  # 判断是否相撞而爆炸
        is_minimized()  # 判断窗口是否最小化而暂停游戏
        show_shot_1()  # 展示坦克1的子弹
        show_shot_2()  # 展示坦克2的子弹
        draw_score_1()  # 绘制坦克1的分数
        draw_score_2()  # 绘制坦克1的分数
        draw_multishot_1()  # 绘制坦克1的可用大招数目
        draw_multishot_2()  # 绘制坦克2的可用大招数目
        multishot_create()  # 刷新大招buff图片
        multishot_eat()     # 判定是否吃到大招buff
        pygame.display.update()  # 屏幕刷新

# ------------------------------PVP模式代码结束------------------------------
