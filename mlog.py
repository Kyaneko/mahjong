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
import japanize_matplotlib

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
            plt.pie(x, labels=['Riichi','Pon & Chi','Snipe'], colors=c)
            plt.show()
    
    def summary(self,uma=[10,20]):
        
        csv = pd.read_csv(self.save, index_col=0)
        players = list(csv.index)
        players2 =  players[:]+['(平均)']
        length = len(players)
        y = np.arange(length)
        y2 = np.arange(length+1)
        width = 0.6
        
        fig = plt.figure(figsize=(20,length*3),dpi=200)
        cm = plt.get_cmap('hsv')
        color_step = 256//length
        color_list = [cm(i*color_step) for i in range(length)]
        color_list2 = color_list[:]+['gray']
        
        # 平均得失点
        平均得失点 = []
        for player in players:
            score = csv.loc[player,'得点']
            score += (uma[1]+20)*1000*csv.loc[player,'1位']
            score += uma[0]*1000*csv.loc[player,'2位']
            score -= uma[0]*1000*csv.loc[player,'3位']
            score -= uma[1]*1000*csv.loc[player,'4位']
            score //= csv.loc[player,'半荘']
            score -= 30000
            平均得失点.append(score)
            
        ax1 = fig.add_subplot(3, 2, 1)
        ax1.plot([0,0],[-0.5,length-0.5],c='gray',ls=':',lw=2,zorder=-1)
        ax1.barh(y, 平均得失点, width, color=color_list)
        ax1.set_title('平均得失点（ウマ：{}-{}）'.format(uma[0],uma[1]))
        ax1.set_yticks(y)
        ax1.set_yticklabels(players)
        ax1.set_xlim(min(平均得失点)-2000, max(平均得失点)+2000)
        ax1.set_ylim(-0.5,length-0.5)
        for i,j in zip(平均得失点, y):
            ax1.text(
                i-100 if i<0 else i+100, j, i,
                ha='right' if i<0 else 'left',va='center'
            )
        
        # 平均順位
        平均順位 = []
        for player in players:
            rank = 0
            rank += 1*csv.loc[player,'1位']
            rank += 2*csv.loc[player,'2位']
            rank += 3*csv.loc[player,'3位']
            rank += 4*csv.loc[player,'4位']
            rank /= csv.loc[player,'半荘']
            平均順位.append(rank)
        
        ax2 = fig.add_subplot(3, 2, 3)
        ax2.plot([2.5,2.5],[-0.5,length-0.5],c='gray',ls=':',lw=2,zorder=-1)
        ax2.barh(y, 平均順位, width, color=color_list)
        ax2.set_title('平均順位')
        ax2.set_yticks(y)
        ax2.set_yticklabels(players)
        ax2.set_xlim(1.0,max(平均順位)+0.15)
        ax2.set_ylim(-0.5,length-0.5)
        for i,j in zip(平均順位, y):
            ax2.text(
                i+0.02, j, i,
                ha='left',va='center'
            )
        
        # 平均和了点数
        平均和了点数 = []
        和了回数 = dict()
        合計和了回数 = 0
        tmp = 0
        for player in players:
            win = csv.loc[player,'ツモ']+csv.loc[player,'ロン']
            和了回数[player] = win
            平均和了点数.append(csv.loc[player,'和了点']//win if win!=0 else 0.0)
            合計和了回数 += win
            tmp += csv.loc[player,'和了点']
        ave = tmp//合計和了回数
        
        ax3 = fig.add_subplot(3, 2, 5)
        ax3.plot([ave,ave],[-0.5,length-0.5],c='gray',ls=':',lw=2,zorder=-1)
        ax3.barh(y, 平均和了点数, width, color=color_list)
        ax3.set_title('平均和了点数')
        ax3.set_yticks(y)
        ax3.set_yticklabels(players)
        ax3.set_xlim(0,max(平均和了点数)+1000)
        ax3.set_ylim(-0.5,length-0.5)
        for i,j in zip(平均和了点数, y):
            ax3.text(
                i+100, j, i,
                ha='left',va='center'
            )
        
        # 和了率・放銃率
        和了率 = []
        放銃率 = []
        合計局数 = 0
        tmp = 0
        for player in players:
            和了率.append(100*和了回数[player]/csv.loc[player,'局'])
            放銃率.append(100*csv.loc[player,'放銃']/csv.loc[player,'局'])
            合計局数 += csv.loc[player,'局']
            tmp += csv.loc[player,'放銃']
        和了率.append(100*合計和了回数/合計局数)
        放銃率.append(100*tmp/合計局数)
        
        ax4 = fig.add_subplot(3, 2, 2)
        ax4.barh(y2+(width/4+0.05), 和了率, width/2, color=color_list2)
        ax4.barh(y2-(width/4+0.05), 放銃率, width/2, color=color_list2)
        ax4.set_title('和了率・放銃率')
        ax4.set_yticks(y2)
        ax4.set_yticklabels(players2)
        ax4.set_xlim(0,max(max(和了率),max(放銃率))+5)
        ax4.set_ylim(-0.5,length+0.5)
        for h,i,j in zip(和了率, 放銃率, y2):
            ax4.text(
                max(h,i)+0.5, j,
                '{:.3}/{:.3}%'.format(h,i),
                ha='left',va='center'
            )
        
        # 立直率・副露率
        立直率 = []
        副露率 = []
        合計立直回数 = 0
        tmp = 0
        for player in players:
            立直率.append(100*csv.loc[player,'立直']/csv.loc[player,'局'])
            副露率.append(100*csv.loc[player,'副露']/csv.loc[player,'局'])
            合計立直回数 += csv.loc[player,'立直']
            tmp += csv.loc[player,'副露']
        立直率.append(100*合計立直回数/合計局数)
        副露率.append(100*tmp/合計局数)
        
        ax5 = fig.add_subplot(3, 2, 4)
        ax5.barh(y2+(width/4+0.05), 立直率, width/2, color=color_list2)
        ax5.barh(y2-(width/4+0.05), 副露率, width/2, color=color_list2)
        ax5.set_title('立直率・副露率')
        ax5.set_yticks(y2)
        ax5.set_yticklabels(players2)
        ax5.set_xlim(0,max(max(立直率),max(副露率))+5)
        ax5.set_ylim(-0.5,length+0.5)
        for h,i,j in zip(立直率, 副露率, y2):
            ax5.text(
                max(h,i)+0.5, j,
                '{:.3}/{:.3}%'.format(h,i),
                ha='left',va='center'
            )
        
        # 和了割合
        # カラーマップは['moccasin','palegreen','pink']
        立直和了率 = []
        副露和了率 = []
        ダマ和了率 = []
        tmp1 = 0
        tmp2 = 0
        tmp3 = 0
        for player in players:
            win = 和了回数[player]
            立直和了率.append(100*csv.loc[player,'立直和了']/win if win!=0 else 0.0)
            副露和了率.append(100*csv.loc[player,'副露和了']/win if win!=0 else 0.0)
            tmp = win-csv.loc[player,'立直和了']-csv.loc[player,'副露和了']
            ダマ和了率.append(100*tmp/win if win!=0 else 0.0)
            tmp1 += csv.loc[player,'立直和了']
            tmp2 += csv.loc[player,'副露和了']
            tmp3 += tmp
        立直和了率.append(100*tmp1/合計和了回数)
        副露和了率.append(100*tmp2/合計和了回数)
        ダマ和了率.append(100*tmp3/合計和了回数)
        
        ax6 = fig.add_subplot(3, 2, 6)
        ax6.barh(y2, 立直和了率, width, color='moccasin', label='立直和了率')
        ax6.barh(y2, 副露和了率, width, color='palegreen', left=立直和了率, label='副露和了率')
        left = [x+y for x,y in zip(立直和了率,副露和了率)]
        ax6.barh(y2, ダマ和了率, width, color='pink', left=left, label='ダマ和了率')
        ax6.set_title('和了の内訳')
        ax6.set_yticks(y2)
        ax6.set_yticklabels(players2)
        ax6.set_xlim(0,100)
        ax6.set_ylim(-0.5,length+0.5)
        ax6.legend(loc='upper left')
        for g,h,i,j in zip(立直和了率, 副露和了率, ダマ和了率, y2):
            if g!=0:
                ax6.text(
                    g/2, j,'{:.3}%'.format(g),ha='center',va='center'
                )
            if h!=0:
                ax6.text(
                    g+h/2, j,'{:.3}%'.format(h),ha='center',va='center'
                )
            if i!=0:
                ax6.text(
                    g+h+i/2, j,'{:.3}%'.format(i),ha='center',va='center'
                )
        
        plt.savefig('summary.jpg')
        fig.tight_layout()
        plt.show()
