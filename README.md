# mahjong

麻雀成績管理システム「mlog」

### 閲覧：個人成績

1. 「mlog.py」と「save.csv」をダウンロード
2. 以下を実行
```
    from mlog import mlog
    a = mlog()
    a.set_save('save.csv')
    a.get('名前')
```

### 閲覧：全体成績

```summary()```を実行するだけ！

「save.csv」は友人戦が行われるたびに更新していきます．
なお，「summary.jpg」は```summary()```で得られる成績とまったく同じものです．
