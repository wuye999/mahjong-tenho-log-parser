import json
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import parse_qs, urlparse
import pandas as pd  # pip install pandas
from tqdm import tqdm  # pip install tqdm
import requests  # pip install requests
import toml  # pip install toml
import openpyxl  # pip install openpyxl
import matplotlib.pyplot as plt  # pip install matplotlib
import numpy as np  # pip install numpy
import seaborn as sns
import scipy
from 四麻风格分析 import MahjongAnalyzer

# 在pyinstaller打包环境下返回资源地址
def resource_path(relative_path):
    executable_path = sys.argv[0] 
    current_path = Path(Path(executable_path).resolve()).parents[0]  # 读取当前路径
    return Path('/').joinpath(current_path, relative_path)


def extract_log_id(url):
    """从原始URL中提取log参数值"""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return params.get('log', [None])[0]

def build_download_url(original_url):
    """构建下载用URL"""
    log_id = extract_log_id(original_url)
    if not log_id:
        return None
    return f"https://tenhou.net/5/mjlog2json.cgi?{log_id}"

def get_headers(referer):
    """生成请求头"""
    return {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9,zh-HK;q=0.8,zh-TW;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'tenhou.net',
        'Referer': referer,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
        'sec-ch-ua': '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

def download_paipu(original_url, save_dir="paipu_data"):
    """下载单个牌谱"""
    save_dir_path = Path(resource_path(save_dir))
    save_dir_path.mkdir(parents=True, exist_ok=True)
    # os.makedirs(save_dir, exist_ok=True)
    
    download_url = build_download_url(original_url)
    if not download_url:
        print(f"无效URL: {original_url}")
        return None
    
    try:
        # 保存文件
        log_id = extract_log_id(original_url) 
        # save_path = os.path.join(save_dir, f"{log_id}.json") 
        save_path = Path(save_dir).joinpath(f"{log_id}.json")
        # 判断文件是否存在
        if save_path.exists():
            print(f"该牌谱已存在，跳过下载: {original_url}")
            return save_path

        response = requests.get(
            download_url,
            headers=get_headers(original_url),
            timeout=10
        )
        response.raise_for_status()
        
        with open(resource_path(save_path), 'w', encoding='utf-8') as f:
            json.dump(response.json(), f)
        print(f"下载成功: {original_url}")
        return save_path
    except Exception as e:
        print(f"下载失败 {original_url}: {str(e)}")
        return None

def process_paipu_file(txt_path, target_player):
    """处理整个牌谱文件"""
    print("开始下载牌谱文件...")
    with open(resource_path(txt_path), 'r', encoding='utf-8') as f:
        for line in f:
            url = line.strip()
            if not url:
                continue
            
            # 下载牌谱
            json_path = download_paipu(url, f"paipu_data/{target_player}")
            if not json_path:
                continue

def parse_ref_time(ref_str):
    """解析牌谱ref中的时间"""
    try:
        # 示例 ref: 2025021117gm-0089-0000-406067c8
        time_part = ref_str.split('gm-')[0]
        dt = datetime.strptime(time_part, "%Y%m%d%H")
        return dt.strftime("%Y-%m-%d %H:00:00")
    except Exception as e:
        print(f"时间解析失败 {ref_str}: {str(e)}")
        return None

def load_config(config_path="config.toml"):
    """加载配置文件"""
    try:
        with open(resource_path(config_path), "r", encoding='utf-8') as f:
            config = toml.load(f)

        # 将时间格式转换为datetime对象
        config['filter']['timebefore'] = datetime.strptime(config['filter']['timebefore'], "%Y-%m-%d %H:%M:%S")
        config['filter']['timeafter'] = datetime.strptime(config['filter']['timeafter'], "%Y-%m-%d %H:%M:%S")

        return config
    except FileNotFoundError:
        print(f"配置文件 {config_path} 不存在")
        return None
    except Exception as e:
        print(f"配置文件加载失败: {str(e)}")
        return None
    

def process_paipu(file_path, target_player, config):
    """处理单个牌谱文件"""
    try:
        with open(resource_path(file_path), 'r', encoding='utf-8') as f:
            raw = f.read()
            paipu = json.loads(raw)
    except Exception as e:
        print(f"解析错误 {file_path}: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()
    
    # 基础过滤
    if not config:
        return pd.DataFrame(), pd.DataFrame()
    
    # 1. 玩家过滤
    if target_player not in paipu.get('name', []):
        return pd.DataFrame(), pd.DataFrame()
    
    seat = paipu['name'].index(target_player)
    dan = paipu['dan'][seat]
    rate = paipu['rate'][seat]
    ref = paipu['ref']
    if len(paipu['name']) == 4:
        rule_disp = "四" + paipu['rule']['disp']
    elif len(paipu['name']) == 3:
        rule_disp = "三" +paipu['rule']['disp']

    # 2. 牌桌级别过滤
    if rule_disp not in config['filter']['levels']:
        return pd.DataFrame(), pd.DataFrame()
    
    # 3. 时间过滤
    game_time = datetime.strptime(parse_ref_time(ref), "%Y-%m-%d %H:%M:%S")
    if not (config['filter']['timeafter'] <= game_time <= config['filter']['timebefore']):
        return pd.DataFrame(), pd.DataFrame()

    records = []
    
    for game_idx, game in enumerate(paipu['log']):
        # 过滤特殊流局 九种九牌 四风连打等
        if len(game[16]) == 1:
            print(f"特殊流局，跳过该小局：{game[16]}")
            continue

        # 基础信息
        game_info = {
            '牌谱': ref,
            '牌桌': rule_disp,
            '对局时间': parse_ref_time(ref),
            '玩家昵称': target_player,
            '玩家位置': seat,
            '玩家段位': dan,
            '玩家rate': rate,
            '场次': game[0],
            '四家点数': game[1]
        }
        
        # 收集各玩家立直信息
        riichi_turns = []
        for player_seat in range(4):
            discard_actions = game[6 + 3*player_seat]
            riichi_turn = None
            for turn_idx, action in enumerate(discard_actions):
                if isinstance(action, str) and action.startswith('r'):
                    riichi_turn = turn_idx
                    break  # 只记录第一次立直
            riichi_turns.append(riichi_turn)
        

        # 遍历玩家副露
        calls = []
        for a in game[6 + 3*seat - 1]:  # 玩家摸牌
            if isinstance(a, str) and any(op in a for op in ['c', 'p', 'm', 'k'])  :  # 包含吃/碰/明杠/加杠标识
                calls.append(a)
        for a in game[6 + 3*seat]:  # 玩家出牌
            if isinstance(a, str) and any(op in a for op in ['c', 'p', 'm', 'k'])  :
                calls.append(a)

        discard_actions = game[6 + 3*seat]  # 玩家出牌
        has_riichi = any(isinstance(a, str) and a.startswith('r') for a in discard_actions)
        
        # 结果解析
        result = game[16]
        game_info.update({
            '和了': False,
            '放铳': False,
            '副露': len(calls) > 0,
            '立直': has_riichi,
            '默听': None,
            '和了打点': None,
            '和了巡目': None,
            '放铳打点': None,
            '流局时听牌': None,
            '流局时得点': None,
            '立直先制': None,
            '立直巡目': None,
            '追立': False,
            '自摸': False,
            '流局': False,
        })
        
        # 处理结果类型
        if result[0] == '和了':
            for i, v in enumerate(result[1]):
                if i != seat:
                    continue
                if v > 0:
                    game_info.update({
                        '和了': True,
                        '和了打点': result[1][seat],
                        '和了巡目': len(discard_actions),
                        '默听': has_riichi is False and game_info['副露'] is False,
                        '自摸': False,
                    })
                    # 自摸时巡目加一
                    if 0 not in result[1]:  # 自摸
                        game_info['和了巡目'] += 1
                        game_info.update({
                            '自摸': True,
                        })
                elif v < 0:
                    if 0 not in result[1]:  # 被自摸，不算放铳
                        game_info.update({
                            '放铳': False,
                            '放铳打点': None
                        })
                    else:
                        game_info.update({
                            '放铳': True,
                            '放铳打点': result[1][seat]
                        })
                elif v == 0:
                    game_info.update({
                        '和了': False,
                        '和了打点': None,
                        '和了巡目': None,
                        '默听': None,
                        '放铳': False,
                        '放铳打点':None,
                    })
                else:
                    raise ValueError(f'Unexpected result value: {result}')


        # 修正后代码
        if result[0] == '流局':
            delta = result[1][seat]
            game_info['流局时听牌'] = delta > 0
            game_info['流局时得点'] = delta
            # # 特殊处理立直后的流局听牌
            # if game_info['立直'] and delta == 1000:
            #     game_info['流局时听牌'] = True
            game_info.update({
                '放铳': False,
                '放铳打点': None,
                '流局': True,
            })


        # 处理立直类型
        if has_riichi:
            target_turn = next(i for i, a in enumerate(discard_actions) 
                             if isinstance(a, str) and a.startswith('r'))
            is_senzu = True
            
            for other_seat, other_turn in enumerate(riichi_turns):
                if other_seat == seat or other_turn is None:
                    continue
                
                # 比较巡目和座位顺序
                if (other_turn < target_turn) or \
                   (other_turn == target_turn and other_seat < seat):
                    is_senzu = False
                    break
            
            game_info.update({
                '立直先制': is_senzu,
                '追立': not is_senzu,
                '立直巡目': target_turn,

            })
        
        records.append(game_info)

    
    # 新增半庄数据
    hanchan_data = {
        '牌谱': ref,
        '牌桌': rule_disp,
        '对局时间': parse_ref_time(ref),
        '玩家昵称': target_player,
        '玩家位置': seat,
        '玩家段位': dan,
        '玩家rate': rate,
    }
    hanchan_data.update(process_hanchan_stats(paipu, target_player))
        
    return pd.DataFrame(records), pd.DataFrame([hanchan_data])

def analyze_directory(directory, target_player, config):
    """分析整个目录的牌谱"""
    all_kyoku_dfs = []
    all_hanchan_dfs = []
    path = Path(resource_path(directory))
    
    for file_path in tqdm(list(path.glob('*.json')) + list(path.glob('*.txt')), desc='Processing'):
        try:
            kyoku_df, hanchan_df = process_paipu(file_path, target_player, config)
            if not kyoku_df.empty:
                all_kyoku_dfs.append(kyoku_df)
            if not hanchan_df.empty:
                all_hanchan_dfs.append(hanchan_df)
        except Exception as e:
            print(f"处理错误 {file_path}: {str(e)}")
    
    if not all_kyoku_dfs:
        return pd.DataFrame(), pd.DataFrame()
    if not all_hanchan_dfs:
        return pd.DataFrame(), pd.DataFrame()
    
    final_kyoku_df = pd.concat(all_kyoku_dfs, ignore_index=True)
    final_hanchan_df = pd.concat(all_hanchan_dfs, ignore_index=True)
    return final_kyoku_df, final_hanchan_df

def generate_statistics(final_kyoku_df, final_hanchan_df, target_player):
    """生成统计报告"""
    if final_kyoku_df.empty:
        print("无有效数据可生成报告")
        return pd.DataFrame()


    # 新增半庄统计
    hanchan_stats = {
        '有效牌谱数': final_hanchan_df['牌谱'].nunique(),  # 不同牌谱文件数量
        '有效小局数': final_kyoku_df.shape[0],        # 总对局数
        '平均顺位': final_hanchan_df['rank'].mean(),
        '平均得点': final_hanchan_df['delta'].mean(),
        '一位率': (final_hanchan_df['rank'] == 1).mean(),
        '二位率': (final_hanchan_df['rank'] == 2).mean(),
        '三位率': (final_hanchan_df['rank'] == 3).mean(),
        '四位率': (final_hanchan_df['rank'] == 4).mean(),
        '连对率': ((final_hanchan_df['rank'] == 1) | (final_hanchan_df['rank'] == 2)).mean(),
        '被飞率': final_hanchan_df['is_negative'].mean()
    }
    kyoku_stats = {
        '和了率': final_kyoku_df['和了'].mean(),
        '放铳率': final_kyoku_df['放铳'].mean(),
        '副露率': final_kyoku_df['副露'].mean(),
        '立直率': final_kyoku_df['立直'].mean(),
        '默听率': final_kyoku_df.loc[ final_kyoku_df['和了'], '默听' ].mean(),
        '和牌时立直率': final_kyoku_df.loc[final_kyoku_df['和了'], '立直'].mean(),
        '和牌时副露率': final_kyoku_df.loc[final_kyoku_df['和了'], '副露'].mean(),
        '和牌自摸率': final_kyoku_df.loc[final_kyoku_df['和了'], '自摸'].mean(),
        '平均和了打点': final_kyoku_df.loc[final_kyoku_df['和了'], '和了打点'].mean(),
        '平均和了巡目': final_kyoku_df.loc[final_kyoku_df['和了'], '和了巡目'].mean(),
        '立直先制率': final_kyoku_df.loc[final_kyoku_df['立直'], '立直先制'].mean(),
        '追立率': final_kyoku_df.loc[final_kyoku_df['立直'], '追立'].mean(),
        '立直后和牌率': final_kyoku_df.loc[final_kyoku_df['立直'], '和了'].mean(),
        '立直后放铳率': final_kyoku_df.loc[final_kyoku_df['立直'], '放铳'].mean(),
        '立直后流局率': final_kyoku_df.loc[final_kyoku_df['立直'], '流局'].mean(),
        '立直和牌打点': final_kyoku_df.loc[final_kyoku_df['立直'], '和了打点'].mean(),
        '立直和牌巡目': final_kyoku_df.loc[final_kyoku_df['立直'], '和了巡目'].mean(),
        '平均立直巡目': final_kyoku_df.loc[final_kyoku_df['立直'], '立直巡目'].mean(),
        '副露后和牌率': final_kyoku_df.loc[final_kyoku_df['副露'], '和了'].mean(),
        '副露后放铳率': final_kyoku_df.loc[final_kyoku_df['副露'], '放铳'].mean(),
        '副露后流局率': final_kyoku_df.loc[final_kyoku_df['副露'], '流局'].mean(),
        '副露和牌打点': final_kyoku_df.loc[final_kyoku_df['副露'], '和了打点'].mean(),
        '副露和牌巡目': final_kyoku_df.loc[final_kyoku_df['副露'], '和了巡目'].mean(),
        '平均放铳打点': abs(final_kyoku_df.loc[final_kyoku_df['放铳'], '放铳打点'].mean()),
        '放铳时立直率': final_kyoku_df.loc[final_kyoku_df['放铳'], '立直'].mean(),
        '放铳时副露率': final_kyoku_df.loc[final_kyoku_df['放铳'], '副露'].mean(),
        '放铳时门清率': (
                    (final_kyoku_df[final_kyoku_df['放铳']]['立直'] == False) & 
                    (final_kyoku_df[final_kyoku_df['放铳']]['副露'] == False)
                ).mean(),
        '流局率': final_kyoku_df['流局'].mean(),
        '流局听牌率': final_kyoku_df.loc[final_kyoku_df['流局'], '流局时听牌'].mean(),
        '流局平均得点': final_kyoku_df.loc[final_kyoku_df['流局'], '流局时得点'].mean(),
        '立直流局时听牌率': final_kyoku_df.loc[final_kyoku_df['流局'] & final_kyoku_df['立直'], '流局时听牌'].mean(),
        '副露流局时听牌率': final_kyoku_df.loc[final_kyoku_df['流局'] & final_kyoku_df['副露'], '流局时听牌'].mean(),
        '门清流局时听牌率': final_kyoku_df.loc[
                    final_kyoku_df['流局'] & 
                    (final_kyoku_df['立直'] == False) & 
                    (final_kyoku_df['副露'] == False), 
                    '流局时听牌'
                ].mean(),
    }
    # 四麻风格分析
    mahjong_analyzer = MahjongAnalyzer()
    data = {
        'horyu_rate': kyoku_stats['和了率']*100,
        'houju_rate': kyoku_stats['放铳率']*100,
        'furo_rate': kyoku_stats['副露率']*100,
        'riichi_rate': kyoku_stats['立直率']*100,
        'dama_rate': kyoku_stats['默听率']*100,
        'average_score': kyoku_stats['平均和了打点'],
        'avg_horyu_turn': kyoku_stats['平均和了巡目'],
        'avg_houju_score': kyoku_stats['平均放铳打点'],
        'ryukyoku_rate': kyoku_stats['流局听牌率']*100,
        'riichi_turn': kyoku_stats['平均立直巡目'],
        'riichi_first_rate': kyoku_stats['立直先制率']*100,
        'riichi_chase_rate': kyoku_stats['追立率']*100,
    }
    X, Y, style = mahjong_analyzer.analyze(data=data, output_filename=resource_path(f"{target_player}_风格分析.png"))
    print(f"成功生成风格分析图：{target_player}_风格分析.png")

    # 合并统计指标
    hanchan_stats.update(kyoku_stats)
    hanchan_stats.update({
        '风格分析结果': style,
    })

    # 格式处理：数值保留3位小数
    formatted_stats = pd.Series(hanchan_stats).to_frame('统计值')
    formatted_stats['统计值'] = formatted_stats['统计值'].apply(
        lambda x: round(x, 3) if isinstance(x, float) else x
    )

    # 生成Excel文件
    file_name = resource_path(f"{target_player}_统计报告.xlsx")
    try:
        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            # 主统计表
            formatted_stats.to_excel(
                writer, 
                sheet_name='综合统计',
                index=True,
                header=['统计值'],
                index_label='统计指标'
            )
            
            # 原始数据表（可选）
            final_kyoku_df.to_excel(
                writer,
                sheet_name='小局原始数据',
                index=False
            )
            # 原始数据表（可选）
            final_hanchan_df.to_excel(
                writer,
                sheet_name='半庄原始数据',
                index=False
            )
            
        print(f"成功生成统计报告：{target_player}_统计报告.xlsx")

        # 相关性热力图
        filtered_df = final_kyoku_df[['和了', '放铳', '副露', '立直', '默听', "和了打点", "和了巡目", "放铳打点","流局时听牌","流局时得点","立直先制","立直巡目","追立","自摸","流局"]]
        methods = [
            'pearson',   # 皮尔逊相关系数
            'spearman',   # 斯皮尔曼等级相关系数
            'kendall'  # 肯德尔秩相关系数
            ]
        for method in methods:
            try:
                # 计算相关系数
                correlation = filtered_df.corr(method=method)
                # 绘制热力图
                plt.figure(figsize=(10, 8))
                sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt=".2f")
                plt.title(f'{method}相关系数热力图')
                # 保存图片
                plt.tight_layout()
                save_path = resource_path(f"{target_player}_{method}相关系数热力图.png")
                plt.savefig(save_path, dpi=300, bbox_inches="tight")
                plt.close()  # 防止内存泄漏
                print(f"成功生成{method}相关系数热力图：{target_player}_{method}相关系数热力图.png")
            except Exception as e:
                print(f"生成{method}相关系数热力图失败：{str(e)}")


    except Exception as e:
        print(f"文件保存失败：{str(e)}")
    
    return formatted_stats


def process_hanchan_stats(json_data, target_player):
    """处理单个半庄的统计数据"""
    # 找到目标玩家的索引
    try:
        player_index = json_data['name'].index(target_player)
    except ValueError:
        return None

    # 提取终局点数 (sc数组中的偶数索引)
    scores = json_data['sc'][::2]  # [玩家0点数, 玩家1点数, 玩家2点数, 玩家3点数]
    target_score = scores[player_index]

    # 计算顺位
    sorted_scores = sorted(scores, reverse=True)
    rank = sorted_scores.index(target_score) + 1  # 顺位从1开始

    # 计算得点 (sc数组中的奇数索引)
    delta = json_data['sc'][player_index*2+1]

    return {
        'rank': rank,
        'score': target_score,
        'delta': delta,
        'is_negative': target_score < 0
    }


if __name__ == "__main__":
    # 加载配置文件
    config = load_config()

    # 下载牌谱
    process_paipu_file(config["filter"]["paipu_txt"], config["filter"]["players"])

    # 分析所有牌谱
    final_kyoku_df, final_hanchan_df = analyze_directory(f'./paipu_data/{config["filter"]["players"]}', config["filter"]["players"], config)
    
    # 生成统计报告
    if not final_kyoku_df.empty:
        report = generate_statistics(final_kyoku_df, final_hanchan_df, config["filter"]["players"])
        print("\n综合统计报告:")
        print(report)
    else:
        print("未找到符合条件的牌谱数据")

    print(f"统计报告已生成，请自行查看")
    input('按回车关闭')
