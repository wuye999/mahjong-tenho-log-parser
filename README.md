
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
    - https://cdn.jsdelivr.net/gh/wuye999/mahjong-tenho-log-parser@latest/default.zip
    - https://gh-proxy.com/github.com/wuye999/mahjong-tenho-log-parser/releases/latest/download/default.zip
   
    下载解压后将得到以下文件
    - config.toml
    - 牌谱.txt
    - 天凤牌谱数据统计.exe

2. 准备牌谱链接文件
   
   - 方法一（推荐）：安装使用油猴插件自动获取牌谱
      - 安装该插件：https://greasyfork.org/zh-CN/scripts/527090-天凤牌谱链接提取器
      - 进入牌谱界面，点击下载即可得到”牌谱.txt“文件。

   - 方法二：创建或编辑`牌谱.txt`，每行放一个tenhou牌谱链接
   ```
   https://tenhou.net/6/?log=2025021117gm-0089-0000-406067c8&tw=2
   https://tenhou.net/6/?log=2025021117gm-0089-0000-c16837d6&tw=2
   ```

4. 编辑配置文件
   ```toml
   # config.toml
   [filter]
   players = "鹿目円"    # 需要分析的玩家昵称
   levels = ["四般東喰赤", "四般南喰赤", "四上南喰赤"]    # 牌桌级别
   paipu_txt = "牌谱.txt"    # 存放牌谱链接的文件名
   timeafter = "1970-01-01 08:00:00"    # 分析起始时间
   timebefore = "2099-12-31 23:59:59"    # 分析截止时间
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
![image](https://github.com/user-attachments/assets/5e2aeb80-4e25-4aa5-8c45-0bf10dfd3b9b)


### 风格分析图

关于风格分析的python版本代码在本库“四麻风格分析.py”里。
![鹿目円_风格分析](https://github.com/user-attachments/assets/19cba814-5b1c-4645-af1f-1ec398d7635e)

### 相关系数热力图
展示spearman相关系数热力图，其余未展示的两个分别是pearson相关系数、kendall相关系数。
![image](https://github.com/user-attachments/assets/b021ecf9-ba9d-48d2-885f-ff7090d69845)


## 📌 注意事项

1. 需要保持网络连接以访问tenhou.net
2. 首次运行会自动创建`paipu_data/`目录存储下载的牌谱
3. 每个牌谱约占用3-15KB存储空间
4. 如有疑问请查看并使用源代码

## 📄 协议

本项目基于 [MIT License](LICENSE) 开放源代码
