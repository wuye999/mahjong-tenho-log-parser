import matplotlib.pyplot as plt
import pandas as pd
import numpy as np



# 生成rate变化柱状图和折线图
def plot_rate_changes(
    df: pd.DataFrame,
    time_col: str = '对局时间',
    rate_col: str = 'rate变动',
    figsize: tuple = (18, 12),
    font_scale: float = 2.5,
    max_time_labels: int = 20,  # 新增参数控制最大时间标签数
    first_rate: int = 0,  # 新增参数，用于设置初始rate值
) -> plt.Figure:
    """
    绘制rate变动分析图（含智能标注）

    参数：
    ----------
    df : pandas.DataFrame
        需要可视化的数据表，必须包含时间列和rate变动列
    time_col : str, 可选（默认：'对局时间'）
        时间列的名称，该列应为可转换为datetime的字符串格式
    rate_col : str, 可选（默认：'rate变动'）
        rate变动值的列名称
    figsize : tuple, 可选（默认：(18, 12)）
        图表尺寸（宽，高）单位英寸
    font_scale : float, 可选（默认：1.2）
        字体缩放系数（1.0为基准大小）
    max_time_labels: int, 可选（默认：15）
        横轴时间标签的最大数量，超过此数量将自动调整标签密度

    返回：
    -------
    matplotlib.figure.Figure
        生成的图表对象，可用于保存或进一步修改

    功能说明：
    ----------
    1. 生成双图布局（上为柱状图，下为折线图）
    2. 柱状图显示单局rate变动，相同值仅标注首次出现
    3. 折线图显示累计rate趋势，标注最高/最低点
    4. 自适应横轴标签密度
    5. 自动处理时间格式和显示重叠

    示例：
    ----------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import matplotlib.pyplot as plt
    >>> from rate变化图生成 import plot_rate_changes

    >>> # 创建示例数据
    >>> data = [
        {'对局时间': '2023-01-01 14:00', 'rate变动': 60},
        {'对局时间': '2023-01-01 14:00', 'rate变动': 15},
        {'对局时间': '2023-01-02 09:00', 'rate变动': -30},
        {'对局时间': '2023-01-03 18:00', 'rate变动': 45}
    ]
    >>> df = pd.DataFrame(data)
    
    >>> # 生成图表
    >>> fig = plot_rate_changes(df)
    >>> plt.show()
    
    >>> # 保存图表
    >>> fig.savefig('rate_analysis.png', dpi=300, bbox_inches='tight')
    """
    plt.rcdefaults()  # 恢复所有配置到默认值
    # 预处理数据
    plot_df = df.copy()
    plot_df['_datetime'] = pd.to_datetime(plot_df[time_col])
    plot_df = plot_df.sort_values('_datetime').reset_index(drop=True)
    
    # 新增高度调整字段（仅用于可视化高度）
    plot_df['_rate_height'] = plot_df[rate_col].apply(lambda x: 0 if x == 0 else x)  # 新增行

    # 生成顺序索引和格式化时间标签
    plot_df['order'] = np.arange(len(plot_df))
      # 修改累计rate计算方式（关键修改处）
    plot_df['累计rate'] = first_rate + plot_df[rate_col].cumsum()  # 新增first_rate参数

    plot_df['date_label'] = plot_df['_datetime'].dt.strftime('%m-%d')  # 新列名称
     # 创建显示用标签（关键修改）
    plot_df['display_label'] = plot_df['date_label'].where(
        ~plot_df['date_label'].duplicated(),
        ''
    )   

    # 设置字体参数
    base_font = 10 * font_scale
    plt.rcParams.update({
        'font.size': base_font,
        'axes.titlesize': base_font + 2,
        'axes.labelsize': base_font + 1,
        'xtick.labelsize': base_font,
        'ytick.labelsize': base_font
    })

    # 设置样式兼容性
    def get_compatible_style():
        available = plt.style.available
        styles = ['seaborn-v0_8', 'seaborn', 'ggplot', 'classic']
        return next((s for s in styles if s in available), 'classic')
    
    plt.style.use(get_compatible_style())
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 创建画布和子图
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)

    # --- 柱状图（调整字体）---
    bar_width = 0.8
    # colors = ['#4CAF50' if x >=0 else '#F44336' for x in plot_df[rate_col]]
    # --- 颜色生成修改 ---
    colors = []
    for x in plot_df[rate_col]:  # 保持原始值判断逻辑
        if x > 0:
            colors.append('#4CAF50')
        elif x < 0:
            colors.append('#F44336')
        else:
            colors.append('#757575')  # 0值颜色
    # 修改bar调用使用_rate_height作为高度
    bars = ax1.bar(plot_df['order'], plot_df['_rate_height'],  # 修改为_rate_height
                   width=bar_width, color=colors, alpha=0.8)
    
    # --- 智能标注修改 ---
    # 过滤掉零值变动
    non_zero_df = plot_df[plot_df[rate_col] != 0]
    # --- 最终优化版标注代码 ---
    if not non_zero_df.empty:
        # 创建绝对值列用于排序
        non_zero_df = non_zero_df.assign(abs_rate=lambda x: x[rate_col].abs())
        
        # 动态调整标注数量（最大12个）
        max_annot = min(12, len(non_zero_df))
        sorted_df = non_zero_df.sort_values('abs_rate', ascending=False).head(max_annot)
        
        # 智能字体计算（优化版）
        fig_width_inch = figsize[0]
        base_font_size = max(8, min(14, 72 * fig_width_inch / (len(plot_df)*0.6)))
        
        # 标注样式设置
        bbox_props = dict(
            boxstyle="round,pad=0.2",  # 减小内边距
            facecolor="white",
            edgecolor="none",
            alpha=0.9
        )
        
        # 动态位置调整（基于柱子高度）
        for idx in sorted_df.index:
            bar = bars[idx]
            value = sorted_df.at[idx, rate_col]
            bar_height = bar.get_height()
            
            # 智能偏移计算（正负差异处理）
            if value > 0:
                offset = bar_height * 0.15  # 正数：标注在柱子顶部高度的15%处
                y_pos = bar_height - offset  # 向下移动贴近柱子
                va = 'top'  # 顶部对齐
            else:
                offset = abs(bar_height) * 0.15  # 负数：标注在柱子底部的15%处
                y_pos = bar_height + offset  # 向上移动贴近柱子
                va = 'bottom'  # 底部对齐
            
            # 边界保护（确保在可视区域内）
            y_min, y_max = ax1.get_ylim()
            if value > 0:
                y_pos = max(y_min + 0.05*(y_max-y_min), y_pos)  # 至少留出5%空间
            else:
                y_pos = min(y_max - 0.05*(y_max-y_min), y_pos)
            
            # 添加标注（优化位置参数）
            ax1.text(
                x=bar.get_x() + bar_width/2,
                y=y_pos,
                s=f"{int(value)}",
                ha='center',
                va=va,
                fontsize=base_font_size,
                bbox=bbox_props,
                zorder=10
            )

    # --- 保持其他代码不变 ---
    
    ax1.set_title(f'rate变动分析（共{len(plot_df)}局）', pad=20, fontsize=base_font+4)
    ax1.set_ylabel('rate变动值', labelpad=15, fontsize=base_font-3)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    ax1.set_xlim(-0.5, len(plot_df)-0.5)

    # --- 折线图（调整标注样式）---
    line = ax2.plot(plot_df['order'], plot_df['累计rate'], 
                    marker=None, markersize=8*font_scale, 
                    linestyle='-', linewidth=2*font_scale,
                    color='#2196F3', markerfacecolor='white')
    
    # 查找极值点
    max_rate = plot_df['累计rate'].max()
    min_rate = plot_df['累计rate'].min()
    max_indices = plot_df.index[plot_df['累计rate'] == max_rate].tolist()[0]
    min_indices = plot_df.index[plot_df['累计rate'] == min_rate].tolist()[0]
    # --- 折线图标注调整（关键修复）---

    # 计算数据范围用于动态调整标注位置
    rate_range = plot_df['累计rate'].max() - plot_df['累计rate'].min()
    vertical_offset = rate_range * 0.08  # 动态偏移量（原为固定百分比）

    # 标注最高点（使用动态偏移）
    ax2.annotate(f'峰值: {int(max_rate)}',
                xy=(max_indices, max_rate),
                xytext=(max_indices-0.5, max_rate + vertical_offset),  # 动态Y偏移
                arrowprops=dict(
                    arrowstyle='->',
                    color='red',
                    linewidth=1.5*font_scale,
                    shrinkA=0,
                    shrinkB=5
                ),
                # bbox=bbox_props,
                fontsize=base_font,
                color='red')

    # 标注最低点
    ax2.annotate(f'谷值: {int(min_rate)}',
                xy=(min_indices, min_rate),
                xytext=(min_indices-0.5, min_rate - vertical_offset),  # 动态Y偏移
                arrowprops=dict(
                    arrowstyle='->',
                    color='blue',
                    linewidth=1.5*font_scale,
                    shrinkA=0,
                    shrinkB=5
                ),
                # bbox=bbox_props,
                fontsize=base_font,
                color='blue')

    ax2.set_title('rate变动趋势', pad=20, fontsize=base_font+4)
    ax2.set_ylabel('当前rate值', labelpad=15, fontsize=base_font-3)
    ax2.grid(axis='both', linestyle='--', alpha=0.7)

    # --- 智能横轴标签 ---
    def smart_xticks(ax):
        """更新后的智能标签函数"""
        total = len(plot_df)
        
        if total <= max_time_labels:
            indices = plot_df['order']
            labels = plot_df['display_label']  # 使用处理后的标签
        else:
            indices = np.linspace(0, total-1, num=max_time_labels, dtype=int)
            labels = plot_df['display_label'].iloc[indices]  # 使用处理后的标签

        # 清理连续空白标签（新增逻辑）
        cleaned_labels = []
        prev_label = None
        for label in labels:
            if label == prev_label and label == '':
                cleaned_labels.append(None)  # 彻底隐藏连续空白
            else:
                cleaned_labels.append(label)
                prev_label = label

        # 设置最终标签
        ax.set_xticks(indices)
        ax.set_xticklabels(
            cleaned_labels,  # 使用清理后的标签
            rotation=45 if total > max_time_labels else 30,
            ha='right',
            fontsize=base_font-5
        )
        
    smart_xticks(ax1)
    # 应用设置到Y轴
    ax1.tick_params(axis='x', labelsize=base_font-5)
    ax2.tick_params(axis='x', labelsize=base_font-5)
    ax1.tick_params(axis='y', labelsize=base_font-5)
    ax2.tick_params(axis='y', labelsize=base_font-5)

    # 紧凑布局
    plt.tight_layout()
    plt.close()
    return fig

if __name__ == '__main__':

    # 创建测试数据
    data = [
        {'对局时间': '2023-01-01 14:00', 'rate变动': 0},
        {'对局时间': '2023-01-01 14:00', 'rate变动': 26.38},
        {'对局时间': '2023-01-02 09:00', 'rate变动': 8.63},
        {'对局时间': '2023-01-03 18:00', 'rate变动': -17.24},
        {'对局时间': '2023-01-04 12:00', 'rate变动': -8.02},
        {'对局时间': '2023-01-05 15:00', 'rate变动': 25.33},
    ]
    df = pd.DataFrame(data)

    # 生成图表
    fig = plot_rate_changes(df,rate_col='rate变动',first_rate=1800)

    # 显示图表
    plt.show()

    # 保存为高清图片
    # fig.savefig('large_font_analysis.png', dpi=300, bbox_inches='tight')
