import streamlit as st
import pandas as pd
from utils import (
    calculate_review_stats,
    create_pie_chart,
    analyze_by_group,
    create_rating_heatmap,
    create_rating_trend_chart,
    save_fig_to_html,
    create_rating_pie_chart
)
import plotly.express as px
import plotly.graph_objects as go

# 设置页面配置
st.set_page_config(
    page_title="Amazon评论分析 - 统计分析",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 统一风格设计
st.markdown("""
<style>
    /* 主标题样式 */
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5em;
        margin-bottom: 0.5em;
        font-weight: bold;
    }
    
    /* 副标题样式 */
    .sub-header {
        text-align: center;
        color: #A23B72;
        font-size: 1.2em;
        margin-bottom: 2em;
    /* 卡片样式 */
    .card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    
    /* 统计卡片样式 */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        text-align: center;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #2E86AB;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin-top: 0.5rem;
    }
    
    /* 按钮样式优化 */
    .stButton > button {
        background: linear-gradient(90deg, #2E86AB, #4a90e2);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #1C6E9C, #357abd);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* 下载按钮样式 */
    .stDownloadButton > button {
        background: linear-gradient(90deg, #A23B72, #c55a9b) !important;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(90deg, #8A2A5F, #b14986) !important;
    }
    
    /* 图表容器样式 */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
    }
    
    /* 信息提示样式 */
    .info-box {
        background-color: #e7f3ff;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-left: 4px solid #2E86AB;
    }
    
    /* 侧边栏样式 */
    .sidebar-content {
        background-color: #f0f8ff;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* 选项卡样式 */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f0f8ff;
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        margin: 0 0.25rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2E86AB !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

def create_overall_trend_chart(df):
    """创建整体评分趋势图"""
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    trend_data = df.groupby('Month')['Rating'].mean().reset_index()
    
    fig = px.line(trend_data, 
                  x='Month', 
                  y='Rating',
                  title='📈 整体评分趋势分析',
                  labels={'Rating': '平均评分', 'Month': '月份'},
                  line_shape='spline')
    
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    fig.update_layout(
        title_font_size=18,
        title_x=0.5,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray')
    )
    fig.update_xaxes(tickangle=45)
    return fig

def main():
    # 页面标题
    st.markdown('<div class="main-header">📈 Amazon评论分析 - 统计分析</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">评论基本统计分析</div>', unsafe_allow_html=True)
    # 使用侧边栏进行导航
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown("### 📋 分析步骤")
        st.markdown("""
        1. **数据上传** 📤
        2. **数据验证** ✅
        3. **基本统计分析** 📊
        4. **可视化展示** 📈
        5. **结果下载** 💾
        """)
        
        st.markdown("---")
        st.markdown("### ℹ️ 使用说明")
        st.info("请上传经过预处理的Excel文件，系统将自动进行评论统计分析和可视化展示。")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 主要内容区域
   
   
    
    # 文件上传部分

    with st.container():
        st.markdown("### 📤 上传数据文件")
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "选择预处理后的Excel文件", 
            type=['xlsx'],
            help="请确保文件包含必要的列：ID, Asin, Title, Content, Model, Rating, Date, Review Type"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file is not None:
        try:
            # 显示文件信息
            st.success("✅ 文件上传成功！正在处理数据...")
            
            with st.spinner('正在加载和验证数据...'):
                df = pd.read_excel(uploaded_file)
            
            # 验证是否是预处理后的文件
            required_columns = ['ID', 'Asin', 'Title', 'Content', 'Model', 'Rating', 'Date', 'Review Type']
            if not all(col in df.columns for col in required_columns):
                st.error("❌ 请上传预处理后的文件！预处理后的文件应包含以下列：" + ", ".join(required_columns))
                return
            
            # 显示数据基本信息
            st.markdown('<div class="sub-header">📊 数据概览</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{len(df)}</div>
                    <div class="stat-label">📈 数据行数</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{df['Rating'].mean():.2f}</div>
                    <div class="stat-label">⭐ 平均评分</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{df['Asin'].nunique()}</div>
                    <div class="stat-label">🏷️ ASIN数量</div>
                </div>
                """, unsafe_allow_html=True)
                
                date_min = df['Date'].min().strftime('%Y-%m')
                date_max = df['Date'].max().strftime('%Y-%m')
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{date_min} 至 {date_max}</div>
                    <div class="stat-label">📅 时间范围</div>
                </div>
                """, unsafe_allow_html=True)
            
            # 整体评论分析
            st.markdown('<div class="sub-header">📈 整体评论分析</div>', unsafe_allow_html=True)
            
            # 安全地获取统计数据
            try:
                stats_df, review_counts, review_percentages = calculate_review_stats(df)
                
                # 饼图和详细统计表
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    pie_chart = create_pie_chart(review_counts)
                    st.plotly_chart(pie_chart, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.markdown("**📋 详细统计表**")
                    st.dataframe(stats_df, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
            except Exception as stats_error:
                st.warning(f"⚠️ 统计分析遇到问题: {str(stats_error)}")
                st.info("正在使用基础统计信息...")
                
                # 基础统计作为备选方案
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("总评论数", len(df))
                with col2:
                    high_rating = len(df[df['Rating'] >= 4])
                    st.metric("高评分(4-5星)", high_rating)
                with col3:
                    low_rating = len(df[df['Rating'] <= 2])
                    st.metric("低评分(1-2星)", low_rating)
                with col4:
                    avg_rating = df['Rating'].mean()
                    st.metric("平均评分", f"{avg_rating:.2f}")
                
                # 创建简单的评分分布图
                rating_counts = df['Rating'].value_counts().sort_index()
                fig_simple = px.bar(x=rating_counts.index, y=rating_counts.values,
                                  title="评分分布", labels={'x': '评分', 'y': '数量'})
                st.plotly_chart(fig_simple, use_container_width=True)
                
                # 为后续使用设置默认值
                pie_chart = fig_simple
            
            # 详细分析部分
            st.markdown('<div class="sub-header">🔍 详细分析</div>', unsafe_allow_html=True)
            
            # 使用选项卡来组织不同的分析
            tab1, tab2, tab3 = st.tabs(["📊 基础分析", "🔥 星级分析", "📈 时序分析"])
            
            with tab1:
                with st.container():
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    analysis_type = st.selectbox(
                        "选择基础分析维度",
                        ["按Asin分析", "按Brand分析", "按Asin+Model组合分析", "按Brand+Asin+Model组合分析"],
                        help="选择不同的维度来查看评论统计"
                    )
                    
                    if analysis_type == "按Asin分析":
                        group_by = 'Asin'
                        display_name = "ASIN"
                    elif analysis_type == "按Brand分析":
                        group_by = 'Brand'
                        display_name = "品牌"
                    elif analysis_type == "按Asin+Model组合分析":
                        group_by = ['Asin', 'Model']
                        display_name = "ASIN-Model组合"
                    else:  # Brand+Asin+Model组合分析
                        group_by = ['Brand', 'Asin', 'Model']
                        display_name = "品牌-ASIN-Model组合"
                    
                    # 获取分组分析结果
                    try:
                        group_stats, rating_dist_pct, group_by_trend = analyze_by_group(df, group_by)
                        
                        # 显示统计信息
                        st.markdown(f"**📊 {display_name}评分统计信息：**")
                        st.dataframe(group_stats, use_container_width=True)
                    except Exception as group_error:
                        st.warning(f"⚠️ 分组分析出现问题: {str(group_error)}")
                        st.info("显示基础分组统计...")
                        
                        # 基础分组统计
                        if isinstance(group_by, list):
                            if all(col in df.columns for col in group_by):
                                basic_stats = df.groupby(group_by)['Rating'].agg(['count', 'mean', 'std']).round(2)
                            else:
                                st.error("数据中缺少必要的列")
                                basic_stats = pd.DataFrame()
                        else:
                            if group_by in df.columns:
                                basic_stats = df.groupby(group_by)['Rating'].agg(['count', 'mean', 'std']).round(2)
                            else:
                                st.error("数据中缺少必要的列")
                                basic_stats = pd.DataFrame()
                        
                        if not basic_stats.empty:
                            st.dataframe(basic_stats, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with tab2:
                with st.container():
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    pie_dimension = st.radio(
                        "选择评分分布分析维度",
                        ["按Asin分析", "按Brand分析", "按Asin+Model组合分析", "按Brand+Asin+Model组合分析"],
                        key="pie_dimension",
                        help="饼图可以直观显示不同维度的评分分布"
                    )
                    
                    # 根据选择的维度重新计算数据
                    if pie_dimension == "按Asin分析":
                        pie_group_by = 'Asin'
                        pie_display_name = "ASIN"
                    elif pie_dimension == "按Brand分析":
                        pie_group_by = 'Brand'
                        pie_display_name = "品牌"
                    elif pie_dimension == "按Asin+Model组合分析":
                        pie_group_by = ['Asin', 'Model']
                        pie_display_name = "ASIN-Model组合"
                    else:  # Brand+Asin+Model组合分析
                        pie_group_by = ['Brand', 'Asin', 'Model']
                        pie_display_name = "品牌-ASIN-Model组合"
                    
                    try:
                        _, pie_dist_pct, _ = analyze_by_group(df, pie_group_by)
                        
                        # 获取所有ASIN或ASIN+Model组合
                        all_groups = pie_dist_pct.index.tolist()
                        
                        # 添加多选框用于选择要显示的ASIN
                        selected_groups = st.multiselect(
                            f"选择要显示的{pie_display_name}（不选择则显示全部）",
                            all_groups,
                            help=f"可以选择特定的{pie_display_name}进行查看"
                        )
                        
                        # 根据选择筛选数据
                        if selected_groups:
                            pie_dist_pct = pie_dist_pct.loc[selected_groups]
                        
                        # 创建饼图
                        pie_charts = create_rating_pie_chart(pie_dist_pct, f"📊 {pie_display_name}的评分分布")
                        
                        # 显示饼图，每行显示3个
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        for i in range(0, len(pie_charts), 3):
                            cols = st.columns(3)
                            for j in range(3):
                                if i + j < len(pie_charts):
                                    with cols[j]:
                                        st.plotly_chart(pie_charts[i + j], use_container_width=True)
                            if i + 3 < len(pie_charts):  # 在每组之间添加分隔线
                                st.markdown("---")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    except Exception as pie_error:
                        st.warning(f"⚠️ 饼图生成出现问题: {str(pie_error)}")
                        st.info("显示基础评分分布...")
                        
                        # 过滤掉占比为0的数据
                        non_zero_mask = pie_dist_pct.values > 0
                        labels = pie_dist_pct.index[non_zero_mask]
                        values = pie_dist_pct.values[non_zero_mask]
                        
                        # 创建备用饼图
                        fig = go.Figure(data=[go.Pie(
                            labels=labels,
                            values=values,
                            hole=0.3,
                            marker=dict(
                                colors=colors,
                                line=dict(color='#FFFFFF', width=1)
                            ),
                            textinfo='percent+label',
                            textposition='outside',
                            textfont_size=14,
                            insidetextorientation='horizontal',
                            hovertemplate='%{label}: %{percent:.1%}<extra></extra>',
                            texttemplate='%{label}<br>%{percent:.1%}'
                        )])
                        
                        # 更新布局
                        fig.update_layout(
                            title=f'📊 {pie_display_name}的评分分布',
                            showlegend=False,  # 去除图例
                            margin=dict(t=50, b=50, l=50, r=50),  # 调整边距
                            uniformtext_minsize=12,  # 设置最小文本大小
                            uniformtext_mode='hide'  # 隐藏太小的文本
                        )
                        
                        # 优化标签位置和显示
                        fig.update_traces(
                            textposition='outside',
                            textinfo='percent+label',
                            rotation=0  # 从0度开始
                        )
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with tab3:
                with st.container():
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    # 创建一个选择框来选择查看方式
                    view_specific = st.radio(
                        "选择查看方式",
                        ["查看整体趋势", "查看特定ASIN趋势", "查看特定品牌趋势"],
                        key="view_specific",
                        help="可以查看整体趋势、特定ASIN或特定品牌的评分变化"
                    )
                    
                    try:
                        if view_specific == "查看特定ASIN趋势":
                            # 多选框选择ASIN
                            all_asins = sorted(df['Asin'].unique())
                            selected_asins = st.multiselect(
                                "选择要查看的ASIN（可多选）",
                                all_asins,
                                help="不选择则显示所有ASIN的趋势"
                            )
                            
                            if selected_asins:
                                filtered_df = df[df['Asin'].isin(selected_asins)]
                                trend_chart = create_rating_trend_chart(filtered_df, 'Asin')
                            else:
                                # 如果没有选择，显示所有ASIN的趋势
                                trend_chart = create_rating_trend_chart(df, 'Asin')
                        elif view_specific == "查看特定品牌趋势":
                            if 'Brand' in df.columns:
                                # 多选框选择品牌
                                all_brands = sorted(df['Brand'].dropna().unique())
                                selected_brands = st.multiselect(
                                    "选择要查看的品牌（可多选）",
                                    all_brands,
                                    help="不选择则显示所有品牌的趋势"
                                )
                                
                                if selected_brands:
                                    filtered_df = df[df['Brand'].isin(selected_brands)]
                                    trend_chart = create_rating_trend_chart(filtered_df, 'Brand')
                                else:
                                    # 如果没有选择，显示所有品牌的趋势
                                    trend_chart = create_rating_trend_chart(df, 'Brand')
                            else:
                                st.warning("数据中未包含品牌信息，请先关联品牌数据")
                                trend_chart = create_overall_trend_chart(df)
                        else:
                            # 显示整体趋势
                            trend_chart = create_overall_trend_chart(df)
                        
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        st.plotly_chart(trend_chart, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    except Exception as trend_error:
                        st.warning(f"⚠️ 趋势图生成出现问题: {str(trend_error)}")
                        st.info("显示基础趋势分析...")
                        
                        # 基础趋势图作为替代
                        if 'Date' in df.columns and 'Rating' in df.columns:
                            df_trend = df.copy()
                            df_trend['Month'] = pd.to_datetime(df_trend['Date']).dt.to_period('M').astype(str)
                            monthly_avg = df_trend.groupby('Month')['Rating'].mean().reset_index()
                            
                            trend_chart = px.line(monthly_avg, x='Month', y='Rating', 
                                                title='月度平均评分趋势',
                                                labels={'Rating': '平均评分', 'Month': '月份'})
                            st.plotly_chart(trend_chart, use_container_width=True)
                        else:
                            st.error("缺少必要的日期或评分数据")
                            trend_chart = px.bar(title="无法生成趋势图")
                    st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ 处理文件时出错: {str(e)}")
            st.markdown("请检查文件格式是否正确，或联系技术支持。")

if __name__ == "__main__":
    main()