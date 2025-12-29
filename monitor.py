import requests
import json
import os
import time
from datetime import datetime, timedelta, timezone
from dateutil import parser

def get_all_pull_requests(owner: str, repo: str, access_token: str, max_retries: int = 3, retry_delay: int = 2, max_pages: int = 5) -> list:
    """
    获取仓库的所有PR，处理分页
    """
    all_pull_requests = []
    page = 1
    per_page = 100  # 每页数量，最大为100
    
    print(f"开始获取仓库 {owner}/{repo} 的PR数据...")
    
    while True:
        # 构建API请求URL
        url = f"https://api.gitcode.com/api/v5/repos/{owner}/{repo}/pulls"
        
        # 设置查询参数
        params = {
            'access_token': access_token,
            'state': 'all',  # 获取所有状态的PR
            'page': page,
            'per_page': per_page
        }
        
        try:
            print(f"正在获取第 {page} 页 (每页 {per_page} 条)...")
            response = requests.get(url, params=params)
            response.raise_for_status()  # 检查HTTP错误
            
            # 解析JSON响应
            prs = response.json()
            
            # 如果没有更多PR，退出循环
            if not prs:
                print(f"已获取所有PR，共 {len(all_pull_requests)} 个")
                break
                
            all_pull_requests.extend(prs)
            print(f"已获取 {len(prs)} 个PR，总计 {len(all_pull_requests)} 个")
            
            # 检查是否还有下一页
            if len(prs) < per_page:
                print("已获取所有PR")
                break
                
            # 延迟以避免API限流
            time.sleep(1)
            
            # 检查是否达到最大页数限制
            if page >= max_pages:
                print(f"已达到最大页数限制 ({max_pages})，停止获取更多PR")
                break
            
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 401:
                print("错误：认证失败。请检查access_token是否正确。")
                raise
            elif response.status_code == 429:
                print(f"错误：API请求过于频繁。正在重试... (剩余重试次数: {max_retries})")
                if max_retries > 0:
                    max_retries -= 1
                    time.sleep(retry_delay)
                    continue
                else:
                    print("错误：API限流错误，重试次数已用尽。")
                    raise
            else:
                print(f"HTTP错误: {http_err}")
                raise
        except requests.exceptions.ConnectionError:
            print("错误：网络连接失败。正在重试...")
            if max_retries > 0:
                max_retries -= 1
                time.sleep(retry_delay)
                continue
            else:
                print("错误：网络连接失败，重试次数已用尽。")
                raise
        except Exception as e:
            print(f"获取PR时发生错误: {e}")
            raise
        
        page += 1
    
    return all_pull_requests

def analyze_pr_data(pr_list: list) -> dict:
    """
    分析PR数据，重点计算近七天已合入PR的平均合入时长
    """
    # 使用UTC时区来确保一致性
    now = datetime.now(timezone.utc)
    
    # 计算7天前的时间
    seven_days_ago = now - timedelta(days=7)
    
    # 待合入PR数量
    open_pr_count = sum(1 for pr in pr_list if pr['state'] == 'open')
    
    # 近七天提交的PR
    recent_submitted_prs = []
    for pr in pr_list:
        if pr['created_at']:
            try:
                created_at = parser.parse(pr['created_at'])
                # 确保所有datetime都有时区信息
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                if created_at >= seven_days_ago:
                    recent_submitted_prs.append(pr)
            except (ValueError, TypeError) as e:
                # 如果日期解析失败，跳过这个PR
                continue
    
    # 近七天已合入的PR的合入时长分析
    recent_merged_prs_analysis = {
        "count": 0,
        "total_duration_days": 0,
        "average_duration_days": 0,
        "min_duration_days": None,
        "max_duration_days": None,
        "pr_details": []
    }
    
    for pr in pr_list:
        if pr['state'] == 'merged' and pr['created_at'] and pr['merged_at']:
            try:
                created_at = parser.parse(pr['created_at'])
                merged_at = parser.parse(pr['merged_at'])
                
                # 确保所有datetime都有时区信息
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                if merged_at.tzinfo is None:
                    merged_at = merged_at.replace(tzinfo=timezone.utc)
                    
                # 只计算近七天创建的PR的合入时长
                if created_at >= seven_days_ago:
                    duration = (merged_at - created_at)
                    duration_days = duration.days + duration.seconds / (24 * 3600)  # 包含小数部分
                    
                    recent_merged_prs_analysis["count"] += 1
                    recent_merged_prs_analysis["total_duration_days"] += duration_days
                    recent_merged_prs_analysis["pr_details"].append({
                        "number": pr['number'],
                        "title": pr['title'],
                        "created_at": pr['created_at'],
                        "merged_at": pr['merged_at'],
                        "duration_days": round(duration_days, 2),
                        "duration_hours": round(duration_days * 24, 2)
                    })
                    
                    # 更新最小/最大时长
                    if (recent_merged_prs_analysis["min_duration_days"] is None or 
                        duration_days < recent_merged_prs_analysis["min_duration_days"]):
                        recent_merged_prs_analysis["min_duration_days"] = duration_days
                    
                    if (recent_merged_prs_analysis["max_duration_days"] is None or 
                        duration_days > recent_merged_prs_analysis["max_duration_days"]):
                        recent_merged_prs_analysis["max_duration_days"] = duration_days
                        
            except (ValueError, TypeError) as e:
                # 如果日期解析失败，跳过这个PR
                continue
    
    # 计算平均时长
    if recent_merged_prs_analysis["count"] > 0:
        recent_merged_prs_analysis["average_duration_days"] = round(
            recent_merged_prs_analysis["total_duration_days"] / recent_merged_prs_analysis["count"], 2
        )
    
    # 近两周PR每日提交次数统计
    fourteen_days_ago = now - timedelta(days=14)
    daily_submissions = {}
    daily_failed_submissions = {}
    
    def is_failed_pr(pr):
        """判断PR是否为失败PR"""
        if 'labels' not in pr or not pr['labels']:
            return False
        
        for label in pr['labels']:
            if isinstance(label, dict) and 'name' in label:
                label_name = label['name'].lower()
                if 'sc-fail' in label_name or 'ci-pipeline-failed' in label_name:
                    return True
        return False
    
    for pr in pr_list:
        if pr['created_at']:
            try:
                created_at = parser.parse(pr['created_at'])
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                
                if created_at >= fourteen_days_ago:
                    date_key = created_at.strftime('%Y-%m-%d')
                    
                    # 总提交数统计
                    if date_key not in daily_submissions:
                        daily_submissions[date_key] = 0
                        daily_failed_submissions[date_key] = 0
                    daily_submissions[date_key] += 1
                    
                    # 失败PR统计
                    if is_failed_pr(pr):
                        daily_failed_submissions[date_key] += 1
                        
            except (ValueError, TypeError):
                continue
    
    return {
        "total_open_prs": open_pr_count,
        "recent_submitted_prs": recent_submitted_prs,
        "recent_merged_prs_analysis": recent_merged_prs_analysis,
        "daily_submissions": daily_submissions,
        "daily_failed_submissions": daily_failed_submissions
    }

def main():
    # 配置
    owner = "Ascend"
    repo = "triton-ascend"
    access_token = "ujpJg3DiifrfP8SooysZq6He"
    output_dir = "D:\\code\\monitor_Gitcode_PR_efficiency"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 获取所有PR
        all_prs = get_all_pull_requests(owner, repo, access_token, max_pages=3)
        
        # 分析PR数据
        analysis_result = analyze_pr_data(all_prs)
        
        # 准备输出数据
        output_data = {
            "repository": f"{owner}/{repo}",
            "total_open_prs": analysis_result["total_open_prs"],
            "recent_submitted_prs": analysis_result["recent_submitted_prs"],
            "recent_merged_prs_analysis": analysis_result["recent_merged_prs_analysis"],
            "daily_submissions": analysis_result["daily_submissions"],
            "daily_failed_submissions": analysis_result["daily_failed_submissions"],
            "all_prs": all_prs
        }
        
        # 保存为JSON文件
        output_file = os.path.join(output_dir, "triton_ascend_prs_analysis.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*50)
        print(f"统计完成！")
        print(f"目标仓库: {owner}/{repo}")
        print(f"待合入PR数量: {analysis_result['total_open_prs']}")
        print(f"近七天提交的PR数量: {len(analysis_result['recent_submitted_prs'])}")
        
        # 近七天已合入PR的合入时长分析
        merged_analysis = analysis_result['recent_merged_prs_analysis']
        print(f"近七天已合入的PR数量: {merged_analysis['count']}")
        if merged_analysis['count'] > 0:
            print(f"平均合入时长: {merged_analysis['average_duration_days']} 天")
            print(f"最短合入时长: {merged_analysis['min_duration_days']} 天")
            print(f"最长合入时长: {merged_analysis['max_duration_days']} 天")
        else:
            print("近七天内没有已合入的PR")
            
        print(f"PR数据已保存到: {output_file}")
        print("="*50)
        
    except Exception as e:
        print(f"\n脚本执行过程中发生错误: {e}")
        raise

if __name__ == "__main__":
    main()