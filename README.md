
# 天凤牌谱分析工具

本工具用于自动化分析日本麻将天凤牌谱数据，支持从tenhou.net平台下载牌谱并生成详细的统计报告。

## 📋 功能特性

- 自动从tenhou.net下载牌谱JSON数据
- 生成包含20+统计指标的Excel报告
- 支持时间范围、段位级别等多维度过滤

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
   - 创建或编辑`牌谱.txt`，每行放一个tenhou牌谱链接
   ```
   https://tenhou.net/6/?log=2025021117gm-0089-0000-406067c8&tw=2
   https://tenhou.net/6/?log=2025021117gm-0089-0000-c16837d6&tw=2
   ```

3. 编辑配置文件
   ```toml
   # config.toml
   [filter]
   players = "鹿目円"  # 需要分析的玩家昵称
   levels = ["四般東喰赤", "四般南喰赤", "四上南喰赤"]  # 牌桌级别
   paipu_txt = "牌谱.txt"  # 存放牌谱链接的文件名
   timeafter = "1970-01-01 08:00:00"  # 分析起始时间
   timebefore = "2099-12-31 23:59:59"  # 分析截止时间
   ```

4. 运行分析程序
   双击运行
   
## 📦 使用源代码运行

### 环境要求
- Python 3.8+
- 支持访问tenhou.net的网络环境

### 安装依赖
```bash
pip install -r requirements.txt
```

## 📊 输出解释

生成的Excel报告包含三个工作表：

### 综合统计表
![image](https://github.com/user-attachments/assets/034d931d-28c3-4cf2-aebf-cb255713ed38)


### 半庄数据表
![image](https://github.com/user-attachments/assets/3ab6f586-fd01-4fb2-b894-8caf3e55299b)



### 小局数据表
![image](https://github.com/user-attachments/assets/7542c6d7-1f3a-48fc-b4f4-fc85e498ee0c)


## 📌 注意事项

1. 需要保持网络连接以访问tenhou.net
2. 首次运行会自动创建`paipu_data/`目录存储下载的牌谱
3. 每个牌谱约占用3-15KB存储空间
4. 如有疑问请查看并使用源代码

## 📄 协议

本项目基于 [MIT License](LICENSE) 开放源代码
