#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
员工福利政策管理和查询模块
功能：批量上传福利政策文档，基于所有文档进行智能问答
"""

import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from resume_analyzer import ResumeAnalyzer  # 复用PDF解析功能

load_dotenv()

class BenefitScreener:
    """员工福利政策管理和查询"""
    
    def __init__(self):
        """初始化"""
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_BASE_URL')
        )
        self.model = os.getenv('OPENAI_MODEL', 'deepseek/deepseek-chat')
        self.document_analyzer = ResumeAnalyzer()  # 复用PDF文本提取
        self.benefit_pool = {}  # 存储福利政策文档池 {doc_id: {文件信息, 文本内容}}
    
    def add_document_to_pool(self, doc_id: str, file_path: str, filename: str) -> Dict[str, Any]:
        """
        将福利政策文档添加到池中（静默处理）
        
        Args:
            doc_id: 文档ID
            file_path: 文件路径
            filename: 原始文件名
            
        Returns:
            确认信息
        """
        try:
            print(f"[福利政策] 开始处理: {filename}")
            
            # 提取PDF文本
            analysis_result = self.document_analyzer.analyze_resume(file_path)
            
            print(f"[福利政策] 解析结果: {list(analysis_result.keys())}")
            
            if 'error' in analysis_result:
                print(f"[福利政策] 解析错误: {analysis_result['error']}")
                self.benefit_pool[doc_id] = {
                    'doc_id': doc_id,
                    'filename': filename,
                    'file_path': file_path,
                    'raw_text': '',
                    'parse_error': True,
                    'error_message': analysis_result.get('error', '解析失败')
                }
                print(f"[福利政策] 已添加(解析失败): {doc_id} -> {filename}")
                return {
                    'success': True,
                    'doc_id': doc_id,
                    'filename': filename,
                    'warning': '文档已添加但解析可能不完整',
                    'message': '文档已添加到福利政策库'
                }
            
            # 存储到政策池
            self.benefit_pool[doc_id] = {
                'doc_id': doc_id,
                'filename': filename,
                'file_path': file_path,
                'raw_text': analysis_result.get('raw_text', ''),
                'parse_error': False
            }
            
            print(f"[福利政策] 已添加(成功): {doc_id} -> {filename}")
            print(f"[福利政策] 当前池大小: {len(self.benefit_pool)}")
            
            return {
                'success': True,
                'doc_id': doc_id,
                'filename': filename,
                'message': '文档已添加到福利政策库'
            }
            
        except Exception as e:
            print(f"[福利政策] 异常: {filename} - {str(e)}")
            import traceback
            traceback.print_exc()
            
            self.benefit_pool[doc_id] = {
                'doc_id': doc_id,
                'filename': filename,
                'file_path': file_path,
                'raw_text': '',
                'parse_error': True,
                'error_message': str(e)
            }
            print(f"[福利政策] 已添加(异常): {doc_id} -> {filename}")
            print(f"[福利政策] 当前池大小: {len(self.benefit_pool)}")
            return {
                'success': True,
                'doc_id': doc_id,
                'filename': filename,
                'warning': f'文档已添加但处理时出错: {str(e)}',
                'message': '文档已添加到福利政策库'
            }
    
    def query_benefits(self, query: str) -> Dict[str, Any]:
        """
        根据自然语言查询福利政策
        
        Args:
            query: 查询问题，如"请假政策是什么？"、"年终奖如何计算？"
            
        Returns:
            AI回答和相关文档信息
        """
        try:
            if not self.benefit_pool:
                return {
                    'success': False,
                    'error': '福利政策库为空，请先上传政策文档'
                }
            
            # 准备所有福利政策文档的完整文本
            documents_data = []
            for doc_id, doc_data in self.benefit_pool.items():
                if not doc_data.get('parse_error', False):
                    full_data = {
                        'doc_id': doc_id,
                        'filename': doc_data['filename'],
                        'content': doc_data['raw_text'][:5000]  # 每份文档最多5000字符
                    }
                    documents_data.append(full_data)
            
            if not documents_data:
                return {
                    'success': False,
                    'error': '所有文档解析失败，无法查询'
                }
            
            # 构建AI提示
            prompt = f"""你是一个专业的HR福利政策助手。我有{len(documents_data)}份员工福利政策文档，员工向你咨询福利相关问题。

员工问题：{query}

以下是所有福利政策文档的完整内容：

{json.dumps(documents_data, ensure_ascii=False, indent=2)}

请仔细阅读所有政策文档的内容（content字段），基于这些文档准确回答员工的问题。

返回JSON格式：
{{
    "answer": "详细的回答内容（基于政策文档）",
    "relevant_documents": ["相关的文档名1", "相关的文档名2"],
    "key_points": ["关键要点1", "关键要点2", "关键要点3"],
    "source_quote": "政策原文引用（如果有）"
}}

注意：
1. 回答要准确、详细，基于实际政策内容
2. 如果多个文档都相关，要综合说明
3. 如果政策中没有相关信息，要明确告知
4. 只返回JSON，不要其他文字"""
            
            # 调用AI分析
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的HR福利政策助手，擅长阅读政策文档并准确回答员工咨询。返回JSON格式结果。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 解析JSON
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
                result_text = result_text.strip()
            
            ai_result = json.loads(result_text)
            
            return {
                'success': True,
                'query': query,
                'answer': ai_result.get('answer', ''),
                'relevant_documents': ai_result.get('relevant_documents', []),
                'key_points': ai_result.get('key_points', []),
                'source_quote': ai_result.get('source_quote', ''),
                'total_documents': len(self.benefit_pool),
                'message': '查询成功'
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f'查询失败: {str(e)}'
            }
    
    def get_pool_status(self) -> Dict[str, Any]:
        """获取福利政策库状态"""
        print(f"[福利政策] 获取池状态: 总数={len(self.benefit_pool)}")
        
        documents_list = []
        for doc_id, data in self.benefit_pool.items():
            doc_info = {
                'doc_id': doc_id,
                'filename': data['filename'],
                'parse_error': data.get('parse_error', False),
                'error_message': data.get('error_message', ''),
                'text_length': len(data.get('raw_text', ''))
            }
            documents_list.append(doc_info)
            print(f"[福利政策]   - {doc_id}: {data['filename']}")
        
        return {
            'total_count': len(self.benefit_pool),
            'documents': documents_list
        }
    
    def clear_pool(self) -> Dict[str, Any]:
        """清空福利政策库"""
        count = len(self.benefit_pool)
        self.benefit_pool.clear()
        return {
            'success': True,
            'message': f'已清空{count}份政策文档'
        }
    
    def remove_document(self, doc_id: str) -> Dict[str, Any]:
        """从池中移除指定文档"""
        if doc_id in self.benefit_pool:
            filename = self.benefit_pool[doc_id]['filename']
            del self.benefit_pool[doc_id]
            return {
                'success': True,
                'message': f'已移除文档: {filename}'
            }
        return {
            'success': False,
            'error': '文档不存在'
        }

