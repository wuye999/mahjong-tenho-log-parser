import json
import base64
from pathlib import Path
import pandas as pd

def generate_html_report(nickname, image_base64_dict, series_sections, output_path):
    """
    生成数据分析报告HTML文件
    
    参数：
    nickname: str - 用户昵称
    image_base64_dict: str - 包含图片base64的字典
    series_sections: list of tuples - 分段数据列表，格式为 (段落标题, pd.Series)
    output_path: str - 生成的HTML文件保存路径
    """
    buttons = []
    # 修改图片处理逻辑，读取图片并转换为base64
    for desc, image_base64 in image_base64_dict.items():
        uri = f"data:image/png;base64,{image_base64}"
        buttons.append((desc, uri))

    about_html = """
<button class="report-btn" style="background:#2196F3" onclick="showAbout()">关于项目</button>
"""

    # 修改按钮生成部分的代码顺序
    buttons_html = [
        '<button class="report-btn" onclick=\'showTable()\'>综合统计</button>'
    ]
    for desc, uri in buttons:
        btn = f'<button class="report-btn" onclick=\'showImage({json.dumps(uri)})\'>{desc}</button>'
        buttons_html.append(btn)
        
    # 最后添加关于项目按钮
    buttons_html.append(about_html)
    buttons_html = "\n".join(buttons_html)

    # # 处理统计数据
    # df = series_data.reset_index()
    # df.columns = ["统计项", "统计值"]
    # html_table = df.to_html(index=False, classes="stats-table", border=0)

    # 生成分段统计表格
    stats_sections = []
    for section_title, series_data in series_sections:
        df = series_data.reset_index()
        df.columns = ["统计项", "统计值"]
        html_table = df.to_html(index=False, classes="stats-table", border=0)
        section_html = f"""
        <div class="stats-section">
            <h3>{section_title}</h3>
            {html_table}
        </div>
        """
        stats_sections.append(section_html)
    
    # stats_table = "\n".join(stats_sections)
    # 包裹横向排列容器
    stats_table = f"""
    <div class="stats-container">
        {"".join(stats_sections)}
    </div>
    """

    # 在JavaScript部分增加showAbout函数
    about_content = """
<div class="about-container">
    <h2>天凤牌谱分析工具</h2>
    <div class="project-links">
        <a href="https://github.com/wuye999/mahjong-tenho-log-parser" target="_blank">
            <img src="https://img.shields.io/badge/GitHub-Repository-blue?logo=github" alt="GitHub仓库">
        </a>
        <a href="https://space.bilibili.com/108919422" target="_blank">
            <img src="https://img.shields.io/badge/B%E7%AB%99-作者主页-pink?logo=bilibili" alt="B站主页">
        </a>
    </div>
    
    <h3>🏆 项目简介</h3>
    <p>本工具提供天凤平台麻将数据自动化分析解决方案，支持从牌谱下载到多维数据分析的全流程处理，帮助玩家深度解析对战表现。</p>
    
    <h3>✨ 核心功能</h3>
    <ul class="feature-list">
        <li>📥 <strong>数据获取</strong> - 自动从tenhou.net下载原始牌谱JSON数据</li>
        <li>📊 <strong>数据分析</strong> - 生成包含20+统计指标的专业报告</li>
        <li>🎨 <strong>可视化呈现</strong> - 自动生成风格分析图、相关系数热力图、pt/rate趋势图表</li>
        <li>⏳ <strong>多维筛选</strong> - 支持按时间段、牌桌类型进行数据过滤</li>
    </ul>
</div>
"""
    
    # 构建HTML模板
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{nickname} 的统计报告</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f8f9fa;
        }}
        .header {{
            background: #ffffff;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }}
        .button-container {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin: 25px 0;
        }}
        .report-btn {{
            padding: 12px 28px;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            color: white;
            background: #4CAF50;
            transition: all 0.3s;
            font-size: 15px;
            font-weight: 500;
        }}
        .report-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76,175,80,0.3);
        }}
        #main-content {{
            margin-top: 25px;
            position: relative;
        }}
        .stats-wrapper {{
            position: relative;
            margin: 20px 0;
        }}
        .stats-container {{
            display: flex;
            gap: 35px;
            overflow-x: auto;
            padding: 25px 0;
            scrollbar-width: thin;
        }}
        .stats-container::after {{
            content: "";
            position: absolute;
            top: 0;
            right: 0;
            bottom: 0;
            width: 80px;
            background: linear-gradient(to right, rgba(255,255,255,0) 0%, #ffffff 90%);
            pointer-events: none;
        }}
        .stats-section {{
            flex: 0 0 auto;
            width: 380px;
            background: #fff;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.08);
            transition: transform 0.3s;
        }}
        .stats-section:hover {{
            transform: translateY(-3px);
        }}
        .stats-table {{
            width: 100%;
            margin-top: 18px;
            border-collapse: collapse;
        }}
        .stats-table th, .stats-table td {{
            padding: 14px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        .stats-table th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
        .hidden {{
            display: none;
        }}
        #aboutContent {{
            max-width: 850px;
            margin: 25px auto;
            padding: 35px;
            background: #fff;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            line-height: 1.7;
        }}
        .scroll-hint {{
            position: fixed;
            right: 30px;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(76,175,80,0.95);
            color: white;
            padding: 12px 25px;
            border-radius: 30px;
            font-size: 15px;
            display: flex;
            align-items: center;
            gap: 12px;
            animation: bounce 1.2s infinite;
            z-index: 1000;
            box-shadow: 0 5px 15px rgba(76,175,80,0.3);
            border: 2px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(3px);
        }}
        @keyframes bounce {{
            0%, 100% {{ transform: translateY(-50%) translateX(0); }}
            50% {{ transform: translateY(-50%) translateX(8px); }}
        }}
        .stats-container::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        .stats-container::-webkit-scrollbar-thumb {{
            background: #c1c1c1;
            border-radius: 4px;
        }}
        @media (max-width: 768px) {{
            .scroll-hint {{
                right: 15px;
                padding: 10px 20px;
                font-size: 14px;
            }}
            .scroll-hint::after {{
                font-size: 18px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 style="color: #2c3e50; margin-bottom: 15px;">{nickname} 的统计报告</h1>
        <div class="button-container">
            {buttons_html}
        </div>
    </div>
    
    <div id="main-content">
        <div id="tableContent" class="hidden">
            <div class="stats-wrapper">
                <div class="stats-container">
                    {"".join(stats_sections)}
                </div>
            </div>
        </div>
        <img id="dynamicImage" class="hidden" style="max-width:100%; border-radius:12px;">
        <div id="aboutContent" class="hidden">
            {about_content}
        </div>
    </div>

    <div class="scroll-hint">滑动查看完整数据</div>

    <script>
        // 滑动提示控制
        const scrollHint = document.querySelector('.scroll-hint');
        const statsContainer = document.querySelector('.stats-container');
        
        // 初始检测
        function updateScrollHint() {{
            const canScroll = statsContainer.scrollWidth > statsContainer.clientWidth;
            const scrollEnd = statsContainer.scrollLeft >= (statsContainer.scrollWidth - statsContainer.clientWidth - 50);
            
            scrollHint.style.display = canScroll && !scrollEnd ? 'flex' : 'none';
        }}
        
        // 滚动事件监听
        statsContainer.addEventListener('scroll', () => {{
            const scrollEnd = statsContainer.scrollLeft >= (statsContainer.scrollWidth - statsContainer.clientWidth - 50);
            scrollHint.style.opacity = scrollEnd ? '0' : '1';
            scrollHint.style.display = scrollEnd ? 'none' : 'flex';
        }});
        
        // 窗口大小变化监听
        window.addEventListener('resize', updateScrollHint);
        
        // 初始化
        updateScrollHint();
        
        // 按钮功能保持不变
        function showImage(uri) {{
            document.getElementById('tableContent').classList.add('hidden');
            document.getElementById('aboutContent').classList.add('hidden');
            const img = document.getElementById('dynamicImage');
            img.src = uri;
            img.classList.remove('hidden');
            scrollHint.style.display = 'none';
        }}
        
        function showTable() {{
            document.getElementById('dynamicImage').classList.add('hidden');
            document.getElementById('aboutContent').classList.add('hidden');
            document.getElementById('tableContent').classList.remove('hidden');
            statsContainer.scrollTo({{ left: 0, behavior: 'auto' }});
            updateScrollHint();
        }}
        
        function showAbout() {{
            document.getElementById('tableContent').classList.add('hidden');
            document.getElementById('dynamicImage').classList.add('hidden');
            document.getElementById('aboutContent').classList.remove('hidden');
            scrollHint.style.display = 'none';
        }}
    </script>
</body>
</html>"""

    # 保存HTML文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_template)

# 使用示例
if __name__ == "__main__":
    # 原始数据（示例）
    data = {
        "有效牌谱数": 89,
        "平均顺位": 2.3258,
        "一位率": 0.2697,
        "和了率": 0.2436,
        "立直率": 0.1683,
        "副露率": 0.3987,
        # 其他数据...
    }
    original_series = pd.Series(data)

    # 数据分段
    series_sections = [
        ("基础统计", original_series[["有效牌谱数", "平均顺位"]]),
        ("和牌分析", original_series[["一位率", "和了率"]]),
        ("战术特征", original_series[["立直率", "副露率"]])
    ]

    # 生成报告
    generate_html_report(
        nickname="示例用户",
        image_dir="./images",
        series_sections=series_sections,
        output_path="./analysis_report.html"
    )