# 🚀 Gitcode PR效率监控看板

一个专业的Gitcode PR（Pull Request）效率监控和分析系统，帮助团队实时跟踪和优化代码评审流程。

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## ✨ 核心功能

### 📊 数据收集与分析
- **Gitcode API集成**：自动获取Ascend/triton-ascend仓库PR数据
- **实时统计分析**：PR提交数量、合入时长、失败率等关键指标
- **趋势分析**：近两周PR每日提交活跃度图表
- **效率评估**：平均合入时长、合入效率等KPI监控

### 🎨 交互式看板
- **响应式设计**：支持桌面端和移动端访问
- **实时图表**：基于Chart.js的动态数据可视化
- **详细数据**：近期合入PR详情、失败PR统计
- **进度指标**：直观的进度条和效率评估

### 🔄 自动化工具
- **一键更新**：`refresh_dashboard.py` 快速刷新所有数据
- **数据验证**：`verify_dashboard.py` 确保数据完整性
- **编码兼容**：自动处理多种编码格式（UTF-8/GBK等）

## 🛠 安装与使用

### 环境要求
- Python 3.7+
- 网络连接（访问Gitcode API）
- 有效的Gitcode访问令牌

### 快速开始

1. **克隆项目**
```bash
git clone https://github.com/tianli-Backkom/monitor_Gitcode_PR_efficiency.git
cd monitor_Gitcode_PR_efficiency
```

2. **安装依赖**
```bash
pip install requests python-dateutil
```

3. **配置访问令牌**
编辑 `monitor.py` 文件，设置您的Gitcode访问令牌：
```python
ACCESS_TOKEN = "your_gitcode_access_token_here"
```

4. **运行数据收集**
```bash
python monitor.py
```

5. **生成看板**
```bash
python pr_dashboard.py
```

6. **一键更新（推荐）**
```bash
python refresh_dashboard.py
```

## 📁 项目结构

```
monitor_Gitcode_PR_efficiency/
├── monitor.py                 # 核心数据收集模块
│   ├── get_all_pull_requests()    # Gitcode API集成
│   └── analyze_pr_data()          # 数据分析算法
├── pr_dashboard.py            # 看板生成器
│   ├── generate_pr_dashboard()    # HTML生成引擎
│   └── generate_daily_chart_data() # 图表数据处理
├── refresh_dashboard.py       # 一键更新脚本
│   ├── run_command()              # 编码兼容命令执行
│   └── check_dependencies()       # 环境检查
├── verify_dashboard.py        # 结果验证工具
├── README.md                  # 项目文档
└── generated_files/
    ├── triton_ascend_prs_analysis.json  # 原始数据
    └── triton_pr_dashboard.html         # 可视化看板
```

## 📈 数据指标说明

### 核心统计
- **待合入PR**：当前状态为`open`的PR数量
- **近7天提交**：过去7天内创建的PR总数
- **近7天合入**：过去7天内合并的PR数量
- **近7天失败**：带有失败标签的PR数量
- **平均合入时长**：已合入PR的平均处理时间

### 分析维度
- **时间范围**：支持7天、14天等自定义时间窗口
- **PR状态**：open/closed/merged状态分析
- **失败识别**：基于标签（sc-fail, ci-pipeline-failed）的失败PR检测
- **趋势分析**：每日PR提交量变化趋势

## 🎯 使用场景

### 开发团队
- 监控代码评审效率
- 识别PR处理瓶颈
- 优化开发流程

### 项目管理
- 跟踪项目进展
- 评估团队效率
- 制定改进计划

### 技术决策
- 数据驱动的流程优化
- 资源分配参考
- 质量标准制定

## 🔧 高级配置

### 自定义仓库监控
修改 `monitor.py` 中的仓库配置：
```python
# 监控其他仓库
OWNER = "your-organization"
REPO = "your-repo"
```

### 时间窗口调整
在 `analyze_pr_data()` 函数中修改分析周期：
```python
# 调整为14天分析周期
fourteen_days_ago = now - timedelta(days=14)
```

### 失败标签配置
自定义失败PR识别标签：
```python
def is_failed_pr(pr):
    failed_labels = ['sc-fail', 'ci-pipeline-failed', 'build-failed']
    # 您的自定义逻辑
```

## 📊 看板预览

生成的HTML看板包含：
- **统计卡片**：关键指标的直观展示
- **进度条**：效率和速度的可视化
- **趋势图**：近两周PR活跃度分析
- **详情列表**：具体PR的处理详情

## 🛡️ 错误处理

### 编码兼容性
- 自动检测和转换多种编码格式
- UnicodeDecodeError智能处理
- Windows/Linux跨平台兼容

### API限流
- 请求频率控制
- 自动重试机制
- 优雅降级处理

### 数据验证
- 完整性检查
- 格式验证
- 异常数据过滤

## 🚀 性能优化

- **分页处理**：支持大量PR数据的分页获取
- **缓存机制**：避免重复API调用
- **异步处理**：非阻塞的数据收集
- **内存优化**：大数据集的流式处理

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📝 更新日志

### v1.0.0 (2025-12-29)
- ✨ 初始版本发布
- 🎯 Gitcode API集成
- 📊 基础PR数据分析
- 🎨 交互式HTML看板
- 🔄 一键更新功能
- ✅ 编码兼容性修复

## 📞 联系方式

- **项目地址**: https://github.com/tianli-Backkom/monitor_Gitcode_PR_efficiency
- **问题反馈**: https://github.com/tianli-Backkom/monitor_Gitcode_PR_efficiency/issues

## 📄 许可证

本项目基于MIT许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

**⭐ 如果这个项目对您有帮助，请给我们一个Star！**