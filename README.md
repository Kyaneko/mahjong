# mahjong

麻雀成績管理システム「mlog」

### 成績閲覧の仕方

1. 「mlog.py」と「save.csv」をダウンロード
2. 以下を実行
```
from mlog import mlog
a = mlog()
a.set_save('save.fig')
a.get('名前')
```

「save.csv」は友人戦が行われるたびに更新していきます．
