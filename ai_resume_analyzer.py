#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI增强简历分析器 - 使用大模型进行智能分析
"""

import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai

# 加载环境变量
load_dotenv()

class AIResumeAnalyzer:
    """基于大模型的简历分析器"""
    
    def __init__(self, model_type=None):
        """
        初始化AI分析器
        
        Args:
            model_type: 模型类型，可选 'deepseek' 或 'gemini'，默认从环境变量读取
        """
        self.model_type = model_type or os.getenv('DEFAULT_AI_MODEL', 'deepseek')
        
        if self.model_type == 'gemini':
            # 初始化 Gemini
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            self.model = os.getenv('GOOGLE_MODEL', 'gemini-2.5-flash')
            self.base_url = os.getenv('GOOGLE_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta')
            self.gemini_model = genai.GenerativeModel(self.model)
            self.client = None
        else:
            # 初始化 DeepSeek (OpenAI兼容)
            self.client = OpenAI(
                api_key=os.getenv('OPENAI_API_KEY'),
                base_url=os.getenv('OPENAI_BASE_URL')
            )
            self.model = os.getenv('OPENAI_MODEL', 'deepseek/deepseek-chat-v3.1:free')
            self.gemini_model = None
    
    def analyze_resume_with_ai(self, resume_text: str) -> Dict[str, Any]:
        """
        使用AI分析简历内容
        
        Args:
            resume_text: 简历文本内容
            
        Returns:
            结构化的简历分析结果
        """
        try:
            prompt = self._create_analysis_prompt(resume_text)
            
            if self.model_type == 'gemini':
                # 使用 Gemini API
                response = self.gemini_model.generate_content(
                    f"你是一个专业的HR简历分析助手，擅长从简历中提取关键信息并进行结构化分析。请用中文回答，返回JSON格式的结果。\n\n{prompt}",
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=2000,
                    )
                )
                result_text = response.text.strip()
            else:
                # 使用 DeepSeek API (OpenAI兼容)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一个专业的HR简历分析助手，擅长从简历中提取关键信息并进行结构化分析。请用中文回答，返回JSON格式的结果。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                result_text = response.choices[0].message.content.strip()
            
            # 尝试解析JSON
            try:
                # 移除可能的markdown代码块标记
                if result_text.startswith('```'):
                    result_text = result_text.split('```')[1]
                    if result_text.startswith('json'):
                        result_text = result_text[4:]
                    result_text = result_text.strip()
                
                analysis_result = json.loads(result_text)
                return analysis_result
                
            except json.JSONDecodeError:
                # 如果无法解析JSON，返回文本结果
                return {
                    'error': 'AI返回结果格式错误',
                    'raw_response': result_text
                }
                
        except Exception as e:
            return {
                'error': f'AI分析失败: {str(e)}'
            }
    
    def _create_analysis_prompt(self, resume_text: str) -> str:
        """创建分析提示词"""
        prompt = f"""请分析以下简历内容，提取关键信息并返回JSON格式的结果。

简历内容：
{resume_text[:3000]}

请按照以下JSON格式返回分析结果：
{{
    "name": "候选人姓名",
    "contact": {{
        "email": "邮箱地址",
        "phone": "电话号码"
    }},
    "education": [
        {{
            "degree": "学历（如：本科、硕士、博士）",
            "school": "学校名称",
            "major": "专业",
            "graduation_year": "毕业年份"
        }}
    ],
    "experience_years": 工作年限（数字）,
    "work_experience": [
        {{
            "company": "公司名称",
            "position": "职位",
            "period": "工作时间段",
            "description": "工作描述"
        }}
    ],
    "skills": [
        "技能1", "技能2", "技能3"
    ],
    "projects": [
        {{
            "name": "项目名称",
            "role": "项目角色",
            "description": "项目描述",
            "technologies": ["技术栈1", "技术栈2"]
        }}
    ],
    "summary": "简历总结（1-2句话概括候选人的核心优势）"
}}

注意：
1. 如果某些信息在简历中没有，可以省略或设为空
2. 技能要尽可能详细提取
3. 工作年限通过工作经历时间段推算
4. 只返回JSON，不要有其他解释文字"""
        
        return prompt
    
    def enhance_screening_with_ai(self, resume_analysis: Dict[str, Any], requirements: str) -> Dict[str, Any]:
        """
        使用AI增强筛选分析
        
        Args:
            resume_analysis: 简历分析结果
            requirements: 职位要求
            
        Returns:
            AI增强的匹配分析
        """
        try:
            prompt = f"""请作为专业HR，分析以下候选人是否匹配职位要求。

职位要求：
{requirements}

候选人简历分析：
{json.dumps(resume_analysis, ensure_ascii=False, indent=2)}

请返回JSON格式的匹配分析：
{{
    "match_score": 85,  // 匹配度评分（0-100）
    "strengths": ["优势1", "优势2"],  // 候选人的优势
    "weaknesses": ["不足1", "不足2"],  // 候选人的不足
    "recommendations": "招聘建议",  // 是否推荐面试及原因
    "key_highlights": ["亮点1", "亮点2"],  // 候选人的亮点
    "concerns": ["关注点1", "关注点2"]  // 需要关注的问题
}}

只返回JSON，不要有其他文字。"""
            
            if self.model_type == 'gemini':
                # 使用 Gemini API
                response = self.gemini_model.generate_content(
                    f"你是一个经验丰富的HR专家，擅长评估候选人与职位的匹配度。请用中文回答，返回JSON格式。\n\n{prompt}",
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.5,
                        max_output_tokens=1500,
                    )
                )
                result_text = response.text.strip()
            else:
                # 使用 DeepSeek API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一个经验丰富的HR专家，擅长评估候选人与职位的匹配度。请用中文回答，返回JSON格式。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.5,
                    max_tokens=1500
                )
                result_text = response.choices[0].message.content.strip()
            
            # 解析JSON
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
                result_text = result_text.strip()
            
            ai_analysis = json.loads(result_text)
            return ai_analysis
            
        except Exception as e:
            return {
                'error': f'AI筛选分析失败: {str(e)}'
            }
