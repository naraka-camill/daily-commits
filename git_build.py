#!/usr/bin/env python3
import subprocess
import random
from datetime import datetime, timedelta
import os
import sys

# 配置
repo_path = "."  # 当前目录，或者改成你的仓库路径
start_date = datetime.now() - timedelta(days=10)  # 从days天前开始
end_date = datetime.now()

# 设置随机种子（可选）
# random.seed(42)

def get_commit_count(date):
    """
    根据日期返回提交次数
    周一到周五：1-10个提交，每个概率10%
    周六：0-1个提交，0的概率75%，1的概率25%
    周日：0-1个提交，0的概率75%，1的概率25%
    """
    weekday = date.weekday()  # 0=周一, 1=周二, 2=周三, 3=周四, 4=周五, 5=周六, 6=周日
    
    if weekday <= 4:  # 周一到周五
        return random.randint(1, 10) # 修改每天的提交次数，概率平均分布
    else:  # 周六和周日
        return 0 if random.random() < 0.75 else 1

def check_existing_commits_on_date(date):
    """检查指定日期是否已有提交"""
    date_str = date.strftime("%Y-%m-%d")
    
    # 获取该日期的所有提交
    result = subprocess.run(
        ["git", "log", f"--since={date_str} 00:00:00", f"--until={date_str} 23:59:59", "--oneline"],
        capture_output=True,
        text=True
    )
    
    # 统计提交数量
    if result.stdout.strip():
        commits = result.stdout.strip().split('\n')
        return len(commits)
    return 0

def create_commits_for_date(date, commit_count, skip_existing=False):
    """为指定日期创建指定数量的提交"""
    date_str = date.strftime("%Y-%m-%d")
    
    # 检查是否已有提交
    existing_commits = 0
    if skip_existing:
        existing_commits = check_existing_commits_on_date(date)
        if existing_commits >= commit_count:
            print(f"  {date_str}: 已有 {existing_commits} 个提交，跳过")
            return 0
        elif existing_commits > 0:
            commit_count = max(0, commit_count - existing_commits)
            print(f"  {date_str}: 已有 {existing_commits} 个提交，将补充 {commit_count} 个")
    
    new_commits = 0
    for i in range(commit_count):
        # 为每个提交创建不同的时间
        hour = random.randint(9, 17)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        commit_time = date.replace(hour=hour, minute=minute, second=second)
        commit_time_str = commit_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # 创建或修改文件（使用现有文件或创建新文件）
        log_file = "daily_commits.log"
        with open(log_file, "a") as f:
            f.write(f"Commit #{existing_commits + i + 1} for {date_str} at {commit_time.strftime('%H:%M:%S')}\n")
        
        # 添加文件
        subprocess.run(["git", "add", log_file], check=True, capture_output=True)
        
        # 提交
        subprocess.run(["git", "commit", "-m", f"Daily commit #{existing_commits + i + 1} for {date_str}"], 
                      check=True, capture_output=True)
        
        # 修改提交日期和时间
        subprocess.run([
            "git", "commit", "--amend", "--no-edit",
            "--date", commit_time_str
        ], check=True, capture_output=True)
        
        print(f"  Created commit #{existing_commits + i + 1}/{existing_commits + commit_count} for {date_str} at {commit_time_str}")
        new_commits += 1
    
    return new_commits

def main():
    # 检查是否在 git 仓库中
    try:
        subprocess.run(["git", "status"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("错误：当前目录不是 git 仓库！")
        print("请在 git 仓库目录中运行此脚本，或修改 repo_path 变量")
        sys.exit(1)
    
    # 询问是否跳过已有提交的日期
    skip_existing = input("是否跳过已有提交的日期？(y/n，默认 y): ").lower() != 'n'
    
    # 获取当前分支
    branch_result = subprocess.run(["git", "branch", "--show-current"], 
                                  capture_output=True, text=True)
    current_branch = branch_result.stdout.strip()
    print(f"\n当前分支: {current_branch}")
    
    # 确认开始
    print(f"\n将在当前仓库创建从 {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')} 的提交")
    confirm = input("是否继续？(y/n): ").lower()
    if confirm != 'y':
        print("已取消")
        sys.exit(0)
    
    # 统计变量
    total_commits = 0
    days_with_commits = 0
    days_skipped = 0
    
    # 生成每日提交
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        weekday_name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][current_date.weekday()]
        
        # 获取今天的提交数量
        commit_count = get_commit_count(current_date)
        
        if commit_count > 0:
            print(f"\n{date_str} ({weekday_name}): 目标 {commit_count} 个提交")
            new_commits = create_commits_for_date(current_date, commit_count, skip_existing)
            if new_commits > 0:
                total_commits += new_commits
                days_with_commits += 1
            else:
                days_skipped += 1
        else:
            print(f"\n{date_str} ({weekday_name}): 跳过 (0个提交)")
        
        current_date += timedelta(days=1)
    
    # 输出统计信息
    print("\n" + "="*50)
    print(f"完成！")
    print(f"时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
    print(f"总天数: {(end_date - start_date).days + 1} 天")
    print(f"有提交的天数: {days_with_commits} 天")
    print(f"跳过（已有提交）的天数: {days_skipped} 天")
    print(f"新增提交数: {total_commits} 个")
    
    # 询问是否推送
    print("\n" + "="*50)
    push_now = input("\n是否立即推送到远程仓库？(y/n): ").lower()
    if push_now == 'y':
        print(f"正在推送到 origin/{current_branch}...")
        subprocess.run(["git", "push", "origin", current_branch], check=True)
        print("推送完成！")
    else:
        print(f"稍后可以运行: git push origin {current_branch}")

if __name__ == "__main__":
    main()