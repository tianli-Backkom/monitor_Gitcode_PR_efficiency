#!/usr/bin/env python3
import json
import os
from datetime import datetime, timedelta

def generate_pr_details_html(pr_details):
    """生成PR详情HTML"""
    if not pr_details:
        return '<div style="text-align: center; color: #666; padding: 40px;">暂无数据</div>'
    
    html = ''
    for pr in pr_details[:20]:  # 只显示前20个
        html += f"""
        <div class="pr-item">
            <div class="pr-header">
                <span class="pr-number">#{pr['number']}</span>
                <span class="duration-badge">{pr['duration_days']:.1f}天</span>
            </div>
            <div class="pr-title">{pr['title'][:80]}{'...' if len(pr['title']) > 80 else ''}</div>
            <div class="pr-meta">
                <span>创建: {pr['created_at'][:10]}</span>
                <span>合入: {pr['merged_at'][:10]}</span>
                <span>耗时: {pr['duration_hours']:.1f}小时</span>
            </div>
        </div>
        """
    return html

def generate_daily_chart_data(daily_submissions, daily_failed_submissions=None):
    """生成每日提交折线图数据"""
    if not daily_submissions:
        return {
            'labels': ['无数据'],
            'total_values': [0],
            'failed_values': [0] if daily_failed_submissions else [0]
        }
    
    # 获取最近14天的日期
    today = datetime.now().date()
    date_list = []
    total_value_list = []
    failed_value_list = []
    
    for i in range(14):
        date = today - timedelta(days=13-i)  # 从13天前到今天
        date_str = date.strftime('%Y-%m-%d')
        date_list.append(date.strftime('%m-%d'))  # 显示格式为 MM-DD
        total_value_list.append(daily_submissions.get(date_str, 0))
        if daily_failed_submissions:
            failed_value_list.append(daily_failed_submissions.get(date_str, 0))
        else:
            failed_value_list.append(0)
    
    return {
        'labels': date_list,
        'total_values': total_value_list,
        'failed_values': failed_value_list
    }

def generate_pr_dashboard():
    """
    基于PR分析数据生成HTML看板
    """
    try:
        # 读取PR分析数据
        with open('D:\\code\\monitor_Gitcode_PR_efficiency\\triton_ascend_prs_analysis.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        merged_analysis = data['recent_merged_prs_analysis']
        
        # 准备统计数据
        stats = {
            'repository': data['repository'],
            'total_open_prs': data['total_open_prs'],
            'recent_submitted_count': len(data['recent_submitted_prs']),
            'recent_merged_count': merged_analysis['count'],
            'avg_duration': merged_analysis['average_duration_days'],
            'min_duration': merged_analysis['min_duration_days'],
            'max_duration': merged_analysis['max_duration_days'],
            'daily_submissions': data['daily_submissions'],
            'daily_failed_submissions': data.get('daily_failed_submissions', {})
        }
        
        # 计算失败PR统计
        total_recent_failed = sum(stats['daily_failed_submissions'].values()) if stats['daily_failed_submissions'] else 0
        stats['total_recent_failed'] = total_recent_failed
        stats['failure_rate'] = round((total_recent_failed / stats['recent_submitted_count'] * 100), 1) if stats['recent_submitted_count'] > 0 else 0
        
        # 生成HTML内容
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Triton Ascend PR效率看板</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }}
        
        .stat-title {{
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-unit {{
            font-size: 0.9rem;
            color: #888;
        }}
        
        .open-prs {{ color: #e74c3c; }}
        .submitted-prs {{ color: #3498db; }}
        .merged-prs {{ color: #27ae60; }}
        .failed-prs {{ color: #e74c3c; }}
        .avg-duration {{ color: #f39c12; }}
        
        .section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .section-title {{
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }}
        
        .pr-list {{
            max-height: 600px;
            overflow-y: auto;
        }}
        
        .pr-item {{
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            transition: all 0.3s ease;
        }}
        
        .pr-item:hover {{
            border-color: #667eea;
            box-shadow: 0 2px 10px rgba(102, 126, 234, 0.1);
        }}
        
        .pr-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        
        .pr-number {{
            font-weight: bold;
            color: #667eea;
            font-size: 1.1rem;
        }}
        
        .pr-title {{
            color: #333;
            font-weight: 500;
            margin-bottom: 5px;
        }}
        
        .pr-meta {{
            font-size: 0.85rem;
            color: #666;
            display: flex;
            gap: 15px;
        }}
        
        .duration-badge {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        

        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.8;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2rem; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
            .stat-card {{ padding: 20px; }}
            .stat-value {{ font-size: 2rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Triton Ascend PR效率看板</h1>
            <p>实时监控Pull Request提交与合入效率</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-title">待合入PR</div>
                <div class="stat-value open-prs">{stats['total_open_prs']}</div>
                <div class="stat-unit">个PR等待处理</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-title">近7天提交</div>
                <div class="stat-value submitted-prs">{stats['recent_submitted_count']}</div>
                <div class="stat-unit">个新PR</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-title">近7天合入</div>
                <div class="stat-value merged-prs">{stats['recent_merged_count']}</div>
                <div class="stat-unit">个PR已合入</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-title">近7天失败</div>
                <div class="stat-value failed-prs">{stats['total_recent_failed']}</div>
                <div class="stat-unit">个PR失败 (失败率{stats['failure_rate']}%)</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-title">平均合入时长</div>
                <div class="stat-value avg-duration">{stats['avg_duration']:.1f}</div>
                <div class="stat-unit">天 ({stats['avg_duration']*24:.1f}小时)</div>
            </div>
        </div>
        

        
        <div class="section">
            <h2 class="section-title">📈 近两周每日PR提交活跃度</h2>
            <div style="height: 400px; position: relative;">
                <canvas id="dailyChart"></canvas>
            </div>
            <div style="text-align: center; margin-top: 15px; color: #666; font-size: 0.9rem;">
                横轴：日期 | 纵轴：PR提交数量 | 总计: {sum(stats['daily_submissions'].values())} 个PR，失败: {sum(stats['daily_failed_submissions'].values())} 个
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">⚡ 近期合入PR详情</h2>
            <div class="pr-list">
                {generate_pr_details_html(merged_analysis['pr_details'])}
            </div>
        </div>
        
        <div class="footer">
            <p>数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>基于Gitcode API数据生成</p>
        </div>
    </div>
    
    <script>
        // 添加一些交互效果
        document.querySelectorAll('.stat-card').forEach(card => {{
            card.addEventListener('mouseenter', function() {{
                this.style.transform = 'translateY(-5px) scale(1.02)';
            }});
            
            card.addEventListener('mouseleave', function() {{
                this.style.transform = 'translateY(0) scale(1)';
            }});
        }});
        
        window.addEventListener('load', function() {{
            initDailyChart();
        }});
        
        function initDailyChart() {{
            const ctx = document.getElementById('dailyChart');
            if (!ctx) return;
            
            // 准备图表数据
            const chartData = {json.dumps(generate_daily_chart_data(stats['daily_submissions'], stats['daily_failed_submissions']))};
            const dailyData = {{
                labels: chartData.labels,
                totalValues: chartData.total_values,
                failedValues: chartData.failed_values
            }};
            
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: dailyData.labels,
                    datasets: [{{
                        label: 'PR提交总数',
                        data: dailyData.totalValues,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#667eea',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 5,
                        pointHoverRadius: 8
                    }}, {{
                        label: '失败PR数量',
                        data: dailyData.failedValues,
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#e74c3c',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 5,
                        pointHoverRadius: 8
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            display: false
                        }},
                        tooltip: {{
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#fff',
                            bodyColor: '#fff',
                            borderColor: '#667eea',
                            borderWidth: 1,
                            callbacks: {{
                                title: function(context) {{
                                    return '日期: ' + context[0].label;
                                }},
                                label: function(context) {{
                                    return '提交数量: ' + context.parsed.y + ' 个PR';
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            display: true,
                            title: {{
                                display: true,
                                text: '日期',
                                color: '#666',
                                font: {{
                                    size: 12,
                                    weight: 'bold'
                                }}
                            }},
                            grid: {{
                                display: true,
                                color: 'rgba(0, 0, 0, 0.1)'
                            }},
                            ticks: {{
                                color: '#666',
                                maxRotation: 45,
                                font: {{
                                    size: 10
                                }}
                            }}
                        }},
                        y: {{
                            display: true,
                            title: {{
                                display: true,
                                text: 'PR提交数量',
                                color: '#666',
                                font: {{
                                    size: 12,
                                    weight: 'bold'
                                }}
                            }},
                            beginAtZero: true,
                            grid: {{
                                display: true,
                                color: 'rgba(0, 0, 0, 0.1)'
                            }},
                            ticks: {{
                                color: '#666',
                                font: {{
                                    size: 10
                                }},
                                stepSize: 1
                            }}
                        }}
                    }},
                    elements: {{
                        point: {{
                            hoverBackgroundColor: '#667eea'
                        }}
                    }}
                }}
            }});
        }}
    </script>
</body>
</html>"""
        
        # 生成PR详情HTML
        def generate_pr_details(pr_details):
            if not pr_details:
                return '<div style="text-align: center; color: #666; padding: 40px;">暂无数据</div>'
            
            html = ''
            for pr in pr_details[:20]:  # 只显示前20个
                html += f"""
                <div class="pr-item">
                    <div class="pr-header">
                        <span class="pr-number">#{pr['number']}</span>
                        <span class="duration-badge">{pr['duration_days']:.1f}天</span>
                    </div>
                    <div class="pr-title">{pr['title'][:80]}{'...' if len(pr['title']) > 80 else ''}</div>
                    <div class="pr-meta">
                        <span>创建: {pr['created_at'][:10]}</span>
                        <span>合入: {pr['merged_at'][:10]}</span>
                        <span>耗时: {pr['duration_hours']:.1f}小时</span>
                    </div>
                </div>
                """
            return html
        
        return html_content
        
    except Exception as e:
        return f"<h1>错误</h1><p>生成看板时出错: {e}</p>"

def main():
    # 生成HTML看板
    html_content = generate_pr_dashboard()
    
    # 保存到文件
    output_file = 'triton_pr_dashboard.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[成功] PR效率看板已生成: {output_file}")
    print(f"[文件] 打开文件: {os.path.abspath(output_file)}")
    print(f"[浏览器] 在浏览器中打开该文件即可查看看板")

if __name__ == '__main__':
    main()