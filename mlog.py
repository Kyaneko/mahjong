# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
import numpy as np
import pandas as pd
from pandas import DataFrame as df
import matplotlib.pyplot as plt

class mlog:
    
    def __init__(self):
        
        self.LOG_NAMES = ['round','name1','name2','name3','name4','status','riichi','claim']
        self.RESULT_COLUMNS = ['局','得点','順位','放銃','立直','副露','立直和了','副露和了','ツモ','ロン','和了点']
        self.SAVE_COLUMNS = ['半荘','局','得点','1位','2位','3位','4位','放銃','立直','副露','立直和了','副露和了','ツモ','ロン','和了点']
        self.log = None
        self.result = 0
        self.save = None
    
    def main(self):
        print('Please enter the path of log -> save file in order.')
        l = input()
        s = input()
        self.read_log(l)
        self.set_save(s)
        self.save_log()
        
    def read_log(self, path):
        
        def print_error(i):
            print('エラー：{}'.format(i))
            
        def is_num(x):
            return x.replace('-','').isnumeric()
        
        def len_is_4(s):
            return len(s)==4
        
        # csvファイルの読み込み
        log = pd.read_csv(path, names=self.LOG_NAMES)
        length = log.shape[0]
        
        # 最初の行からプレイヤー名を取得
        if log.loc[0,'round']!='start':
            print_error(0)
            return
        
        player_names = list(log.loc[0,'name1':'name4'])
        result = df([],index=player_names,columns=self.RESULT_COLUMNS)
        result[:] = 0
        point = [25000]*4
        
        
        # 得点のやり取り
        for i in range(1,length-1):
            
            if not all([len_is_4(s) for s in list(log.loc[i,'status':'claim'])]):
                print_error(i)
                return
            status,riichi,claim = list(log.loc[i,'status':'claim'])
            
            if not all([is_num(x) for x in list(log.loc[i,'name1':'name4'])]):
                print_error(i)
                return
            tmp = list(map(int,list(log.loc[i,'name1':'name4'])))
            
            for j in range(4):
                
                player = player_names[j]
                
                if riichi[j]=='o':
                    result.loc[player,'立直'] += 1
                    tmp[j] -= 1000
                    if status[j] in ['t','r']:
                        result.loc[player,'立直和了'] += 1
                if claim[j]=='o':
                    result.loc[player,'副露'] += 1
                    if status[j] in ['t','r']:
                        result.loc[player,'副露和了'] += 1
                if status[j]=='h':
                    result.loc[player,'放銃'] += 1
                if status[j]=='t':
                    result.loc[player,'ツモ'] += 1
                    result.loc[player,'和了点'] += tmp[j]
                if status[j]=='r':
                    result.loc[player,'ロン'] += 1
                    result.loc[player,'和了点'] += tmp[j]
                
                point[j] += tmp[j]
        
        # 最後の行で得点を調整
        if log.loc[length-1,'round']!='end':
            print_error(length-1)
            return
        
        tmp = list(map(int,list(log.loc[length-1,'name1':'name4'])))
        for j in range(4):
            point[j] += tmp[j]
        
        if sum(point)!=100000:
            print_error(length-1)
            return
        
        result['局'] = length-2
        result['得点'] = point
        
        for j in range(4):
            player = player_names[j]
            rank = 0
            for k in range(4):
                if point[j]<point[k] or (point[j]==point[k] and j>=k):
                    rank += 1
            result.loc[player,'順位'] = rank
 
        # 記録を保存
        self.log = log
        self.result = result
        
        print('Log is updated.')
        
    def set_save(self, path):
        
        self.save = path
        print('Save file is designed.')
    
    def new_save(self):
        
        if self.save == None:
            print('Please use set_save() to design the path of CSV file.')
            return
        
        tmp = df([],columns=self.SAVE_COLUMNS)
        tmp.to_csv(self.save)
        print('New save file is created.')
    
    def save_log(self):
        
        # エラーの確認
        if type(self.log) != type(self.result):
            print('Please use read_log() to read CSV file.')
            return
        if self.save == None:
            print('Please use set_save() to design the path of CSV file.')
            return
        print('Result will be updated. OK? (enter \'Yes\'):')
        s = input()
        if s!='Yes':
            return
        
        # 記録の書き込み
        new = pd.read_csv(self.save, index_col=0)
        
        for player in list(self.result.index):
            
            if player in new.index:
                tmp = pd.Series(new.loc[player],index=self.SAVE_COLUMNS)
            else:
                tmp = pd.Series([0]*len(self.SAVE_COLUMNS),index=self.SAVE_COLUMNS)
            
            tmp['半荘'] += 1
            for col in self.RESULT_COLUMNS:
                if col=='順位':
                    rank = str(self.result.loc[player,'順位'])+'位'
                    tmp[rank] += 1
                else:
                    tmp[col] += self.result.loc[player,col]
            
            new.loc[player] = tmp
        
        new.to_csv(self.save)
        print('Result is updated.')
        
    def show(self):
        return pd.read_csv(self.save, index_col=0)

    def get(self,player,uma=[10,20]):

        csv = pd.read_csv(self.save, index_col=0)

        print('Name：{}'.format(player))
        print('総半荘数：{}'.format(csv.loc[player,'半荘']))
        print('総局数：{}'.format(csv.loc[player,'局']))
        score = csv.loc[player,'得点']
        score += (uma[1]+20)*1000*csv.loc[player,'1位']
        score += uma[0]*1000*csv.loc[player,'2位']
        score -= uma[0]*1000*csv.loc[player,'3位']
        score -= uma[1]*1000*csv.loc[player,'4位']
        score //= csv.loc[player,'半荘']
        score -= 30000
        print('平均得失点：{}'.format(score))
        rank = 0
        rank += 1*csv.loc[player,'1位']
        rank += 2*csv.loc[player,'2位']
        rank += 3*csv.loc[player,'3位']
        rank += 4*csv.loc[player,'4位']
        rank /= csv.loc[player,'半荘']
        print('平均順位：{:.3}'.format(rank))
        win = csv.loc[player,'ツモ']+csv.loc[player,'ロン']
        print('平均和了点数：{}'.format(csv.loc[player,'和了点']//win if win!=0 else 0.0))
        print('和了率：{:.3}%'.format(100*win/csv.loc[player,'局']))
        print('放銃率：{:.3}%'.format(100*csv.loc[player,'放銃']/csv.loc[player,'局']))
        print('立直率：{:.3}%'.format(100*csv.loc[player,'立直']/csv.loc[player,'局']))
        print('副露率：{:.3}%'.format(100*csv.loc[player,'副露']/csv.loc[player,'局']))
        reach_success = csv.loc[player,'立直和了']/csv.loc[player,'立直'] if csv.loc[player,'立直']!=0 else 0.0
        print('立直成功率：{:.3}%'.format(100*reach_success))
        
        if win!=0:
            plt.figure(figsize=(6, 4))
            plt.subplot(1,2,1)
            x = [csv.loc[player,'ツモ'],csv.loc[player,'ロン']]
            c = ['lightcoral','skyblue']
            plt.pie(x, labels=['Tsumo','Ron'], colors=c)
            plt.subplot(1,2,2)
            dma = win-csv.loc[player,'立直和了']-csv.loc[player,'副露和了']
            x = [csv.loc[player,'立直和了'],csv.loc[player,'副露和了'],dma]
            c = ['moccasin','palegreen','pink']
            plt.pie(x, labels=['Riichi','Pon & Chi','Sniper'], colors=c)
            plt.show()
