#!/usr/bin/env python3
"""
修复 random.choice 的 weights 参数问题
将 random.choice(options, weights=weights) 替换为 random.choices(options, weights=weights)[0]
"""

import re
import os
import glob

def fix_random_choice_in_file(filepath):
    """修复单个文件中的 random.choice weights 问题"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配 random.choice(options, weights=weights) 模式
    pattern = r'random\.choice\(([^)]+),\s*weights=([^)]+)\)'
    
    def replace_func(match):
        options = match.group(1)
        weights = match.group(2)
        return f'random.choices({options}, weights={weights})[0]'
    
    new_content = re.sub(pattern, replace_func, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed: {filepath}")
        return True
    return False

def main():
    """主函数"""
    # 查找所有Python文件
    python_files = glob.glob('generators/*.py')
    
    fixed_count = 0
    for filepath in python_files:
        if fix_random_choice_in_file(filepath):
            fixed_count += 1
    
    print(f"Total files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
