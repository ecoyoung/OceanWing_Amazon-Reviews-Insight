import streamlit as st
import re

# 设置页面配置必须是第一个st命令
st.set_page_config(
    page_title="Amazon评论分析 - 关键词匹配",
    page_icon="🔍",
    layout="wide"
)

import pandas as pd
import json
import os
from collections import defaultdict
import plotly.graph_objects as go

# 预设人群类别和关键词
PRESET_CATEGORIES = {
    "人群画像": {
        "儿童或青少年": "kids,girl,girls,boy,boys,children,teen,picky eater,child-friendly,baby,sugar coating,candy-like,my daughter,my son",
        "孕妇或哺乳期女性": "pregnant,pregnancy,nursing,breastfeeding,menstrual,period,hormonal support,prenatal,postpartum,label says do not use during pregnancy",
        "素食者或健康饮食者": "vegan,vegetarian,plant-based,no artificial,no gluten,no high fructose corn syrup,organic,non-GMO,natural ingredients,sugar-free,low sugar,stevia",
        "健身运动人群": "fitness,exercise,training,athlete,workout,gym,sports,muscle,strength,endurance,protein,Boosts endurance,Boosts strength"
    },
    "购买动机": {
        "消化系统健康": "digestive, gut, bloating, fiber, strains,GI"
    },
    "用户痛点": {
        "产品效果痛点": "ineffective,not effective,doesn't work,no results,didn't notice any change,no effect,no improvement,didn't help,weak effect,didn't feel anything,too mild,lack of results,unnoticeable change,not strong enough",
        "健康改善痛点": "still tired,no energy,constantly sick,weak immune system,didn't boost energy,low stamina,fatigue persists,feel drained,didn't help recovery,always exhausted,immunity not improved,keeps getting sick",
        "口感与体验痛点": "bad taste,terrible flavor,unpleasant aftertaste,tastes bad,too bitter,tastes like medicine,chemical taste,weird smell,chalky,grainy,hard to swallow,too sweet,artificial taste,nauseating flavor",
        "症状缓解痛点": "cough didn't go away,still congested,no relief,breathing issues remain,didn't ease symptoms,no change in cough,mucus still there,asthma got worse,sinuses still blocked,chest still tight,didn't help with colds",
        "包装与便利性痛点": "too small,not enough doses,bottle leaks,poorly designed packaging,hard to open,messy to use,inconvenient size,not portable,dosage unclear,ran out quickly,frequent repurchase,short supply,not user-friendly",
        "天然与安全性痛点": "contains chemicals,artificial ingredients,synthetic fillers,caused reaction,allergic response,unsafe formula,questionable ingredients,not natural,GMO concern,unclear label,hidden additives,harsh ingredients",
        "消费者体验与反馈痛点": "bad reviews,low rating,not recommended,disappointed,didn't meet expectations,poor experience,wouldn't buy again,waste of money,overhyped,felt scammed,not as described,unreliable product,inconsistent results"
    }
}

def load_categories():
    """从文件加载已保存的类别和关键词"""
    if os.path.exists('categories.json'):
        with open('categories.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 处理旧格式的数据
            if isinstance(data, dict) and all(isinstance(v, str) for v in data.values()):
                # 将旧格式转换为新格式
                new_data = {
                    "人群画像": {},
                    "购买动机": {},
                    "用户痛点": {}
                }
                for category, keywords in data.items():
                    if category in PRESET_CATEGORIES["人群画像"]:
                        new_data["人群画像"][category] = keywords
                    elif category in PRESET_CATEGORIES["购买动机"]:
                        new_data["购买动机"][category] = keywords
                    else:
                        new_data["用户痛点"][category] = keywords
                return new_data
            return data
    return {"人群画像": {}, "购买动机": {}, "用户痛点": {}}

def save_categories(categories):
    """保存类别和关键词到文件"""
    with open('categories.json', 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

def process_keywords(keywords_text):
    """处理关键词文本"""
    if not keywords_text:
        return []
    
    # 使用更高效的文本处理
    keywords = [k.strip() for k in keywords_text.split('\n') if k.strip()]
    # 使用集合去重
    return list(set(keywords))

def find_matches(text, keywords):
    """查找文本中的关键词匹配"""
    if pd.isna(text):
        return []
    
    text = str(text).lower()
    # 使用集合操作提高效率
    return [k for k in keywords if k.lower() in text]

def analyze_keyword_matches(df, keywords):
    """分析关键词匹配"""
    # 使用向量化操作处理文本
    df['Matches'] = df['Content'].apply(lambda x: find_matches(x, keywords))
    df['Match_Count'] = df['Matches'].str.len()
    
    # 计算匹配统计
    total_reviews = len(df)
    matched_reviews = (df['Match_Count'] > 0).sum()
    match_rate = matched_reviews / total_reviews * 100
    
    # 使用更高效的分组统计
    rating_stats = df[df['Match_Count'] > 0].groupby('Rating')['Match_Count'].agg(['count', 'mean']).round(2)
    rating_stats.columns = ['评论数', '平均匹配数']
    
    return {
        'total_reviews': total_reviews,
        'matched_reviews': matched_reviews,
        'match_rate': match_rate,
        'rating_stats': rating_stats
    }

def create_match_visualization(df, keywords):
    """创建匹配可视化"""
    # 使用更高效的数据处理
    match_data = df[df['Match_Count'] > 0].copy()
    
    # 创建匹配词云
    word_freq = {}
    for matches in match_data['Matches']:
        for word in matches:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # 使用更高效的图表创建
    fig = go.Figure()
    
    # 添加匹配分布
    fig.add_trace(go.Bar(
        x=match_data['Rating'].value_counts().index,
        y=match_data['Rating'].value_counts().values,
        name='匹配评论数',
        marker_color='#2E86AB'
    ))
    
    fig.update_layout(
        title='关键词匹配分布',
        xaxis_title='评分',
        yaxis_title='评论数',
        showlegend=True,
        template='plotly_white'
    )
    
    return fig, word_freq

def analyze_reviews(df, categories):
    """分析评论并进行分类"""
    # 创建结果DataFrame，保留ID列
    results = pd.DataFrame()
    results['ID'] = df['ID']  # 保留原始ID
    results['Content'] = df['Content']
    results['Original Review Type'] = df['Review Type']
    
    # 为每个类别创建一列
    for main_category, sub_categories in categories.items():
        if isinstance(sub_categories, dict):  # 新格式
            for sub_category, keywords in sub_categories.items():
                # 将关键词字符串转换为列表
                keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
                results[f'Is {main_category} - {sub_category}'] = df['Content'].apply(
                    lambda x: len(find_matches(x, keyword_list)) > 0
                )
        else:  # 旧格式
            # 将关键词字符串转换为列表
            keyword_list = [k.strip() for k in sub_categories.split(',') if k.strip()]
            results[f'Is {main_category}'] = df['Content'].apply(
                lambda x: len(find_matches(x, keyword_list)) > 0
            )
    
    # 统计每个类别的匹配数量
    stats = {}
    for main_category, sub_categories in categories.items():
        stats[main_category] = {}
        if isinstance(sub_categories, dict):  # 新格式
            for sub_category in sub_categories:
                matched = results[f'Is {main_category} - {sub_category}'].sum()
                stats[main_category][sub_category] = {
                    'matched': int(matched),
                    'percentage': round(matched / len(df) * 100, 2)
                }
        else:  # 旧格式
            matched = results[f'Is {main_category}'].sum()
            stats[main_category] = {
                'matched': int(matched),
                'percentage': round(matched / len(df) * 100, 2)
            }
    
    return results, stats

def analyze_keyword_frequency(df, categories):
    """分析每个类别的关键词匹配频率"""
    keyword_stats = {}
    
    for main_category, sub_categories in categories.items():
        keyword_stats[main_category] = {}
        if isinstance(sub_categories, dict):  # 新格式
            for sub_category, keywords in sub_categories.items():
                # 将关键词字符串转换为列表
                keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
                # 统计每个关键词的匹配次数
                keyword_freq = defaultdict(int)
                for content in df['Content']:
                    matches = find_matches(content, keyword_list)
                    for match in matches:
                        keyword_freq[match] += 1
                
                # 转换为DataFrame并排序
                if keyword_freq:
                    freq_df = pd.DataFrame({
                        '关键词': list(keyword_freq.keys()),
                        '匹配次数': list(keyword_freq.values())
                    })
                    freq_df = freq_df.sort_values('匹配次数', ascending=False)
                    keyword_stats[main_category][sub_category] = freq_df
                else:
                    keyword_stats[main_category][sub_category] = pd.DataFrame(columns=['关键词', '匹配次数'])
    
    return keyword_stats

def main():
    # 页面标题和样式
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5em;
        margin-bottom: 0.5em;
        font-weight: bold;
    }
    .sub-header {
        text-align: center;
        color: #A23B72;
        font-size: 1.2em;
        margin-bottom: 2em;
    }
    .category-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .preset-category {
        background-color: #e7f3ff;
        border-left: 4px solid #2E86AB;
    }
    .stats-card {
        background-color: #fff;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header">🔍 Amazon评论分析 - 关键词匹配</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">基于关键词匹配的评论分类分析工具</div>', unsafe_allow_html=True)
    
    # 加载已保存的类别
    categories = load_categories()
    
    # 侧边栏：预设类别快速导入
    with st.sidebar:
        st.markdown("### 🎯 预设类别")
        st.markdown("---")
        
        for main_category, sub_categories in PRESET_CATEGORIES.items():
            st.markdown(f"#### {main_category}")
            for sub_category, keywords in sub_categories.items():
                with st.container():
                    st.markdown(f"**{sub_category}**")
                    
                    # 显示关键词预览
                    preview_keywords = keywords.split(',')[:5]
                    preview_text = ', '.join(preview_keywords)
                    if len(keywords.split(',')) > 5:
                        preview_text += f"... (共{len(keywords.split(','))}个关键词)"
                    
                    st.markdown(f"<small style='color: #666;'>{preview_text}</small>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"一键导入", key=f"import_{main_category}_{sub_category}"):
                            if main_category not in categories:
                                categories[main_category] = {}
                            categories[main_category][sub_category] = keywords
                            save_categories(categories)
                            st.success("导入成功！")
                            st.rerun()
                    
                    with col2:
                        if main_category in categories and sub_category in categories[main_category]:
                            st.markdown("✅ 已导入")
                        else:
                            st.markdown("⭕ 未导入")
                    
                    st.markdown("---")
    
    # 主要内容区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 类别管理")
        
        # 添加新类别
        with st.container():
            st.markdown("#### 手动添加自定义类别")
            col_input, col_btn = st.columns([3, 1])
            
            with col_input:
                new_category = st.text_input("输入类别名称", placeholder="例如：慢性病老年人、孕期女性用户等")
                category_type = st.selectbox("选择类别类型", ["人群画像", "购买动机", "用户痛点"])
            
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)  # 对齐按钮
                if st.button("添加类别", type="primary") and new_category:
                    if category_type not in categories:
                        categories[category_type] = {}
                    if new_category not in categories[category_type]:
                        categories[category_type][new_category] = ""
                        save_categories(categories)
                        st.success(f"✅ 已添加类别: {new_category}")
                        st.rerun()
                    else:
                        st.warning("⚠️ 该类别已存在！")
    
    with col2:
        if categories:
            st.markdown("### 📊 当前统计")
            st.metric("已配置类别", sum(len(sub_cats) for sub_cats in categories.values()))
            
            # 显示类别概览
            category_summary = []
            for main_cat, sub_cats in categories.items():
                for sub_cat, keywords in sub_cats.items():
                    keyword_count = len([k for k in keywords.split(',') if k.strip()]) if keywords else 0
                    category_summary.append({
                        "主类别": main_cat,
                        "子类别": sub_cat,
                        "关键词数": keyword_count
                    })
            
            if category_summary:
                summary_df = pd.DataFrame(category_summary)
                st.dataframe(summary_df, use_container_width=True)
    
    # 显示和编辑现有类别
    if categories:
        st.markdown("### ✏️ 编辑类别和关键词")
        
        edited_categories = {"人群画像": {}, "购买动机": {}, "用户痛点": {}}
        
        for main_category, sub_categories in categories.items():
            st.markdown(f"#### {main_category}")
            for sub_category, keywords in sub_categories.items():
                # 判断是否为预设类别
                is_preset = (main_category in PRESET_CATEGORIES and 
                           sub_category in PRESET_CATEGORIES[main_category])
                card_class = "category-card preset-category" if is_preset else "category-card"
                
                st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([2, 6, 1])
                
                with col1:
                    if is_preset:
                        st.markdown(f"**🎯 {sub_category}**")
                        st.markdown("<small style='color: #2E86AB;'>预设类别</small>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**📝 {sub_category}**")
                        st.markdown("<small style='color: #666;'>自定义类别</small>", unsafe_allow_html=True)
                
                with col2:
                    keywords = st.text_area(
                        "关键词（用逗号分隔）",
                        value=keywords,
                        key=f"keywords_{main_category}_{sub_category}",
                        help="输入多个关键词，用逗号分隔。支持英文西语关键词。",
                        height=80
                    )
                    edited_categories[main_category][sub_category] = keywords
                    
                    # 显示关键词统计
                    if keywords:
                        keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
                        st.markdown(f"<small style='color: #666;'>共 {len(keyword_list)} 个关键词</small>", 
                                  unsafe_allow_html=True)
                
                with col3:
                    st.markdown("<br><br>", unsafe_allow_html=True)  # 对齐按钮
                    if st.button("🗑️", key=f"delete_{main_category}_{sub_category}", help="删除此类别"):
                        del categories[main_category][sub_category]
                        if not categories[main_category]:  # 如果主类别为空，也删除主类别
                            del categories[main_category]
                        save_categories(categories)
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # 如果关键词有修改，保存更新
        if edited_categories != categories:
            categories = edited_categories
            save_categories(categories)
        
        # 文件上传和分析
        st.markdown("---")
        st.markdown("### 📊 评论分析")
        
        uploaded_file = st.file_uploader(
            "选择预处理后的Excel文件", 
            type=['xlsx'],
            help="请上传包含ID、Content和Review Type列的Excel文件"
        )
        
        if uploaded_file is not None:
            try:
                with st.spinner('正在处理文件...'):
                    df = pd.read_excel(uploaded_file)
                
                # 验证文件格式
                required_columns = ['ID', 'Content', 'Review Type']
                if not all(col in df.columns for col in required_columns):
                    st.error("❌ 请上传包含ID、Content和Review Type列的预处理文件！")
                    return
                
                st.success(f"✅ 文件上传成功！共 {len(df)} 条评论")
                
                # 分析评论
                with st.spinner('正在分析评论...'):
                    results, stats = analyze_reviews(df, categories)
                
                # 显示统计信息
                st.markdown("### 📈 匹配统计结果")
                
                # 创建美观的统计卡片
                all_stats = []
                for main_category, sub_categories in stats.items():
                    for sub_category, stat in sub_categories.items():
                        all_stats.append({
                            'category': f"{main_category} - {sub_category}",
                            'matched': stat['matched'],
                            'percentage': stat['percentage']
                        })
                
                # 每行显示4个统计卡片
                cols = st.columns(min(len(all_stats), 4))
                for i, stat in enumerate(all_stats):
                    with cols[i % 4]:
                        st.markdown(f"""
                        <div class="stats-card">
                            <h4 style="color: #2E86AB; margin: 0;">{stat['category']}</h4>
                            <h2 style="color: #A23B72; margin: 0.5rem 0;">{stat['matched']}</h2>
                            <p style="color: #666; margin: 0;">匹配率: {stat['percentage']}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # 详细统计表格
                stats_df = pd.DataFrame([
                    {
                        '主类别': main_category,
                        '子类别': sub_category,
                        '匹配数量': stats[main_category][sub_category]['matched'],
                        '匹配比例': f"{stats[main_category][sub_category]['percentage']}%",
                        '未匹配数量': len(df) - stats[main_category][sub_category]['matched']
                    }
                    for main_category in stats
                    for sub_category in stats[main_category]
                ])
                
                st.markdown("#### 📋 详细统计表")
                st.dataframe(stats_df, use_container_width=True)
                
                # 显示详细结果
                st.markdown("### 📄 详细分析结果")
                
                # 添加关键词匹配统计
                st.markdown("### 🔍 关键词匹配统计")
                keyword_freq_stats = analyze_keyword_frequency(df, categories)
                
                # 为每个类别创建选项卡
                tabs = st.tabs(list(keyword_freq_stats.keys()))
                
                for tab, main_category in zip(tabs, keyword_freq_stats.keys()):
                    with tab:
                        st.markdown(f"#### {main_category}关键词匹配统计")
                        for sub_category, freq_df in keyword_freq_stats[main_category].items():
                            if not freq_df.empty:
                                st.markdown(f"**{sub_category}**")
                                # 显示前10个最常匹配的关键词
                                top_keywords = freq_df.head(10)
                                
                                # 创建柱状图
                                fig = go.Figure(data=[
                                    go.Bar(
                                        x=top_keywords['关键词'],
                                        y=top_keywords['匹配次数'],
                                        marker_color='#2E86AB'
                                    )
                                ])
                                
                                fig.update_layout(
                                    title=f"{sub_category} - 关键词匹配频率",
                                    xaxis_title="关键词",
                                    yaxis_title="匹配次数",
                                    showlegend=False,
                                    height=400
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # 显示详细数据表格
                                with st.expander("查看完整数据"):
                                    st.dataframe(freq_df, use_container_width=True)
                            else:
                                st.info(f"{sub_category} 没有匹配的关键词")
                
                # 添加筛选选项
                col1, col2 = st.columns(2)
                with col1:
                    show_all = st.checkbox("显示所有记录", value=True)
                
                with col2:
                    if not show_all:
                        # 创建类别选择列表
                        category_options = [
                            f"{main_category} - {sub_category}"
                            for main_category in categories
                            for sub_category in categories[main_category]
                        ]
                        selected_category = st.selectbox(
                            "选择要查看的类别",
                            options=category_options
                        )
                
                # 根据筛选条件显示结果
                if show_all:
                    st.dataframe(results, use_container_width=True)
                else:
                    filtered_results = results[results[f'Is {selected_category}'] == True]
                    st.dataframe(filtered_results, use_container_width=True)
                    st.info(f"显示 {len(filtered_results)} 条匹配 '{selected_category}' 的记录")
                
            except Exception as e:
                st.error(f"❌ 处理文件时出错: {str(e)}")
    else:
        st.info("👆 请先从侧边栏导入预设类别或添加自定义类别")

if __name__ == "__main__":
    main()