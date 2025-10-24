#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档对话模块 - 直接将PDF发送给大模型进行处理和对话
简单实现，遵循KISS原则
"""

import os
import base64
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from config_manager import get_model_config, is_model_available

load_dotenv()

class DocumentChatAgent:
    """文档对话代理 - 处理PDF并支持对话交互"""
    
    def __init__(self, model_type=None):
        """初始化对话代理"""
        self.model_type = model_type or os.getenv('DEFAULT_AI_MODEL', 'deepseek')
        
        # 检查模型是否可用
        if not is_model_available(self.model_type):
            raise ValueError(f"模型 '{self.model_type}' 不可用或配置不完整")
        
        # 获取模型配置
        config = get_model_config(self.model_type)
        if not config:
            raise ValueError(f"无法获取模型 '{self.model_type}' 的配置")
        
        self.api_key = config['api_key']
        self.base_url = config['base_url']
        self.model = config['model']
        self.display_name = config['display_name']
        
        # 初始化客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        self.conversation_history = {}  # 存储每个文档的对话历史
    
    def read_pdf_as_base64(self, pdf_path: str) -> str:
        """读取PDF文件并转换为base64"""
        try:
            with open(pdf_path, 'rb') as f:
                pdf_content = f.read()
                return base64.b64encode(pdf_content).decode('utf-8')
        except Exception as e:
            raise Exception(f"读取PDF文件失败: {str(e)}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        使用PyPDF2简单提取PDF文本
        这是一个轻量级的备用方案
        """
        try:
            import PyPDF2
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"提取PDF文本失败: {str(e)}"
    
    def analyze_document(self, pdf_path: str, doc_id: str) -> Dict[str, Any]:
        """
        分析PDF文档
        将PDF文本发送给大模型进行初步分析
        
        Args:
            pdf_path: PDF文件路径
            doc_id: 文档ID，用于跟踪对话历史
            
        Returns:
            分析结果
        """
        try:
            # 提取PDF文本
            pdf_text = self.extract_text_from_pdf(pdf_path)
            
            if not pdf_text or pdf_text.startswith("提取PDF文本失败"):
                return {
                    'error': 'PDF文本提取失败',
                    'message': pdf_text
                }
            
            # 初始化对话历史
            self.conversation_history[doc_id] = [
                {
                    "role": "system",
                    "content": "你是一个专业的HR助手，擅长分析简历并回答相关问题。用户上传了一份简历，请仔细分析。"
                },
                {
                    "role": "user",
                    "content": f"这是一份简历的完整内容：\n\n{pdf_text}\n\n请分析这份简历，提取关键信息并总结候选人的情况。"
                }
            ]
            
            # 调用AI分析
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history[doc_id],
                temperature=0.7,
                max_tokens=2000
            )
            
            assistant_message = response.choices[0].message.content
            
            # 保存AI回复到历史
            self.conversation_history[doc_id].append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return {
                'success': True,
                'doc_id': doc_id,
                'analysis': assistant_message,
                'pdf_text_length': len(pdf_text),
                'message': '文档分析完成'
            }
            
        except Exception as e:
            return {
                'error': f'分析文档时出错: {str(e)}'
            }
    
    def chat_with_document(self, doc_id: str, user_message: str) -> Dict[str, Any]:
        """
        基于已上传的文档进行对话
        
        Args:
            doc_id: 文档ID
            user_message: 用户的问题或消息
            
        Returns:
            AI的回复
        """
        try:
            # 检查文档是否已分析
            if doc_id not in self.conversation_history:
                return {
                    'error': '文档未找到，请先上传并分析文档'
                }
            
            # 添加用户消息到历史
            self.conversation_history[doc_id].append({
                "role": "user",
                "content": user_message
            })
            
            # 调用AI获取回复
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history[doc_id],
                temperature=0.7,
                max_tokens=1500
            )
            
            assistant_message = response.choices[0].message.content
            
            # 保存AI回复到历史
            self.conversation_history[doc_id].append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return {
                'success': True,
                'doc_id': doc_id,
                'user_message': user_message,
                'ai_response': assistant_message,
                'conversation_length': len(self.conversation_history[doc_id])
            }
            
        except Exception as e:
            return {
                'error': f'对话时出错: {str(e)}'
            }
    
    def get_conversation_history(self, doc_id: str) -> List[Dict[str, str]]:
        """
        获取对话历史
        
        Args:
            doc_id: 文档ID
            
        Returns:
            对话历史列表
        """
        if doc_id not in self.conversation_history:
            return []
        
        # 返回除了系统消息外的对话历史
        history = []
        for msg in self.conversation_history[doc_id]:
            if msg['role'] != 'system':
                history.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        return history
    
    def clear_conversation(self, doc_id: str) -> bool:
        """
        清除特定文档的对话历史
        
        Args:
            doc_id: 文档ID
            
        Returns:
            是否成功
        """
        if doc_id in self.conversation_history:
            del self.conversation_history[doc_id]
            return True
        return False
