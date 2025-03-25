# 首先确保已经安装了必要的库
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64


# 定义MahjongAnalyzer类（与之前相同）
class MahjongAnalyzer:
    def __init__(self):
        self.parameters = {
            'horyu_rate': 0,
            'houju_rate': 0,
            'furo_rate': 0,
            'riichi_rate': 0,
            'dama_rate': 0,
            'average_score': 0,
            'avg_horyu_turn': 0,
            'avg_houju_score': 0,
            'ryukyoku_rate': 0,
            'riichi_turn': 0,
            'riichi_first_rate': 0,
            'riichi_chase_rate': 0
        }
        self.bluedata_points = [
            {"label": "和了率", "x": -20.0, "y": 3.9},
            {"label": "放铳率", "x": -4.6, "y": 20.0},
            {"label": "副露率", "x": -20.0, "y": -7.2},
            {"label": "立直率", "x": -0.6, "y": 20.0},
            {"label": "默胡率", "x": 9.6, "y": -20.0},
            {"label": "平均打点", "x": 20.0, "y": -3.1},
            {"label": "平均和了巡数", "x": 20.0, "y": 14.4},
            {"label": "平均放铳打点", "x": -20.0, "y": 17.5},
            {"label": "流局时聴牌率", "x": -14.3, "y": 20.0},
            {"label": "立直巡目", "x": 20.0, "y": 15.5},
            {"label": "立直先制率", "x": -5.1, "y": -20.0},
            {"label": "追立率", "x": 14.4, "y": 20.0},
        ]
        self.blackdata_points = [
            {"label": "后手反击型", "x": 7, "y": 22},
            {"label": "门前打点型", "x": 17, "y": 1},
            {"label": "铁壁地藏型", "x": 7, "y": -25},
            {"label": "先手躱手型", "x": -15, "y": -25},
            {"label": "副露速度型", "x": -25, "y": -4},
            {"label": "全局参与型", "x": -15, "y": 22},
        ]
        plt.rcdefaults()  # 恢复所有配置到默认值
        plt.rcParams['font.family'] = 'SimHei'
        plt.rcParams['axes.unicode_minus'] = False  # 是否显示负号

    def standardize(self, value, mean, std_dev):
        return (value - mean) / std_dev

    def calculate_X(self, horyu_rate, houju_rate, furo_rate, riichi_rate, dama_rate,
                   average_score, avg_horyu_turn, avg_houju_score, ryuku_rate,
                   riichi_turn, riichi_first_rate, riichi_chase_rate):
        return (
            horyu_rate * -1.166081274 +
            houju_rate * -0.202381694 +
            furo_rate * -1.258740534 +
            riichi_rate * -0.013917045 +
            dama_rate * 0.708071254 +
            average_score * 1.249496931 +
            avg_horyu_turn * 0.73499073 +
            avg_houju_score * -0.231466343 +
            ryuku_rate * -0.585817047 +
            riichi_turn * 0.831715773 +
            riichi_first_rate * -0.612817769 +
            riichi_chase_rate * 0.546947012
        )

    def calculate_Y(self, horyu_rate, houju_rate, furo_rate, riichi_rate, dama_rate,
                   average_score, avg_horyu_turn, avg_houju_score, ryuku_rate,
                   riichi_turn, riichi_first_rate, riichi_chase_rate):
        return (
            horyu_rate * 0.22551386 +
            houju_rate * 0.889258806 +
            furo_rate * -0.453560713 +
            riichi_rate * 0.451204072 +
            dama_rate * -1.48123253 +
            average_score * -0.194681556 +
            avg_horyu_turn * 0.531014201 +
            avg_houju_score * 0.202878547 +
            ryuku_rate * 0.81983416 +
            riichi_turn * 0.644693651 +
            riichi_first_rate * -2.393675857 +
            riichi_chase_rate * 0.75875334
        )

    def get_style(self, X, Y):
        S = (X**2 + Y**2)**0.5
        if S > 12.71:
            T = "超重度"
        elif S > 8.89:
            T = "重度"
        elif S > 3.2:
            T = "中度"
        elif S > 1.47:
            T = "轻度"
        else:
            T = "中庸"

        A = Y / X if X != 0 else 0

        if A > 1:
            if X > 0:
                U = "后手反击型"
            else:
                U = "先手躱手型"
        elif A > -0.35:
            if X > 0:
                U = "门前打点型"
            else:
                U = "副露速度型"
        else:
            if X > 0:
                U = "铁壁地藏型"
            else:
                U = "全局参与型"
        return f"{T}{U}"

    def plot_result(self, X, Y, output_filename, style):
        plt.figure(figsize=(10, 10))
        origin_x = 0
        origin_y = 0
        scale = 1

        x = np.linspace(-30, 30, 100)
        y = x * 0
        plt.plot(x, y, color='black', linewidth=1)
        plt.plot(y, x, color='black', linewidth=1)

        plt.plot(x, x, color='green', linestyle='--')
        plt.plot(x, -0.35 * x, color='green', linestyle='--')
        plt.plot(x * 0, x, color='green', linestyle='--')

        for point in self.bluedata_points:
            plt.scatter(point['x'], point['y'], color='blue', s=50)
            plt.annotate(point['label'], (point['x'], point['y']), 
                        xytext=(point['x'] + 0.1, point['y'] + 0.1), 
                        fontsize=8)

        for point in self.blackdata_points:
            # plt.scatter(point['x'], point['y'], color='black', s=100)
            plt.annotate(point['label'], (point['x'], point['y']), 
                        xytext=(point['x'] + 0.1, point['y'] - 0.1),
                        fontsize=15, fontweight='bold')

        # 绘制当前点
        plt.scatter(X, Y, color='red', s=100, zorder=3)
        plt.text(-20, 28, f'坐标: ({X:.1f}, {Y:.1f})\n风格: {style}',
                    ha='left', va='bottom',
                    fontsize=12, color='red',
                  )

        plt.xlim(-27, 27)
        plt.ylim(-27, 27)
        plt.xticks(range(-25, 26, 5))
        plt.yticks(range(-25, 26, 5))
        plt.gca().grid(True, which="both", linestyle='--', alpha=0.5)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('麻将风格分析')
        # if output_filename:
        #     plt.savefig(output_filename, dpi=300)
        # plt.show()
        # 保存到内存缓冲区
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300)
        plt.close()  # 关闭图像，防止内存泄漏

        # 获取二进制数据
        img_bytes = img_buffer.getvalue()
        # 获取Base64编码数据
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        # 如果需要保存到文件
        if output_filename:
            with open(output_filename, 'wb') as f:
                f.write(img_bytes)

        return img_bytes, img_base64  # 返回二进制和Base64数据


    def analyze(self, **kwargs):
        data = kwargs.get('data', None)
        output_filename = kwargs.get('output_filename', "风格分析图.png")
        if not data:
            raise ValueError("未传入数据或数据不完整")

        required_keys = self.parameters.keys()
        for key in required_keys:
            if key not in data:
                raise ValueError(f"缺少参数: {key}")

        horyu_rate = data['horyu_rate'] / 100
        houju_rate = data['houju_rate'] / 100
        furo_rate = data['furo_rate'] / 100
        riichi_rate = data['riichi_rate'] / 100
        dama_rate = data['dama_rate'] / 100
        ryuku_rate = data['ryukyoku_rate'] / 100
        riichi_first_rate = data['riichi_first_rate'] / 100
        riichi_chase_rate = data['riichi_chase_rate'] / 100

        std_horyu = self.standardize(horyu_rate, 0.229400816, 0.01018886)
        std_houju = self.standardize(houju_rate, 0.11106952, 0.009595166)
        std_furo = self.standardize(furo_rate, 0.331713127, 0.037372193)
        std_riichi = self.standardize(riichi_rate, 0.182824374, 0.018407074)
        std_dama = self.standardize(dama_rate, 0.128029668, 0.029703506)
        std_average = self.standardize(data['average_score'], 6454.787778, 235.6563516)
        std_horyu_turn = self.standardize(data['avg_horyu_turn'], 12.12006667, 0.11553016)
        std_houju_score = self.standardize(data['avg_houju_score'], 5387.771667, 141.1658779)
        std_ryuku = self.standardize(ryuku_rate, 0.421591309, 0.04623791)
        std_riichi_turn = self.standardize(data['riichi_turn'], 9.298394589, 0.193397116)
        std_riichi_first = self.standardize(riichi_first_rate, 0.828159779, 0.021060104)
        std_riich_chase = self.standardize(riichi_chase_rate, 0.171840221, 0.021060104)

        X = self.calculate_X(std_horyu, std_houju, std_furo, std_riichi, std_dama,
                            std_average, std_horyu_turn, std_houju_score, std_ryuku,
                            std_riichi_turn, std_riichi_first, std_riich_chase)
        Y = self.calculate_Y(std_horyu, std_houju, std_furo, std_riichi, std_dama,
                            std_average, std_horyu_turn, std_houju_score, std_ryuku,
                            std_riichi_turn, std_riichi_first, std_riich_chase)

        style = self.get_style(X, Y)
        img_bytes, img_base64 = self.plot_result(X, Y, output_filename, style)
        return X, Y, style, img_bytes, img_base64


if __name__ == '__main__':
    # 使用示例：
    mahjong_analyzer = MahjongAnalyzer()

    data = {
        'horyu_rate': 27.7,
        'houju_rate': 12.3,
        'furo_rate': 40.4,
        'riichi_rate': 20,
        'dama_rate': 7.7,
        'average_score': 6443,
        'avg_horyu_turn': 11.231,
        'avg_houju_score': 4965,
        'ryukyoku_rate': 50,
        'riichi_turn': 7.681,
        'riichi_first_rate': 72.3,
        'riichi_chase_rate': 27.7
    }

    X, Y, style = mahjong_analyzer.analyze(data=data)

    print(f"X: {X:.2f}, Y: {Y:.2f}")
    print(f"风格分析结果：{style}")
