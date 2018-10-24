# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def doAction(self):
        try:
            # 当前态势
            l_ourbops = self.dic_metadata['l_obops'] #我方算子
            l_enemybops = self.dic_metadata['l_ubops'] #敌方算子
            l_cities = self.dic_metadata['l_cities'] #夺控点列表
            # 夺控动作
            for cur_bop in l_ourbops:
                if self.genOccupyAction(cur_bop): #判断是否可以夺控
                    self.obj_interface.setOccupy(cur_bop.ObjID) #调用接口执行夺控动作
                    return True
            # 射击动作
            for att_bop in l_ourbops:
                for obj_bop in l_enemybops:
                    flag,weaponID = self.genShootAction(att_bop, obj_bop) #判断是否可以射击,若可以射击，返回最佳射击武器
                    if flag: #可以射击
                        exe_success,_ = self.obj_interface.setFire(att_bop.ObjID,obj_bop.ObjID,(int)(weaponID)) #调用接口执行射击动作
                        if exe_success == 0: # 执行成功
                            return True

            l_cityloc = [l_cities[i] for i in range(len(l_cities)) if i % 3 == 0] # 所有夺控点坐标
            # 人员下车
            for cur_bop in l_ourbops:
                if cur_bop.ObjTypeX == 1 and cur_bop.ObjSonNum == 1:  # 载人车辆
                    for city_loc in l_cityloc:
                        _, dis = self.obj_interface.getMapDistance(cur_bop.ObjPos, city_loc) # 距离夺控点的距离
                        if dis <= 3:  # 距离<3下车
                            if self.genGetOffAction(cur_bop): #判断是否满足下车条件
                                self.obj_interface.setGetoff(cur_bop.ObjID) # 调用接口执行下车动作
                                return True

            city_loc = random.sample(l_cityloc, 1)[0]  # 随机选择一个夺控点机动
            # 机动
            for cur_bop in l_ourbops:
                flag_move = True
                if cur_bop.ObjTypeX in [1, 2]:
                    '''，人和战车能观察到敌方算子且距离小于10，放弃机动机会'''
                    cur_ser = wgobject.bop2Ser(cur_bop)
                    for ubop in l_enemybops:
                        obj_ser = wgobject.bop2Ser(ubop)
                        _, flag_see = self.obj_interface.flagISU(cur_ser, obj_ser)
                        _, distance = self.obj_interface.getMapDistance(cur_bop.ObjPos, ubop.ObjPos)
                        if flag_see and distance <= 10:
                            flag_move = False
                            break
                if flag_move:
                    if cur_bop.ObjPos != city_loc:
                        flag, l_path = self.genMoveAction(cur_bop, city_loc)  # 判断能否执行机动动作，如果能，返回机动路径
                        if flag and l_path:
                            # 张庶修改:每走完一次判断是否能射击，如果能射击则射击完后走下一格
                            print('l_path=: {}'.format(l_path))
                            l_path_troops = []
                            for index in range(len(l_path)-1):
                                l_path_troops.append([l_path[index], l_path[index+1]])
                            print('l_path_troops = {}'.format(l_path_troops))

                            for index, item in enumerate(l_path_troops):
                                # self.obj_interface.setMove(cur_bop.ObjID, l_path)
                                # 判断是否能攻击
                                for obj_bop in l_enemybops:
                                    flag, weaponID = self.genShootAction(cur_bop, obj_bop)  # 判断是否可以射击,若可以射击，返回最佳射击武器
                                    if flag:  # 可以射击
                                        exe_success, _ = self.obj_interface.setFire(cur_bop.ObjID, obj_bop.ObjID,
                                                                                    (int)(weaponID))  # 调用接口执行射击动作
                                        if exe_success == 0:  # 执行成功
                                            print('机动中攻击:{}===>>{}'.format(cur_bop.ObjPos, obj_bop.ObjPos))
                                # # 切换行军状态
                                # if self.GridType(int(item[0])) == 2 and self.GridType(int(item[1])) == 2:
                                #     bollen = self.obj_interface.setState(cur_bop.ObjID, 1)
                                #     print('切换机动状态bollen=:{}'.format(bollen))

                                self.obj_interface.setMove(cur_bop.ObjID, item)  # 调用接口函数执行机动动作
                            return True
            return False  #没有动作执行返回False
        except Exception as e:
            print('error in run_onestep(): ' + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            print('error in run_onestep(): ' + str(k))
            self.__del__()
            raise
