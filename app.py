#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HR简历筛选系统 - 主应用程序
遵循KISS原则，使用Flask轻量级框架
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import sqlite3
from werkzeug.utils import secure_filename
import json
from datetime import datetime
from dotenv import load_dotenv
from resume_analyzer import ResumeAnalyzer
from resume_screener import ResumeScreener
from ai_resume_analyzer import AIResumeAnalyzer
from document_chat import DocumentChatAgent
from batch_screener import BatchResumeScreener
from benefit_screener import BenefitScreener

# 加载环境变量
load_dotenv()

# 初始化代理
chat_agent = DocumentChatAgent()
batch_screener = BatchResumeScreener()
benefit_screener = BenefitScreener()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hr_resume_system_2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect('resumes.db')
    cursor = conn.cursor()
    
    # 创建简历表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            analysis_result TEXT,
            file_path TEXT NOT NULL
        )
    ''')
    
    # 创建筛选记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS screening_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requirements TEXT NOT NULL,
            results TEXT,
            created_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """主页 - Tab化界面"""
    return render_template('home.html')

@app.route('/old')
def old_index():
    """旧版主页 - 简历筛选系统"""
    return render_template('index.html')

@app.route('/chat')
def document_chat():
    """文档对话页面"""
    return render_template('document_chat.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """处理文件上传"""
    if 'files' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    uploaded_files = []
    analyzer = ResumeAnalyzer()
    ai_analyzer = AIResumeAnalyzer()
    use_ai = os.getenv('OPENAI_API_KEY') is not None
    
    for file in files:
        if file and allowed_file(file.filename):
            # 安全的文件名处理
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            unique_filename = timestamp + filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            try:
                # 保存文件
                file.save(file_path)
                
                # 分析简历 - 先用基础分析器提取文本
                analysis_result = analyzer.analyze_resume(file_path)
                
                # 如果配置了AI，使用AI增强分析
                if use_ai and 'raw_text' in analysis_result:
                    ai_result = ai_analyzer.analyze_resume_with_ai(analysis_result['raw_text'])
                    if 'error' not in ai_result:
                        # 合并AI分析结果
                        analysis_result.update(ai_result)
                        analysis_result['ai_enhanced'] = True
                
                # 保存到数据库
                conn = sqlite3.connect('resumes.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO resumes (filename, original_name, analysis_result, file_path)
                    VALUES (?, ?, ?, ?)
                ''', (unique_filename, file.filename, json.dumps(analysis_result, ensure_ascii=False), file_path))
                conn.commit()
                resume_id = cursor.lastrowid
                conn.close()
                
                uploaded_files.append({
                    'id': resume_id,
                    'filename': file.filename,
                    'analysis': analysis_result
                })
                
            except Exception as e:
                return jsonify({'error': f'处理文件 {file.filename} 时出错: {str(e)}'}), 500
        else:
            return jsonify({'error': f'不支持的文件格式: {file.filename}'}), 400
    
    return jsonify({
        'message': f'成功上传 {len(uploaded_files)} 个文件',
        'files': uploaded_files
    })

@app.route('/screen', methods=['POST'])
def screen_resumes():
    """根据需求筛选简历"""
    data = request.get_json()
    if not data or 'requirements' not in data:
        return jsonify({'error': '请输入筛选需求'}), 400
    
    requirements = data['requirements']
    
    try:
        # 获取所有简历
        conn = sqlite3.connect('resumes.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, filename, original_name, analysis_result FROM resumes')
        resumes = cursor.fetchall()
        conn.close()
        
        if not resumes:
            return jsonify({'error': '没有可筛选的简历'}), 400
        
        # 执行筛选
        screener = ResumeScreener()
        ai_analyzer = AIResumeAnalyzer()
        use_ai = os.getenv('OPENAI_API_KEY') is not None
        screening_results = []
        
        for resume in resumes:
            resume_id, filename, original_name, analysis_json = resume
            analysis_result = json.loads(analysis_json) if analysis_json else {}
            
            # 基础筛选
            match_score, match_details = screener.screen_resume(analysis_result, requirements)
            
            # AI增强筛选分析
            ai_insights = None
            if use_ai:
                ai_insights = ai_analyzer.enhance_screening_with_ai(analysis_result, requirements)
                # 如果AI给出了评分，可以与基础评分结合
                if 'match_score' in ai_insights and 'error' not in ai_insights:
                    # 综合评分：基础评分70% + AI评分30%
                    match_score = match_score * 0.7 + ai_insights['match_score'] * 0.3
            
            screening_results.append({
                'id': resume_id,
                'filename': original_name,
                'match_score': round(match_score, 2),
                'match_details': match_details,
                'ai_insights': ai_insights,  # 添加AI洞察
                'analysis': analysis_result
            })
        
        # 按匹配度排序
        screening_results.sort(key=lambda x: x['match_score'], reverse=True)
        
        # 保存筛选记录
        conn = sqlite3.connect('resumes.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO screening_records (requirements, results)
            VALUES (?, ?)
        ''', (requirements, json.dumps(screening_results, ensure_ascii=False)))
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': '筛选完成',
            'requirements': requirements,
            'results': screening_results,
            'total_count': len(screening_results)
        })
        
    except Exception as e:
        return jsonify({'error': f'筛选过程中出错: {str(e)}'}), 500

@app.route('/resumes')
def list_resumes():
    """获取所有简历列表"""
    conn = sqlite3.connect('resumes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, original_name, upload_time, analysis_result FROM resumes ORDER BY upload_time DESC')
    resumes = cursor.fetchall()
    conn.close()
    
    resume_list = []
    for resume in resumes:
        resume_id, original_name, upload_time, analysis_json = resume
        analysis_result = json.loads(analysis_json) if analysis_json else {}
        
        resume_list.append({
            'id': resume_id,
            'filename': original_name,
            'upload_time': upload_time,
            'summary': {
                'name': analysis_result.get('name', '未识别'),
                'experience_years': analysis_result.get('experience_years', 0),
                'skills_count': len(analysis_result.get('skills', []))
            }
        })
    
    return jsonify(resume_list)

@app.route('/resume/<int:resume_id>')
def get_resume_detail(resume_id):
    """获取简历详情"""
    conn = sqlite3.connect('resumes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT original_name, upload_time, analysis_result FROM resumes WHERE id = ?', (resume_id,))
    resume = cursor.fetchone()
    conn.close()
    
    if not resume:
        return jsonify({'error': '简历不存在'}), 404
    
    original_name, upload_time, analysis_json = resume
    analysis_result = json.loads(analysis_json) if analysis_json else {}
    
    return jsonify({
        'id': resume_id,
        'filename': original_name,
        'upload_time': upload_time,
        'analysis': analysis_result
    })

@app.route('/api/upload_document', methods=['POST'])
def api_upload_document():
    """API: 上传文档并分析"""
    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': '只支持PDF格式'}), 400
    
    try:
        # 保存文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        unique_filename = timestamp + filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # 生成文档ID
        doc_id = unique_filename.replace('.pdf', '')
        
        # 使用AI分析文档
        result = chat_agent.analyze_document(file_path, doc_id)
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'处理文档时出错: {str(e)}'}), 500

@app.route('/api/chat_with_document', methods=['POST'])
def api_chat_with_document():
    """API: 与文档对话"""
    data = request.get_json()
    
    if not data or 'doc_id' not in data or 'message' not in data:
        return jsonify({'error': '缺少必要参数'}), 400
    
    doc_id = data['doc_id']
    message = data['message']
    
    try:
        result = chat_agent.chat_with_document(doc_id, message)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'对话时出错: {str(e)}'}), 500

@app.route('/api/clear_conversation', methods=['POST'])
def api_clear_conversation():
    """API: 清除对话历史"""
    data = request.get_json()
    
    if not data or 'doc_id' not in data:
        return jsonify({'error': '缺少文档ID'}), 400
    
    doc_id = data['doc_id']
    success = chat_agent.clear_conversation(doc_id)
    
    return jsonify({
        'success': success,
        'message': '对话已清除' if success else '文档不存在'
    })

@app.route('/api/conversation_history/<doc_id>')
def api_get_conversation_history(doc_id):
    """API: 获取对话历史"""
    history = chat_agent.get_conversation_history(doc_id)
    return jsonify({
        'doc_id': doc_id,
        'history': history,
        'count': len(history)
    })

# ============= 批量筛选相关API =============

@app.route('/api/batch_add_resume', methods=['POST'])
def api_batch_add_resume():
    """API: 添加简历到批量筛选池（静默处理）"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '没有选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '没有选择文件'}), 400
    
    # 支持PDF和TXT格式
    allowed_extensions = ['.pdf', '.txt']
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        return jsonify({'success': False, 'error': '只支持PDF和TXT格式'}), 400
    
    try:
        # 保存原始文件名（包含中文）
        original_filename = file.filename
        
        # 获取文件扩展名
        file_extension = os.path.splitext(original_filename)[1].lower()
        
        # 生成安全的文件名用于存储（使用时间戳+随机数）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        import random
        safe_filename = f"{timestamp}{random.randint(1000, 9999)}{file_extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(file_path)
        
        # 生成文档ID（移除扩展名）
        doc_id = os.path.splitext(safe_filename)[0]
        
        # 添加到简历池（使用原始文件名显示，而不是safe_filename）
        result = batch_screener.add_resume_to_pool(doc_id, file_path, original_filename)
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"批量上传错误: {error_detail}")  # 打印到控制台
        return jsonify({'success': False, 'error': f'处理文件时出错: {str(e)}'}), 500

@app.route('/api/batch_query', methods=['POST'])
def api_batch_query():
    """API: 根据自然语言查询筛选简历"""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'success': False, 'error': '缺少查询参数'}), 400
    
    query = data['query']
    
    try:
        result = batch_screener.query_resumes(query)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'查询失败: {str(e)}'}), 500

@app.route('/api/batch_pool_status')
def api_batch_pool_status():
    """API: 获取简历池状态"""
    try:
        status = batch_screener.get_pool_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': f'获取状态失败: {str(e)}'}), 500

@app.route('/api/batch_clear_pool', methods=['POST'])
def api_batch_clear_pool():
    """API: 清空简历池"""
    try:
        result = batch_screener.clear_pool()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'清空失败: {str(e)}'}), 500

@app.route('/api/batch_remove_resume', methods=['POST'])
def api_batch_remove_resume():
    """API: 从池中移除指定简历"""
    data = request.get_json()
    
    if not data or 'doc_id' not in data:
        return jsonify({'success': False, 'error': '缺少文档ID'}), 400
    
    try:
        result = batch_screener.remove_resume(data['doc_id'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'移除失败: {str(e)}'}), 500

@app.route('/api/download_resume/<doc_id>')
def api_download_resume(doc_id):
    """API: 下载简历文件"""
    try:
        # 从简历池获取文件信息
        if doc_id not in batch_screener.resume_pool:
            return jsonify({'error': '简历不存在'}), 404
        
        resume_data = batch_screener.resume_pool[doc_id]
        file_path = resume_data['file_path']
        original_filename = resume_data['filename']
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        # 发送文件
        from flask import send_file
        return send_file(
            file_path,
            as_attachment=True,
            download_name=original_filename,  # 使用原始文件名
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

# ==================== 员工福利政策相关接口 ====================

@app.route('/api/benefit_add_document', methods=['POST'])
def api_benefit_add_document():
    """API: 添加福利政策文档到库中（静默处理）"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '没有选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '没有选择文件'}), 400
    
    # 支持PDF和TXT格式
    allowed_extensions = ['.pdf', '.txt']
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        return jsonify({'success': False, 'error': '只支持PDF和TXT格式'}), 400
    
    try:
        # 保存原始文件名（包含中文）
        original_filename = file.filename
        
        # 获取文件扩展名
        file_extension = os.path.splitext(original_filename)[1].lower()
        
        # 生成安全的文件名用于存储
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        import random
        safe_filename = f"benefit_{timestamp}{random.randint(1000, 9999)}{file_extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(file_path)
        
        # 生成文档ID（移除扩展名）
        doc_id = os.path.splitext(safe_filename)[0]
        
        # 添加到福利政策库
        result = benefit_screener.add_document_to_pool(doc_id, file_path, original_filename)
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"福利政策上传错误: {error_detail}")
        return jsonify({'success': False, 'error': f'处理文件时出错: {str(e)}'}), 500

@app.route('/api/benefit_query', methods=['POST'])
def api_benefit_query():
    """API: 查询福利政策"""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'success': False, 'error': '缺少查询内容'}), 400
    
    try:
        result = benefit_screener.query_benefits(data['query'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'查询失败: {str(e)}'}), 500

@app.route('/api/benefit_pool_status')
def api_benefit_pool_status():
    """API: 获取福利政策库状态"""
    try:
        result = benefit_screener.get_pool_status()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'获取状态失败: {str(e)}'}), 500

@app.route('/api/benefit_clear_pool', methods=['POST'])
def api_benefit_clear_pool():
    """API: 清空福利政策库"""
    try:
        result = benefit_screener.clear_pool()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'清空失败: {str(e)}'}), 500

@app.route('/api/benefit_remove_document', methods=['POST'])
def api_benefit_remove_document():
    """API: 从库中移除指定文档"""
    data = request.get_json()
    
    if not data or 'doc_id' not in data:
        return jsonify({'success': False, 'error': '缺少文档ID'}), 400
    
    try:
        result = benefit_screener.remove_document(data['doc_id'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'移除失败: {str(e)}'}), 500

@app.route('/api/download_benefit/<doc_id>')
def api_download_benefit(doc_id):
    """API: 下载福利政策文档"""
    try:
        # 从福利政策库获取文件信息
        if doc_id not in benefit_screener.benefit_pool:
            return jsonify({'error': '文档不存在'}), 404
        
        doc_data = benefit_screener.benefit_pool[doc_id]
        file_path = doc_data['file_path']
        original_filename = doc_data['filename']
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        # 发送文件
        from flask import send_file
        return send_file(
            file_path,
            as_attachment=True,
            download_name=original_filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5001)

