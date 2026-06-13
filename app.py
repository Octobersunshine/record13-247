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
            padding: 20px;
        }
        .wrapper {
            max-width: 900px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
        }
        @media (max-width: 768px) {
            .wrapper {
                grid-template-columns: 1fr;
            }
        }
        .card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 30px;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 24px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 25px;
            font-size: 13px;
        }
        .form-group {
            margin-bottom: 18px;
        }
        label {
            display: block;
            margin-bottom: 6px;
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }
        input[type="text"], select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
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
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 15px;
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
            margin-top: 20px;
            padding: 15px;
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
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 12px;
        }
        .result-info {
            font-size: 13px;
            line-height: 1.8;
        }
        .result-info strong {
            color: #333;
        }
        .winner-card {
            background: rgba(255, 255, 255, 0.5);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
        }
        .winner-card:last-child {
            margin-bottom: 0;
        }
        .sample-codes {
            margin-top: 15px;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 8px;
            font-size: 11px;
            color: #666;
        }
        .sample-codes strong {
            color: #333;
        }
        .hint {
            font-size: 11px;
            color: #999;
            margin-top: 4px;
        }
        .stats-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #f0f0f0;
        }
        .stats-header h2 {
            font-size: 20px;
            color: #333;
        }
        .stats-header .icon {
            font-size: 24px;
        }
        .summary-cards {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 20px;
        }
        .summary-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
        }
        .summary-card.primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .summary-card.success {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .summary-card.warning {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        .summary-card.info {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        .summary-value {
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .summary-label {
            font-size: 11px;
            opacity: 0.9;
        }
        .trend-box {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 18px;
            font-size: 12px;
        }
        .trend-item {
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
        }
        .trend-label {
            color: #666;
        }
        .trend-value {
            font-weight: 600;
            color: #333;
        }
        .trend-value.hard {
            color: #dc3545;
        }
        .trend-value.easy {
            color: #28a745;
        }
        .rounds-list {
            max-height: 280px;
            overflow-y: auto;
        }
        .round-item {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 10px;
            transition: box-shadow 0.2s;
        }
        .round-item:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        .round-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        .round-name {
            font-weight: 700;
            color: #333;
            font-size: 14px;
        }
        .rate-badge {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        }
        .rate-badge.high {
            background: #d4edda;
            color: #155724;
        }
        .rate-badge.medium {
            background: #fff3cd;
            color: #856404;
        }
        .rate-badge.low {
            background: #f8d7da;
            color: #721c24;
        }
        .round-stats {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 8px;
            font-size: 11px;
        }
        .round-stat {
            text-align: center;
            padding: 6px;
            background: #f8f9fa;
            border-radius: 6px;
        }
        .round-stat-value {
            font-weight: 700;
            color: #333;
            font-size: 13px;
            display: block;
        }
        .round-stat-label {
            color: #888;
            font-size: 10px;
        }
        .round-desc {
            margin-top: 8px;
            font-size: 11px;
            color: #888;
            font-style: italic;
        }
        .round-progress {
            margin-top: 8px;
            height: 6px;
            background: #e9ecef;
            border-radius: 3px;
            overflow: hidden;
        }
        .round-progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 3px;
        }
        .page-title {
            grid-column: 1 / -1;
            text-align: center;
            color: white;
            padding: 10px 0;
        }
        .page-title h1 {
            color: white;
            font-size: 32px;
            margin-bottom: 8px;
        }
        .page-title p {
            color: rgba(255, 255, 255, 0.85);
            font-size: 14px;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #999;
            font-size: 13px;
        }
        .loading::after {
            content: '...';
            animation: dots 1.5s steps(4, end) infinite;
        }
        @keyframes dots {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60%, 100% { content: '...'; }
        }
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="page-title">
            <h1>🚗 车牌摇号结果查询系统</h1>
            <p>查询中签结果 · 查看历史中签率统计</p>
        </div>

        <div class="card">
            <h1>🔍 摇号结果查询</h1>
            <p class="subtitle">输入摇号编码查询是否中签</p>
            
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
                2024年第1期：2024001001、2024001002<br>
                2024年第2期：2024002001、2024002002<br>
                2024年第3期：2024003001
            </div>
        </div>

        <div class="card">
            <div class="stats-header">
                <h2>📊 历史中签率统计</h2>
                <span class="icon">📈</span>
            </div>

            <div id="statsLoading" class="loading">加载统计数据</div>

            <div id="statsContent" style="display: none;">
                <div class="summary-cards">
                    <div class="summary-card info">
                        <div class="summary-value" id="totalRounds">0</div>
                        <div class="summary-label">总期数</div>
                    </div>
                    <div class="summary-card primary">
                        <div class="summary-value" id="totalApplicants">0</div>
                        <div class="summary-label">累计申请人数</div>
                    </div>
                    <div class="summary-card success">
                        <div class="summary-value" id="totalQuota">0</div>
                        <div class="summary-label">累计指标数</div>
                    </div>
                    <div class="summary-card warning">
                        <div class="summary-value" id="overallRate">0%</div>
                        <div class="summary-label">综合中签率</div>
                    </div>
                </div>

                <div class="trend-box">
                    <div class="trend-item">
                        <span class="trend-label">🏆 最难中签期</span>
                        <span class="trend-value hard" id="hardestRound">-</span>
                    </div>
                    <div class="trend-item">
                        <span class="trend-label">🎯 最易中签期</span>
                        <span class="trend-value easy" id="easiestRound">-</span>
                    </div>
                    <div class="trend-item">
                        <span class="trend-label">📐 平均中签比例</span>
                        <span class="trend-value" id="avgRatio">-</span>
                    </div>
                </div>

                <label style="font-size: 13px; font-weight: 600; color: #333; margin-bottom: 10px; display: block;">
                    📋 各期详情（按中签率从低到高）
                </label>
                <div class="rounds-list" id="roundsList"></div>
            </div>
        </div>
    </div>

    <script>
        function formatNumber(num) {
            if (num === null || num === undefined) return '-';
            return num.toLocaleString('zh-CN');
        }

        function getRateClass(rate) {
            if (rate >= 1) return 'high';
            if (rate >= 0.1) return 'medium';
            return 'low';
        }

        function calculateBarWidth(rate, maxRate) {
            if (maxRate <= 0) return 0;
            return Math.min(100, (rate / maxRate) * 100);
        }

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

        async function loadRoundStats() {
            const loadingEl = document.getElementById('statsLoading');
            const contentEl = document.getElementById('statsContent');

            try {
                const response = await fetch('/api/round-stats');
                const data = await response.json();

                if (data.success) {
                    loadingEl.style.display = 'none';
                    contentEl.style.display = 'block';

                    const summary = data.summary;
                    document.getElementById('totalRounds').textContent = formatNumber(summary.total_rounds);
                    document.getElementById('totalApplicants').textContent = formatNumber(summary.total_applicants);
                    document.getElementById('totalQuota').textContent = formatNumber(summary.total_quota);
                    document.getElementById('overallRate').textContent = summary.overall_win_rate.rate_percent + '%';

                    if (data.trend.hardest_round) {
                        document.getElementById('hardestRound').textContent = 
                            data.trend.hardest_round.round_name + 
                            ' (' + data.trend.hardest_round.win_rate.rate_percent + '%)';
                    }
                    if (data.trend.easiest_round) {
                        document.getElementById('easiestRound').textContent = 
                            data.trend.easiest_round.round_name + 
                            ' (' + data.trend.easiest_round.win_rate.rate_percent + '%)';
                    }
                    document.getElementById('avgRatio').textContent = '1 : ' + summary.overall_win_rate.one_in_n;

                    const maxRate = Math.max(...data.rounds.map(r => r.win_rate.rate_percent));
                    const listEl = document.getElementById('roundsList');
                    listEl.innerHTML = data.rounds.map(round => {
                        const rateClass = getRateClass(round.win_rate.rate_percent);
                        const barWidth = calculateBarWidth(round.win_rate.rate_percent, maxRate);
                        return `
                            <div class="round-item">
                                <div class="round-top">
                                    <span class="round-name">${round.round_name}</span>
                                    <span class="rate-badge ${rateClass}">
                                        中签率 ${round.win_rate.rate_percent}%
                                    </span>
                                </div>
                                <div class="round-stats">
                                    <div class="round-stat">
                                        <span class="round-stat-value">${formatNumber(round.applicant_count)}</span>
                                        <span class="round-stat-label">申请人数</span>
                                    </div>
                                    <div class="round-stat">
                                        <span class="round-stat-value">${formatNumber(round.quota_count)}</span>
                                        <span class="round-stat-label">指标数</span>
                                    </div>
                                    <div class="round-stat">
                                        <span class="round-stat-value">1/${round.win_rate.one_in_n}</span>
                                        <span class="round-stat-label">中签比例</span>
                                    </div>
                                </div>
                                <div class="round-progress">
                                    <div class="round-progress-bar" style="width: ${barWidth}%;"></div>
                                </div>
                                ${round.description ? `<div class="round-desc">📝 ${round.description}</div>` : ''}
                            </div>
                        `;
                    }).join('');
                }
            } catch (error) {
                console.error('加载统计数据失败:', error);
                loadingEl.innerHTML = '<span style="color: #dc3545;">加载失败，请刷新重试</span>';
            }
        }

        loadRounds();
        loadRoundStats();

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
                        if (data.is_duplicate_across_rounds) {
                            html += '<div style="font-size: 12px; margin-bottom: 10px; padding: 6px 10px; background: rgba(255,255,255,0.5); border-radius: 6px;">⚠️ 提示：该编码在多个期数中签</div>';
                        }
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


@app.route('/api/round-stats', methods=['GET'])
def get_round_stats():
    try:
        round_name = request.args.get('round', '').strip()
        if not round_name:
            round_name = None

        result = data_manager.get_round_stats(round_name)
        if not result.get("success", True):
            return jsonify(result), 404
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/round-meta', methods=['GET'])
def get_round_meta():
    try:
        round_name = request.args.get('round', '').strip()
        if not round_name:
            round_name = None

        meta = data_manager.get_round_meta(round_name)
        return jsonify({
            'success': True,
            'meta': meta
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/round-meta', methods=['POST'])
def set_round_meta():
    try:
        data = request.get_json()
        required_fields = ['round_name', 'applicant_count', 'quota_count']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'缺少参数: {field}'
                }), 400

        round_name = data['round_name'].strip()
        try:
            applicant_count = int(data['applicant_count'])
            quota_count = int(data['quota_count'])
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': '申请人数和指标数必须是整数'
            }), 400

        description = data.get('description', '').strip()

        success, message = data_manager.set_round_meta(
            round_name=round_name,
            applicant_count=applicant_count,
            quota_count=quota_count,
            description=description
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


@app.route('/api/rounds/<round_name>', methods=['DELETE'])
def delete_round(round_name):
    try:
        success, message = data_manager.delete_round(round_name)
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


if __name__ == '__main__':
    print("🚗 车牌摇号结果查询服务启动中...")
    print("📋 服务地址: http://localhost:5000")
    print("🔍 查询接口: POST http://localhost:5000/api/query")
    print("📊 中签率统计: GET http://localhost:5000/api/round-stats")
    print("📝 测试用中签编码: 2024001001, 2024001002, 2024002001, 2024002002, 2024003001")
    app.run(host='0.0.0.0', port=5000, debug=True)
