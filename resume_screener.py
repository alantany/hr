#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历筛选器 - 负责根据需求筛选简历
遵循单一职责原则，专门处理简历筛选逻辑
"""

import re
from typing import Dict, List, Tuple, Any

class ResumeScreener:
    """简历筛选器类"""
    
    def __init__(self):
        """初始化筛选器"""
        # 筛选权重配置
        self.weights = {
            'skills': 0.4,      # 技能匹配权重
            'experience': 0.3,  # 经验匹配权重
            'education': 0.2,   # 学历匹配权重
            'keywords': 0.1     # 关键词匹配权重
        }
    
    def screen_resume(self, resume_analysis: Dict[str, Any], requirements: str) -> Tuple[float, Dict[str, Any]]:
        """
        筛选单份简历
        
        Args:
            resume_analysis: 简历分析结果
            requirements: 筛选需求文本
            
        Returns:
            Tuple[匹配度评分(0-100), 匹配详情]
        """
        if not resume_analysis or 'error' in resume_analysis:
            return 0.0, {'error': '简历分析失败'}
        
        # 解析需求
        parsed_requirements = self._parse_requirements(requirements)
        
        # 计算各维度匹配度
        skills_score = self._calculate_skills_match(resume_analysis, parsed_requirements)
        experience_score = self._calculate_experience_match(resume_analysis, parsed_requirements)
        education_score = self._calculate_education_match(resume_analysis, parsed_requirements)
        keywords_score = self._calculate_keywords_match(resume_analysis, parsed_requirements)
        
        # 加权计算总分
        total_score = (
            skills_score * self.weights['skills'] +
            experience_score * self.weights['experience'] +
            education_score * self.weights['education'] +
            keywords_score * self.weights['keywords']
        ) * 100
        
        # 匹配详情
        match_details = {
            'skills_match': {
                'score': skills_score,
                'matched_skills': self._get_matched_skills(resume_analysis, parsed_requirements),
                'missing_skills': self._get_missing_skills(resume_analysis, parsed_requirements)
            },
            'experience_match': {
                'score': experience_score,
                'resume_years': resume_analysis.get('experience_years', 0),
                'required_years': parsed_requirements.get('min_experience_years', 0)
            },
            'education_match': {
                'score': education_score,
                'resume_education': resume_analysis.get('education', []),
                'required_education': parsed_requirements.get('education_requirements', [])
            },
            'keywords_match': {
                'score': keywords_score,
                'matched_keywords': self._get_matched_keywords(resume_analysis, parsed_requirements)
            }
        }
        
        return round(total_score, 2), match_details
    
    def _parse_requirements(self, requirements: str) -> Dict[str, Any]:
        """解析需求文本"""
        parsed = {
            'required_skills': [],
            'preferred_skills': [],
            'min_experience_years': 0,
            'education_requirements': [],
            'keywords': [],
            'salary_range': None
        }
        
        requirements_lower = requirements.lower()
        
        # 提取技能要求
        skill_patterns = [
            r'技能.*?[:：]\s*([^\n]+)',
            r'要求.*?[:：]\s*([^\n]+)',
            r'熟悉\s*([^\n，,。.]+)',
            r'掌握\s*([^\n，,。.]+)',
            r'精通\s*([^\n，,。.]+)'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, requirements, re.IGNORECASE)
            for match in matches:
                # 分割技能
                skills = re.split(r'[，,、；;]', match)
                for skill in skills:
                    skill = skill.strip()
                    if skill and len(skill) > 1:
                        parsed['required_skills'].append(skill)
        
        # 提取工作年限要求
        experience_patterns = [
            r'(\d+)\s*年以上.*?经验',
            r'(\d+)\s*年.*?工作经验',
            r'(\d+)\+\s*years',
            r'至少\s*(\d+)\s*年'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, requirements)
            if matches:
                try:
                    parsed['min_experience_years'] = int(matches[0])
                    break
                except ValueError:
                    continue
        
        # 提取学历要求
        education_patterns = [
            r'(本科|学士|bachelor)以上',
            r'(硕士|master)以上',
            r'(博士|phd|doctor)',
            r'(专科|大专)以上'
        ]
        
        for pattern in education_patterns:
            matches = re.findall(pattern, requirements_lower)
            if matches:
                parsed['education_requirements'].extend(matches)
        
        # 提取关键词
        keyword_patterns = [
            r'关键词.*?[:：]\s*([^\n]+)',
            r'优先.*?[:：]\s*([^\n]+)'
        ]
        
        for pattern in keyword_patterns:
            matches = re.findall(pattern, requirements, re.IGNORECASE)
            for match in matches:
                keywords = re.split(r'[，,、；;]', match)
                for keyword in keywords:
                    keyword = keyword.strip()
                    if keyword:
                        parsed['keywords'].append(keyword)
        
        # 提取薪资要求
        salary_patterns = [
            r'薪资.*?(\d+)[-到至]\s*(\d+)',
            r'(\d+)k[-到至]\s*(\d+)k',
            r'月薪.*?(\d+)'
        ]
        
        for pattern in salary_patterns:
            matches = re.findall(pattern, requirements_lower)
            if matches:
                parsed['salary_range'] = matches[0]
                break
        
        return parsed
    
    def _calculate_skills_match(self, resume_analysis: Dict[str, Any], requirements: Dict[str, Any]) -> float:
        """计算技能匹配度"""
        resume_skills = [skill.lower() for skill in resume_analysis.get('skills', [])]
        required_skills = [skill.lower() for skill in requirements.get('required_skills', [])]
        
        if not required_skills:
            return 1.0  # 如果没有技能要求，返回满分
        
        matched_count = 0
        for required_skill in required_skills:
            # 模糊匹配
            for resume_skill in resume_skills:
                if required_skill in resume_skill or resume_skill in required_skill:
                    matched_count += 1
                    break
        
        return matched_count / len(required_skills)
    
    def _calculate_experience_match(self, resume_analysis: Dict[str, Any], requirements: Dict[str, Any]) -> float:
        """计算经验匹配度"""
        resume_years = resume_analysis.get('experience_years', 0)
        required_years = requirements.get('min_experience_years', 0)
        
        if required_years == 0:
            return 1.0  # 如果没有经验要求，返回满分
        
        if resume_years >= required_years:
            return 1.0
        elif resume_years >= required_years * 0.8:  # 80%以上认为基本符合
            return 0.8
        elif resume_years >= required_years * 0.6:  # 60%以上认为部分符合
            return 0.6
        else:
            return resume_years / required_years  # 按比例计算
    
    def _calculate_education_match(self, resume_analysis: Dict[str, Any], requirements: Dict[str, Any]) -> float:
        """计算学历匹配度"""
        resume_education = [edu.lower() for edu in resume_analysis.get('education', [])]
        required_education = [edu.lower() for edu in requirements.get('education_requirements', [])]
        
        if not required_education:
            return 1.0  # 如果没有学历要求，返回满分
        
        # 学历等级映射
        education_levels = {
            '博士': 4, 'phd': 4, 'doctor': 4,
            '硕士': 3, 'master': 3,
            '本科': 2, '学士': 2, 'bachelor': 2,
            '专科': 1, '大专': 1
        }
        
        # 获取简历最高学历等级
        resume_max_level = 0
        for edu in resume_education:
            for level_name, level_value in education_levels.items():
                if level_name in edu:
                    resume_max_level = max(resume_max_level, level_value)
        
        # 获取要求最低学历等级
        required_min_level = 0
        for edu in required_education:
            for level_name, level_value in education_levels.items():
                if level_name in edu:
                    required_min_level = max(required_min_level, level_value)
        
        if required_min_level == 0:
            return 1.0
        
        return min(1.0, resume_max_level / required_min_level)
    
    def _calculate_keywords_match(self, resume_analysis: Dict[str, Any], requirements: Dict[str, Any]) -> float:
        """计算关键词匹配度"""
        resume_text = resume_analysis.get('raw_text', '').lower()
        keywords = requirements.get('keywords', [])
        
        if not keywords:
            return 1.0  # 如果没有关键词要求，返回满分
        
        matched_count = 0
        for keyword in keywords:
            if keyword.lower() in resume_text:
                matched_count += 1
        
        return matched_count / len(keywords)
    
    def _get_matched_skills(self, resume_analysis: Dict[str, Any], requirements: Dict[str, Any]) -> List[str]:
        """获取匹配的技能列表"""
        resume_skills = [skill.lower() for skill in resume_analysis.get('skills', [])]
        required_skills = [skill.lower() for skill in requirements.get('required_skills', [])]
        
        matched_skills = []
        for required_skill in required_skills:
            for resume_skill in resume_analysis.get('skills', []):
                if required_skill in resume_skill.lower() or resume_skill.lower() in required_skill:
                    matched_skills.append(resume_skill)
                    break
        
        return matched_skills
    
    def _get_missing_skills(self, resume_analysis: Dict[str, Any], requirements: Dict[str, Any]) -> List[str]:
        """获取缺失的技能列表"""
        resume_skills = [skill.lower() for skill in resume_analysis.get('skills', [])]
        required_skills = requirements.get('required_skills', [])
        
        missing_skills = []
        for required_skill in required_skills:
            found = False
            for resume_skill in resume_skills:
                if required_skill.lower() in resume_skill or resume_skill in required_skill.lower():
                    found = True
                    break
            if not found:
                missing_skills.append(required_skill)
        
        return missing_skills
    
    def _get_matched_keywords(self, resume_analysis: Dict[str, Any], requirements: Dict[str, Any]) -> List[str]:
        """获取匹配的关键词列表"""
        resume_text = resume_analysis.get('raw_text', '').lower()
        keywords = requirements.get('keywords', [])
        
        matched_keywords = []
        for keyword in keywords:
            if keyword.lower() in resume_text:
                matched_keywords.append(keyword)
        
        return matched_keywords

