# 导入所需依赖库
import streamlit as st
import os
import json
from datetime import datetime, date
import pysentiment2 as ps
from dotenv import load_dotenv
import openai
import pandas as pd
import matplotlib.pyplot as plt
# -------------------------- 新增：登录系统（放在代码最开头） --------------------------
import streamlit as st
import os

# 设置页面配置（最先执行）
st.set_page_config(
    page_title="大连工业大学 AI心理咨询助手",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化用户会话状态
if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "logged_in": False,
        "username": "",
        "role": "",  # "guest" 或 "admin"
        "name": ""
    }

# 管理员账号信息
ADMIN_ACCOUNTS = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "name": "系统管理员"
    },
    "psycenter": {
        "password": "psychology123", 
        "role": "admin",
        "name": "心理中心管理员"
    }
}

def verify_login(username, password):
    """验证登录"""
    if username in ADMIN_ACCOUNTS:
        if password == ADMIN_ACCOUNTS[username]["password"]:
            return True, ADMIN_ACCOUNTS[username]["role"], ADMIN_ACCOUNTS[username]["name"]
    # 游客登录（任意非管理员账号）
    if username and password:
        return True, "guest", "游客用户"
    return False, "", ""

def show_login_page():
    """显示登录页面"""
    st.title("🔐 大连工业大学 AI心理咨询助手登录")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 游客登录")
        st.info("""
        **游客权限**：
        - ✅ 查看所有心理资源
        - ✅ 使用心理咨询功能
        - ✅ 记录情绪日记
        - ✅ 进行焦虑自评
        - ✅ 体验正念练习
        - ❌ 无法管理资源内容
        """)
        
        with st.form("guest_login"):
            guest_username = st.text_input("用户名）", placeholder="姓名", key="guest_username")
            guest_password = st.text_input("密码", type="password", placeholder="学号", key="guest_password")
            guest_login = st.form_submit_button("🚀 游客登录", use_container_width=True)
            
            if guest_login:
                if guest_username and guest_password:
                    st.session_state.user_info = {
                        "logged_in": True,
                        "username": guest_username,
                        "role": "guest",
                        "name": f"游客({guest_username})"
                    }
                    st.success("🎉 欢迎以游客身份访问！")
                    st.balloons()
                    st.rerun()
                else:
                    st.warning("⚠️ 请输入用户名和密码")
    
    with col2:
        st.markdown("### 👑 管理员登录")
        st.info("""
        **管理员额外权限**：
        - ✅ 所有游客权限
        - ✅ 添加心理资源
        - ✅ 编辑心理资源  
        - ✅ 删除心理资源
        - ✅ 管理学校服务内容
        """)
        
        with st.form("admin_login"):
            admin_username = st.text_input("管理员账号", placeholder="请输入管理员账号", key="admin_username")
            admin_password = st.text_input("密码", type="password", placeholder="请输入密码", key="admin_password")
            
            st.markdown("**测试管理员账号**：")
            st.markdown("- 账号：`admin` 密码：`admin123`")
            st.markdown("- 账号：`psycenter` 密码：`psychology123`")
            
            admin_login = st.form_submit_button("🔐 管理员登录", use_container_width=True)
            
            if admin_login:
                if admin_username and admin_password:
                    success, role, name = verify_login(admin_username, admin_password)
                    if success and role == "admin":
                        st.session_state.user_info = {
                            "logged_in": True,
                            "username": admin_username,
                            "role": role,
                            "name": name
                        }
                        st.success(f"🎉 欢迎回来，{name}！")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ 用户名或密码错误！")
                else:
                    st.warning("⚠️ 请输入用户名和密码")
    
    st.markdown("---")
    st.markdown("""
    ### 💡 使用说明
    1. **游客登录**：输入任意用户名和密码即可体验基本功能
    2. **管理员登录**：需要使用正确的管理员账号密码
    3. **权限区别**：管理员可以管理资源内容，游客只能查看
    4. **数据安全**：所有对话记录仅保存在本地，保障隐私安全
    """)

def check_login():
    """检查登录状态，如果未登录则显示登录页面"""
    if not st.session_state.user_info["logged_in"]:
        show_login_page()
        st.stop()  # 停止执行后续代码，显示登录页面
    return True

def logout():
    """退出登录"""
    st.session_state.user_info = {
        "logged_in": False,
        "username": "",
        "role": "",
        "name": ""
    }
    st.rerun()

def is_admin():
    """检查当前用户是否为管理员"""
    return st.session_state.user_info.get("role") == "admin"

# 检查登录状态
check_login()

# 显示顶部登录状态栏
st.sidebar.markdown("---")
if st.session_state.user_info["logged_in"]:
    if is_admin():
        st.sidebar.success(f"👑 管理员：{st.session_state.user_info['name']}")
    else:
        st.sidebar.info(f"👤 游客：{st.session_state.user_info['name']}")
    
    if st.sidebar.button("🚪 退出登录", use_container_width=True):
        logout()

# -------------------------- 您的原有代码从这里开始 --------------------------
# 注意：您原有的所有代码保持不动，我只是在开头添加了登录系统

# 您的导入语句
import json
from datetime import datetime, date
import pysentiment2 as ps
from dotenv import load_dotenv
import openai
import pandas as pd
import matplotlib.pyplot as plt

# 设置中文字体（解决matplotlib中文显示问题）
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams['axes.unicode_minus'] = False

# 您的其余代码保持不变...
load_dotenv()

# 您的其余初始化代码...
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
# ... 您原有的所有代码都保持原样
# 设置中文字体（解决matplotlib中文显示问题）
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams['axes.unicode_minus'] = False

# -------------------------- 1. 基础配置 --------------------------
load_dotenv()
st.set_page_config(
    page_title="大连工业大学 AI心理咨询助手",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "response_style" not in st.session_state:
    st.session_state.response_style = "温和型"
if "language" not in st.session_state:
    st.session_state.language = "中文"
if "emotion_record" not in st.session_state:
    st.session_state.emotion_record = []
if "show_anxiety_resources" not in st.session_state:
    st.session_state.show_anxiety_resources = False

# 新增状态：情绪日记、自评记录
if "emotion_diary" not in st.session_state:
    st.session_state.emotion_diary = []
if "anxiety_assessment" not in st.session_state:
    st.session_state.anxiety_assessment = []

# 新增状态：校园心理资源自定义
if "custom_psychology_resources" not in st.session_state:
    st.session_state.custom_psychology_resources = {
        "psychological_course": [],
        "psychological_activity": [],
        "psychological_test": [],
        "online_resources": []
    }
if "editing_resource_idx" not in st.session_state:
    st.session_state.editing_resource_idx = -1
if "editing_resource_type" not in st.session_state:
    st.session_state.editing_resource_type = ""
if "editing_resource_content" not in st.session_state:
    st.session_state.editing_resource_content = ""

# -------------------------- 2. 工具函数：安全加载图片 --------------------------
def safe_load_image(image_path, alt_text="教师照片"):
    """
    安全加载图片，若路径不存在则显示默认头像
    """
    # 检查文件是否存在
    if os.path.exists(image_path):
        return image_path
    # 检查是否是绝对路径/相对路径问题
    elif os.path.exists(os.path.join(os.getcwd(), image_path)):
        return os.path.join(os.getcwd(), image_path)
    # 所有路径都不存在，返回None（使用默认头像）
    else:
        st.toast(f"提示：未找到图片文件 {image_path}，将显示默认头像", icon="ℹ️")
        return None

# -------------------------- 3. 师资信息（使用绝对路径） --------------------------
DLPU_TEACHERS = [
    {
        "name": "梁瑛楠",
        "title": "教授、博士、硕士研究生导师",
        "position": "大学生心理健康教育中心专职教师",
        "experience": "20余年心理咨询实践经验",
        "training": "系统接受过认知行为治疗、沙盘治疗、绘画心理治疗、叙事治疗、短程焦点治疗、心理危机干预、家庭治疗、团体心理辅导等方面的国内外专业培训和督导",
        "specialty": "擅长将所学各流派理论整合应用于个案实践，咨询风格温和细腻，能灵活选用不同理论和技术，陪伴支持来访者发现自身资源与力量，获得新的理解和体验",
        "fields": ["情绪困扰", "压力管理", "关系处理", "个人成长", "心理测评及团体心理辅导"],
        "services": ["个体心理咨询疏导", "团体心理辅导", "心理测评", "心理健康科普培训"],
        "honor": "中国心理学会临床与咨询心理学专业机构注册心理咨询师，国家二级心理咨询师，国家心理行为训练师，全球职业规划师GCDF，绘画心理分析师，沙盘游戏指导师。大连理工大学访问学者，辽宁省百千万人才工程'千'层次人才，辽宁省青年社科人才库成员，辽宁省公益慈善专家库成员，辽宁省高校心理健康教育骨干教师，辽宁省首批中小学科学副校长，大连市心理学会副秘书长及常务理事，大连市重大决策社会稳定风险评估专家，大连市科技界评审专家，大连市科普讲师团讲师，大连市总工会职工心理咨询服务特聘专家，大连市12355青少年服务台心理危机干预专家，'大爱心连'平台心理咨询专家，辽宁省学校公益心理援助平台志愿者",
        "avatar_path": "C:/Users/A1384/Desktop/newfold/images/teacher1.jpg.png"
    },
    {
        "name": "郭志峰",
        "title": "副教授、硕士",
        "position": "大学生心理健康教育中心专职教师",
        "experience": "18年心理咨询实践经验",
        "training": "系统接受过元认知干预技术、眼动脱敏技术、音乐心理治疗、绘画心理治疗、认知行为治疗、团体心理训练、心理危机干预等心理学相关专业技术培训",
        "specialty": "擅长将认知行为疗法与其他疗法相整合，能帮助大学生更好地应对心理困惑",
        "fields": ["人际关系改善", "自我心理调适", "压力管理", "学业困难", "职业生涯发展"],
        "services": ["个体心理咨询疏导", "沙盘、绘画、音乐心理放松活动的培训指导"],
        "honor": "国家二级心理咨询师，中国心理学会注册心理师，国家心理行为训练师，国家心理测评师，绘画心理分析师，职业发展辅导员。中国心理学会青年工作委员会委员，辽宁省应用心理学专业委员会委员，大连市心理咨询师协会常务理事，大连市学校心理健康教育专家库成员",
        "avatar_path": "C:/Users/A1384/Desktop/newfold/images/teacher2.jpg.png"
    },
    {
        "name": "李永芬",
        "title": "副教授、博士",
        "position": "大学生心理健康教育中心专职教师",
        "experience": "多年心理咨询实践经验",
        "training": "系统讲授中科院心理研究所心理培训课程，具备丰富的心理健康教育工作建设评估经验",
        "specialty": "擅长青少年心理问题家庭治疗及成人情绪问题咨询，多次参与政府、企事业单位心理健康教育工作建设评估工作",
        "fields": ["心理危机干预", "学业困难", "婚姻与恋爱", "原生家庭创伤疗愈", "人际关系困扰及生涯发展规划"],
        "services": ["个体咨询", "团体心理辅导", "心理健康讲座与培训"],
        "honor": "中国心理学会临床心理学注册心理师，国家二级心理咨询师，大连市重大决策社会稳定风险评估专家，大连市教育局抗疫心理援助平台心理危机干预专家，教育部华中师范大学心理援助平台咨询师，大连市沙河口区中小学家庭教育讲师团成员，EAP咨询师",
        "avatar_path": "C:/Users/A1384/Desktop/newfold/images/teacher3.jpg.png"
    },
    {
        "name": "李春伟",
        "title": "副教授、硕士",
        "position": "大学生心理健康教育中心专职教师",
        "experience": "20多年心理咨询实践经验",
        "training": "系统接受过认知行为治疗、绘画分析、沙盘治疗、系统式家庭治疗、心理动力学治疗、叙事治疗、心理危机干预、团体心理辅导、能量疗愈等心理学相关专业技术培训",
        "specialty": "咨询以整合取向为主，善于从传统文化中汲取心理咨询的智慧，咨询兼具人文温度和实践效能",
        "fields": ["自我探索", "人际关系（家庭关系、寝室关系等）处理", "情绪调适", "压力管理", "团体心理辅导", "心理综合评估"],
        "services": ["个体咨询", "团体心理辅导", "心理测评", "心理健康科普培训"],
        "honor": "国家二级心理咨询师，国家心理行为训练师，沙盘游戏指导师，绘画心理分析师",
        "avatar_path": "C:/Users/A1384/Desktop/newfold/images/teacher4.jpg.png"
    }
]

# 2.2 学校咨询服务信息
DLPU_CONSULT_SERVICE = {
    "service_object": "大连工业大学全体在校本科生、研究生",
    "service_type": [
        "个体咨询：一对一的专业心理咨询服务，每次50分钟左右，涵盖情绪调节、压力管理、人际交往、学业困难、恋爱心理、生涯规划等多个领域",
        "团体辅导：针对特定主题的小组心理辅导（如人际关系提升、压力管理、情绪调节、新生适应、毕业生就业心理等），每组8-12人，周期4-8次",
        "心理测评：提供专业的心理量表测评（包括焦虑、抑郁、压力、人格、人际关系、生涯规划等），帮助学生了解自身心理状态",
        "危机干预：针对自杀倾向、自伤行为、严重情绪崩溃等心理危机事件的紧急干预与支持，24小时响应",
        "心理健康讲座：面向全校开展的心理健康科普讲座（如情绪管理、压力应对、恋爱心理、生涯规划等）",
        "心理工作坊：互动式体验活动（如正念冥想工作坊、艺术疗愈工作坊、沟通技巧工作坊等）",
        "心理健康课程：《大学生心理健康教育》公共必修课、《情绪管理与压力应对》《生涯规划与心理健康》等通识选修课"
    ],
    "reservation_method": [
        "线上预约：通过大连工业大学心理健康教育中心小程序、企业微信工作台预约（推荐方式）",
        "线下预约：门诊部303、304房间登记预约",
        "电话预约：0411-8618792（工作日8:30-11:30，13:30-17:00）",
        "紧急情况：可直接前往心理健康教育中心，或第一时间联系辅导员/班主任、学院副书记，也可拨打学校24小时值班电话"
    ],
    "consult_address": "1.门诊部303、304房间",
    "consult_time": "周一至周五：8:30-11:30，13:30-17:00（寒暑假及法定节假日另行通知，紧急情况除外）",
    "service_principle": [
        "保密原则：咨询内容严格保密，未经来访者同意，不得向任何第三方泄露（法律规定的特殊情况除外，如涉及自杀、自伤、伤害他人等）",
        "自愿原则：来访者自愿参与咨询，可根据自身情况随时终止咨询",
        "中立原则：咨询师保持客观中立的态度，不评判来访者的想法、行为和价值观",
        "专业原则：严格遵循心理咨询专业伦理规范，提供科学、专业的心理服务",
        "免费原则：学校心理健康教育中心所有咨询服务、测评、讲座、工作坊等均为免费提供"
    ],
    "notice": "1. 首次咨询需提前1-3天预约，预约成功后请按时前往，若无法按时前往请提前24小时取消预约；2. 咨询时请携带学生证或校园卡以便登记；3. 心理咨询是一个专业的助人过程，需要来访者与咨询师的共同配合，建议保持开放的心态参与；4. 若需心理测评，可在预约时说明，测评后将提供专业的结果解读。"
}

# 2.3 校园心理资源
DLPU_PSYCHOLOGY_RESOURCES = {
    "psychological_course": [
        "《大学生心理健康教育》- 全校公共必修课（1学分），覆盖心理健康基础知识、情绪管理、压力应对、人际交往、生涯规划等内容",
        "《情绪管理与压力应对》- 通识选修课（0.5学分），通过理论讲解和实践体验，帮助学生掌握情绪调节和压力管理的实用方法",
        "《生涯规划与心理健康》- 通识选修课（0.5学分），结合生涯规划与心理健康，帮助学生明确职业方向，提升心理韧性",
        "《正念冥想与心理成长》- 特色工作坊（无学分），每周1次，持续8周，通过正念练习帮助学生提升专注力和情绪稳定性",
        "《艺术疗愈入门》- 通识选修课（0.5学分），通过绘画、音乐、戏剧等艺术形式，帮助学生释放情绪、探索自我"
    ],
    "psychological_activity": [
        "5·25心理健康月系列活动（每年5月）：包括心理讲座、心理剧比赛、心理漫画征集、团体辅导体验、心理健康知识竞赛等",
        "新生心理健康适应周活动（每年9月）：针对新生开展适应讲座、团体辅导、心理测评、校园打卡等活动，帮助新生快速适应大学生活",
        "毕业生心理健康护航计划（每年3-6月）：包括就业心理讲座、压力管理工作坊、一对一就业心理辅导等，帮助毕业生应对就业压力",
        "心理健康进学院/班级活动：根据学院需求，开展定制化的心理健康讲座、团体辅导、心理测评等服务",
        "心理委员培训：每年春秋两季开展，培训心理委员的心理健康知识、朋辈辅导技巧、危机识别与上报能力",
        "心理健康科普宣传：通过微信公众号、校园广播、宣传海报、手册等形式，普及心理健康知识"
    ],
    "psychological_test": [
        "症状自评量表（SCL-90）：全面评估心理健康状况，包括躯体化、强迫、人际关系敏感、抑郁、焦虑等9个维度",
        "焦虑自评量表（SAS）：评估焦虑情绪的严重程度",
        "抑郁自评量表（SDS）：评估抑郁情绪的严重程度",
        "压力知觉量表（PSS）：评估个体感受到的压力水平",
        "人际关系综合诊断量表：评估人际交往中的困扰程度",
        "艾森克人格问卷（EPQ）：评估人格特质（内外向、神经质、精神质、掩饰性）",
        "霍兰德职业兴趣测试：帮助学生了解自身职业兴趣类型，为生涯规划提供参考"
    ],
    "crisis_hotline": {
        "school_hotline": "0411-86318792（工作日8:30-11:30，13:30-17:00）",
        "school_24h_hotline": "0411-86323110（学校24小时值班电话，紧急情况拨打）",
        "dalian_hotline": "0411-84689595（大连市24小时心理危机干预热线）",
        "provincial_hotline": "400-161-9995（辽宁省心理危机干预热线，24小时）",
        "national_hotline": "400-161-9995（全国24小时心理危机干预热线）"
    },
    "online_resources": [
        "大连工业大学心理健康教育中心微信公众号：定期推送心理健康科普文章、活动通知、心理测试、冥想音频等",
        "心理测评系统：线上心理测评平台，学生可通过学校官网登录进行自助测评",
        "冥想音频库：提供正念冥想、放松训练等音频资源，可通过公众号或中心官网下载",
        "心理健康电子书库：涵盖情绪管理、压力应对、人际交往、生涯规划等领域的电子书籍和文章"
    ]
}

# 2.4 心理健康科普
DLPU_PSYCHOLOGY_SCIENCE = {
    "common_problems": [
        {
            "title": "大学生常见心理问题及应对",
            "content": "大学生常见的心理问题包括：适应障碍（新生入学适应、环境适应）、学业压力、人际交往困扰、情绪调节问题（焦虑、抑郁、愤怒）、恋爱心理问题、生涯规划迷茫、家庭关系冲突等。应对建议：1. 主动了解心理健康知识，提升自我调适能力；2. 积极参与校园活动，拓展人际交往；3. 遇到问题及时向辅导员、同学、家人倾诉；4. 必要时寻求专业心理咨询帮助。"
        },
        {
            "title": "焦虑情绪的识别与调节",
            "content": "焦虑情绪的常见表现：心理上（紧张、担忧、烦躁、注意力不集中）、生理上（心跳加快、呼吸急促、头晕、失眠、食欲不振）、行为上（坐立不安、拖延、回避）。调节方法：1. 呼吸放松法（4-7-8呼吸法、腹式呼吸）；2. 正念冥想，专注当下；3. 认知重构，调整负面思维；4. 适当运动，释放压力；5. 合理规划时间，避免过度压力。"
        },
        {
            "title": "抑郁情绪的识别与应对",
            "content": "抑郁情绪的常见表现：持续情绪低落、兴趣减退、精力下降、自我评价降低、睡眠障碍（失眠或嗜睡）、食欲改变、注意力不集中、有自杀念头等。应对建议：1. 及时寻求专业帮助（心理咨询、心理治疗、药物治疗）；2. 保持规律作息和饮食；3. 适当参与户外活动和社交；4. 做一些能带来成就感的小事；5. 避免独处过久，多与他人交流。"
        },
        {
            "title": "人际交往困扰的解决方法",
            "content": "大学生人际交往困扰主要表现为：社交恐惧、人际冲突、孤独感、缺乏沟通技巧等。解决方法：1. 提升沟通技巧，学会倾听和表达；2. 尊重他人，换位思考；3. 主动参与社交活动，逐步克服社交恐惧；4. 遇到人际冲突时，冷静沟通，避免指责；5. 接纳自己的社交风格，不必强求完美。"
        }
    ],
    "mental_health_tips": [
        "保持规律作息：充足的睡眠是心理健康的基础，建议每天睡眠7-8小时，避免熬夜。",
        "合理饮食：均衡营养，多吃蔬菜水果、全谷物、优质蛋白质，少吃辛辣刺激、高糖高脂食物。",
        "坚持运动：每周进行3次以上有氧运动（跑步、游泳、瑜伽、打球等），每次30分钟以上，促进多巴胺分泌，改善情绪。",
        "学会情绪表达：不要压抑情绪，可通过倾诉、写日记、绘画、听音乐等方式释放情绪。",
        "培养兴趣爱好：参与自己喜欢的活动（如读书、绘画、音乐、摄影、志愿服务等），丰富课余生活，提升幸福感。",
        "建立支持系统：与家人、朋友、同学保持良好沟通，遇到问题时能获得情感支持。",
        "避免过度使用电子产品：减少手机、电脑使用时间，多进行面对面交流和户外活动。",
        "学会自我接纳：接受自己的不完美，关注自身优点，避免过度自我批评。"
    ],
    "crisis_identification": {
        "title": "心理危机的识别与应对",
        "content": "心理危机的常见信号：1. 言语上：经常说'活着没意思''想自杀''不想活了'等消极言论；2. 行为上：突然与他人疏远、整理物品、赠送礼物、自伤行为、情绪剧烈波动；3. 情绪上：持续抑郁、焦虑、愤怒、麻木不仁；4. 生活上：突然改变作息、饮食，放弃兴趣爱好，学业/工作表现急剧下降。应对方法：1. 保持冷静，主动关心，倾听其感受，不要评判；2. 不要离开其身边，确保其安全；3. 及时联系辅导员、学校心理健康教育中心、家人或拨打危机干预热线；4. 不要让其单独待在封闭空间，移除可能的危险物品。"
    }
}

# -------------------------- 3. 原有功能：心理资源库 --------------------------
# 焦虑缓解方法库
ANXIETY_METHODS = {
    "呼吸放松法": [
        {"name": "4-7-8呼吸法", "desc": "吸气4秒→屏息7秒→呼气8秒，重复5次，快速平复焦虑", "steps": ["找安静的地方坐下/躺下", "用鼻子安静吸气4秒", "屏住呼吸7秒", "用嘴巴缓慢呼气8秒", "重复5-10次"]},
        {"name": "腹式呼吸", "desc": "用鼻子吸气（腹部鼓起），嘴巴呼气（腹部收缩），每次3分钟", "steps": ["一手放胸口，一手放腹部", "鼻子吸气，感受腹部鼓起（胸口不动）", "嘴巴呼气，感受腹部收缩", "每分钟呼吸6-8次，持续3分钟"]},
        {"name": "交替鼻孔呼吸", "desc": "左鼻孔吸→右鼻孔呼，再反之，平衡交感神经", "steps": ["用拇指按住右鼻孔", "左鼻孔吸气4秒", "按住左鼻孔，松开右鼻孔呼气6秒", "右鼻孔吸气4秒，按住右鼻孔，松开左鼻孔呼气6秒", "重复5轮"]}
    ],
    "正念练习": [
        {"name": "5分钟正念冥想", "desc": "专注当下的感受，不评判想法，只观察呼吸", "steps": ["找安静环境，坐姿端正", "闭眼，将注意力集中在呼吸上", "发现走神时，温和拉回注意力", "不评判任何想法，只是观察", "持续5分钟"]},
        {"name": "身体扫描冥想", "desc": "从脚尖到头顶逐部位感受，释放身体紧绷感", "steps": ["平躺，闭眼，深呼吸3次", "从脚尖开始，逐部位感受（脚、小腿、大腿、腰、背、肩、头）", "每个部位停留10秒，感受紧张并释放", "最后整体感受全身，深呼吸5次"]},
        {"name": "感恩冥想", "desc": "默念3件感恩的小事，转移焦虑焦点", "steps": ["安静坐下，闭眼", "回想今天发生的3件值得感恩的小事", "感受每件事带来的温暖情绪", "默念感谢，持续3分钟"]}
    ],
    "认知调节": [
        {"name": "认知重构", "desc": "识别并调整焦虑的负面思维", "steps": ["写下让你焦虑的想法", "分析想法的客观性（有证据吗？）", "找出更合理的替代想法", "用新想法替代负面想法，重复默念"]},
        {"name": "担忧时间", "desc": "专门预留时间处理焦虑，避免全天被困扰", "steps": ["每天固定15分钟作为'担忧时间'", "非担忧时间出现焦虑时，记录下来", "到担忧时间集中处理这些焦虑", "分析每个担忧的可解决性，制定小步骤"]},
        {"name": "积极自我对话", "desc": "用鼓励的语言替代自我批评", "steps": ["识别自我批评的话语", "写下对应的积极替代语", "每天早晚默念5分钟", "焦虑时立刻使用积极自我对话"]}
    ],
    "行为调节": [
        {"name": "渐进式肌肉放松", "desc": "通过肌肉紧张-放松循环释放焦虑", "steps": ["从脚开始，逐部位绷紧肌肉5秒", "突然放松，感受肌肉松弛感", "依次放松小腿、大腿、腹部、背部、肩颈、面部", "每个部位重复2次，全程10分钟"]},
        {"name": "感官接地法", "desc": "通过5种感官锚定当下，缓解焦虑发作", "steps": ["说出你看到的5样东西", "说出你能触摸到的4样东西", "说出你能听到的3样声音", "说出你能闻到的2种气味", "说出你能尝到的1种味道"]},
        {"name": "微行动拆解", "desc": "将焦虑的任务拆解为极小的行动步骤", "steps": ["写下让你焦虑的任务", "拆解到每个步骤只需1-2分钟完成", "先完成最容易的那个小步骤", "完成后记录成就感，逐步推进"]}
    ]
}

# 心理知识库
PSYCHOLOGY_KNOWLEDGE = {
    "焦虑相关": [
        {"title": "焦虑的生理机制", "content": "焦虑是身体的应激反应，交感神经激活导致心跳加快、呼吸急促。短期焦虑有保护作用，长期则影响身心健康。"},
        {"title": "正常焦虑vs病理性焦虑", "content": "正常焦虑有明确诱因，持续时间短，不影响日常；病理性焦虑无明确诱因，持续6个月以上，影响工作生活，需专业干预。"},
        {"title": "焦虑的自我调节原则", "content": "先调节生理（呼吸、放松），再调节认知（思维），最后调节行为（行动），循序渐进。"}
    ],
    "情绪管理": [
        {"title": "情绪ABC理论", "content": "引发情绪的不是事件本身，而是对事件的认知（信念）。改变认知可以改变情绪反应。"},
        {"title": "情绪日记的作用", "content": "记录情绪可以提高情绪觉察能力，识别情绪触发点，找到有效的调节方法。"},
        {"title": "接纳情绪的重要性", "content": "压抑情绪会加剧心理不适，接纳情绪（不评判、不抗拒）反而能减少其负面影响。"}
    ],
    "正念相关": [
        {"title": "正念的核心概念", "content": "正念是不加评判地关注当下的体验，帮助脱离过去的后悔和未来的焦虑，活在当下。"},
        {"title": "正念练习的常见误区", "content": "正念不是要清空思绪，而是要觉察思绪；不是要追求放松，而是要培养觉察能力。"},
        {"title": "正念练习的频率建议", "content": "每天10分钟的持续练习，比偶尔1小时的练习效果更好，关键是坚持。"}
    ]
}

# 焦虑自评量表（GAD-7简化版）
ANXIETY_SCALE = [
    {"question": "感觉紧张、焦虑或烦躁", "options": ["完全没有", "几天", "一半以上日子", "几乎每天"]},
    {"question": "不能停止或控制担忧", "options": ["完全没有", "几天", "一半以上日子", "几乎每天"]},
    {"question": "对各种事情过度担忧", "options": ["完全没有", "几天", "一半以上日子", "几乎每天"]},
    {"question": "很难放松下来", "options": ["完全没有", "几天", "一半以上日子", "几乎每天"]},
    {"question": "由于不安而难以静坐", "options": ["完全没有", "几天", "一半以上日子", "几乎每天"]},
    {"question": "容易生气或易怒", "options": ["完全没有", "几天", "一半以上日子", "几乎每天"]},
    {"question": "感到害怕，似乎有可怕的事情即将发生", "options": ["完全没有", "几天", "一半以上日子", "几乎每天"]}
]

# -------------------------- 4. 核心工具函数 --------------------------
def init_ai_client():
    """初始化智谱AI客户端"""
    zhipu_api_key = os.getenv("ZHIPU_API_KEY")
    if not zhipu_api_key:
        st.error("未检测到API密钥！请检查.env文件是否配置正确")
        st.stop()
    client = openai.OpenAI(
        api_key=zhipu_api_key,
        base_url="https://open.bigmodel.cn/api/paas/v4/"
    )
    return client

def analyze_emotion(text):
    """情感分析：识别焦虑/积极/中性"""
    try:
        lm = ps.LM()
        tokens = lm.tokenize(text)
        score = lm.get_score(tokens)
        polarity = round(score['polarity'], 2)
        
        # 强化焦虑情绪识别（关键词+极性值）
        anxiety_keywords = ["焦虑", "压力大", "睡不着", "烦躁", "紧张", "心慌", "焦虑症", "压抑"]
        is_anxiety = any(word in text for word in anxiety_keywords) or polarity < -0.2
        if is_anxiety:
            emotion = "焦虑/消极"
            st.session_state.show_anxiety_resources = True
        elif polarity > 0.2:
            emotion = "积极"
            st.session_state.show_anxiety_resources = False
        else:
            emotion = "中性"
            st.session_state.show_anxiety_resources = False
        return emotion, polarity, is_anxiety
    except Exception as e:
        st.warning(f"情感分析暂时不可用：{str(e)}")
        return "未知", 0.0, False

def get_psychology_prompt():
    """优化提示词：仅保留指定的0411-86318792一个电话"""
    style_templates = {
        "温和型": "你是一位温柔、有共情力的大连工业大学心理咨询师，用温暖的语言回应，若用户有焦虑情绪，除了共情，还要结合学校提供的心理资源和缓解焦虑的方法（如呼吸法、正念练习）给出具体建议，不空洞。",
        "专业型": "你是一位专业的大连工业大学心理咨询师，分析用户焦虑的可能原因，同时结合学校咨询服务和科学的缓解方法（如腹式呼吸、认知重构）给出建议，语言专业但易懂。",
        "鼓励型": "你是一位擅长赋能的大连工业大学心理咨询师，激励用户行动起来缓解焦虑（如感官接地法、微行动拆解），同时引导用户合理利用学校的心理资源，聚焦可落地的小步骤，语言充满力量。"
    }
    # 核心修改：只保留0411-86318792这一个电话，删除其他冗余号码
    lang_template = """
    所有回应必须使用中文，语言自然流畅，避免重复，根据用户情绪调整语气，回应要具体、有针对性，并且严格使用以下大连工业大学心理服务信息：
    1. 心理咨询唯一预约电话：0411-86318792
    2. 咨询地址：大学生活动中心三楼
    3. 咨询预约时间：工作日下午2点到5点
    禁止编造任何电话号码、地址、时间等信息！仅可使用上述指定的0411-86318792这一个电话。
    """
    core_rules = """
    1. 优先倾听和共情，不急于给建议；
    2. 不做医疗诊断，严重时提醒用户联系大连工业大学心理健康教育中心；
    3. 记住历史对话，保持连贯性；
    4. 若用户有焦虑情绪，主动推荐1-2个具体的缓解方法和学校的咨询服务；
    5. 不否定用户的感受，先安抚再引导。
    """
    prompt = f"{style_templates[st.session_state.response_style]}\n{lang_template}\n{core_rules}"
    return prompt

def generate_ai_response(user_input):
    """生成AI回应（结合大连工业大学心理中心内容）"""
    client = init_ai_client()
    messages = [{"role": "system", "content": get_psychology_prompt()}]
    for msg in st.session_state.chat_history:
        messages.append({"role": "user", "content": msg["user"]})
        messages.append({"role": "assistant", "content": msg["ai"]})
    messages.append({"role": "user", "content": user_input})
    
    try:
        response = client.chat.completions.create(
            model="glm-4",
            messages=messages,
            temperature=0.8,
            max_tokens=1000,
            stream=False
        )
        return response.choices[0].message.content.strip(), None
    except Exception as e:
        return f"我理解你的感受。作为大连工业大学心理咨询助手，我建议你可以尝试学校的正念练习或者预约心理咨询服务。具体来说：{str(e)[:100]}...", f"API调用失败，使用备用响应：{str(e)}"

def save_chat_record():
    """保存会话记录"""
    if not st.session_state.chat_history:
        st.warning("暂无对话记录可保存！")
        return
    save_dir = "psychology_chat_records"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    filename = f"{save_dir}/chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_data = {
        "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "response_style": st.session_state.response_style,
        "language": st.session_state.language,
        "chat_history": st.session_state.chat_history,
        "emotion_record": st.session_state.emotion_record,
        "emotion_diary": st.session_state.emotion_diary,
        "anxiety_assessment": st.session_state.anxiety_assessment
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    st.success(f"会话记录已保存：{filename}")

def calculate_anxiety_score(answers):
    """计算焦虑自评量表得分"""
    score_map = {"完全没有": 0, "几天": 1, "一半以上日子": 2, "几乎每天": 3}
    total_score = sum([score_map[ans] for ans in answers])
    
    if total_score <= 4:
        level = "无焦虑"
        suggestion = "你的焦虑水平处于正常范围，继续保持良好的情绪管理习惯，可关注学校的心理健康活动。"
    elif total_score <= 9:
        level = "轻度焦虑"
        suggestion = "你有轻度焦虑情绪，可以尝试学校提供的正念冥想工作坊或呼吸放松法等自我调节方法。"
    elif total_score <= 14:
        level = "中度焦虑"
        suggestion = "你有中度焦虑情绪，建议预约学校心理健康教育中心的个体咨询，同时增加自我调节频率。"
    else:
        level = "重度焦虑"
        suggestion = "你有重度焦虑情绪，强烈建议尽快联系学校心理健康教育中心（0411-86318792）或线下心理机构进行专业评估和干预。"
    
    return total_score, level, suggestion

def add_emotion_diary(date_str, emotion, intensity, content, coping_method):
    """添加情绪日记"""
    st.session_state.emotion_diary.append({
        "date": date_str,
        "emotion": emotion,
        "intensity": intensity,
        "content": content,
        "coping_method": coping_method,
        "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    st.success("情绪日记已保存！")

def plot_emotion_trend():
    """绘制情绪变化趋势图"""
    if not st.session_state.emotion_diary:
        st.warning("暂无情绪日记数据，无法生成趋势图！")
        return
    
    # 处理数据
    diary_df = pd.DataFrame(st.session_state.emotion_diary)
    diary_df['date'] = pd.to_datetime(diary_df['date'])
    diary_df = diary_df.sort_values('date')
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # 绘制情绪强度趋势
    ax.plot(diary_df['date'], diary_df['intensity'], marker='o', linewidth=2, color='#1f77b4')
    ax.set_title('情绪强度变化趋势', fontsize=14, fontweight='bold')
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('情绪强度（1-10）', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # 美化图表
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    st.pyplot(fig)
    
    # 情绪统计
    st.markdown("### 📊 情绪统计")
    emotion_counts = diary_df['emotion'].value_counts()
    for emo, count in emotion_counts.items():
        st.markdown(f"- **{emo}**：{count} 次")
    
    avg_intensity = round(diary_df['intensity'].mean(), 1)
    st.markdown(f"- **平均情绪强度**：{avg_intensity}/10")

# -------------------------- 新增：校园心理资源自定义工具函数 --------------------------
def add_custom_resource(resource_type, content):
    """添加自定义资源"""
    if not content.strip():
        st.error("内容不能为空！")
        return False
    
    # 如果是编辑现有资源
    if st.session_state.editing_resource_idx >= 0 and st.session_state.editing_resource_type == resource_type:
        st.session_state.custom_psychology_resources[resource_type][st.session_state.editing_resource_idx] = content
        st.session_state.editing_resource_idx = -1
        st.session_state.editing_resource_type = ""
        st.success("资源已更新！")
    else:
        st.session_state.custom_psychology_resources[resource_type].append(content)
        st.success("资源已添加！")
    return True

def delete_custom_resource(resource_type, resource_idx):
    """删除自定义资源"""
    if 0 <= resource_idx < len(st.session_state.custom_psychology_resources[resource_type]):
        del st.session_state.custom_psychology_resources[resource_type][resource_idx]
        st.success("资源已删除！")
        return True
    return False

def get_combined_resources():
    """获取合并后的资源（默认+自定义）"""
    combined = {
        "psychological_course": DLPU_PSYCHOLOGY_RESOURCES["psychological_course"] + st.session_state.custom_psychology_resources["psychological_course"],
        "psychological_activity": DLPU_PSYCHOLOGY_RESOURCES["psychological_activity"] + st.session_state.custom_psychology_resources["psychological_activity"],
        "psychological_test": DLPU_PSYCHOLOGY_RESOURCES["psychological_test"] + st.session_state.custom_psychology_resources["psychological_test"],
        "online_resources": DLPU_PSYCHOLOGY_RESOURCES["online_resources"] + st.session_state.custom_psychology_resources["online_resources"]
    }
    return combined

# -------------------------- 5. 页面布局 --------------------------
# 侧边栏：设置+功能
with st.sidebar:
    st.title("✨ 大连工业大学 心理咨询设置")
    
    # 原有设置
    st.session_state.response_style = st.selectbox(
        "AI回应风格",
        options=["温和型", "专业型", "鼓励型"],
        index=0,
        help="不同风格对应不同的语言表达习惯"
    )
    st.session_state.language = st.selectbox(
        "对话语言",
        options=["中文"],
        index=0,
        disabled=True,
        help="当前仅支持中文心理咨询"
    )
    
    # 焦虑缓解方法
    st.markdown("---")
    st.title("🧘 焦虑缓解方法")
    method_type = st.selectbox("选择方法类型", list(ANXIETY_METHODS.keys()), index=0, key="method_type_sidebar")
    
    # 显示选中的方法详情
    for method in ANXIETY_METHODS[method_type]:
        with st.expander(f"📖 {method['name']}"):
            st.markdown(f"**说明**：{method['desc']}")
            st.markdown("**操作步骤**：")
            for i, step in enumerate(method['steps'], 1):
                st.markdown(f"{i}. {step}")
    
    # 心理知识库
    st.markdown("---")
    st.title("📚 心理知识库")
    knowledge_type = st.selectbox("选择知识分类", list(PSYCHOLOGY_KNOWLEDGE.keys()), index=0, key="knowledge_type_sidebar")
    for knowledge in PSYCHOLOGY_KNOWLEDGE[knowledge_type]:
        with st.expander(f"📝 {knowledge['title']}"):
            st.markdown(knowledge['content'])
    
    # 新增：心理健康科普（官网内容）
    st.markdown("---")
    st.title("📖 心理健康科普")
    science_type = st.selectbox(
        "选择科普内容",
        ["常见心理问题", "心理健康小贴士", "心理危机识别"],
        index=0,
        key="science_type_sidebar"
    )
    if science_type == "常见心理问题":
        for problem in DLPU_PSYCHOLOGY_SCIENCE["common_problems"]:
            with st.expander(f"❓ {problem['title']}"):
                st.markdown(problem['content'])
    elif science_type == "心理健康小贴士":
        st.markdown("**日常心理健康维护建议**：")
        for tip in DLPU_PSYCHOLOGY_SCIENCE["mental_health_tips"]:
            st.markdown(f"- {tip}")
    else:
        with st.expander(f"⚠️ {DLPU_PSYCHOLOGY_SCIENCE['crisis_identification']['title']}"):
            st.markdown(DLPU_PSYCHOLOGY_SCIENCE['crisis_identification']['content'])
    
    # 学校心理服务快捷入口
    st.markdown("---")
    st.title("🏫 学校心理服务")
    st.markdown(f"📞 咨询电话：0411-86318792（门诊部）")
    st.markdown(f"📞 24小时值班：{DLPU_PSYCHOLOGY_RESOURCES['crisis_hotline']['school_24h_hotline']}")
    st.markdown(f"📍 咨询地址：{DLPU_CONSULT_SERVICE['consult_address']}")
    st.markdown(f"⏰ 咨询时间：{DLPU_CONSULT_SERVICE['consult_time']}")
    
    # 危机热线
    st.markdown("⚠️ 24小时危机热线：")
    st.markdown(f"- 大连市：{DLPU_PSYCHOLOGY_RESOURCES['crisis_hotline']['dalian_hotline']}")
    st.markdown(f"- 辽宁省：{DLPU_PSYCHOLOGY_RESOURCES['crisis_hotline']['provincial_hotline']}")
    st.markdown(f"- 全国：{DLPU_PSYCHOLOGY_RESOURCES['crisis_hotline']['national_hotline']}")
    
    # 功能按钮
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 保存会话记录", use_container_width=True):
            save_chat_record()
    with col2:
        if st.button("🗑️ 清空对话", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.emotion_record = []
            st.session_state.show_anxiety_resources = False
            st.rerun()
    
    # 免责声明
    st.markdown("---")
    st.markdown("### ⚠️ 免责声明")
    st.markdown("""
    本工具仅为大连工业大学AI辅助心理支持，**不可替代学校专业心理咨询师**。
    若你正经历严重心理困扰，请及时联系学校心理健康教育中心或线下心理机构。
    """)
with st.sidebar:
    # === 新增：用户状态显示 ===
    if st.session_state.user_info["logged_in"]:
        if is_admin():
            st.success(f"👑 管理员：{st.session_state.user_info['name']}")
        else:
            st.info(f"👤 游客：{st.session_state.user_info['name']}")
        
        if st.button("退出登录", use_container_width=True, key="logout_button"):
            st.session_state.user_info = {
                "logged_in": False,
                "username": "",
                "role": "",
                "name": ""
            }
            st.rerun()
        
        st.markdown("---")
    
    # 原有的侧边栏内容保持不变...
    st.title("✨ 大连工业大学 心理咨询设置")
    # ... 您原有的其他侧边栏代码
# 主页面：新增学校专属标签页
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 心理咨询对话", 
    "📓 情绪日记", 
    "📝 焦虑自评", 
    "🧠 正念练习引导",
    "👨‍🏫 师资团队",
    "🏫 学校咨询服务"
])

# 标签页1：心理咨询对话
import random  # Python内置库，无外部依赖

with tab1:
    st.title("💬 大连工业大学 AI心理咨询助手")
    st.markdown("#### 一个有温度、专属工大的智能心理陪伴者")
    st.markdown("---")

    # 初始化已使用的方法记录（新增，不改变开头结构）
    if "used_breathing_methods" not in st.session_state:
        st.session_state.used_breathing_methods = []
    if "used_mindfulness_methods" not in st.session_state:
        st.session_state.used_mindfulness_methods = []

    # 新增：获取指定分类下不重复的方法（保留核心逻辑）
    def get_unique_method(category, used_key):
        all_methods = ANXIETY_METHODS[category]
        unused_indices = [i for i in range(len(all_methods)) if i not in st.session_state[used_key]]
        
        if not unused_indices:
            st.session_state[used_key] = []
            unused_indices = list(range(len(all_methods)))
        
        selected_idx = random.choice(unused_indices)
        st.session_state[used_key].append(selected_idx)
        
        return all_methods[selected_idx]

    # 焦虑检测提示（大幅丰富内容，布局不变）
    if st.session_state.show_anxiety_resources:
        with st.warning("💡 检测到你可能有焦虑情绪，推荐这些缓解方法："):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🧘 推荐放松方法**：")
                st.markdown("> 🌟 这些方法简单易操作，适合日常随时练习")
                
                # 呼吸放松法（丰富内容：补充适用场景+完整步骤）
                method1 = get_unique_method('呼吸放松法', 'used_breathing_methods')
                st.markdown(f"**{method1['name']}**")
                st.markdown(f"📝 适用场景：{method1.get('scene', '学习/睡前/感到紧张时')}")
                st.markdown(f"💬 方法说明：{method1['desc']}")
                # 完整展示步骤，添加序号更清晰
                steps_text = " → ".join([f"{i+1}.{step}" for i, step in enumerate(method1['steps'])])
                st.markdown(f"🚶 操作步骤：{steps_text}")
                
                st.markdown("---")  # 分隔线增强排版
                
                # 正念练习（同样丰富内容）
                method2 = get_unique_method('正念练习', 'used_mindfulness_methods')
                st.markdown(f"**{method2['name']}**")
                st.markdown(f"📝 适用场景：{method2.get('scene', '课间休息/情绪低落时')}")
                st.markdown(f"💬 方法说明：{method2['desc']}")
                # 步骤过多时合理截断，保留核心
                if len(method2['steps']) > 3:
                    steps_text = " → ".join([f"{i+1}.{step}" for i, step in enumerate(method2['steps'][:3])]) + " → ...（剩余步骤可逐步尝试）"
                else:
                    steps_text = " → ".join([f"{i+1}.{step}" for i, step in enumerate(method2['steps'])])
                st.markdown(f"🚶 操作步骤：{steps_text}")
        
            with col2:
                st.markdown("**🏫 学校专属支持**：")
                st.markdown("> 🎓 遇到难以调节的情绪，记得寻求专业帮助")
                
                # 丰富学校支持信息：补充咨询时间、预约方式
                st.markdown(f"- 心理咨询门诊部：0411-86318792")
                st.markdown(f"⏰ **咨询时间**：周一至周五 8:30-11:30、14:00-17:00（法定节假日除外）")
                st.markdown(f"📌 **预约方式**：")
                st.markdown(f"- 线下：学生活动中心3楼心理咨询室现场预约")
                
                st.markdown("---")
                
                # 新增温馨提示
                st.markdown("💖 **温馨提醒**：")
                st.markdown("- 心理咨询完全免费且严格保密")
                st.markdown("- 不必有心理负担，主动求助是勇敢的表现")
                st.markdown("- 除了专业咨询，也可以和辅导员、亲友倾诉哦～")
    # 显示历史对话
    if st.session_state.chat_history:
        for msg in st.session_state.chat_history:
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"**你**：{msg['user']}")
                st.caption(f"情感分析：{msg['emotion']}（极性值：{msg['polarity']}）")
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(f"**工大AI心理咨询师**：{msg['ai']}")
    else:
        with st.chat_message("assistant", avatar="🤖"):
            welcome_text = "你好呀～我是大连工业大学AI心理咨询助手，无论你有什么烦恼、压力或困惑，都可以放心地告诉我，我会认真倾听并陪伴你"
            st.markdown(welcome_text)

    # 用户输入框
    user_input = st.chat_input("请输入你想倾诉的内容（比如'最近压力好大，睡不着觉'）")
    if user_input:
        # 情感分析
        emotion, polarity, is_anxiety = analyze_emotion(user_input)
        st.session_state.emotion_record.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "content": user_input,
            "emotion": emotion,
            "polarity": polarity,
            "is_anxiety": is_anxiety
        })
        
        # 生成AI回应
        with st.spinner("我正在认真倾听你的心声..."):
            ai_response, error = generate_ai_response(user_input)
        
        # 处理结果
        if error:
            st.error(error)
        else:
            st.session_state.chat_history.append({
                "user": user_input,
                "ai": ai_response,
                "emotion": emotion,
                "polarity": polarity
            })
            st.rerun()

# 标签页2：情绪日记
with tab2:
    st.title("📓 情绪日记")
    st.markdown("#### 记录你的情绪，更好地了解自己")
    st.markdown("---")
    
    # 情绪日记表单
    with st.form("emotion_diary_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            diary_date = st.date_input("日期", value=date.today())
            emotion_type = st.selectbox("情绪类型", ["开心", "平静", "焦虑", "悲伤", "愤怒", "疲惫", "其他"])
        with col2:
            emotion_intensity = st.slider("情绪强度（1-10）", 1, 10, 5)
            coping_method = st.selectbox("应对方式", ["呼吸放松", "正念练习", "找人倾诉", "运动", "听音乐", "预约学校咨询", "其他"])
        
        diary_content = st.text_area("情绪描述", placeholder="描述一下你此刻的情绪、触发事件、感受...", height=100)
        submit_btn = st.form_submit_button("保存情绪日记", use_container_width=True)
        
        if submit_btn and diary_content:
            add_emotion_diary(
                date_str=diary_date.strftime("%Y-%m-%d"),
                emotion=emotion_type,
                intensity=emotion_intensity,
                content=diary_content,
                coping_method=coping_method
            )
    
    st.markdown("---")
    
    # 查看情绪日记和趋势
    st.markdown("### 📈 我的情绪趋势")
    if st.button("生成情绪趋势图", use_container_width=True):
        plot_emotion_trend()
    
    st.markdown("### 📋 历史情绪日记")
    if st.session_state.emotion_diary:
        for idx, diary in enumerate(reversed(st.session_state.emotion_diary[:5]), 1):
            with st.expander(f"📅 {diary['date']} - {diary['emotion']}（强度：{diary['intensity']}）"):
                st.markdown(f"**情绪描述**：{diary['content']}")
                st.markdown(f"**应对方式**：{diary['coping_method']}")
                st.markdown(f"**记录时间**：{diary['create_time']}")
    else:
        st.info("还没有记录情绪日记，开始记录你的第一条吧")

# 标签页3：焦虑自评
with tab3:
    st.title("📝 焦虑自评量表（GAD-7简化版）")
    st.markdown("#### 评估你的焦虑水平，了解自己的心理状态")
    st.markdown("---")
    
    # 自评表单
    with st.form("anxiety_assessment_form", clear_on_submit=True):
        st.markdown("**请根据过去2周的感受，选择最符合的选项：**")
        answers = []
        for i, q in enumerate(ANXIETY_SCALE):
            st.markdown(f"**{i+1}. {q['question']}**")
            answer = st.radio("", q['options'], key=f"q{i}", horizontal=True)
            answers.append(answer)
        
        submit_assessment = st.form_submit_button("提交评估", use_container_width=True)
        
        if submit_assessment:
            score, level, suggestion = calculate_anxiety_score(answers)
            assessment_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 保存自评记录
            st.session_state.anxiety_assessment.append({
                "time": assessment_time,
                "score": score,
                "level": level,
                "suggestion": suggestion,
                "answers": answers
            })
            
            # 显示评估结果
            st.markdown("---")
            with st.container(border=True):
                st.markdown(f"### 📊 你的评估结果")
                st.markdown(f"**总分**：{score}/21")
                st.markdown(f"**焦虑水平**：{level}")
                st.markdown(f"**专业建议**：{suggestion}")
                
                # 根据不同水平给出对应建议
                if level == "轻度焦虑":
                    st.markdown("#### 💡 推荐调节方法：")
                    st.markdown(f"- {ANXIETY_METHODS['呼吸放松法'][0]['name']}：{ANXIETY_METHODS['呼吸放松法'][0]['desc']}")
                elif level == "中度焦虑":
                    st.markdown("#### 💡 推荐调节方法：")
                    st.markdown(f"- {ANXIETY_METHODS['正念练习'][0]['name']}：{ANXIETY_METHODS['正念练习'][0]['desc']}")
                    st.markdown(f"- {ANXIETY_METHODS['认知调节'][0]['name']}：{ANXIETY_METHODS['认知调节'][0]['desc']}")
                    st.markdown(f"#### 🏫 学校支持：")
                    st.markdown(f"建议预约学校心理咨询：0411-86318792（门诊部）")
                elif level == "重度焦虑":
                    st.markdown("#### ⚠️ 重要提醒：")
                    st.markdown("请尽快联系学校心理健康教育中心或线下心理机构进行专业评估和干预！")
                    st.markdown(f"- 学校咨询电话：0411-86318792（门诊部）")
                    st.markdown(f"- 24小时危机热线：{DLPU_PSYCHOLOGY_RESOURCES['crisis_hotline']['dalian_hotline']}")
    
    st.markdown("---")
    
    # 查看历史自评记录
    st.markdown("### 📋 历史自评记录")
    if st.session_state.anxiety_assessment:
        for assessment in reversed(st.session_state.anxiety_assessment):
            with st.expander(f"🕒 {assessment['time']} - {assessment['level']}（{assessment['score']}分）"):
                st.markdown(f"**专业建议**：{assessment['suggestion']}")
    else:
        st.info("还没有进行焦虑自评，完成评估了解你的焦虑水平吧")

# 标签页4：正念练习引导
with tab4:
    st.title("🧠 正念练习引导")
    st.markdown("#### 跟随引导进行正念练习，缓解焦虑，活在当下")
    st.markdown("---")
    
    # 选择练习类型
    practice_type = st.selectbox("选择练习类型", ["5分钟正念冥想", "身体扫描冥想", "感恩冥想"], index=0)
    
    # 根据选择显示引导内容
    st.markdown("---")
    if practice_type == "5分钟正念冥想":
        with st.container(border=True):
            st.markdown("### 🧘 5分钟正念冥想引导")
            st.markdown("#### 准备阶段：")
            st.markdown("1. 找一个安静、舒适的环境，坐在椅子上或盘腿坐在垫子上")
            st.markdown("2. 保持脊柱挺直，放松肩膀，双手自然放在膝盖上")
            st.markdown("3. 轻轻闭上眼睛，或者将视线柔和地落在前方地面")
            
            st.markdown("#### 练习阶段（跟随引导）：")
            st.markdown("**第1分钟**：深呼吸3次，用鼻子吸气，嘴巴呼气，感受气息进出身体")
            st.markdown("**第2-4分钟**：将注意力集中在呼吸上，感受腹部的起伏")
            st.markdown("  - 当你发现思绪走神时，不要评判自己")
            st.markdown("  - 温和地将注意力拉回到呼吸上")
            st.markdown("**第5分钟**：慢慢将注意力扩展到全身，感受整体的放松状态")
            
            st.markdown("#### 结束阶段：")
            st.markdown("1. 慢慢睁开眼睛")
            st.markdown("2. 活动一下手指和脚趾，伸展身体")
            st.markdown("3. 感受此刻的身心状态，停留1分钟")
    
    elif practice_type == "身体扫描冥想":
        with st.container(border=True):
            st.markdown("### 🧘 身体扫描冥想引导（10分钟）")
            st.markdown("#### 准备阶段：")
            st.markdown("1. 平躺下来，找一个舒适的姿势，双腿自然分开，手臂放在身体两侧")
            st.markdown("2. 轻轻闭上眼睛，做3次深呼吸，放松全身")
            
            st.markdown("#### 扫描阶段：")
            st.markdown("**第1-2分钟**：将注意力带到双脚，感受脚趾、脚底、脚跟的感觉，停留并放松")
            st.markdown("**第3-4分钟**：慢慢向上扫描小腿、膝盖、大腿，每个部位停留并放松")
            st.markdown("**第5-6分钟**：扫描腹部、胸部、背部，感受呼吸带来的起伏")
            st.markdown("**第7-8分钟**：扫描肩膀、手臂、手部，逐个手指放松")
            st.markdown("**第9-10分钟**：扫描颈部、面部、头部，放松额头、眼睛、下巴")
            
            st.markdown("#### 结束阶段：")
            st.markdown("1. 感受全身的放松状态，深呼吸5次")
            st.markdown("2. 慢慢活动身体，坐起来，感受身体的变化")
    
    else:  # 感恩冥想
        with st.container(border=True):
            st.markdown("### 🧘 感恩冥想引导（3分钟）")
            st.markdown("#### 准备阶段：")
            st.markdown("1. 找一个安静的地方坐下，保持舒适的姿势")
            st.markdown("2. 闭上眼睛，深呼吸3次，让身心平静下来")
            
            st.markdown("#### 练习阶段：")
            st.markdown("**第1分钟**：回想今天发生的第一件值得感恩的小事")
            st.markdown("  - 可以是一杯温暖的咖啡，一个微笑，一次顺利的通勤")
            st.markdown("  - 感受这件事带来的温暖和美好")
            st.markdown("**第2分钟**：回想第二件值得感恩的小事")
            st.markdown("  - 可以是家人的关心，朋友的帮助，自己的一个小成就")
            st.markdown("  - 用心感受这份感恩的情绪")
            st.markdown("**第3分钟**：回想第三件值得感恩的小事")
            st.markdown("  - 可以是健康的身体，美好的自然，简单的快乐")
            st.markdown("  - 默念感谢，让感恩的情绪充满内心")
            
            st.markdown("#### 结束阶段：")
            st.markdown("1. 慢慢睁开眼睛")
            st.markdown("2. 带着这份感恩的心情，继续你的一天")
    
    # 练习计时器
    st.markdown("---")
    st.markdown("### ⏱️ 练习计时器")
    col1, col2, col3 = st.columns(3)
    with col1:
        timer_minutes = st.selectbox("选择时长（分钟）", [3, 5, 10, 15], index=1)
    with col2:
        if st.button("开始练习", use_container_width=True):
            st.session_state['timer_start'] = datetime.now()
            st.success(f"⏳ 开始{timer_minutes}分钟的{practice_type}练习，专注当下")
    with col3:
        if st.button("结束练习", use_container_width=True):
            if 'timer_start' in st.session_state:
                duration = (datetime.now() - st.session_state['timer_start']).total_seconds() / 60
                st.success(f"✅ 练习完成！你坚持了{duration:.1f}分钟，太棒了")
            else:
                st.info("还没有开始练习")

# 标签页5：大连工业大学师资团队
with tab5:
    st.title("👨‍🏫 大连工业大学 心理健康教育中心 师资团队")
    st.markdown("专业的心理咨询师团队，为你的心理健康保驾护航")
    st.markdown("---")
    
    # 先展示四宫格头像概览
    col1, col2, col3, col4 = st.columns(4)
    teacher_avatars = []
    for i, teacher in enumerate(DLPU_TEACHERS):
        avatar_path = safe_load_image(teacher["avatar_path"], teacher["name"])
        teacher_avatars.append(avatar_path)
    
    with col1:
        if teacher_avatars[0]:
            st.image(teacher_avatars[0], caption=DLPU_TEACHERS[0]["name"], use_container_width=True)
        else:
            st.markdown(f"""
            <div style="
                background-color: #f0f2f6;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            ">
                <span style="font-size: 50px; color: #4b5563;">👩‍🏫</span>
                <p style="margin-top: 10px; font-weight: bold; color: #1f2937;">{DLPU_TEACHERS[0]['name']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if teacher_avatars[1]:
            st.image(teacher_avatars[1], caption=DLPU_TEACHERS[1]["name"], use_container_width=True)
        else:
            st.markdown(f"""
            <div style="
                background-color: #f0f2f6;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            ">
                <span style="font-size: 50px; color: #4b5563;">👨‍🏫</span>
                <p style="margin-top: 10px; font-weight: bold; color: #1f2937;">{DLPU_TEACHERS[1]['name']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if teacher_avatars[2]:
            st.image(teacher_avatars[2], caption=DLPU_TEACHERS[2]["name"], use_container_width=True)
        else:
            st.markdown(f"""
            <div style="
                background-color: #f0f2f6;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            ">
                <span style="font-size: 50px; color: #4b5563;">👩‍🏫</span>
                <p style="margin-top: 10px; font-weight: bold; color: #1f2937;">{DLPU_TEACHERS[2]['name']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if teacher_avatars[3]:
            st.image(teacher_avatars[3], caption=DLPU_TEACHERS[3]["name"], use_container_width=True)
        else:
            st.markdown(f"""
            <div style="
                background-color: #f0f2f6;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            ">
                <span style="font-size: 50px; color: #4b5563;">👨‍🏫</span>
                <p style="margin-top: 10px; font-weight: bold; color: #1f2937;">{DLPU_TEACHERS[3]['name']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 展示每位教师详细信息
    for i, teacher in enumerate(DLPU_TEACHERS):
        with st.container(border=True):
            col_left, col_right = st.columns([1, 3])
            with col_left:
                avatar_path = teacher_avatars[i]
                if avatar_path:
                    st.image(avatar_path, use_container_width=True)
                else:
                    st.markdown(f"""
                    <div style="
                        background-color: #f0f2f6;
                        border-radius: 10px;
                        padding: 30px;
                        text-align: center;
                        height: 100%;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    ">
                        <span style="font-size: 80px; color: #4b5563;">{'👩‍🏫' if '女' in teacher['name'] or '楠' in teacher['name'] or '芬' in teacher['name'] else '👨‍🏫'}</span>
                    </div>
                    """, unsafe_allow_html=True)
            with col_right:
                st.markdown(f"### {teacher['name']}")
                st.markdown(f"**职称**：{teacher['title']}")
                st.markdown(f"**职位**：{teacher['position']}")
                st.markdown(f"**咨询经验**：{teacher['experience']}")
                
                st.markdown("**擅长领域**：")
                for field in teacher['fields']:
                    st.markdown(f"- {field}")
                
                st.markdown("**提供服务**：")
                for service in teacher['services']:
                    st.markdown(f"- {service}")
        st.markdown("---")

# 标签页6：学校咨询服务（包含校园心理资源自定义功能）
with tab6:
    # 标签页6：学校咨询服务（包含严格的权限控制）
    st.title("🏫 大连工业大学 心理咨询服务指南")
    st.markdown("#### 了解学校的心理咨询服务，获取专业的心理支持")
    st.markdown("---")
    
    # 显示当前用户权限状态
    if is_admin():
        st.success("👑 管理员模式：您可以管理所有心理资源")
    else:
        st.info("👤 游客模式：您只能查看心理资源内容")
    
    st.markdown("---")
    
    # 服务对象
    st.markdown("### 🎓 服务对象")
    st.markdown(f">{DLPU_CONSULT_SERVICE['service_object']}")
    
    st.markdown("---")
    
    # 服务类型
    st.markdown("### 📋 服务类型")
    for service in DLPU_CONSULT_SERVICE['service_type']:
        st.markdown(f"- {service}")
    
    st.markdown("---")
    
    # 预约方式
    st.markdown("### 📱 预约方式")
    for method in DLPU_CONSULT_SERVICE['reservation_method']:
        st.markdown(f"- {method}")
    
    st.markdown("---")
    
    # 咨询地点和时间
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📍 咨询地点")
        st.markdown(f">{DLPU_CONSULT_SERVICE['consult_address']}")
    with col2:
        st.markdown("### ⏰ 咨询时间")
        st.markdown(f">{DLPU_CONSULT_SERVICE['consult_time']}")
    
    st.markdown("---")
    
    # 服务原则
    st.markdown("### 📜 服务原则")
    for principle in DLPU_CONSULT_SERVICE['service_principle']:
        st.markdown(f"- {principle}")
    
    st.markdown("---")
    
    # 校园心理资源（严格的权限控制）
    st.markdown("### 📚 校园心理资源")
    
    # 资源类型选择
    resource_types = {
        "psychological_course": "心理健康课程",
        "psychological_activity": "心理健康活动", 
        "psychological_test": "心理测评工具",
        "online_resources": "线上资源"
    }
    
    resource_type_to_manage = st.selectbox(
        "选择资源类型",
        list(resource_types.values()),
        key="resource_type_select"
    )
    
    # 获取对应的键
    resource_type_key = [k for k, v in resource_types.items() if v == resource_type_to_manage][0]
    
    # 只有管理员才能看到资源管理功能
    if is_admin():
        st.markdown("#### 📝 资源管理（管理员专属）")
        
        # 添加资源表单
        with st.form("add_resource_form", clear_on_submit=True):
            new_resource = st.text_area(
                "新增资源内容", 
                placeholder=f"请输入新的{resource_type_to_manage}内容...",
                height=100
            )
            col1, col2 = st.columns(2)
            with col1:
                submit_add = st.form_submit_button("➕ 添加资源", use_container_width=True)
            with col2:
                clear_form = st.form_submit_button("🗑️ 清空内容", use_container_width=True)
            
            if submit_add and new_resource.strip():
                # 添加资源到自定义资源列表
                if resource_type_key not in st.session_state.custom_psychology_resources:
                    st.session_state.custom_psychology_resources[resource_type_key] = []
                st.session_state.custom_psychology_resources[resource_type_key].append(new_resource)
                st.success("✅ 资源添加成功！")
                st.rerun()
        
        st.markdown("---")
        
        # 显示自定义资源（管理员可以管理）
        st.markdown("#### 🔧 自定义资源管理")
        if (resource_type_key in st.session_state.custom_psychology_resources and 
            st.session_state.custom_psychology_resources[resource_type_key]):
            
            for idx, resource in enumerate(st.session_state.custom_psychology_resources[resource_type_key]):
                col_content, col_delete = st.columns([5, 1])
                with col_content:
                    st.markdown(f"🔹 {resource}")
                with col_delete:
                    if st.button("🗑️ 删除", key=f"delete_{resource_type_key}_{idx}"):
                        # 删除资源
                        st.session_state.custom_psychology_resources[resource_type_key].pop(idx)
                        st.success("✅ 资源已删除！")
                        st.rerun()
        else:
            st.info(f"暂无自定义{resource_type_to_manage}，请添加")
    else:
        # 游客只能查看，完全隐藏编辑功能
        st.markdown("#### 📋 资源查看")
        st.info("💡 提示：您当前以游客身份访问，只能查看资源内容。如需管理权限，请使用管理员账号登录。")
    
    st.markdown("---")
    
    # 显示完整的资源列表（所有用户可见）
    st.markdown(f"#### 📋 完整的{resource_type_to_manage}列表")
    
    combined_resources = get_combined_resources()
    all_resources = combined_resources[resource_type_key]
    
    if all_resources:
        for resource in all_resources:
            # 标记自定义资源
            is_custom = (resource_type_key in st.session_state.custom_psychology_resources and 
                        resource in st.session_state.custom_psychology_resources[resource_type_key])
            icon = "🔹" if is_custom else "📌"
            label = "（管理员添加）" if is_custom else "（系统内置）"
            st.markdown(f"{icon} {resource} {label}")
    else:
        st.info(f"暂无{resource_type_to_manage}内容")
    
    st.markdown("---")
    
    # 危机干预热线
    st.markdown("### 🆘 危机干预热线")
    st.markdown(f"- **学校工作日热线**：0411-86318792（门诊部）")
    st.markdown(f"- **大连市24小时热线**：{DLPU_PSYCHOLOGY_RESOURCES['crisis_hotline']['dalian_hotline']}")
    st.markdown(f"- **辽宁省24小时热线**：{DLPU_PSYCHOLOGY_RESOURCES['crisis_hotline']['provincial_hotline']}")
    st.markdown(f"- **全国24小时热线**：{DLPU_PSYCHOLOGY_RESOURCES['crisis_hotline']['national_hotline']}")
    
    st.markdown("---")
    
    # 温馨提示
    with st.info("💡 温馨提示"):
        st.markdown(DLPU_CONSULT_SERVICE['notice'])
    
    # 新增：心理健康科普
    st.markdown("---")
    st.markdown("### 📖 心理健康科普")
    tab6_1, tab6_2, tab6_3 = st.tabs(["常见问题", "健康贴士", "危机识别"])
    with tab6_1:
        for problem in DLPU_PSYCHOLOGY_SCIENCE["common_problems"]:
            with st.expander(problem['title']):
                st.markdown(problem['content'])
    with tab6_2:
        st.markdown("### 日常心理健康维护建议")
        for tip in DLPU_PSYCHOLOGY_SCIENCE["mental_health_tips"]:
            st.markdown(f"- {tip}")
    with tab6_3:
        st.markdown(f"### {DLPU_PSYCHOLOGY_SCIENCE['crisis_identification']['title']}")
        st.markdown(DLPU_PSYCHOLOGY_SCIENCE['crisis_identification']['content'])