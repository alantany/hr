#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量简历智能筛选器
上传时静默处理，查询时AI分析
"""

import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai
from resume_analyzer import ResumeAnalyzer

load_dotenv()

class BatchResumeScreener:
    """批量简历筛选器"""
    
    def __init__(self, model_type=None):
        """
        初始化筛选器
        
        Args:
            model_type: 模型类型，可选 'deepseek' 或 'gemini'
        """
        self.model_type = model_type or os.getenv('DEFAULT_AI_MODEL', 'deepseek')
        
        if self.model_type == 'gemini':
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            self.model = os.getenv('GOOGLE_MODEL', 'gemini-2.5-flash')
            self.gemini_model = genai.GenerativeModel(self.model)
            self.client = None
        else:
            self.client = OpenAI(
                api_key=os.getenv('OPENAI_API_KEY'),
                base_url=os.getenv('OPENAI_BASE_URL')
            )
            self.model = os.getenv('OPENAI_MODEL', 'deepseek/deepseek-chat')
            self.gemini_model = None
        
        self.resume_analyzer = ResumeAnalyzer()
        self.resume_pool = {}  # 存储简历池 {doc_id: {文件信息, 提取的文本}}
    
    def add_resume_to_pool(self, doc_id: str, file_path: str, filename: str) -> Dict[str, Any]:
        """
        将简历添加到池中（静默处理，不返回分析内容）
        
        Args:
            doc_id: 文档ID
            file_path: 文件路径
            filename: 原始文件名
            
        Returns:
            简单的确认信息（不包含简历内容）
        """
        try:
            print(f"[批量筛选] 开始处理: {filename}")  # 添加日志
            
            # 提取文本
            analysis_result = self.resume_analyzer.analyze_resume(file_path)
            
            print(f"[批量筛选] 解析结果: {list(analysis_result.keys())}")  # 显示解析的字段
            
            if 'error' in analysis_result:
                print(f"[批量筛选] 解析错误: {analysis_result['error']}")  # 记录错误
                # 即使分析失败，也添加到池中，只是标记为未分析
                self.resume_pool[doc_id] = {
                    'doc_id': doc_id,
                    'filename': filename,
                    'file_path': file_path,
                    'raw_text': '',
                    'basic_info': {
                        'name': filename.replace('.pdf', ''),  # 使用文件名作为临时名称
                        'contact': {},
                        'education': [],
                        'experience_years': 0,
                        'skills': []
                    },
                    'parse_error': True,
                    'error_message': analysis_result.get('error', '解析失败')
                }
                print(f"[批量筛选] 已添加(解析失败): {doc_id} -> {filename}")
                return {
                    'success': True,  # 仍然返回成功，但标记为部分成功
                    'doc_id': doc_id,
                    'filename': filename,
                    'warning': '简历已添加但解析可能不完整',
                    'message': '简历已添加到筛选池'
                }
            
            # 存储到简历池
            # 直接使用文件名，不尝试识别姓名
            display_name = filename.replace('.pdf', '').replace('.PDF', '')
            
            self.resume_pool[doc_id] = {
                'doc_id': doc_id,
                'filename': filename,
                'file_path': file_path,
                'raw_text': analysis_result.get('raw_text', ''),
                'basic_info': {
                    'name': display_name,  # 直接使用文件名
                    'contact': analysis_result.get('contact', {}),
                    'education': analysis_result.get('education', []),
                    'experience_years': analysis_result.get('experience_years', 0),
                    'skills': analysis_result.get('skills', [])
                },
                'parse_error': False
            }
            
            print(f"[批量筛选] 已添加(成功): {doc_id} -> {filename}")
            print(f"[批量筛选] 当前池大小: {len(self.resume_pool)}")
            
            return {
                'success': True,
                'doc_id': doc_id,
                'filename': filename,
                'message': '简历已添加到筛选池'
            }
            
        except Exception as e:
            print(f"[批量筛选] 异常: {filename} - {str(e)}")
            import traceback
            traceback.print_exc()  # 打印完整堆栈
            # 捕获异常，但仍然添加到池中
            self.resume_pool[doc_id] = {
                'doc_id': doc_id,
                'filename': filename,
                'file_path': file_path,
                'raw_text': '',
                'basic_info': {
                    'name': filename.replace('.pdf', ''),
                    'contact': {},
                    'education': [],
                    'experience_years': 0,
                    'skills': []
                },
                'parse_error': True,
                'error_message': str(e)
            }
            print(f"[批量筛选] 已添加(异常): {doc_id} -> {filename}")
            print(f"[批量筛选] 当前池大小: {len(self.resume_pool)}")
            return {
                'success': True,
                'doc_id': doc_id,
                'filename': filename,
                'warning': f'简历已添加但处理时出错: {str(e)}',
                'message': '简历已添加到筛选池'
            }
    
    def query_resumes(self, query: str) -> Dict[str, Any]:
        """
        根据自然语言查询筛选简历
        
        Args:
            query: 查询条件，如"帮我找到本科以上的候选人"
            
        Returns:
            匹配的简历列表和AI分析
        """
        try:
            if not self.resume_pool:
                return {
                    'success': False,
                    'error': '简历池为空，请先上传简历'
                }
            
            # 准备完整简历信息（包含原始文本）
            resume_data_list = []
            for doc_id, resume_data in self.resume_pool.items():
                # 发送完整的简历文本，而不是仅摘要
                full_data = {
                    'doc_id': doc_id,
                    'filename': resume_data['filename'],
                    'name': resume_data['basic_info']['name'],
                    'full_text': resume_data['raw_text'][:3000],  # 限制每份简历最多3000字符，避免token超限
                    'basic_info': {
                        'education': resume_data['basic_info']['education'],
                        'experience_years': resume_data['basic_info']['experience_years'],
                        'skills': resume_data['basic_info']['skills']
                    }
                }
                resume_data_list.append(full_data)
            
            # 构建AI提示 - 包含完整简历文本
            prompt = f"""你是一个专业的HR助手。我有{len(self.resume_pool)}份简历，需要根据以下要求进行筛选：

查询要求：{query}

以下是所有简历的完整信息（包含原始简历文本）：

{json.dumps(resume_data_list, ensure_ascii=False, indent=2)}

请仔细阅读每份简历的完整内容（full_text字段），分析工作经历、项目经验、教育背景等所有细节，然后返回符合要求的候选人。

返回JSON格式：
{{
    "matched_candidates": [
        {{
            "doc_id": "文档ID",
            "filename": "文件名",
            "name": "候选人姓名",
            "reason": "符合原因（基于简历原文的详细说明）",
            "highlights": ["亮点1（具体工作经历）", "亮点2（具体项目经验）", "亮点3"]
        }}
    ],
    "summary": "筛选总结（一句话）",
    "match_count": 匹配数量
}}

只返回JSON，不要其他文字。"""
            
            # 调用AI分析
            if self.model_type == 'gemini':
                # 使用 Gemini API
                response = self.gemini_model.generate_content(
                    f"你是一个专业的HR筛选助手，擅长仔细阅读简历原文并根据要求筛选候选人。返回JSON格式结果。\n\n{prompt}",
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=4000,
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
                            "content": "你是一个专业的HR筛选助手，擅长仔细阅读简历原文并根据要求筛选候选人。返回JSON格式结果。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=4000  # 增加token限制，因为需要处理更多内容
                )
                result_text = response.choices[0].message.content.strip()
            
            # 解析JSON
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
                result_text = result_text.strip()
            
            ai_result = json.loads(result_text)
            
            # 补充完整的简历信息
            matched_resumes = []
            for candidate in ai_result.get('matched_candidates', []):
                doc_id = candidate['doc_id']
                if doc_id in self.resume_pool:
                    resume_data = self.resume_pool[doc_id]
                    matched_resumes.append({
                        'doc_id': doc_id,
                        'filename': resume_data['filename'],
                        'name': candidate.get('name', resume_data['basic_info']['name']),
                        'reason': candidate.get('reason', ''),
                        'highlights': candidate.get('highlights', []),
                        'basic_info': resume_data['basic_info']
                    })
            
            return {
                'success': True,
                'query': query,
                'total_resumes': len(self.resume_pool),
                'match_count': len(matched_resumes),
                'matched_resumes': matched_resumes,
                'summary': ai_result.get('summary', ''),
                'message': f'找到{len(matched_resumes)}份符合条件的简历'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'查询失败: {str(e)}'
            }
    
    def get_pool_status(self) -> Dict[str, Any]:
        """获取简历池状态"""
        print(f"[批量筛选] 获取池状态: 总数={len(self.resume_pool)}")
        
        resumes_list = []
        for doc_id, data in self.resume_pool.items():
            resume_info = {
                'doc_id': doc_id,
                'filename': data['filename'],
                'name': data['basic_info']['name'],
                'parse_error': data.get('parse_error', False),
                'error_message': data.get('error_message', '')
            }
            resumes_list.append(resume_info)
            print(f"[批量筛选]   - {doc_id}: {data['filename']}")
        
        return {
            'total_count': len(self.resume_pool),
            'resumes': resumes_list
        }
    
    def clear_pool(self) -> Dict[str, Any]:
        """清空简历池"""
        count = len(self.resume_pool)
        self.resume_pool.clear()
        return {
            'success': True,
            'message': f'已清空{count}份简历'
        }
    
    def remove_resume(self, doc_id: str) -> Dict[str, Any]:
        """从池中移除指定简历"""
        if doc_id in self.resume_pool:
            filename = self.resume_pool[doc_id]['filename']
            del self.resume_pool[doc_id]
            return {
                'success': True,
                'message': f'已移除简历: {filename}'
            }
        return {
            'success': False,
            'error': '简历不存在'
        }
