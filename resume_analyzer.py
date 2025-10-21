#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历分析器 - 负责解析和分析简历内容
遵循单一职责原则，专门处理简历分析逻辑
"""

import os
import re
import json
from typing import Dict, List, Any
import PyPDF2
import docx
from datetime import datetime

class ResumeAnalyzer:
    """简历分析器类"""
    
    def __init__(self):
        """初始化分析器"""
        # 技能关键词库（可扩展）
        self.skill_keywords = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'go', 'rust', 'swift'],
            'web': ['html', 'css', 'react', 'vue', 'angular', 'nodejs', 'express', 'django', 'flask'],
            'database': ['mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sql server'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins'],
            'mobile': ['android', 'ios', 'flutter', 'react native'],
            'ai_ml': ['机器学习', 'deep learning', 'tensorflow', 'pytorch', 'opencv', 'nlp']
        }
        
        # 学历关键词
        self.education_keywords = ['博士', '硕士', '学士', '本科', '专科', '大专', 'phd', 'master', 'bachelor']
        
        # 工作经验关键词
        self.experience_keywords = ['工作经验', '工作经历', '项目经验', '实习经历', '职业经历']
    
    def analyze_resume(self, file_path: str) -> Dict[str, Any]:
        """分析简历文件"""
        try:
            # 提取文本内容
            text_content = self._extract_text(file_path)
            
            if not text_content:
                return {'error': '无法提取文件内容'}
            
            # 分析各个维度
            analysis_result = {
                'file_path': file_path,
                'analysis_time': datetime.now().isoformat(),
                'name': self._extract_name(text_content),
                'contact': self._extract_contact(text_content),
                'education': self._extract_education(text_content),
                'experience_years': self._extract_experience_years(text_content),
                'skills': self._extract_skills(text_content),
                'work_experience': self._extract_work_experience(text_content),
                'projects': self._extract_projects(text_content),
                'raw_text': text_content[:1000]  # 保留前1000字符用于调试
            }
            
            return analysis_result
            
        except Exception as e:
            return {'error': f'分析简历时出错: {str(e)}'}
    
    def _extract_text(self, file_path: str) -> str:
        """从文件中提取文本内容"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_extension in ['.doc', '.docx']:
                return self._extract_from_docx(file_path)
            elif file_extension == '.txt':
                return self._extract_from_txt(file_path)
            else:
                raise ValueError(f'不支持的文件格式: {file_extension}')
        except Exception as e:
            raise Exception(f'提取文本失败: {str(e)}')
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """从PDF文件提取文本"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """从Word文件提取文本"""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def _extract_from_txt(self, file_path: str) -> str:
        """从文本文件提取内容"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _extract_name(self, text: str) -> str:
        """提取姓名"""
        # 简单的姓名提取逻辑，可以根据需要改进
        lines = text.split('\n')
        for line in lines[:5]:  # 通常姓名在前几行
            line = line.strip()
            if line and len(line) <= 10 and not any(keyword in line.lower() for keyword in ['email', 'phone', 'tel', '电话', '邮箱']):
                # 检查是否包含中文姓名模式
                chinese_name_pattern = r'^[\u4e00-\u9fa5]{2,4}$'
                english_name_pattern = r'^[A-Za-z\s]{2,20}$'
                
                if re.match(chinese_name_pattern, line) or re.match(english_name_pattern, line):
                    return line
        
        return "未识别"
    
    def _extract_contact(self, text: str) -> Dict[str, str]:
        """提取联系方式"""
        contact_info = {}
        
        # 提取邮箱
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # 提取电话号码
        phone_patterns = [
            r'1[3-9]\d{9}',  # 中国手机号
            r'\d{3}-\d{4}-\d{4}',  # 美国电话格式
            r'\d{11}',  # 11位数字
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                contact_info['phone'] = phones[0]
                break
        
        return contact_info
    
    def _extract_education(self, text: str) -> List[str]:
        """提取教育背景"""
        education_info = []
        text_lower = text.lower()
        
        for keyword in self.education_keywords:
            if keyword.lower() in text_lower:
                education_info.append(keyword)
        
        # 提取学校名称（简单实现）
        university_keywords = ['大学', '学院', 'university', 'college', 'institute']
        lines = text.split('\n')
        
        for line in lines:
            for keyword in university_keywords:
                if keyword in line.lower():
                    education_info.append(line.strip())
                    break
        
        return list(set(education_info))  # 去重
    
    def _extract_experience_years(self, text: str) -> int:
        """提取工作年限"""
        # 查找年限相关的表述
        year_patterns = [
            r'(\d+)\s*年.*?经验',
            r'(\d+)\s*years.*?experience',
            r'工作.*?(\d+)\s*年',
            r'经验.*?(\d+)\s*年'
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    return int(matches[0])
                except ValueError:
                    continue
        
        # 通过工作经历时间段推算
        date_patterns = [
            r'(\d{4})\s*[-至到]\s*(\d{4})',
            r'(\d{4})\s*[-至到]\s*现在',
            r'(\d{4})\s*[-至到]\s*至今'
        ]
        
        total_years = 0
        current_year = datetime.now().year
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    start_year = int(match[0])
                    end_year = current_year if match[1] in ['现在', '至今'] else int(match[1])
                    total_years += max(0, end_year - start_year)
                except (ValueError, IndexError):
                    continue
        
        return min(total_years, 50)  # 限制最大年限
    
    def _extract_skills(self, text: str) -> List[str]:
        """提取技能"""
        skills = []
        text_lower = text.lower()
        
        # 遍历技能关键词库
        for category, keywords in self.skill_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    skills.append(keyword)
        
        # 查找技能相关段落
        skill_section_patterns = [
            r'技能.*?(?=\n\n|\n[A-Z]|\n\d+\.|\Z)',
            r'专业技能.*?(?=\n\n|\n[A-Z]|\n\d+\.|\Z)',
            r'skills.*?(?=\n\n|\n[A-Z]|\n\d+\.|\Z)'
        ]
        
        for pattern in skill_section_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # 从技能段落中提取更多技能
                for category, keywords in self.skill_keywords.items():
                    for keyword in keywords:
                        if keyword.lower() in match.lower() and keyword not in skills:
                            skills.append(keyword)
        
        return list(set(skills))  # 去重
    
    def _extract_work_experience(self, text: str) -> List[Dict[str, str]]:
        """提取工作经历"""
        experiences = []
        
        # 查找工作经历段落
        experience_patterns = [
            r'工作经[历验].*?(?=\n\n|\n[A-Z]|\n教育|\n项目|\Z)',
            r'职业经历.*?(?=\n\n|\n[A-Z]|\n教育|\n项目|\Z)',
            r'work experience.*?(?=\n\n|\neducation|\nprojects|\Z)'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # 简单解析工作经历
                lines = match.split('\n')
                current_experience = {}
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 查找时间段
                    date_match = re.search(r'(\d{4})\s*[-至到]\s*(\d{4}|现在|至今)', line)
                    if date_match:
                        current_experience['period'] = date_match.group(0)
                    
                    # 查找公司名称（包含"公司"、"有限公司"等）
                    if any(keyword in line for keyword in ['公司', '集团', 'company', 'corp', 'ltd']):
                        current_experience['company'] = line
                    
                    # 查找职位
                    if any(keyword in line for keyword in ['工程师', '经理', '主管', '总监', 'engineer', 'manager', 'director']):
                        current_experience['position'] = line
                
                if current_experience:
                    experiences.append(current_experience)
        
        return experiences
    
    def _extract_projects(self, text: str) -> List[Dict[str, str]]:
        """提取项目经历"""
        projects = []
        
        # 查找项目经历段落
        project_patterns = [
            r'项目经[历验].*?(?=\n\n|\n[A-Z]|\n工作|\n教育|\Z)',
            r'项目.*?(?=\n\n|\n[A-Z]|\n工作|\n教育|\Z)',
            r'projects.*?(?=\n\n|\nwork|\neducation|\Z)'
        ]
        
        for pattern in project_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # 简单解析项目信息
                lines = match.split('\n')
                current_project = {}
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 项目名称通常在开头
                    if '项目' in line and not current_project.get('name'):
                        current_project['name'] = line
                    
                    # 技术栈
                    if any(keyword in line.lower() for keyword in ['技术', 'technology', 'tech']):
                        current_project['technology'] = line
                
                if current_project:
                    projects.append(current_project)
        
        return projects

