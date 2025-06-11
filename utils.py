import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

def process_data(df, brand_df=None):
    """数据预处理函数"""
    # 确保所需列存在
    required_columns = ['Asin', 'Title', 'Content', 'Model', 'Rating', 'Date']
    if not all(col in df.columns for col in required_columns):
        st.error(f"缺少必要的列: {[col for col in required_columns if col not in df.columns]}")
        return None
    
    # 只保留必要的列，减少内存使用
    df = df[required_columns].copy()
    
    # 使用向量化操作替代apply，提高性能
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # 使用str.strip()的向量化操作
    text_columns = ['Title', 'Content', 'Model']
    for col in text_columns:
        df[col] = df[col].astype(str).str.strip()
    
    # 添加ID列（确保唯一性）
    df.insert(0, 'ID', range(1, len(df) + 1))
    
    # 使用向量化操作替代apply
    df['Review Type'] = pd.cut(
        df['Rating'],
        bins=[-float('inf'), 2, 3, float('inf')],
        labels=['negative', 'neutral', 'positive']
    )
    
    # 如果提供了品牌数据，进行关联
    if brand_df is not None and 'Asin' in brand_df.columns and 'Brand' in brand_df.columns:
        # 清理品牌数据
        brand_df = brand_df[['Asin', 'Brand']].copy()
        brand_df['Asin'] = brand_df['Asin'].astype(str).str.strip()
        brand_df['Brand'] = brand_df['Brand'].astype(str).str.strip()
        
        # 处理重复的ASIN，保留最新的品牌信息
        brand_df = brand_df.drop_duplicates(subset=['Asin'], keep='last')
        
        # 备份原始ID
        original_ids = df['ID'].copy()
        
        # 通过ASIN关联品牌信息
        df = df.merge(brand_df, on='Asin', how='left')
        
        # 恢复原始ID
        df['ID'] = original_ids
        
        st.success(f"✅ 成功关联品牌数据！共关联 {df['Brand'].notna().sum()} 条记录")
    
    # 重新排序列
    column_order = ['ID', 'Asin', 'Brand', 'Title', 'Content', 'Model', 'Rating', 'Date', 'Review Type']
    existing_columns = [col for col in column_order if col in df.columns]
    df = df[existing_columns]
    
    return df

def calculate_review_stats(df):
    """计算评论类型的统计信息"""
    # 计算各类型数量
    review_counts = df['Review Type'].value_counts()
    
    # 计算百分比
    review_percentages = (review_counts / len(df) * 100).round(2)
    
    # 合并统计信息
    stats_df = pd.DataFrame({
        '数量': review_counts,
        '占比(%)': review_percentages
    })
    
    return stats_df, review_counts, review_percentages

def create_pie_chart(review_counts, title='评论类型分布'):
    # 确保索引顺序与颜色映射一致
    review_counts = review_counts.reindex(
        ['positive', 'neutral', 'negative'], 
        fill_value=0
    )
    
    # 创建数据框确保顺序
    df = pd.DataFrame({
        'type': review_counts.index,
        'count': review_counts.values
    })
    
    fig = px.pie(
        df,
        values='count',
        names='type',
        title=title,
        color='type',  # 关键：通过color参数指定分组
        color_discrete_map={
            'positive': '#2ECC71',  # 绿色
            'neutral': '#F1C40F',   # 黄色
            'negative': '#E74C3C'   # 红色
        },
        category_orders={'type': ['positive', 'neutral', 'negative']}
    )
    
    # 禁用主题干扰
    fig.update_layout(template='none')
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=1))  # 添加白色边框
    )
    return fig

def analyze_by_group(df, group_by):
    """按指定字段进行分组分析"""
    # 使用更高效的分组操作
    if isinstance(group_by, list):
        if 'Brand' in group_by:
            df['Group'] = df['Brand'] + ' - ' + df['Asin'] + ' - ' + df['Model']
        else:
            df['Group'] = df['Asin'] + ' - ' + df['Model']
        group_by = 'Group'
    
    # 一次性计算所有统计信息
    stats = df.groupby(group_by).agg({
        'Rating': ['count', 'mean', 'std'],
        'Review Type': lambda x: x.value_counts().to_dict()
    }).round(2)
    
    # 重命名列
    stats.columns = ['评论数量', '平均评分', '标准差', '评论类型分布']
    
    # 计算评分分布
    rating_dist = pd.crosstab(df[group_by], df['Rating'], normalize='index') * 100
    
    return stats, rating_dist, group_by

def create_rating_trend_chart(df, group_by):
    """创建评分趋势图"""
    # 使用更高效的时间处理
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    trend_data = df.groupby(['Month', group_by])['Rating'].mean().reset_index()
    
    # 创建趋势图
    title = f'{group_by}随时间的平均评分变化'
    
    fig = px.line(trend_data, 
                  x='Month', 
                  y='Rating', 
                  color=group_by,
                  title=title,
                  labels={'Rating': '平均评分', 'Month': '月份'})
    
    fig.update_xaxes(tickangle=45)
    return fig

def create_rating_heatmap(rating_dist_pct, title):
    """创建评分分布热力图"""
    fig = go.Figure(data=go.Heatmap(
        z=rating_dist_pct.values,
        x=rating_dist_pct.columns,
        y=rating_dist_pct.index,
        colorscale='RdYlGn',
        text=rating_dist_pct.round(1).values,
        texttemplate='%{text}%',
        textfont={"size": 10},
        hoverongaps=False))
    
    fig.update_layout(
        title=title,
        xaxis_title='评分',
        yaxis_title='产品',
        height=max(300, len(rating_dist_pct) * 30))
    
    return fig

def create_rating_pie_chart(rating_dist_pct, title):
    """创建评分分布饼图"""
    # 创建一个空的图表列表
    figs = []
    
    # 定义颜色映射 - 确保星级和颜色一一对应
    color_map = {
        5: 'rgb(0, 128, 0)',      # 绿色 - 5星
        4: 'rgb(135, 206, 235)',  # 浅蓝色 - 4星
        3: 'rgb(255, 215, 0)',    # 黄色 - 3星
        2: 'rgb(255, 0, 0)',      # 红色 - 2星
        1: 'rgb(139, 0, 0)'       # 深红色 - 1星
    }
    
    # 为每个ASIN或ASIN+Model创建饼图
    for idx, row in rating_dist_pct.iterrows():
        # 创建数据框
        df_pie = pd.DataFrame({
            '评分': row.index,
            '占比': row.values
        })
        
        # 过滤掉占比为0的数据
        df_pie = df_pie[df_pie['占比'] > 0]
        
        # 确保评分按降序排列
        df_pie = df_pie.sort_values('评分', ascending=False)
        
        # 使用go.Figure直接创建饼图
        fig = go.Figure(data=[go.Pie(
            labels=df_pie['评分'],
            values=df_pie['占比'],
            hole=0.3,
            marker=dict(
                colors=[color_map[rating] for rating in df_pie['评分']],
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
            title=f'{idx} 评分分布',
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
        
        figs.append(fig)
    
    return figs

def save_fig_to_html(fig, filename):
    """保存图表为HTML文件"""
    return fig.to_html()

def get_download_data(df, file_format='excel'):
    """准备下载数据"""
    if file_format == 'excel':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        data = output.getvalue()
        return data
    else:  # txt format
        # 将DataFrame转换为格式化的文本
        output = io.StringIO()
        
        # 写入表头
        headers = df.columns.tolist()
        output.write('\t'.join(headers) + '\n')
        output.write('-' * 100 + '\n')  # 分隔线
        
        # 写入数据行
        for _, row in df.iterrows():
            # 确保所有值都转换为字符串，并处理可能的空值
            row_values = [str(val) if pd.notna(val) else '' for val in row]
            # 使用制表符分隔，这样在文本编辑器中会对齐
            output.write('\t'.join(row_values) + '\n')
        
        return output.getvalue().encode('utf-8') 
