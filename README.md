
# 天凤牌谱分析工具

本工具用于自动化分析日本麻将天凤牌谱数据，支持从tenhou.net平台下载牌谱并生成详细的统计报告。

## 📋 功能特性

- 📥 数据获取 - 自动从tenhou.net下载原始牌谱JSON数据
- 📊 数据分析 - 生成包含20+统计指标的专业报告
- 🎨 可视化呈现 - 自动生成html网页、风格分析图、相关系数热力图、pt变化趋势图表、rate变化趋势图表。
- ⏳ 多维筛选 - 支持按玩家昵称、时间段、牌桌类型进行数据过滤

## 🚀 快速开始
0. 下载exe程序压缩包
   
    下载链接，任选一个
    - https://github.com/wuye999/mahjong-tenho-log-parser/releases/latest/download/default.zip
    - https://gh-proxy.com/github.com/wuye999/mahjong-tenho-log-parser/releases/latest/download/default.zip
    - https://github.abskoop.workers.dev/https://github.com/wuye999/mahjong-tenho-log-parser/releases/download/latest/default.zip
   
    下载解压后将得到以下文件
    - config.toml
    - 牌谱.txt
    - 天凤牌谱数据统计.exe

2. 准备牌谱链接文件
   
   - 方法一（推荐）：安装使用油猴插件自动获取牌谱
      - 安装该插件：https://greasyfork.org/zh-CN/scripts/527090-天凤牌谱链接提取器
      - 进入牌谱界面，点击开始获取，等待获取完成，点击下载牌谱即可。

   - 方法二：创建或编辑`牌谱.txt`，每行放一个tenhou牌谱链接
   ```
   https://tenhou.net/6/?log=2025021117gm-0089-0000-406067c8&tw=2
   https://tenhou.net/6/?log=2025021117gm-0089-0000-c16837d6&tw=2
   ```

4. 编辑配置文件


请用记事本打开配置文件"config.toml"，并修改其玩家昵称、牌桌级别。然后Ctrl+S保存配置文件。


示例：


   ```toml
   # config.toml
   [filter]
   players = "鹿目円"    # 需要分析的玩家昵称
   levels = ["四般東喰赤", "四般南喰赤", "四上南喰赤"]    # 牌桌级别，留空全部分析
   timeafter = "1970-01-01 08:00:00"    # 分析起始时间
   timebefore = "2099-12-31 23:59:59"    # 分析截止时间

   # 后续一般不需要修改

   ```

5. 运行分析程序
   
   双击运行，即可生成html网页，打开即可查看。里面包含20+统计指标的专业报告，风格分析图、相关系数热力图、pt变化趋势图表、rate变化趋势图表。
   
## 📦 使用源代码运行

### 环境要求
- Python 3.8+
- 支持访问tenhou.net的网络环境

### 安装依赖
```bash
pip install -r requirements.txt
```


## 📊 输出解释
输出包含1个“统计报告.html“文件，一个”统计报告”文件夹，用于存放html网页所需的文件。

生成的网页示例：

### 综合统计表
统计数据示例：
```csv
,统计值
有效牌谱数,58.0
有效小局数,345.0
平均顺位,2.2069
总pt变动,720.0
总rate变动,-46.41
一位率,0.3621
二位率,0.2586
三位率,0.1897
四位率,0.1897
连对率,0.6207
被飞率,0.0
和了率,0.229
放铳率,0.1014
副露率,0.3971
立直率,0.142
默听率,0.1899
和牌时立直率,0.4177
和牌时副露率,0.3924
和牌自摸率,0.481
平均和了打点,6117.7215
平均和了巡目,11.8861
立直先制率,0.898
追立率,0.102
立直后和牌率,0.6735
立直后放铳率,0.0816
立直后流局率,0.102
立直和牌打点,9112.1212
立直和牌巡目,11.2424
平均立直巡目,6.6531
副露后和牌率,0.2263
副露后放铳率,0.1168
副露后流局率,0.1971
副露和牌打点,3693.5484
副露和牌巡目,12.4194
平均放铳打点,3400.0
放铳时立直率,0.1143
放铳时副露率,0.4571
放铳时门清率,0.4286
流局率,0.1739
流局听牌率,0.3667
流局平均得点,-183.3333
立直流局时听牌率,1.0
副露流局时听牌率,0.5185
门清流局时听牌率,0.1071
```

![image](https://github.com/user-attachments/assets/5e2aeb80-4e25-4aa5-8c45-0bf10dfd3b9b)

### pt变化图

![アンさん_pt变化图](https://github.com/user-attachments/assets/3012261e-c680-4885-be21-a51fd59cb510)


### rate变化图

当牌谱不连续时，缺失的数据会导致rate的变化幅度看起来非常大。例如：1月1日rate为2200，9月1日rate为1800，但中间的牌谱缺失。虽然看起来变化幅度会显得异常大，但数据是准确的。

![アンさん_rate变化图](https://github.com/user-attachments/assets/7de8d8b9-29f5-45f0-98f7-e135876ee609)



### 风格分析图

![鹿目円_风格分析](https://github.com/user-attachments/assets/19cba814-5b1c-4645-af1f-1ec398d7635e)

### 相关系数热力图
展示spearman系数热力图。
![image](https://github.com/user-attachments/assets/b021ecf9-ba9d-48d2-885f-ff7090d69845)

### excel文件、csv文件
默认不生成，有需要自行修改配置文件“config.toml”

## 📌 注意事项

1. 需要保持网络连接以访问tenhou.net
2. 首次运行会自动创建`paipu_data/`目录存储下载的牌谱
3. 每个牌谱约占用3-15KB存储空间
4. 如有疑问请查看并使用源代码

## 📄 协议

本项目基于 [MIT License](LICENSE) 开放源代码
