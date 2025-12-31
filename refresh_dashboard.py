#!/usr/bin/env python3
"""
Triton Ascend PR数据看板一键更新脚本
功能：自动获取最新PR数据并生成更新的看板
"""

import os
import sys
import subprocess
import time
from datetime import datetime
import json

def print_header():
    """打印脚本标题"""
    print("=" * 70)
    print("🚀 Triton Ascend PR数据看板一键更新脚本")
    print("=" * 70)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def print_step(step_num, title, description=""):
    """打印步骤信息"""
    print(f"📋 步骤 {step_num}: {title}")
    if description:
        print(f"   {description}")
    print()

def print_success(message):
    """打印成功信息"""
    print(f"✅ {message}")
    print()

def print_error(message):
    """打印错误信息"""
    print(f"❌ {message}")
    print()

def print_warning(message):
    """打印警告信息"""
    print(f"⚠️  {message}")
    print()

def run_command(command, description=""):
    """执行命令并返回结果"""
    try:
        print(f"🔄 执行命令: {command}")
        if description:
            print(f"   {description}")
        
        # 使用 bytes 模式处理编码，避免UnicodeDecodeError
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            cwd=os.getcwd()
        )
        
        # 尝试多种编码解码输出
        def decode_output(output_bytes):
            if not output_bytes:
                return ""
            
            # 尝试的编码列表
            encodings = ['utf-8', 'gbk', 'gb2312', 'cp936', 'latin1']
            
            for encoding in encodings:
                try:
                    return output_bytes.decode(encoding)
                except UnicodeDecodeError:
                    continue
            
            # 如果所有编码都失败，使用错误处理
            return output_bytes.decode('utf-8', errors='replace')
        
        stdout_text = decode_output(result.stdout)
        stderr_text = decode_output(result.stderr)
        
        if result.returncode == 0:
            print_success("命令执行成功")
            return True, stdout_text
        else:
            print_error(f"命令执行失败 (退出码: {result.returncode})")
            if stderr_text:
                print(f"错误信息: {stderr_text}")
            return False, stderr_text
            
    except Exception as e:
        print_error(f"命令执行异常: {str(e)}")
        return False, str(e)

def check_dependencies():
    """检查依赖"""
    print_step(0, "检查环境和依赖")
    
    # 检查Python模块
    required_modules = ['requests', 'json', 'os', 'subprocess']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print_error(f"缺少必要的Python模块: {', '.join(missing_modules)}")
        print("请运行: pip install requests")
        return False
    
    print_success("环境检查通过")
    return True

def run_pr_data_collection():
    """执行PR数据收集"""
    print_step(1, "收集最新PR数据", "从Gitcode API获取仓库PR信息...")
    
    success, output = run_command("python monitor.py", "正在从Ascend/triton-ascend仓库获取PR数据...")
    
    if not success:
        return False
    
    # 检查是否生成了数据文件
    data_file = "/home/runner/work/monitor_Gitcode_PR_efficiency/monitor_Gitcode_PR_efficiency/triton_ascend_prs_analysis.json"
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            total_prs = len(data.get('all_prs', []))
            total_open_prs = data.get('total_open_prs', 0)
            
            print_success(f"数据收集完成")
            print(f"   - 获取PR总数: {total_prs}")
            print(f"   - 待合入PR: {total_open_prs}")
            
            # 检查失败PR数据
            daily_failed = data.get('daily_failed_submissions', {})
            total_failed = sum(daily_failed.values())
            if total_failed > 0:
                print(f"   - 失败PR数量: {total_failed}")
            
            return True
        except Exception as e:
            print_error(f"读取数据文件失败: {str(e)}")
            return False
    else:
        print_error("数据文件未生成")
        return False

def run_dashboard_generation():
    """执行看板生成"""
    print_step(2, "生成HTML看板", "基于最新数据生成交互式看板...")
    
    success, output = run_command("python pr_dashboard.py", "正在生成HTML看板文件...")
    
    if success:
        dashboard_file = "triton_pr_dashboard.html"
        if os.path.exists(dashboard_file):
            file_size = os.path.getsize(dashboard_file)
            print_success(f"看板生成完成")
            print(f"   - 文件: {dashboard_file}")
            print(f"   - 大小: {file_size / 1024:.1f} KB")
            return True
        else:
            print_error("看板文件未生成")
            return False
    else:
        return False

def validate_results():
    """验证结果"""
    print_step(3, "验证结果", "检查生成的文件和数据...")
    
    # 检查数据文件
    data_file = "/home/runner/work/monitor_Gitcode_PR_efficiency/monitor_Gitcode_PR_efficiency/triton_ascend_prs_analysis.json"
    if os.path.exists(data_file):
        print_success("✅ 数据文件存在")
    else:
        print_error("❌ 数据文件不存在")
        return False
    
    # 检查看板文件
    dashboard_file = "triton_pr_dashboard.html"
    if os.path.exists(dashboard_file):
        print_success("✅ 看板文件存在")
    else:
        print_error("❌ 看板文件不存在")
        return False
    
    # 验证数据内容
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        required_fields = ['repository', 'total_open_prs', 'daily_submissions', 'daily_failed_submissions']
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            print_error(f"❌ 数据文件缺少必要字段: {', '.join(missing_fields)}")
            return False
        else:
            print_success("✅ 数据文件格式正确")
            
        # 检查失败PR数据
        daily_failed = data.get('daily_failed_submissions', {})
        if daily_failed:
            total_failed = sum(daily_failed.values())
            print_success(f"✅ 失败PR数据完整 ({total_failed}个失败PR)")
        else:
            print_warning("⚠️  未检测到失败PR数据")
            
    except Exception as e:
        print_error(f"❌ 数据文件验证失败: {str(e)}")
        return False
    
    return True

def print_final_summary():
    """打印最终总结"""
    print("=" * 70)
    print("🎉 任务完成总结")
    print("=" * 70)
    
    data_file = "/home/runner/work/monitor_Gitcode_PR_efficiency/monitor_Gitcode_PR_efficiency/triton_ascend_prs_analysis.json"
    dashboard_file = "triton_pr_dashboard.html"
    
    print("📁 生成的文件:")
    print(f"   • 数据文件: {data_file}")
    print(f"   • 看板文件: {os.path.abspath(dashboard_file)}")
    
    print("\n🌐 查看方式:")
    print("   • 在浏览器中打开HTML文件即可查看看板")
    print("   • 看板包含: PR统计、失败PR分析、每日提交趋势图")
    
    print(f"\n⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

def main():
    """主函数"""
    print_header()
    
    try:
        # 步骤0: 检查依赖
        if not check_dependencies():
            print_error("环境检查失败，请解决依赖问题后重试")
            return 1
        
        # 步骤1: 收集PR数据
        if not run_pr_data_collection():
            print_error("PR数据收集失败")
            return 1
        
        # 步骤2: 生成看板
        if not run_dashboard_generation():
            print_error("看板生成失败")
            return 1
        
        # 步骤3: 验证结果
        if not validate_results():
            print_error("结果验证失败")
            return 1
        
        # 打印最终总结
        print_final_summary()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        return 1
    except Exception as e:
        print_error(f"脚本执行异常: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
