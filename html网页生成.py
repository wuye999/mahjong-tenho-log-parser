import json
from pathlib import Path
import pandas as pd

def generate_html_report(nickname, image_dir, series_data, output_path):
    """
    生成数据分析报告HTML文件
    
    参数：
    nickname: str - 用户昵称
    image_dir: str - 包含图片的目录路径
    series_data: pd.Series - 统计数据的Series对象
    output_path: str - 生成的HTML文件保存路径
    """
    # 处理图片文件
    image_dir = Path(image_dir)
    if not image_dir.exists():
        raise FileNotFoundError(f"图片目录不存在: {image_dir}")
    
    image_files = list(image_dir.glob(f"{nickname}_*.png"))
    buttons = []
    for file in image_files:
        if "_" not in file.stem:
            continue
        desc = file.stem.split("_", 1)[1]
        uri = file.resolve().as_uri()
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

    # 处理统计数据
    df = series_data.reset_index()
    df.columns = ["统计项", "统计值"]
    html_table = df.to_html(index=False, classes="stats-table", border=0)

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
    # 在HTML模板的<style>区块末尾插入additional_css
    # 修改JavaScript部分添加：
    about_content=json.dumps(about_content)

    
    # 构建HTML模板
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{nickname}的数据分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; border-bottom: 2px solid #666; }}
        .report-btn {{
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            margin: 5px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
        .report-btn:hover {{ background: #45a049; }}
        #contentArea {{ margin-top: 20px; padding: 15px; border: 1px solid #ddd; }}
        .stats-table {{
            width: auto;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        .stats-table th, .stats-table td {{
            padding: 12px;
            border: 1px solid #ddd;
            text-align: left;
        }}
        .stats-table th {{ background-color: #f8f9fa; }}
        img {{ max-width: 100%; height: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}

        /* 关于项目样式 */
        .about-container {{
            max-width: 800px;
            margin: 0 auto;
            line-height: 1.6;
        }}

        .project-links {{
            margin: 20px 0;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}

        .feature-list {{
            padding-left: 20px;
            list-style-type: '✅ ';
        }}

        .feature-list li {{
            margin: 8px 0;
            padding-left: 8px;
        }}

        .analysis-dims {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }}

        .dim-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .dim-card h4 {{
            color: #2c3e50;
            margin-top: 0;
        }}

        @media (max-width: 600px) {{
            .analysis-dims {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <h1>{nickname}的数据分析报告</h1>
    <div id="buttonArea">
        {buttons_html}
    </div>
    <div id="contentArea"><!-- 内容展示区域 --></div>

    <script>
    // 保持原有showTable和showImage函数
        const aboutHtml = {about_content};

        function showAbout() {{
            document.getElementById('contentArea').innerHTML = aboutHtml;
        }}
        const tableHtml = {json.dumps(html_table)};
        
        function showTable() {{
            document.getElementById('contentArea').innerHTML = tableHtml;
        }}

        function showImage(imgUri) {{
            document.getElementById('contentArea').innerHTML = 
                `<img src="${{imgUri}}" alt="分析图表">`;
        }}
    </script>
</body>
</html>"""


    # 保存HTML文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_template)

# 使用示例（需要替换实际参数）
if __name__ == "__main__":
    # 示例数据（实际使用时替换为真实数据）
    example_series = pd.Series({
        "有效牌谱数": 25,
        "平均顺位": 2.08,
        "一位率": 0.36
    }, name="统计值")
    
    generate_html_report(
        nickname="鹿目円",
        image_dir="path/to/images",
        series_data=example_series,
        output_path="analysis_report.html"
    )
