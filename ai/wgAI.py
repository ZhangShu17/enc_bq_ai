#coding:utf-8
from ai import wgobject,wgruler,wgsdata,common
import random,time,sys
# import pandas as pd
# import numpy as np
sys.path.append('../interface/')
'''AI类 调用接口读取态势数据，生成动作以及动作执行'''
class AI:
    def __init__(self, obj_interface, flag_color):
        '''
        初始化
        :param obj_interface: 接口类
        :param flag_color: 'RED'/红色 'BLUE'/蓝色
        '''
        try:
            self.obj_interface = obj_interface
            self.flag_color = 0 if flag_color == 'RED' else 1
            # l_obops:我方算子列表; l_ubops:敌方算子列表; l_cities:夺控点信息列表; l_stage:阶段信息
            self.dic_metadata = {'l_obops': [], 'l_ubops': [], 'l_cities': [], 'l_stage': []}
            # 记录最初始算子
            self.my_obops = []
            self.updateSDData() # 更新态势数据
            # 用来记录战车是否在第三次机动过程中完成兵力投放
            self.already_complete_in_third = {str(self.dic_metadata['l_obops'][0].ObjID): False,
                                              str(self.dic_metadata['l_obops'][1].ObjID): False}
            # self.mapData = pd.read_csv('map2.csv')
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def run(self):
        '''
        主循环
        :return:
        '''
        try:
            #主循环
            while ((not self.timeIsout()) and (not self.oneWin())): # 游戏是否结束或一方胜利
                self.updateSDData()  # 更新态势数据
                if self.dic_metadata['l_stage'][1] % 2 == self.flag_color:
                    common.echosentence_color('-' * 20)  # 打印
                flag_validAction = self.doAction()  # 执行动作
                if not flag_validAction:  # 没有有效动作
                    self.wait(self.dic_metadata, self.flag_color) #等待下个有效动作，打印等待信息
                time.sleep(0.5)
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def updateSDData(self):
        '''
        更新态势数据，放在成员变量dic_metadata中
        :return:
        '''
        try:
            # 时间信息
            self.dic_metadata['l_stage'] = self.obj_interface.getSimTime()

            # 我方算子
            self.dic_metadata['l_obops'] = []
            df_myOp = self.obj_interface.getSideOperatorsData()
            for index, row in df_myOp.iterrows():
                bop = wgobject.Gen_Op(row)
                bop = wgruler.cvtMapBop2AIBop(bop,self.dic_metadata['l_stage'])
                self.dic_metadata['l_obops'].append(bop)
                # 张庶修改
                if [bop.ObjID, bop.ObjTypeX] not in self.my_obops:
                    self.my_obops.append([bop.ObjID, bop.ObjTypeX])
        # 敌方算子
            self.dic_metadata['l_ubops'] = []
            df_enemyOp = self.obj_interface.getEnemyOperatorsData()
            for index,row in df_enemyOp.iterrows(): #敌方算子不包括血量为0的算子
                bop = wgobject.Gen_Op(row)
                bop = wgruler.cvtMapBop2AIBop(bop, self.dic_metadata['l_stage'])
                self.dic_metadata['l_ubops'].append(bop)

            # 堆叠检查
            wgruler.stackCheck(self.dic_metadata['l_obops'])
            wgruler.stackCheck(self.dic_metadata['l_ubops'])
            #同格检查
            wgruler.tonggeCheck(self.dic_metadata['l_obops'], self.dic_metadata['l_ubops'])
            wgruler.tonggeCheck(self.dic_metadata['l_ubops'], self.dic_metadata['l_obops'])

            #城市列表
            df_city = self.obj_interface.getCityData()
            df_city = df_city.sort_values(by='C1', ascending=True)
            self.dic_metadata['l_cities'] = []
            dic_color2flag = {'GREEN': -1, 'RED': 0, 'BLUE': 1}
            for index, row in df_city.iterrows():
                self.dic_metadata['l_cities'] += [row.MapID, dic_color2flag[row.UserFlag], row.C1]
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def timeIsout(self):
        '''
        游戏时间是否结束
        :return: True/是 False/否
        '''
        try:
            return self.obj_interface.flagTimeOut()
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def oneWin(self):
        '''
        是否一方胜利
        :return: True/是 False/否
        '''
        try:
            num_obops, num_ubops = len(self.dic_metadata['l_obops']), len(self.dic_metadata['l_ubops'])
            return num_obops == 0
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def doAction(self):
        try:
            # 蓝方部署阶段
            # 当前态势
            l_ourbops = self.dic_metadata['l_obops']  # 我方算子
            l_enemybops = self.dic_metadata['l_ubops']  # 敌方算子
            l_cities = self.dic_metadata['l_cities']  # 夺控点列表
            # 本方颜色
            color = self.flag_color
            # 当前环节
            current_stage = self.dic_metadata['l_stage']
            # 我方是蓝方
            if color == 1:
                # 射能射击就射击
                for att_bop in l_ourbops:
                    for obj_bop in l_enemybops:
                        flag, weaponID = self.genShootAction(att_bop, obj_bop)  # 判断是否可以射击,若可以射击，返回最佳射击武器
                        if flag:  # 可以射击
                            exe_success, result = self.obj_interface.setFire(att_bop.ObjID, obj_bop.ObjID,
                                                                        (int)(weaponID))  # 调用接口执行射击动作
                            if exe_success == 0:  # 执行成功
                                print('打印射击裁决结果==>{}'.format(result))
                                return True
                # 按照策略进行机动行军
                # 蓝方第一次机动
                if current_stage[0] == 0 and current_stage[1] == 1 and current_stage[2] == 1:
                    # 算子0为80080(1640)处的战车；算子1为80082(1641)处的战车；
                    # 算子2为70081(1540)处的坦克; 算子3为80081(1740)处的坦克
                    move_obj_list = [80069, 90070, 90072, 90070]
                    for i in range(len(l_ourbops)):
                        boolen, l_path = self.genMoveAction(l_ourbops[i], move_obj_list[i])
                        if boolen:
                            # self.shootingOnMoving(l_ourbops[i], l_path)
                            self.obj_interface.setMove(l_ourbops[i].ObjID, l_path)
                    return True
                # 蓝方第二次机动环节 行军
                if current_stage[0] == 0 and current_stage[1] == 3 and current_stage[2] == 1:
                    move_obj_list = [[80069, 80070, 70069, 70067, 70065, 70063, 80062, 80061, 90060, 90058, 90057, 100056, 100055, 110054],
                                     [90070, 90068, 90066, 90064, 90062, 90060, 90058, 90056],
                                     [90072, 90070, 90068, 90066, 90064, 90062, 90060],
                                     [90070, 80069, 80070, 70069, 70067, 70065, 70063, 80062, 80061, 90060]
                                     ]
                    # 切换成行军状态
                    for i in range(len(l_ourbops)):
                        # 切换成行军状态
                        if i == 0 or i == 3:
                            state_change_bollen = self.obj_interface.setState(l_ourbops[i].ObjID, 1)
                        # 获取当前算子的位置
                        cur_pos = l_ourbops[i].ObjPos
                        # 在move_obj_list中的索引位置
                        index = move_obj_list[i].index(cur_pos)
                        if index < len(move_obj_list[i])-1:
                            move_obj_list[i] = move_obj_list[i][index+1:]
                            self.obj_interface.setMove(l_ourbops[i].ObjID, move_obj_list[i])
                    return True
                # 蓝方第三次机动，下步兵
                if current_stage[0] == 1 and current_stage[1] == 1 and current_stage[2] == 1:
                    for index, my_bop in enumerate(l_ourbops):
                        # 切换成机动状态
                        state_change_bollen = self.obj_interface.setState(my_bop.ObjID, 0)
                        obj_pos_solider = -1
                        obj_pos_back = -1
                        obj_tank = -1
                        if self.my_obops.index([my_bop.ObjID, my_bop.ObjTypeX]) == 0:  # 第一个战车
                            obj_pos_solider = 100051
                            obj_pos_back = 90053
                        elif self.my_obops.index([my_bop.ObjID, my_bop.ObjTypeX]) == 1:  # 第二个战车
                            obj_pos_solider = 90054
                            obj_pos_back = 90060
                        elif self.my_obops.index([my_bop.ObjID, my_bop.ObjTypeX]) == 2:  # 第一个坦克
                            obj_tank = 90053
                        elif self.my_obops.index([my_bop.ObjID, my_bop.ObjTypeX]) == 3:  # 第二个坦克
                            obj_tank = 90053

                        # 战车到达步兵下车地点并让步兵下车，并机动到另一地点
                        if obj_pos_solider > 0:

                            if not self.already_complete_in_third[str(my_bop.ObjID)]:
                                boolen_1, l_path_1 = self.genMoveAction(my_bop, obj_pos_solider)
                                if boolen_1:
                                    self.shootingOnMoving(my_bop, l_path_1)

                                # 更新本方算子
                                self.updateSDData()
                                exist = False
                                for index, bop in enumerate(self.dic_metadata['l_obops']):
                                    if my_bop.ObjID == bop.ObjID:
                                        my_bop = bop
                                        exist = True
                                        break

                                if exist:
                                    if my_bop.ObjPos == obj_pos_solider:
                                        if my_bop.ObjSonNum == 1:
                                            if self.genGetOffAction(my_bop):
                                                self.obj_interface.setGetoff(my_bop.ObjID)  # 调用接口执行下车动作
                                        boolen_2, l_path_2 = self.genMoveAction(my_bop, obj_pos_back)
                                        if boolen_2:
                                            self.shootingOnMoving(my_bop, l_path_2)
                                        self.already_complete_in_third[str(my_bop.ObjID)] = True

                        # 如果是坦克，坦克机动到指定地点
                        if obj_tank > 0:
                            boolen_3, l_path_3 = self.genMoveAction(my_bop, obj_tank)
                            if boolen_3:
                                self.shootingOnMoving(my_bop, l_path_3)
                    return True
            return False
        except Exception as e:
            print('error in run_onestep(): ' + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            print('error in run_onestep(): ' + str(k))
            self.__del__()
            raise

    def genShootAction(self, bop_attacker, bop_obj):
        '''
        判断能否射击
        :param bop_attacker:
        :param bop_obj:
        :return: (True,wp_index)/(能射击,武器编号),(False,None)/(不能射击，None)
        '''
        try:
            list_g_stage = self.dic_metadata['l_stage']
            flag_str_shooting = wgruler.Shooting(list_g_stage, bop_attacker, bop_obj)

            if flag_str_shooting != 'N' and flag_str_shooting != 'TS':
                ser_att = wgobject.bop2Ser(bop_attacker)
                ser_obj = wgobject.bop2Ser(bop_obj)
                flag_success, wp_index = self.obj_interface.chooseWeaponIndex(ser_att,ser_obj) # 获取武器编号
                if flag_success == 0:
                    return (True,wp_index)
            return (False,None)
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def genOccupyAction(self, cur_bop):
        '''
        判断是否可以原地夺控制
        :param cur_bop:
        :return: True/可以夺控,False/不能夺控
        '''
        try:
            list_g_stage = self.dic_metadata['l_stage']
            list_loc_notmycity = wgsdata.updateNotMyCityList(self.dic_metadata['l_cities'], cur_bop.GameColor)
            list_ubops = self.dic_metadata['l_ubops']

            if wgruler.OccupyingRightNow(list_g_stage, cur_bop, list_loc_notmycity, list_ubops) == 'O':
                return True
            return False
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def genGetOffAction(self, cur_bop):
        '''
        判断能否下车
        :param cur_bop:
        :return: True/可以下车 Flase/不能下车
        '''
        try:
            list_g_stage = self.dic_metadata['l_stage']
            # 下车模型首先保证能够机动
            flag_str_moving = wgruler.Moving(list_g_stage, cur_bop=cur_bop)
            if flag_str_moving == 'M' and cur_bop.ObjTypeX == 1 and cur_bop.ObjSonNum == 1 and \
                    cur_bop.ObjStep >= cur_bop.ObjStepMax // 2 and cur_bop.ObjKeep == 0:  # 没有被压制
                # and cur_bop.ObjSonNum == 1 and cur_bop.ObjStep >= 3 and cur_bop.ObjKeep == 0:  # 没有被压制  ???3
                return True

            return False
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def genGetOnAction(self, car_bop, peo_bop):
        '''
        生成上车动作
        :param car_bop:
        :param peo_bop:
        :return: True/能上车 False/不能上车
        '''
        try:

            list_g_stage = self.dic_metadata['l_stage']
            flag_car_moving = wgruler.Moving(list_g_stage, cur_bop=car_bop)
            flag_peo_moving = wgruler.Moving(list_g_stage, cur_bop=peo_bop)

            flag_car_geton = car_bop.ObjTypeX == 1 and car_bop.ObjSonNum == 0 and car_bop.ObjStep >= car_bop.ObjStepMax // 2 and car_bop.ObjKeep == 0
            flag_peo_geton = peo_bop.ObjTypeX == 2 and peo_bop.ObjStep == peo_bop.ObjStepMax and peo_bop.ObjKeep == 0
            if flag_car_moving == 'M'and flag_peo_moving == 'M'  and flag_car_geton and flag_peo_geton:
                return True
            return False
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def genMoveAction(self, cur_bop, obj_pos):
        '''
        判断是否机动,若机动，返回机动路线
        :param cur_bop: 机动算子
        :param obj_pos: 目标位置
        :return: (True,list)/(需要机动，机动路线),(False,None)/(不机动，None)
        '''
        try:
            list_g_stage = self.dic_metadata['l_stage']
            flag_str_moving = wgruler.Moving(list_g_stage, cur_bop)
            assert flag_str_moving in ['N', 'M', 'O']
            if flag_str_moving == 'M':
                series = wgobject.bop2Ser(cur_bop)
                flag_result, list_movepath = self.obj_interface.getMovePath(series, obj_pos)
                if(flag_result == 0):
                    return True, list_movepath
            return False, None
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def wait(self, dic_metadata, flag_color):
        '''信息打印'''
        try:
            list_g_stage_now = self.obj_interface.getSimTime()
            dic_metadata['l_stage'] = list_g_stage_now
            if dic_metadata['l_stage'][0:3] == list_g_stage_now[0:3]:
                # if list_g_stage_now[1] % 2 == self.flag_color:
                if list_g_stage_now[1] % 2 == flag_color:
                    print(u'AI 当前阶段({})，无动作输出，等待中...'.format(self.showStage(list_g_stage_now)))
                    while (dic_metadata['l_stage'][0:3] == list_g_stage_now[0:3]):
                        time.sleep(0.5)
                        list_g_stage_now = self.obj_interface.getSimTime()
                else:  # 对方阶段
                    if list_g_stage_now[2] != 1: #对间瞄，最终射击
                        print(u'AI 当前阶段({})，无动作输出，等待中...'.format(self.showStage(list_g_stage_now)))
                        while (dic_metadata['l_stage'][0:3] == list_g_stage_now[0:3]):
                            time.sleep(0.5)
                            list_g_stage_now = self.obj_interface.getSimTime()
                    else:  # 对方机动环节(刷新数据库,重新迭代)
                        time.sleep(0.05)
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def showStage(self, list_g_stage):
        '''打印当前环节信息'''
        try:
            str_redcolor, str_bluecolor = '红方', '蓝方'
            list_huanjie_strs = ['间瞄', '机动', '最终射击', '最终射击', '同格交战']
            str_hoststagecolor, str_gueststagecolor = (str_redcolor, str_bluecolor) if list_g_stage[1] % 2 == 0 \
                else (str_bluecolor, str_redcolor)
            str_prefix = str_hoststagecolor if list_g_stage[2] == 2 else str_gueststagecolor if list_g_stage[2] == 3 else ''
            # str_prefix = str_hoststagecolor if list_g_stage[2] == 2 else str_gueststagecolor
            return '{} 第{}回合 第{}阶段 {}环节 剩余{}秒'.format(
                str_hoststagecolor, list_g_stage[0] + 1, list_g_stage[1] + 1,
                                    str_prefix + list_huanjie_strs[list_g_stage[2]], list_g_stage[3])
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    # 行进间射击
    def shootingOnMoving(self, my_bop, l_path):
        already_shooting = False
        for index, item in enumerate(l_path):
            boolen_1 = self.obj_interface.setMove(my_bop.ObjID, [item])
            print(u'打印行进间射击执行结果={}'.format(boolen_1))
            if not already_shooting:
                self.updateSDData()
                l_enemybops = self.dic_metadata['l_ubops']  # 敌方算子
                l_ourbops = self.dic_metadata['l_obops']  # 我方算子
                for index, ele in enumerate(l_ourbops):
                    if ele.ObjID == my_bop.ObjID:
                        my_bop = ele
                        break
                print('行进间射击敌方算子={}'.format(l_enemybops))
                # 判断是否能攻击
                for obj_bop_enemy in l_enemybops:
                    flag, weaponID = self.genShootAction(my_bop,
                                                         obj_bop_enemy)  # 判断是否可以射击,若可以射击，返回最佳射击武器
                    print(u'是否可以射击 flag={}'.format(flag))
                    if flag:  # 可以射击
                        exe_success, result = self.obj_interface.setFire(my_bop.ObjID,
                                                                    obj_bop_enemy.ObjID,
                                                                    (int)(weaponID))  # 调用接口执行射击动作

                        if exe_success == 0:  # 执行成功
                            already_shooting = True
                            print(u'打印行进间射击裁决结果==>{}'.format(result))
                            print('行进间射击:{}===>>{}'.format(my_bop.ObjPos, obj_bop_enemy.ObjPos))
                            break

    def __del__(self):
        if self.obj_interface is not None:
            self.obj_interface.__del__()
