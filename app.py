from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from data_manager import LotteryDataManager

app = Flask(__name__)
CORS(app)

data_manager = LotteryDataManager()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>车牌摇号结果查询</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            max-width: 500px;
            width: 100%;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        input[type="text"], select {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
            background: white;
        }
        input[type="text"]:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        select {
            cursor: pointer;
            appearance: none;
            background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
            background-repeat: no-repeat;
            background-position: right 1rem center;
            background-size: 1em;
            padding-right: 3rem;
        }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        button:active {
            transform: translateY(0);
        }
        .result {
            margin-top: 25px;
            padding: 20px;
            border-radius: 10px;
            display: none;
        }
        .result.success {
            background: #d4edda;
            border: 2px solid #28a745;
            color: #155724;
        }
        .result.error {
            background: #f8d7da;
            border: 2px solid #dc3545;
            color: #721c24;
        }
        .result.show {
            display: block;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .result-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
        }
        .result-info {
            font-size: 14px;
            line-height: 1.8;
        }
        .result-info strong {
            color: #333;
        }
        .winner-card {
            background: rgba(255, 255, 255, 0.5);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
        }
        .winner-card:last-child {
            margin-bottom: 0;
        }
        .sample-codes {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            font-size: 12px;
            color: #666;
        }
        .sample-codes strong {
            color: #333;
        }
        .hint {
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚗 车牌摇号结果查询</h1>
        <p class="subtitle">请输入您的摇号编码查询中签结果</p>
        
        <form id="queryForm">
            <div class="form-group">
                <label for="lotteryRound">选择期数（可选）</label>
                <select id="lotteryRound">
                    <option value="">全部期数</option>
                </select>
                <p class="hint">如不选择，将查询所有期数</p>
            </div>
            <div class="form-group">
                <label for="lotteryCode">摇号编码</label>
                <input type="text" id="lotteryCode" placeholder="请输入摇号编码，如：2024001001" required>
            </div>
            <button type="submit">查询结果</button>
        </form>
        
        <div id="result" class="result"></div>
        
        <div class="sample-codes">
            <strong>测试用摇号编码：</strong><br>
            2024年第1期中签编码：2024001001、2024001002<br>
            2024年第2期中签编码：2024002001、2024002002<br>
            2024年第3期中签编码：2024003001<br>
            未中签编码可输入任意其他数字测试
        </div>
    </div>

    <script>
        async function loadRounds() {
            try {
                const response = await fetch('/api/rounds');
                const data = await response.json();
                if (data.success) {
                    const select = document.getElementById('lotteryRound');
                    data.rounds.forEach(round => {
                        const option = document.createElement('option');
                        option.value = round;
                        option.textContent = round;
                        select.appendChild(option);
                    });
                }
            } catch (error) {
                console.error('加载期数失败:', error);
            }
        }

        loadRounds();

        document.getElementById('queryForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const code = document.getElementById('lotteryCode').value.trim();
            const round = document.getElementById('lotteryRound').value;
            const resultDiv = document.getElementById('result');
            
            if (!code) {
                resultDiv.className = 'result error show';
                resultDiv.innerHTML = '<div class="result-title">❌ 请输入摇号编码</div>';
                return;
            }
            
            try {
                const requestData = { code: code };
                if (round) {
                    requestData.lottery_round = round;
                }
                
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    if (data.won) {
                        let html = '<div class="result-title">🎉 恭喜！您已中签</div>';
                        html += '<div class="result-info">';
                        
                        if (data.winners.length === 1) {
                            const info = data.winners[0];
                            html += `
                                <div class="winner-card">
                                    <p><strong>摇号编码：</strong>${info.code}</p>
                                    <p><strong>姓名：</strong>${info.name}</p>
                                    <p><strong>车牌号码：</strong>${info.plate_number}</p>
                                    <p><strong>摇号期数：</strong>${info.lottery_round}</p>
                                    <p><strong>中签日期：</strong>${info.win_date}</p>
                                </div>
                            `;
                        } else {
                            html += `<p>您在 <strong>${data.winners.length}</strong> 个期数中中签：</p>`;
                            data.winners.forEach((info, index) => {
                                html += `
                                    <div class="winner-card">
                                        <p><strong>第 ${index + 1} 条记录</strong></p>
                                        <p><strong>摇号编码：</strong>${info.code}</p>
                                        <p><strong>姓名：</strong>${info.name}</p>
                                        <p><strong>车牌号码：</strong>${info.plate_number}</p>
                                        <p><strong>摇号期数：</strong>${info.lottery_round}</p>
                                        <p><strong>中签日期：</strong>${info.win_date}</p>
                                    </div>
                                `;
                            });
                        }
                        
                        html += '</div>';
                        resultDiv.className = 'result success show';
                        resultDiv.innerHTML = html;
                    } else {
                        resultDiv.className = 'result error show';
                        resultDiv.innerHTML = `
                            <div class="result-title">😔 很遗憾，暂未中签</div>
                            <div class="result-info">
                                <p>摇号编码：<strong>${code}</strong></p>
                                ${round ? `<p>查询期数：<strong>${round}</strong></p>` : ''}
                                <p>请继续关注下期摇号结果</p>
                            </div>
                        `;
                    }
                } else {
                    resultDiv.className = 'result error show';
                    resultDiv.innerHTML = `<div class="result-title">❌ 查询失败</div><div class="result-info">${data.message}</div>`;
                }
            } catch (error) {
                resultDiv.className = 'result error show';
                resultDiv.innerHTML = `<div class="result-title">❌ 网络错误</div><div class="result-info">请稍后重试</div>`;
            }
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/rounds', methods=['GET'])
def get_rounds():
    try:
        rounds = data_manager.get_rounds()
        return jsonify({
            'success': True,
            'rounds': rounds
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/query', methods=['POST'])
def query():
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({
                'success': False,
                'message': '缺少摇号编码参数'
            }), 400

        code = data['code'].strip()
        if not code:
            return jsonify({
                'success': False,
                'message': '摇号编码不能为空'
            }), 400

        lottery_round = data.get('lottery_round', '').strip()
        if not lottery_round:
            lottery_round = None

        result = data_manager.query_detailed(code, lottery_round)

        return jsonify({
            'success': True,
            'won': result['won'],
            'code': result['code'],
            'lottery_round': result['lottery_round'],
            'count': result['count'],
            'winners': result['winners'],
            'is_duplicate_across_rounds': result['is_duplicate_across_rounds']
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/winners', methods=['GET'])
def get_all_winners():
    try:
        lottery_round = request.args.get('round', '').strip()
        if lottery_round:
            winners = data_manager.get_winners_by_round(lottery_round)
        else:
            winners = data_manager.get_all_winners()
        return jsonify({
            'success': True,
            'count': len(winners),
            'winners': winners
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/winners', methods=['POST'])
def add_winner():
    try:
        data = request.get_json()
        required_fields = ['code', 'name', 'plate_number', 'lottery_round', 'win_date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'缺少参数: {field}'
                }), 400

        is_duplicate = data_manager.check_duplicate(data['code'], data['lottery_round'])
        if is_duplicate:
            return jsonify({
                'success': False,
                'message': f'编码 {data["code"]} 在 {data["lottery_round"]} 中已存在，同一期编码必须唯一'
            }), 409

        success, message = data_manager.add_winner(
            code=data['code'],
            name=data['name'],
            plate_number=data['plate_number'],
            lottery_round=data['lottery_round'],
            win_date=data['win_date']
        )

        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/winners/<code>', methods=['DELETE'])
def delete_winner(code):
    try:
        data = request.get_json(silent=True) or {}
        lottery_round = data.get('lottery_round', '').strip()
        if not lottery_round:
            lottery_round = request.args.get('round', '').strip()
        if not lottery_round:
            lottery_round = None

        success, message = data_manager.remove_winner(code, lottery_round)
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/winners/batch', methods=['POST'])
def batch_add_winners():
    try:
        data = request.get_json()
        if not data or 'winners' not in data:
            return jsonify({
                'success': False,
                'message': '缺少 winners 参数'
            }), 400

        winners = data['winners']
        if not isinstance(winners, list):
            return jsonify({
                'success': False,
                'message': 'winners 必须是数组'
            }), 400

        skip_duplicates = data.get('skip_duplicates', True)

        result = data_manager.batch_add_winners(winners, skip_duplicates)

        status_code = 200 if result['success'] else 409
        return jsonify({
            'success': result['success'],
            'added': result['added'],
            'skipped': result['skipped'],
            'failed': result['failed'],
            'total': len(winners),
            'details': result['details']
        }), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        stats = data_manager.get_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


if __name__ == '__main__':
    print("🚗 车牌摇号结果查询服务启动中...")
    print("📋 服务地址: http://localhost:5000")
    print("🔍 查询接口: POST http://localhost:5000/api/query")
    print("📝 测试用中签编码: 2024001001, 2024001002, 2024002001, 2024002002, 2024003001")
    app.run(host='0.0.0.0', port=5000, debug=True)
