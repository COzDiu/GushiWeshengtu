import hashlib
import os
import time
from io import BytesIO
from http import HTTPStatus
import streamlit as st
from dashscope import ImageSynthesis
import jieba.posseg as pseg
import requests
from PIL import Image
from dotenv import load_dotenv

# 加载.env文件（自动从项目根目录查找）
load_dotenv()

# 集中管理所有风格配置
STYLE_CONFIG = {
    "水墨": {
        "api_style": "traditional_chinese_ink",  # API专用参数
        "prompt_desc": "水墨渲染，淡墨皴擦，宣纸纹理，留白意境",
        "steps": 70,
        "cfg_scale": 8.5
    },
    "青绿": {
        "api_style": None,
        "prompt_desc": "青绿山水，石青石绿设色，金碧辉煌，工笔重彩",
        "steps": 80,
        "cfg_scale": 9.0
    },
    "工笔": {
        "api_style": None,
        "prompt_desc": "工笔重彩，三矾九染，勾线精细，绢本设色",
        "steps": 85,
        "cfg_scale": 9.5
    }
}



# 更健壮的校验方式（避免使用assert）
if not os.getenv('DASHSCOPE_API_KEY'):
    raise EnvironmentError("""
    [错误] 未检测到API密钥配置！
    解决方法：
    1. 在项目根目录创建 .env 文件
    2. 添加配置项：DASHSCOPE_API_KEY=您的API密钥
    """)


# --------------------------
# 配置初始化
# --------------------------


# 初始化会话状态（Session State）
if 'history' not in st.session_state:
    st.session_state.history = []  # 用于存储生成历史
if 'last_creation' not in st.session_state:
    st.session_state.last_creation = None  # 记录最新创作


# --------------------------
# 核心功能模块
# --------------------------
def enhance_poetic_prompt(poem: str,selected_style: str) -> str:
    """
    诗词意境解析与提示词增强
    功能：分析输入诗词，提取关键元素并构建专业提示词

    参数：
        poem: 用户输入的古诗词

    返回：
        结构化提示词字符串
    """
    # 使用jieba进行分词和词性标注
    words = pseg.cut(poem)
    keywords = []
    for word, flag in words:
        # 提取名词和形容词作为关键词
        if flag.startswith('n') or flag.startswith('a'):
            keywords.append(word)

    # 从统一配置获取风格描述
    style_desc = STYLE_CONFIG[selected_style]["prompt_desc"]


    # 构建结构化提示词
    return f'''
    [主题]{poem}
    [风格]{style_desc}
    [要求]绝对禁止出现任何文字、印章、题跋、署名、符号
    [质量]8K高清,无瑕疵,无文字
    [违禁品]文字=禁止，印章=禁止，题跋=禁止
    [关键词]{'+'.join(keywords)}
    '''






def generate_poetic_image(poem: str, selected_style: str) -> str:
    """
    调用API生成诗意图
    功能：对接通义万相API，生成符合诗词意境的图像

    参数：
        poem: 输入诗句
        style: 绘画风格（水墨/青绿/工笔）

    返回：
        生成图片的URL（失败时返回None）
    """
    try:
        # 获取统一配置
        config = STYLE_CONFIG[selected_style]

        # 生成增强提示词（传入风格参数）
        enhanced_prompt = enhance_poetic_prompt(poem,selected_style)

        # API请求参数配置
        response = ImageSynthesis.call(
            model="wanx2.1-t2i-turbo",
            api_key=os.getenv('DASHSCOPE_API_KEY'),
            prompt=enhanced_prompt,
            negative_prompt=(
                "text, watermark, signature, seal, stamp, "
                "calligraphy, inscription, border, frame, "
                "letters, symbols, characters, mark, logo"
            ),
            size="1440*960",  # 优化后的分辨率
            steps=config['steps'],  # 生成步数（影响细节质量）
            cfg_scale=config['cfg_scale'],  # 提示词相关性系数
            style=config["api_style"],
            quality_control={
                "antichain": True,  # 开启反异常扩散
                "detail_boost": 2  # 细节增强级别
            }
        )

        if response.status_code == HTTPStatus.OK:
            return response.output.results[0].url
        return None
    except Exception as e:
        st.error(f"丹青未就：{str(e)}")
        return None


# --------------------------
# 界面设计模块
# --------------------------
def setup_ui():
    """
    古风界面配置
    功能：设置页面布局、样式和基本元素
    """
    # 页面基础配置
    st.set_page_config(
        page_title="墨韵丹青",
        page_icon="🖌️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 自定义CSS样式
    st.markdown("""
    <style>
    /* 主背景 */
    .main {
    
        background: url('https://example.com/ink-bg.jpg');
        background-size: cover;
    }

    /* 输入框字体 */
    .stTextArea textarea {
        font-family: "华文行楷", cursive;
        font-size: 1.2em !important;
    }

    /* 按钮样式 */
    .stButton>button {
        background: #8B4513;
        color: #F5DEB3;
        border: 2px solid #654321;
        border-radius: 5px;
        font-family: "华文楷体";
    }

    /* 历史记录项 */
    .hist-item {
        border: 1px solid #654321 !important;
        border-radius: 10px;
        padding: 1rem;
        background: rgba(245,222,179,0.9);
    }
    </style>
    """, unsafe_allow_html=True)


# --------------------------
# 主程序逻辑
# --------------------------
def main():
    # 初始化界面
    setup_ui()

    # 侧边栏 - 画坊设置
    with st.sidebar:
        st.header("🖌️ 画坊设置")
        selected_style = st.selectbox("笔法选择", ["水墨", "青绿", "工笔"], index=0)
        st.caption("提示：水墨画注重意境和神韵，青绿山水画强调色彩和装饰性，工笔画则追求细节和真实感")

    # 主创作区布局
    col1, col2 = st.columns([5, 3])

    # 左侧输入区
    with col1:
        st.title("《墨韵丹青》")
        poem_input = st.text_area(
            "题诗入画：",
            "孤舟蓑笠翁，独钓寒江雪",
            height=150,
            help="请题写诗句，建议五言、七言格式"
        )

        # 生成按钮逻辑
        if st.button("挥毫泼墨", use_container_width=True):
            if len(poem_input) >= 4:
                with st.spinner("正在研磨丹青，请品茶稍候..."):
                    # 清除旧记录
                    st.session_state.last_creation = None

                    # 调用生成函数
                    start_time = time.time()
                    img_url = generate_poetic_image(poem_input, selected_style)

                    if img_url:
                        # 下载并处理图片
                        response = requests.get(img_url)
                        if response.status_code == 200:
                            content = response.content
                            current_hash = hashlib.md5(content).hexdigest()

                            # 防重复检查
                            should_add = True
                            if st.session_state.history:
                                last_hash = st.session_state.history[-1].get('hash')
                                if current_hash == last_hash:
                                    st.warning("本次创作与最近作品相似，未予珍藏")
                                    should_add = False

                            # 保存到会话状态
                            if should_add:
                                st.session_state.last_creation = {
                                    "poem": poem_input,
                                    "image": content,
                                    "time": time.strftime("%Y-%m-%d %H:%M"),
                                    "style": selected_style,
                                    "hash": current_hash
                                }
                                st.success(f"妙笔丹青成于 {(time.time() - start_time):.1f}秒")
            else:
                st.warning("诗句过短，请题四言以上")

    # 右侧展示区
    if st.session_state.last_creation is not None:
        with col2:
            st.header("最新佳作")
            img_data = st.session_state.last_creation["image"]

            if isinstance(img_data, bytes) and len(img_data) > 0:
                # 装裱效果处理
                img = Image.open(BytesIO(img_data))
                bordered_img = Image.new("RGB", (img.width + 100, img.height + 100), color=(205, 170, 125))
                bordered_img.paste(img, (50, 50))

                # 显示作品
                st.image(bordered_img,
                         caption=st.session_state.last_creation["poem"],
                         use_container_width=True)

                # 下载功能
                st.download_button(
                    label="珍藏此卷",
                    data=img_data,
                    file_name=f"{st.session_state.last_creation['time']}.png",
                    mime="image/png",
                    use_container_width=True
                )

    # 历史记录管理
    if st.session_state.last_creation is not None:
        # 查重逻辑
        current = st.session_state.last_creation
        should_add = True

        if st.session_state.history:
            last = st.session_state.history[-1]
            if (last['poem'] == current['poem']
                    and last['style'] == current['style']
                    and last['hash'] == current['hash']):
                should_add = False

        if should_add:
            st.session_state.history.append(current)
        st.session_state.last_creation = None  # 重置状态

    # 历史画廊展示
    with st.expander("🏯 墨宝珍藏阁", expanded=True):
        if not st.session_state.history:
            st.caption("画阁尚空，期待您的第一幅丹青...")
        else:
            cols = st.columns(3)
            for idx, work in enumerate(reversed(st.session_state.history[-6:])):
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.image(work["image"],
                                 caption=work["poem"][:14] + "..." if len(work["poem"]) > 14 else work["poem"],
                                 use_container_width=True)
                        st.caption(f"〖{work['time']}〗")

    # 使用说明文档
    with st.expander("📜 丹青要诀"):
        st.markdown("""
        ## 创作心法

        ### 1. 诗句格式建议
        ```python
        "大漠孤烟直，长河落日圆"  # 边塞风光
        "采菊东篱下，悠然见南山"  # 田园意境
        "迟日江山丽，春风花草香" 
        ```

        ### 2. 意象组合技巧
        ```python
        "孤舟+蓑笠+寒江雪" → 空寂之境
        "明月+松间+清泉"   → 禅意画面
        ```

        ### 3. 风格匹配指南
        | 诗类   | 推荐风格 | 特点               |
        |--------|----------|--------------------|
        | 山水诗 | 水墨     | 淡墨渲染，留白意境 |
        | 咏物诗 | 工笔     | 细腻写实，细节精致 |
        | 边塞诗 | 青绿     | 色彩浓烈，气势恢宏 |
        """)


if __name__ == "__main__":
    main()