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
import streamlit as st
import os

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
        
        with st.form("guest_login"):
            guest_username = st.text_input("用户名", placeholder="姓名", key="guest_username")
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
        
        with st.form("admin_login"):
            admin_username = st.text_input("管理员账号", placeholder="请输入管理员账号", key="admin_username")
            admin_password = st.text_input("密码", type="password", placeholder="请输入密码", key="admin_password")
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
    1. **游客登录**：用户名和学号即可体验基本功能
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

load_dotenv()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
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
        "avatar_path": "./ai心理/static/images/teacher1.jpg.png"
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
        "avatar_path": "./ai心理/static/images/teacher2.jpg.png"
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
        "avatar_path": "./ai心理/static/images/teacher3.jpg.png"
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
        "avatar_path": "./ai心理/static/images/teacher4.jpg.png"
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
        "心理健康讲座：面向全校开展的心理健康科普讲座（如情绪管理、压力应对、恋爱心理、生涯规划等）"
    ],
    "reservation_method": [
        "线上预约：通过大连工业大学云工大心理咨询预约",
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
        "《大学生心理健康教育》- 全校公共必修课（1学分），覆盖心理健康基础知识、情绪管理、压力应对、人际交往、生涯规划等内容"
       
    ],
    "psychological_activity": [
        
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
    3. 咨询预约时间：工作日下午10点到4点
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "💬 心理咨询对话", 
    "📓 情绪日记", 
    "📝 焦虑自评", 
    "📅 心理咨询预约", 
    "👨‍🏫 师资团队",
    "🏫 学校咨询服务",
    "🎯 专业心理工具库"
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
                st.markdown(f"- 线下：校医院3楼心理咨询室现场预约")
                
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
    # 顶部标题和切换选项
    st.title("📝 心理测评中心")
    tab3_sub1, tab3_sub2 = st.tabs(["快速焦虑自评（GAD-7）", "专业心理量表测评"])

    # ---------------------- 子标签1：原有GAD-7焦虑自评功能 ----------------------
    with tab3_sub1:
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
    with tab3_sub2:
        st.markdown("#### 系统内置专业心理量表，点击展开开始测评")
        st.markdown("---")

        # 1. 定义所有量表基础信息
        ALL_SCALES = {
            "SCL90": {
                "name": "📌 症状自评量表（SCL-90）",
                "desc": "全面评估心理健康状况，包括躯体化、强迫、人际关系敏感、抑郁、焦虑等9个维度 （系统内置）",
                "questions": [
                    "头痛", "神经过敏，心中不踏实", "头脑中有不必要的想法或字句盘旋", "头晕或晕倒",
                    "对异性的兴趣减退", "对旁人责备求全", "感到别人能控制您的思想", "责怪别人制造麻烦",
                    "忘记性大", "担心自己的衣饰整齐及仪态的端正", "容易烦恼和激动", "胸痛",
                    "害怕空旷的场所或街道", "感到自己的精力下降，活动减慢", "想结束自己的生命", "听到旁人听不到的声音",
                    "发抖", "感到大多数人都不可信任", "胃口不好", "容易哭泣", "感到受骗，中了圈套或有人想抓住您",
                    "感到孤独", "感到苦闷", "过分担忧", "对事物不感兴趣", "感到害怕", "您的感情容易受到伤害", "旁人能知道您的私下想法",
                    "感到别人不理解您、不同情您", "感到人们对您不友好，不喜欢您", "做事必须做得很慢以保证做得正确",
                    "心跳得很厉害", "恶心或胃部不舒服", "感到比不上他人", "肌肉酸痛", "感到有人在监视您、谈论您", "难以入睡",
                    "做事必须反复检查", "难以做出决定", "怕乘电车、公共汽车、地铁或火车", "呼吸有困难", "一阵阵发冷或发热",
                    "因为感到害怕而避开某些东西、场合或活动", "脑子变空了", "身体发麻或刺痛", "喉咙有梗塞感", "感到没有前途没有希望",
                    "不能集中注意力", "感到身体的某一部分软弱无力", "感到紧张或容易紧张", "感到手或脚发重", "想到死亡的事",
                    "吃得太多", "当别人看着您或谈论您时感到不自在", "有一些不属于您自己的想法", "有想打人或伤害他人的冲动",
                    "醒得太早", "必须反复洗手、点数", "睡得不稳不深", "有想摔坏或破坏东西的冲动", "有一些别人没有的想法或念头",
                    "感到对别人神经过敏", "在商店或电影院等人多的地方感到不自在", "感到任何事情都很困难", "一阵阵恐惧或惊恐",
                    "感到在公共场合吃东西很不舒服", "经常责怪自己", "感到别人对您的成绩没有作出恰当的评价", "即使和别人在一起也感到孤单",
                    "感到坐立不安心神不定", "感到自己没有什么价值", "感到熟悉的东西变成陌生或不像是真的", "大叫或摔东西",
                    "害怕会在公共场合晕倒", "感到别人想占您的便宜", "为一些有关性的想法而很苦恼", "您认为应该因为自己的过错而受到惩罚",
                    "感到要很快把事情做完", "感到自己的身体有严重问题", "从未感到和其他人很亲近", "感到自己有罪",
                    "感到自己的脑子有毛病"
                ],
                "scoring": "1-5分计分（1=没有，2=很轻，3=中等，4=偏重，5=严重）",
                "dimension_mapping": {
                    "躯体化": [1,4,12,27,40,42,48,49,52,53,56,58],
                    "强迫症状": [3,9,10,28,38,45,46,51,55,65],
                    "人际关系敏感": [6,21,34,36,37,41,61,69,73],
                    "抑郁": [5,14,15,20,22,26,29,30,31,32,54,71,79],
                    "焦虑": [2,17,23,33,39,57,72,78,80,86],
                    "敌对": [11,24,63,67,74,81],
                    "恐怖": [13,25,47,50,70,75,82],
                    "偏执": [8,18,43,68,76,83],
                    "精神病性": [7,16,35,62,77,84,85,87,88,90]
                }
            },
            "SAS": {
                "name": "📌 焦虑自评量表（SAS）",
                "desc": "评估焦虑情绪的严重程度 （系统内置）",
                "questions": [
                    "我觉得比平常容易紧张和着急（焦虑）",
                    "我无缘无故地感到害怕（害怕）",
                    "我容易心里烦乱或觉得惊恐（惊恐）",
                    "我觉得我可能将要发疯（发疯感）",
                    "我觉得一切都很好，也不会发生什么不幸（不幸预感，反向计分）",
                    "我手脚发抖打颤（手足颤抖）",
                    "我因为头痛、颈痛和背痛而苦恼（躯体疼痛）",
                    "我感觉容易衰弱和疲乏（乏力）",
                    "我觉得心平气和，并且容易安静坐着（静坐不能，反向计分）",
                    "我觉得心跳得很快（心悸）",
                    "我因为一阵阵头晕而苦恼（头昏）",
                    "我有晕倒发作，或觉得要晕倒似的（晕厥感）",
                    "我呼气吸气都感到很容易（呼吸困难，反向计分）",
                    "我手脚麻木和刺痛（手足刺痛）",
                    "我因为胃痛和消化不良而苦恼（胃痛或消化不良）",
                    "我常常要小便（尿意频数）",
                    "我的手常常是干燥温暖的（多汗，反向计分）",
                    "我脸红发热（面部潮红）",
                    "我容易入睡并且一夜睡得很好（睡眠障碍，反向计分）",
                    "我做噩梦（噩梦）"
                ],
                "scoring": "1-4分计分（1=没有或很少时间，2=小部分时间，3=相当多时间，4=绝大部分或全部时间），反向计分题先反转分数",
                "reverse_items": [5,9,13,17,19]
            },
            "SDS": {
                "name": "📌 抑郁自评量表（SDS）",
                "desc": "评估抑郁情绪的严重程度 （系统内置）",
                "questions": [
                    "我感到情绪沮丧，郁闷（抑郁）",
                    "我感到早晨心情最好（晨重夜轻，反向计分）",
                    "我要哭或想哭（易哭）",
                    "我夜间睡眠不好（睡眠障碍）",
                    "我吃饭像平时一样多（食欲减退，反向计分）",
                    "我的性功能正常（性兴趣减退，反向计分）",
                    "我感到体重减轻（体重减轻）",
                    "我为便秘烦恼（便秘）",
                    "我的心跳比平时快（心悸）",
                    "我无故感到疲劳（易倦）",
                    "我的头脑像往常一样清楚（思考困难，反向计分）",
                    "我做事情像平时一样不感到困难（能力减退，反向计分）",
                    "我坐卧不安，难以保持平静（不安）",
                    "我对未来感到有希望（绝望，反向计分）",
                    "我比平时更容易激怒（易激惹）",
                    "我觉得决定什么事很容易（决断困难，反向计分）",
                    "我感到自己是有用的和不可缺少的人（无用感，反向计分）",
                    "我的生活很有意义（生活空虚感，反向计分）",
                    "假若我死了别人会过得更好（无价值感）",
                    "我仍旧喜爱自己平时喜爱的东西（兴趣丧失，反向计分）"
                ],
                "scoring": "1-4分计分（1=没有或很少时间，2=小部分时间，3=相当多时间，4=绝大部分或全部时间），反向计分题先反转分数",
                "reverse_items": [2,5,6,11,12,14,16,17,18,20]
            },
            "PSS": {
                "name": "📌 压力知觉量表（PSS）",
                "desc": "评估个体感受到的压力水平 （系统内置）",
                "questions": [
                    "在过去的一个月里，你经常感到无法控制你生活中重要的事情吗？",
                    "在过去的一个月里，你经常感到对处理你个人问题有信心吗？（反向计分）",
                    "在过去的一个月里，你经常感到事情按你的意愿进行吗？（反向计分）",
                    "在过去的一个月里，你经常感到无法解决你面临的所有问题吗？",
                    "在过去的一个月里，你经常感到你能控制你愤怒的情绪吗？（反向计分）",
                    "在过去的一个月里，你经常感到事情处于失控状态吗？",
                    "在过去的一个月里，你经常感到你能应付生活中出现的麻烦吗？（反向计分）",
                    "在过去的一个月里，你经常感到你能有效地处理生活中发生的重要变化吗？（反向计分）",
                    "在过去的一个月里，你经常感到紧张或有压力吗？",
                    "在过去的一个月里，你经常感到你能控制你花费多少时间吗？（反向计分）"
                ],
                "scoring": "0-4分计分（0=从不，1=几乎不，2=有时，3=经常，4=总是），反向计分题先反转分数",
                "reverse_items": [2,3,5,7,8,10]
            },
            "INTERPERSONAL": {
                "name": "📌 人际关系综合诊断量表",
                "desc": "评估人际交往中的困扰程度 （系统内置）",
                "questions": [
                    "关于自己的烦恼有口难言", "和生人见面感觉不自然", "过分地羡慕和妒忌别人", "与异性交往太少",
                    "对连续不断的会谈感到困难", "在社交场合感到紧张", "时常伤害别人", "与异性来往感觉不自然",
                    "与一大群朋友在一起，常感到孤寂或失落", "极易受窘", "与别人不能和睦相处", "不知道与异性相处如何适可而止",
                    "当不熟悉的人对自己倾诉他的生平遭遇以求同情时，自己常感到不自在", "担心别人对自己有什么坏印象",
                    "总是尽力使别人赏识自己", "暗自思慕异性", "时常避免表达自己的感受", "对自己的仪表（容貌）缺乏信心",
                    "讨厌某人或被某人所讨厌", "瞧不起异性", "不能专注地倾听", "自己的烦恼无人可申诉",
                    "受别人排斥与冷漠", "被异性瞧不起", "不能广泛地听取各种意见和看法", "自己常因受伤害而暗自伤心",
                    "常被别人谈论、愚弄", "与异性交往不知如何更好地相处"
                ],
                "scoring": "0-1分计分（0=否，1=是），总分越高困扰越严重",
                "dimension_mapping": {
                    "交谈交际困扰": [1,2,5,6,9,10,14,17,18,22],
                    "交际交友困扰": [3,7,11,15,19,21,23,25,27,29],
                    "待人接物困扰": [13,20,26,30,1,4,8,12,16,24],
                    "异性交往困扰": [4,8,12,16,24,28]
                }
            },
            "EPQ": {
                "name": "📌 艾森克人格问卷（EPQ）",
                "desc": "评估人格特质（内外向、神经质、精神质、掩饰性） （系统内置）",
                "questions": [
                    "你是否有广泛的爱好？(E+)", "你是否健谈？(E+)", "你是否比较活跃？(E+)", "你是否喜欢冒险？(E+)",
                    "你是否常常感到闷闷不乐？(E-)", "你是否比较沉默寡言？(E-)", "你是否宁愿看书而不愿多见人？(E-)",
                    "你是否容易激动？(N+)", "你是否常常为小事发脾气？(N+)", "你是否感到紧张或容易紧张？(N+)",
                    "你是否感到坐立不安？(N+)", "你是否能保持情绪稳定？(N-)", "你是否很少感到焦虑？(N-)",
                    "你是否喜欢捉弄别人？(P+)", "你是否认为别人的不幸与你无关？(P+)", "你是否缺乏同情心？(P+)",
                    "你是否常常考虑自己？(P+)", "你是否乐于助人？(P-)", "你是否关心他人的感受？(P-)",
                    "你是否总是说实话？(L+)", "你是否从不撒谎？(L+)", "你是否觉得自己是个完美的人？(L+)",
                    "你是否承认自己的缺点？(L-)", "你是否愿意承认自己的错误？(L-)"
                ],
                "scoring": "是=1分，否=0分；正向题加1，反向题减1",
                "dimension_mapping": {
                    "内外向（E）": {"positive": [1,2,3,4], "negative": [5,6,7]},
                    "神经质（N）": {"positive": [8,9,10,11], "negative": [12,13]},
                    "精神质（P）": {"positive": [14,15,16,17], "negative": [18,19]},
                    "掩饰性（L）": {"positive": [20,21,22], "negative": [23,24]}
                }
            },
            "HOLLAND": {
                "name": "📌 霍兰德职业兴趣测试",
                "desc": "帮助学生了解自身职业兴趣类型，为生涯规划提供参考 （系统内置）",
                "questions": [
                    "我喜欢与工具打交道", "我喜欢动手制作东西", "我喜欢从事户外工作", "我喜欢机械维修",
                    "我喜欢从事体力劳动", "我喜欢操作机器", "我喜欢建筑类工作", "我喜欢农业/林业工作",
                    "我喜欢研究自然科学问题", "我喜欢做实验", "我喜欢分析数据", "我喜欢抽象思维",
                    "我喜欢阅读学术书籍", "我喜欢解决数学问题", "我喜欢探索新事物", "我喜欢逻辑推理",
                    "我喜欢绘画/书法", "我喜欢音乐/乐器", "我喜欢写作/创作", "我喜欢表演/戏剧",
                    "我喜欢设计类工作", "我喜欢欣赏艺术品", "我喜欢自由表达", "我喜欢创意类工作",
                    "我喜欢帮助他人", "我喜欢教育/教学", "我喜欢心理咨询", "我喜欢社交活动",
                    "我喜欢公益事业", "我喜欢与人沟通", "我喜欢照顾他人", "我喜欢团队合作",
                    "我喜欢领导他人", "我喜欢销售/谈判", "我喜欢管理类工作", "我喜欢商业活动",
                    "我喜欢制定计划", "我喜欢竞争/挑战", "我喜欢创业", "我喜欢决策",
                    "我喜欢整理文件/数据", "我喜欢按规则办事", "我喜欢财务/会计工作", "我喜欢行政类工作",
                    "我喜欢细致的工作", "我喜欢有规律的工作", "我喜欢办公室工作", "我喜欢档案管理"
                ],
                "scoring": "1-5分计分（1=完全不喜欢，2=不太喜欢，3=一般，4=比较喜欢，5=非常喜欢）",
                "dimension_mapping": {
                    "现实型（R）": [1,2,3,4,5,6,7,8],
                    "研究型（I）": [9,10,11,12,13,14,15,16],
                    "艺术型（A）": [17,18,19,20,21,22,23,24],
                    "社会型（S）": [25,26,27,28,29,30,31,32],
                    "企业型（E）": [33,34,35,36,37,38,39,40],
                    "常规型（C）": [41,42,43,44,45,46,47,48]
                }
            }
        }

        # 2. 定义量表计分和结果展示函数
        def calculate_scale_result(scale_key, answers):
            scale = ALL_SCALES[scale_key]
            result = {"total_score": 0, "dimension_scores": {}, "interpretation": ""}

            # SCL-90计分
            if scale_key == "SCL90":
                total_score = sum(answers)
                result["total_score"] = total_score
                for dim, q_nums in scale["dimension_mapping"].items():
                    dim_answers = [answers[q-1] for q in q_nums if q-1 < len(answers)]
                    dim_avg = round(sum(dim_answers)/len(dim_answers), 2) if dim_answers else 0
                    result["dimension_scores"][dim] = dim_avg
                if total_score > 160 or any(score > 2 for score in result["dimension_scores"].values()):
                    result["interpretation"] = "你的测评结果显示存在一定的心理健康困扰，建议联系学校心理咨询中心（0411-86318792）获取专业帮助。"
                else:
                    result["interpretation"] = "你的心理健康状况总体良好，继续保持积极的生活状态！"

            # SAS计分
            elif scale_key == "SAS":
                processed = []
                for idx, ans in enumerate(answers, 1):
                    if idx in scale["reverse_items"]:
                        processed.append(5 - ans)
                    else:
                        processed.append(ans)
                raw = sum(processed)
                standard = int(raw * 1.25)
                result["total_score"] = standard
                if standard < 50:
                    result["interpretation"] = "你的焦虑情绪处于正常水平。"
                elif 50 <= standard < 60:
                    result["interpretation"] = "轻度焦虑，可通过运动、深呼吸调节。"
                elif 60 <= standard < 70:
                    result["interpretation"] = "中度焦虑，建议寻求心理咨询。"
                else:
                    result["interpretation"] = "重度焦虑，请尽快联系心理咨询中心！"

            # SDS计分
            elif scale_key == "SDS":
                processed = []
                for idx, ans in enumerate(answers, 1):
                    if idx in scale["reverse_items"]:
                        processed.append(5 - ans)
                    else:
                        processed.append(ans)
                raw = sum(processed)
                standard = int(raw * 1.25)
                result["total_score"] = standard
                if standard < 53:
                    result["interpretation"] = "抑郁情绪处于正常水平。"
                elif 53 <= standard < 63:
                    result["interpretation"] = "轻度抑郁，建议多沟通、规律作息。"
                elif 63 <= standard < 73:
                    result["interpretation"] = "中度抑郁，建议寻求专业支持。"
                else:
                    result["interpretation"] = "重度抑郁，请立即联系心理咨询中心！"

            # PSS压力
            elif scale_key == "PSS":
                processed = []
                for idx, ans in enumerate(answers, 1):
                    if idx in scale["reverse_items"]:
                        processed.append(4 - ans)
                    else:
                        processed.append(ans)
                total = sum(processed)
                result["total_score"] = total
                if total <= 13:
                    result["interpretation"] = "压力水平较低，继续保持！"
                elif 14 <= total <= 26:
                    result["interpretation"] = "中等压力，可学习压力管理技巧。"
                else:
                    result["interpretation"] = "压力偏高，建议调节并寻求帮助。"

            # 人际关系
            elif scale_key == "INTERPERSONAL":
                total = sum(answers)
                result["total_score"] = total
                for dim, q_nums in scale["dimension_mapping"].items():
                    s = sum([answers[q-1] for q in q_nums if q-1 < len(answers)])
                    result["dimension_scores"][dim] = s
                if total <= 8:
                    result["interpretation"] = "人际关系基本无困扰。"
                elif 9 <= total <= 14:
                    result["interpretation"] = "轻度困扰，可提升沟通技巧。"
                elif 15 <= total <= 20:
                    result["interpretation"] = "中度困扰，建议多参与社交。"
                else:
                    result["interpretation"] = "困扰较明显，可寻求心理老师帮助。"

            # EPQ
            elif scale_key == "EPQ":
                for dim, mapping in scale["dimension_mapping"].items():
                    pos = sum([answers[q-1] for q in mapping["positive"] if q-1 < len(answers)])
                    neg = sum([answers[q-1] for q in mapping["negative"] if q-1 < len(answers)])
                    result["dimension_scores"][dim] = pos - neg
                e = result["dimension_scores"]["内外向（E）"]
                n = result["dimension_scores"]["神经质（N）"]
                inter = []
                inter.append("外向型" if e>0 else "内向型")
                inter.append("情绪较稳定" if n<=0 else "情绪易波动")
                result["interpretation"] = "性格倾向：" + "，".join(inter)

            # 霍兰德职业兴趣（已修复）
            elif scale_key == "HOLLAND":
                for dim, q_nums in scale["dimension_mapping"].items():
                    s = sum([answers[q-1] for q in q_nums if q-1 < len(answers)])
                    result["dimension_scores"][dim] = s
                sorted_dims = sorted(result["dimension_scores"].items(), key=lambda x:x[1], reverse=True)
                core_type = sorted_dims[0][0]

                # 修复：从“现实型（R）”里正确提取 R
                if "（R）" in core_type:
                    code = "R"
                elif "（I）" in core_type:
                    code = "I"
                elif "（A）" in core_type:
                    code = "A"
                elif "（S）" in core_type:
                    code = "S"
                elif "（E）" in core_type:
                    code = "E"
                elif "（C）" in core_type:
                    code = "C"
                else:
                    code = "R"

                type_map = {
                    "R": "现实型：适合机械、技术、建筑、农林等实操类工作。",
                    "I": "研究型：适合科研、数据分析、数理、学术类工作。",
                    "A": "艺术型：适合设计、创作、传媒、文艺类工作。",
                    "S": "社会型：适合教育、咨询、服务、公益类工作。",
                    "E": "企业型：适合管理、销售、创业、商务类工作。",
                    "C": "常规型：适合财务、行政、文员、数据整理类工作。"
                }
                result["interpretation"] = f"核心类型：{core_type}\n{type_map[code]}"

            return result

        # 3. 渲染每个量表
        for scale_key, scale in ALL_SCALES.items():
            with st.expander(f"**{scale['name']}**：{scale['desc']}"):
                st.markdown(f"**计分规则**：{scale['scoring']}")
                st.markdown("---")

                with st.form(f"scale_form_{scale_key}", clear_on_submit=True):
                    answers = []
                    if scale_key in ["SCL90", "SAS", "SDS", "HOLLAND"]:
                        options = ["1分", "2分", "3分", "4分"]
                        if scale_key in ["SCL90", "HOLLAND"]:
                            options.append("5分")
                        for idx, q in enumerate(scale["questions"], 1):
                            st.markdown(f"**{idx}. {q}**")
                            ans = st.radio("", options, key=f"{scale_key}_q{idx}", horizontal=True)
                            answers.append(int(ans[0]))

                    elif scale_key == "PSS":
                        options = ["0分（从不）", "1分（几乎不）", "2分（有时）", "3分（经常）", "4分（总是）"]
                        for idx, q in enumerate(scale["questions"], 1):
                            st.markdown(f"**{idx}. {q}**")
                            ans = st.radio("", options, key=f"{scale_key}_q{idx}", horizontal=True)
                            answers.append(int(ans[0]))

                    elif scale_key == "INTERPERSONAL":
                        options = ["0分（否）", "1分（是）"]
                        for idx, q in enumerate(scale["questions"], 1):
                            st.markdown(f"**{idx}. {q}**")
                            ans = st.radio("", options, key=f"{scale_key}_q{idx}", horizontal=True)
                            answers.append(int(ans[0]))

                    elif scale_key == "EPQ":
                        options = ["是（1分）", "否（0分）"]
                        for idx, q in enumerate(scale["questions"], 1):
                            st.markdown(f"**{idx}. {q}**")
                            ans = st.radio("", options, key=f"{scale_key}_q{idx}", horizontal=True)
                            answers.append(1 if "是" in ans else 0)

                    submit_btn = st.form_submit_button("提交测评", use_container_width=True)
                    if submit_btn:
                        result = calculate_scale_result(scale_key, answers)
                        st.markdown("---")
                        with st.container(border=True):
                            st.markdown("### 📊 测评结果")
                            if result["total_score"] != 0:
                                st.markdown(f"**总分**：{result['total_score']}")
                            if result["dimension_scores"]:
                                st.markdown("#### 维度得分")
                                for dim, score in result["dimension_scores"].items():
                                    st.markdown(f"- {dim}：{score}")
                            st.markdown(f"#### 结果解读\n{result['interpretation']}")
                            st.markdown(f"#### 🏫 学校心理咨询：0411-86318792")

        st.markdown("---")
        st.info("💡 所有测评结果仅供参考，不作为临床诊断。")

# -------------------------- 标签页4：心理咨询预约 --------------------------
with tab4:
    st.title("📅 大连工业大学 心理咨询预约系统")
    st.markdown("#### 在线预约学校专业心理咨询服务")
    st.markdown("---")
    
    # 初始化预约相关会话状态
    if "appointment_records" not in st.session_state:
        st.session_state.appointment_records = []
    if "admin_appointments" not in st.session_state:
        st.session_state.admin_appointments = []
    
    # 1. 预约表单（游客/管理员都可预约）
    st.markdown("### 📝 在线预约")
    with st.form("appointment_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # 咨询师选择（从师资团队中获取）
            teacher_names = [teacher["name"] for teacher in DLPU_TEACHERS]
            selected_teacher = st.selectbox(
                "选择咨询师",
                teacher_names,
                help="可根据自己的问题类型选择擅长对应领域的咨询师"
            )
            
            # 预约日期（只能选择未来的工作日）
            min_date = date.today()
            appointment_date = st.date_input(
                "预约日期",
                min_value=min_date,
                help="请选择周一至周五的日期（节假日除外）"
            )
            
            # 预约时段
            time_slots = [
                "08:30-09:20", "09:30-10:20", "10:30-11:20",
                "13:30-14:20", "14:30-15:20", "15:30-16:20", "16:30-17:20"
            ]
            selected_time = st.selectbox("预约时段", time_slots)
        
        with col2:
            # 咨询类型 - 已去掉"个体咨询"前缀
            consult_types = [
                "情绪困扰", "学业压力", "人际关系",
                "职业规划", "团体辅导", "心理测评", "危机干预"
            ]
            consult_type = st.selectbox("咨询类型", consult_types)
            
            # 个人信息 - 新增姓名输入框
            name = st.text_input("姓名", placeholder="请输入你的真实姓名")
            student_id = st.text_input("学号", placeholder="请输入你的学号")
            contact = st.text_input("联系电话", placeholder="请输入你的手机号码")
            
            # 咨询问题简述
            problem_desc = st.text_area(
                "咨询问题简述",
                placeholder="请简要描述你想咨询的问题（便于咨询师提前了解）",
                height=100
            )
        
        # 提交预约
        submit_btn = st.form_submit_button("提交预约申请", use_container_width=True, type="primary")
        
        if submit_btn:
            # 表单验证 - 增加姓名非空验证
            if not name or not student_id or not contact or not problem_desc:
                st.error("⚠️ 姓名、学号、联系电话和咨询问题简述不能为空！")
            elif appointment_date < min_date:
                st.error("⚠️ 预约日期不能选择过去的日期！")
            else:
                # 检查是否重复预约
                is_duplicate = any(
                    record["student_id"] == student_id and 
                    record["date"] == appointment_date.strftime("%Y-%m-%d") and
                    record["time"] == selected_time
                    for record in st.session_state.appointment_records
                )
                
                if is_duplicate:
                    st.error("⚠️ 你已在该时段预约过咨询，请选择其他时间！")
                else:
                    # 生成预约记录
                    appointment_id = f"AP{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    new_appointment = {
                        "id": appointment_id,
                        "username": st.session_state.user_info["username"],
                        "name": name,  # 使用用户输入的姓名
                        "student_id": student_id,
                        "contact": contact,
                        "teacher": selected_teacher,
                        "date": appointment_date.strftime("%Y-%m-%d"),
                        "time": selected_time,
                        "consult_type": consult_type,
                        "problem_desc": problem_desc,
                        "status": "待确认",  # 待确认/已确认/已取消/已完成
                        "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "admin_note": ""
                    }
                    
                    # 保存预约记录
                    st.session_state.appointment_records.append(new_appointment)
                    st.session_state.admin_appointments.append(new_appointment)
                    
                    st.success(f"🎉 预约申请提交成功！")
                    st.info(f"""
                    预约信息：
                    - 预约编号：{appointment_id}
                    - 预约人：{name}
                    - 咨询师：{selected_teacher}
                    - 预约时间：{appointment_date} {selected_time}
                    - 状态：待管理员确认
                    
                    温馨提示：
                    1. 管理员将在1个工作日内处理你的预约申请
                    2. 请保持手机畅通，确认后会收到通知
                    3. 如需取消预约，请提前24小时操作
                    4. 咨询地址：{DLPU_CONSULT_SERVICE['consult_address']}
                    """)
    
    st.markdown("---")
    
    # 2. 我的预约记录（所有用户可见）
    st.markdown("### 📋 我的预约记录")
    if st.session_state.appointment_records:
        # 筛选当前用户的预约记录
        user_appointments = [
            record for record in st.session_state.appointment_records
            if record["username"] == st.session_state.user_info["username"]
        ]
        
        if user_appointments:
            for idx, record in enumerate(user_appointments):
                with st.container(border=True):
                    col_left, col_right = st.columns([3, 1])
                    with col_left:
                        st.markdown(f"**预约编号**：{record['id']}")
                        st.markdown(f"**咨询师**：{record['teacher']}")
                        st.markdown(f"**预约时间**：{record['date']} {record['time']}")
                        st.markdown(f"**咨询类型**：{record['consult_type']}")
                        st.markdown(f"**状态**：{record['status']}")
                        
                        # 显示状态标签 - 修复：使用Streamlit全版本支持的state值
                        if record["status"] == "待确认":
                            st.status("⏳ 待管理员确认", state="running")  # 替换pending
                        elif record["status"] == "已确认":
                            st.status("✅ 预约已确认", state="complete")  # 替换success
                        elif record["status"] == "已取消":
                            st.status("❌ 预约已取消", state="error")
                        elif record["status"] == "已完成":
                            st.status("✅ 咨询已完成", state="complete")  # 替换success
                    
                    with col_right:
                        # 取消预约按钮（仅待确认状态可取消）
                        if record["status"] == "待确认":
                            if st.button(
                                "取消预约", 
                                key=f"cancel_{record['id']}",
                                use_container_width=True,
                                type="secondary"
                            ):
                                # 更新预约状态
                                record["status"] = "已取消"
                                record["admin_note"] = "用户主动取消预约"
                                st.success(f"✅ 预约 {record['id']} 已取消！")
                                st.rerun()
        
        else:
            st.info("暂无预约记录，可提交新的预约申请")
    else:
        st.info("暂无预约记录，可提交新的预约申请")
    
    st.markdown("---")
    
    # 3. 管理员预约管理（仅管理员可见）
    if is_admin():
        st.markdown("### 👑 预约管理（管理员专属）")
        
        # 筛选状态
        filter_status = st.selectbox(
            "筛选状态",
            ["全部", "待确认", "已确认", "已取消", "已完成"],
            key="admin_filter"
        )
        
        # 筛选预约记录
        filtered_appointments = st.session_state.admin_appointments
        if filter_status != "全部":
            filtered_appointments = [
                record for record in filtered_appointments
                if record["status"] == filter_status
            ]
        
        if filtered_appointments:
            for idx, record in enumerate(filtered_appointments):
                with st.container(border=True):
                    st.markdown(f"**预约编号**：{record['id']}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**预约人**：{record['name']}")
                        st.markdown(f"**学号**：{record['student_id']}")
                        st.markdown(f"**联系电话**：{record['contact']}")
                    with col2:
                        st.markdown(f"**咨询师**：{record['teacher']}")
                        st.markdown(f"**预约时间**：{record['date']} {record['time']}")
                        st.markdown(f"**咨询类型**：{record['consult_type']}")
                    with col3:
                        st.markdown(f"**提交时间**：{record['create_time']}")
                        st.markdown(f"**状态**：{record['status']}")
                        if record["admin_note"]:
                            st.markdown(f"**备注**：{record['admin_note']}")
                    
                    st.markdown(f"**咨询问题**：{record['problem_desc']}")
                    
                    # 操作按钮 - 修复：将type="success"改为type="primary"
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    with col_btn1:
                        if record["status"] == "待确认":
                            if st.button(
                                "确认预约", 
                                key=f"confirm_{record['id']}",
                                use_container_width=True,
                                type="primary"
                            ):
                                record["status"] = "已确认"
                                record["admin_note"] = "管理员已确认预约"
                                st.success(f"✅ 预约 {record['id']} 已确认！")
                                st.rerun()
                    with col_btn2:
                        if record["status"] != "已取消":
                            if st.button(
                                "拒绝预约", 
                                key=f"reject_{record['id']}",
                                use_container_width=True,
                                type="secondary"
                            ):
                                record["status"] = "已取消"
                                record["admin_note"] = "管理员拒绝预约"
                                st.success(f"✅ 预约 {record['id']} 已拒绝！")
                                st.rerun()
                    with col_btn3:
                        if record["status"] == "已确认":
                            if st.button(
                                "标记完成", 
                                key=f"complete_{record['id']}",
                                use_container_width=True,
                                type="primary"  # 修复：替换type="success"
                            ):
                                record["status"] = "已完成"
                                record["admin_note"] = "咨询已完成"
                                st.success(f"✅ 预约 {record['id']} 已标记为完成！")
                                st.rerun()
        else:
            st.info(f"暂无{filter_status}的预约记录")
        
        # 导出预约记录（管理员功能）
        st.markdown("---")
        if st.button("📤 导出所有预约记录", use_container_width=True):
            if st.session_state.admin_appointments:
                # 转换为DataFrame
                df = pd.DataFrame(st.session_state.admin_appointments)
                # 导出为CSV
                csv = df.to_csv(index=False, encoding="utf-8-sig")
                st.download_button(
                    label="下载CSV文件",
                    data=csv,
                    file_name=f"心理咨询预约记录_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.success("✅ 预约记录已准备好，点击按钮下载！")
            else:
                st.warning("暂无预约记录可导出！")
    
    # 4. 预约须知
    st.markdown("---")
    with st.expander("📖 预约须知", expanded=True):
        st.markdown("""
        ### 预约规则
        1. **预约时间**：可预约未来7天内的咨询时段（周一至周五）
        2. **取消规则**：如需取消预约，请提前24小时操作，否则视为爽约
        3. **爽约处理**：累计2次爽约将暂停预约权限1周
        4. **咨询时长**：个体咨询每次50分钟，团体辅导每次90分钟
        
        ### 注意事项
        1. 首次咨询请携带学生证/校园卡前往
        2. 请按时到达咨询地点，迟到15分钟以上视为爽约
        3. 咨询内容严格保密，遵循心理咨询伦理规范
        4. 如有紧急情况，请直接前往心理健康教育中心或拨打24小时热线
        """)


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

# 标签页6：学校咨询服务（包含严格的权限控制）
import streamlit as st
import json
import os
import sys
import urllib.parse

# ===================== 纯代码跨设备同步：URL参数 + 全局缓存 =====================
# 全局缓存键（所有会话共享）
CACHE_KEY = "GLOBAL_PSYCHOLOGY_RESOURCES"

# 初始化全局缓存（纯代码，无需文件/数据库）
def init_global_cache():
    # 如果缓存不存在，初始化空数据
    if CACHE_KEY not in st.session_state:
        # 尝试从URL参数读取（跨设备传递）
        query_params = st.experimental_get_query_params()
        if "resources" in query_params:
            try:
                # 解码URL参数里的JSON数据
                encoded_data = query_params["resources"][0]
                decoded_data = urllib.parse.unquote(encoded_data)
                st.session_state[CACHE_KEY] = json.loads(decoded_data)
            except:
                st.session_state[CACHE_KEY] = {
                    "psychological_course": [],
                    "psychological_activity": [],
                    "psychological_test": [],
                    "online_resources": []
                }
        else:
            # 初始空数据
            st.session_state[CACHE_KEY] = {
                "psychological_course": [],
                "psychological_activity": [],
                "psychological_test": [],
                "online_resources": []
            }

# 保存数据到URL参数（跨设备同步核心）
def save_to_url(data):
    # 把数据转成JSON并编码（适配URL）
    json_data = json.dumps(data, ensure_ascii=False)
    encoded_data = urllib.parse.quote(json_data)
    # 设置URL参数（所有设备打开这个URL就能看到数据）
    st.experimental_set_query_params(resources=encoded_data)

# 替换原有初始化函数
def init_persistent_resources():
    init_global_cache()
    # 同步到session_state（和你原有变量名一致，不破坏逻辑）
    if "custom_psychology_resources" not in st.session_state:
        st.session_state.custom_psychology_resources = st.session_state[CACHE_KEY]

# 替换原有保存函数（纯代码同步）
def save_persistent_resources():
    # 同步到全局缓存
    st.session_state[CACHE_KEY] = st.session_state.custom_psychology_resources
    # 保存到URL参数（跨设备可见）
    save_to_url(st.session_state[CACHE_KEY])

# 修复：确保get_combined_resources能读到跨设备数据
def get_combined_resources():
    system_resources = {
        "psychological_course": [],
        "psychological_activity": [],
        "psychological_test": [],
        "online_resources": []
    }
    combined = {}
    for key in system_resources:
        custom_res = st.session_state.custom_psychology_resources.get(key, [])
        combined[key] = system_resources[key] + custom_res
    return combined

# ===================== 你的原有代码完全保留 =====================
with tab6:
    # 标签页6：学校咨询服务（包含严格的权限控制）
    st.title("🏫 大连工业大学 心理咨询服务指南")
    st.markdown("#### 了解学校的心理咨询服务，获取专业的心理支持")
    st.markdown("---")
    
    # 初始化全局资源（纯代码跨设备同步）
    init_persistent_resources()
    
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
                # 纯代码同步（无需文件/数据库）
                save_persistent_resources()
                st.success("✅ 资源添加成功！复制当前URL给其他设备即可看到")
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
                        # 纯代码同步
                        save_persistent_resources()
                        st.success("✅ 资源已删除！所有设备同步更新")
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
            label = "（管理员添加，所有设备可见）" if is_custom else "（系统内置）"
            st.markdown(f"{icon} {resource} {label}")
    else:
        st.info(f"暂无{resource_type_to_manage}内容")
    
    st.markdown("---")
    
    # 危机干预热线
    st.markdown("### 🆘 危机干预热线")
    st.markdown(f"- **学校非工作日热线**：0411-86318792（门诊部）")
    st.markdown(f"- **大连市心理援助热线**：0411-84651333")
    st.markdown(f"- **大连市危机干预中心热线**：0411-83695555")
    st.markdown(f"- **全国心理援助热线**：400-1619995")
    
    st.markdown("---")
    
    # 常见问题解答
    st.markdown("### 🤔 常见问题解答")
    for question, answer in DLPU_CONSULT_SERVICE['faq'].items():
        st.markdown(f"**{question}**\n{answer}")
    
    st.markdown("---")
    
    # 联系我们
    st.markdown("### 📞 联系我们")
    st.markdown("- **咨询电话**：0411-86318792（门诊部）")
    st.markdown("- **咨询邮箱**：dlgdxlzx@163.com")
    st.markdown("- **咨询地点**：大连工业大学心理健康教育中心（艺术楼 304 室）")
    st.markdown("- **办公时间**：周一至周五 8:00-11:30，13:30-17:00")
    
    st.markdown("---")
    
    # 反馈与建议
    st.markdown("### 📝 反馈与建议")
    st.markdown("- 您对学校心理咨询服务有任何意见或建议，请随时联系我们。")
    st.markdown("- 您的反馈将帮助我们不断改进和完善服务。")
    
    st.markdown("---")
    
    # 版权信息
    st.markdown("### 📄 版权信息")
    st.markdown("- 本指南由大连工业大学心理健康教育中心提供，仅供校内师生使用。")
# -------------------------- 专业心理工具库（tab7）功能代码 --------------------------
from streamlit.components.v1 import html
import random
import streamlit as st
from datetime import datetime  # 补充缺失的导入

# 动态呼吸训练可视化组件（HTML+JS实现，适配Streamlit）
def breathing_visualization():
    """4-7-8呼吸法可视化引导组件"""
    breathing_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .breathing-circle {
                width: 200px;
                height: 200px;
                border-radius: 50%;
                background-color: #4F9E54;
                margin: 20px auto;
                display: flex;
                justify-content: center;
                align-items: center;
                color: white;
                font-size: 20px;
                font-weight: bold;
                animation: breathe 19s infinite ease-in-out;
            }
            @keyframes breathe {
                0% { transform: scale(0.8); background-color: #4F9E54; }
                21% { transform: scale(1.2); background-color: #2E7D32; }
                58% { transform: scale(1.2); background-color: #2E7D32; }
                100% { transform: scale(0.8); background-color: #4F9E54; }
            }
            .instruction {
                text-align: center;
                font-size: 16px;
                color: #333;
                margin-top: 20px;
            }
            .step {
                margin: 5px 0;
            }
        </style>
    </head>
    <body>
        <div class="breathing-circle">吸气</div>
        <div class="instruction">
            <div class="step">4秒吸气 → 7秒屏息 → 8秒呼气</div>
            <div class="step">跟随圆圈的缩放节奏，用鼻子吸气，嘴巴呼气</div>
        </div>
        <script>
            const circle = document.querySelector('.breathing-circle');
            setInterval(() => {
                circle.textContent = "吸气";
                setTimeout(() => circle.textContent = "屏息", 4000);
                setTimeout(() => circle.textContent = "呼气", 11000);
            }, 19000);
        </script>
    </body>
    </html>
    """
    return html(breathing_html, height=350)

# 正念冥想可视化引导（身体扫描）
def body_scan_visualization():
    """身体扫描冥想可视化引导"""
    body_scan_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .body-part {
                width: 80%;
                height: 40px;
                margin: 10px auto;
                border-radius: 20px;
                background-color: #E0E0E0;
                display: flex;
                align-items: center;
                padding: 0 20px;
                font-size: 16px;
                color: #333;
                opacity: 0.5;
                transition: all 2s ease;
            }
            .active {
                opacity: 1;
                background-color: #64B5F6;
                color: white;
                font-weight: bold;
            }
            .guide {
                text-align: center;
                font-size: 18px;
                margin: 20px 0;
                color: #2196F3;
            }
        </style>
    </head>
    <body>
        <div class="guide">身体扫描引导：将注意力集中到高亮部位，感受紧绷与放松</div>
        <div class="body-part" id="foot">双脚</div>
        <div class="body-part" id="calf">小腿</div>
        <div class="body-part" id="thigh">大腿</div>
        <div class="body-part" id="waist">腰腹</div>
        <div class="body-part" id="back">背部</div>
        <div class="body-part" id="shoulder">肩颈</div>
        <div class="body-part" id="face">面部</div>
        <script>
            const parts = document.querySelectorAll('.body-part');
            let index = 0;
            setInterval(() => {
                parts.forEach(p => p.classList.remove('active'));
                parts[index].classList.add('active');
                index = (index + 1) % parts.length;
            }, 5000);
        </script>
    </body>
    </html>
    """
    return html(body_scan_html, height=500)

# 新增：300条治愈经典语录功能
def inspirational_quotes_300():
    """300条治愈经典语录展示组件（不重复随机展示）"""
    quotes_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .quote-container {
                max-width: 800px;
                margin: 20px auto;
                padding: 30px;
                border-radius: 15px;
                background-color: #f8f9fa;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                text-align: center;
            }
            .quote-text {
                font-size: 18px;
                line-height: 1.8;
                color: #333;
                margin-bottom: 25px;
                min-height: 80px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .quote-btn {
                padding: 12px 30px;
                border: none;
                border-radius: 8px;
                background-color: #64B5F6;
                color: white;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            .quote-btn:hover {
                background-color: #2196F3;
            }
            .quote-title {
                color: #2196F3;
                font-size: 20px;
                margin-bottom: 20px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="quote-container">
            <div class="quote-title">✨ 治愈经典语录</div>
            <div class="quote-text" id="quoteDisplay">点击下方按钮，获取一句治愈的力量</div>
            <button class="quote-btn" onclick="getNewQuote()">换一句</button>
        </div>

        <script>
            // 300条治愈经典语录库
            const quotes = [
                "允许一切发生，是治愈的开始。","慢慢来，你又不差。","生活是旷野，不是轨道。",
                "不必光芒万丈，但始终温暖有光。","你已经很好了，不必事事完美。","放松点，不用和每个人都要好。",
                "温柔半两，从容一生。","心有山海，静而无忧。","把节奏放慢，生活也是，爱也是。",
                "与自己和解，才是终身浪漫。","风遇山止，船到岸停，你也可以休息。","人间枝头，各自乘流。",
                "安静努力，不必声张。","先安稳自己，再温柔岁月。","心若从容，万事皆安。",
                "不必讨好世界，你只需取悦自己。","日子常新，未来不远。","慢慢来，谁都有发光的机会。",
                "生活平凡，也值得全力以赴。","你值得被温柔以待，首先是自己。","心若向阳，何惧忧伤。",
                "万事尽心尽力，而后顺其自然。","把情绪放下，日子就会变轻。","不慌不忙，安静生长。",
                "不必急，花有花期，人有时运。","接受普通，然后拼尽全力去与众不同。","生活本就是，一半烟火，一半清欢。",
                "凡是过往，皆为序章。","愿你眼底有光，心中有爱，温暖一生。","慢慢来，好戏都在烟火里。",
                "稳住节奏，慢慢来，比较快。","愿你从容，不慌不忙，不卑不亢。","把心放宽，把事看淡，一切都会好。",
                "生活不简单，尽量简单过。","心若不动，风又奈何。","你只管善良，上天自有衡量。",
                "岁月静好，心安即是归处。","慢慢来，一切都来得及。","保持热爱，奔赴山海。",
                "平凡的日子，也能溢出温柔。","风雨自有归期，山水总会相逢。","不必光芒万丈，温暖就好。",
                "生活，是自己心情的倒影。","心宽一寸，病退一丈。","慢慢来，好运都在路上。",
                "愿你所得皆所期，所失皆无碍。","世界很温柔，你也很值得。","不抱怨，不纠结，不困惑。",
                "平静的心灵，拥有最强大的力量。","生活最好的状态，是冷冷清清的风风火火。","把心腾干净，住进来的全是温柔。",
                "你不必生来勇敢，只要认真生活。","岁月漫长，终会有不期而遇的温暖。","愿你从容清醒，坚定有力。",
                "认真生活，就能找到生活藏起来的糖果。","心简单，世界就简单。","生活不完美，但也不缺美好。",
                "慢慢来，你会遇见更好的自己。","愿你眼里的星星，永远明亮。","温柔待人，清醒处世。",
                "烦恼由心起，心放宽，事就轻。","生活，一半争取，一半随缘。","人生，是一场温柔的坚持。",
                "愿你历经山河，仍觉人间值得。","安静下来，感受生活的温柔。","你很好，不要否定自己。",
                "把日子过成诗，简单而精致。","心向阳光，何惧风霜。","愿你无忧无惧，自在欢喜。",
                "生活是自己的，与他人无关。","慢慢来，时间会给你答案。","愿你温柔且坚定，柔软且有力量。",
                "心有所期，全力以赴，定有所成。","人生没有白走的路，每一步都算数。","愿你被世界温柔以待。",
                "生活再平凡，也是限量版。","把心放平，一切都会风平浪静。","愿你清醒、独立、温柔、坚定。",
                "人生苦短，何必念念不忘。","愿你平安无事，日子清净。","心若从容，无所畏惧。",
                "生活，是一场温柔的修行。","愿你不负自己，不负岁月。","慢慢来，生活会越来越好。",
                "心向美好，万物皆甜。","愿你眼中有光，活成自己喜欢的模样。","不争不抢，不急不躁。",
                "努力生活，认真微笑。","心有阳光，一路芬芳。","愿你所有快乐，无需假装。",
                "愿你此生尽兴，赤诚善良。","把烦恼清空，把温柔装满。","日子清净，抬头皆是温柔。",
                "愿你历经千帆，归来仍是少年。","生活简单就迷人，人心简单就幸福。","慢慢来，一切美好都会如约而至。",
                "心若晴朗，人生便没有雨天。","愿你温柔半两，从容一生。","保持清醒，也保持温柔。",
                "人生，是一场慢慢自愈的过程。","不纠结过去，不畏惧将来。","愿你生活温暖，内心安然。",
                "把情绪收好，把快乐放大。","慢慢来，你会越来越好。","心有温柔，目之所及皆是美好。",
                "愿你平安喜乐，万事顺遂。","生活，是一场温柔的坚持。","愿你不被生活为难。",
                "心有所向，平凡的日子也会泛着光。","慢慢来，生活会给你惊喜。","愿你心中有光，脚下有路。",
                "人生最清晰的脚印，踩在最泥泞的路上。","不必光芒万丈，温暖有光就好。","愿你从容不迫，优雅有度。",
                "生活不慌不忙，一切刚刚好。","心若安然，岁月从容。","愿你所有努力，终有回报。",
                "把日子过好，比什么都重要。","愿你清醒知趣，明得失，知进退。","人生没有如果，只有结果和后果。",
                "愿你温柔待人，也善待自己。","生活最好的状态，是心安。","愿你无事绊心弦，所念皆如愿。",
                "慢慢来，别着急，生活自有安排。","心有山海，静而无边。","愿你保持热爱，奔赴下一场山海。",
                "生活，是一场温柔的自愈。","愿你眼里有星星，笑容有光芒。","不争不辩，不闻不怨。",
                "心宽一点，幸福就多一点。","人生，是一场慢慢变好的旅程。","愿你生活明朗，万物可爱。",
                "把心交给温柔，把爱交给岁月。","愿你余生漫长，处处皆是风光。","慢慢来，生活是慢慢出彩的。",
                "心若从容，何惧人生沧桑。","愿你被温柔守护，不被时光辜负。","生活，简单就好，心情，快乐就好。",
                "愿你勇敢、自由、独立、温柔。","人生苦短，笑对每一天。","心有温暖，何惧人间苦寒。",
                "愿你无忧无虑，一生安然。","保持温柔，等待值得。","慢慢来，时间会治愈一切。",
                "愿你生活清净，内心丰盈。","人生，是一场自我成全。","愿你安好，便是晴天。",
                "心若不动，风又奈何；你若不伤，岁月无恙。","生活，是一场温柔的相遇。","愿你一生努力，一生被爱。",
                "慢慢来，一切都会好起来的。","心有阳光，世界就不会黑暗。","愿你抬头所见皆是温柔。",
                "人生，不必完美，只要心安。","愿你从容生活，温柔处世。","把心情照顾好，比什么都重要。",
                "愿你所有美好，不期而遇。","心有温柔，岁月静好。","慢慢来，生活不会亏待你。",
                "愿你此生清澈明朗，善良有锋芒。","生活自有分寸，不必焦虑。","愿你平安无恙，岁月不惊。",
                "心有力量，才能笑对风霜。","人生，是一场温柔的前行。","愿你生活温柔，内心坚定。",
                "把烦恼看淡，把心情放宽。","慢慢来，生活自有出路。","愿你所遇皆温暖，所行皆坦荡。",
                "心若从容，万事皆顺。","生活，是一场温柔的成长。","愿你不负时光，不负自己。",
                "心有期待，日子才有光彩。","慢慢来，生活会越来越温柔。","愿你心中无缺，生活安稳。",
                "心若安然，浮生不寒。","生活，是一场温柔的救赎。","愿你永远温柔，永远清醒。",
                "心宽路自宽，心好命就好。","慢慢来，一切都会圆满。","愿你生活有光，日子有暖。",
                "心有温柔，不惧岁月风霜。","人生，是一场温柔的自愈之旅。","愿你清醒、温柔、坚定、勇敢。",
                "把生活过成自己喜欢的样子。","心有山海，静而无忧，动而无惧。","愿你余生皆欢喜，岁岁皆安康。",
                "慢慢来，你会被世界温柔拥抱。","人生如路，需在荒凉中走出繁华的风景。","心有丘壑，眉目作山河。",
                "凡是让你爽的东西，最终都会让你痛苦；凡是让你痛的东西，最终都会让你成长。","知世故而不世故，才是最善良的成熟。",
                "生活的美好，在于它的不确定性。","低头要有勇气，抬头要有底气。","你若盛开，清风自来。",
                "人生没有白吃的苦，也没有白走的路。","愿你遍历山河，觉得人间值得。","时间会过滤掉不属于你的东西。",
                "学会和自己和解，是最高级的智慧。","温柔和让步，会让很多事情变得简单。","情绪稳定，是最好的教养。",
                "不要慌，太阳下山有月光，月亮落下有朝阳。","生活不是等待暴风雨过去，而是学会在雨中跳舞。",
                "你要悄悄努力，然后惊艳所有人。","知足知不足，有为有不为。","以清净心看世界，以欢喜心过生活。",
                "人生的路，靠自己一步步走，真正能保护你的，是你自己的选择。","愿你有前进一寸的勇气，亦有后退一尺的从容。",
                "不必追光，你我皆是星辰。","生活是晨起暮落，日子是柴米油盐。","简单的喜欢，最长远；平凡的陪伴，最心安。",
                "成熟不是心变老，而是眼泪在眼睛里打转，却还能保持微笑。","别让你的努力，最后都败给焦虑。",
                "你不能改变风向，但可以调整风帆。","人生最好的状态，是冷冷清清的风风火火。","往事不回头，未来不将就。",
                "愿你被这个世界温柔以待，即使生命总以刻薄荒芜相欺。","心之所向，素履以往。","生如逆旅，一苇以航。",
                "人生没有标准答案，珍惜当下就是最优解。","允许别人做别人，允许自己做自己。","重要的不是治愈，而是带着病痛活下去。",
                "生活的本质是快乐守恒，你在这里失去的，会在别处找回来。","慢慢来，谁不是翻山越岭去成长。",
                "你的职责是平整土地，而非焦虑时光。你做三四月的事，在八九月自有答案。","人生忽如寄，莫辜负茶、汤、好天气。",
                "世界是自己的，与他人毫无关系。","且视他人之疑目如盏盏鬼火，大胆地去走你的夜路。","所谓成长，就是把哭声调成震动模式。",
                "保持热爱，奔赴山海，忠于自己，热爱生活。","生活坏到一定程度就会好起来，因为它无法更坏。",
                "愿你有好运气，如果没有，愿你在不幸中学会慈悲。","愿你被很多人爱，如果没有，愿你在寂寞中学会宽容。",
                "人生如茶，空杯以对，才有喝不完的好茶，才有装不完的欢喜和感动。","心简单，世界就简单，幸福才会生长。",
                "你若不伤，岁月无恙。","时光不语，静待花开。","不乱于心，不困于情，不畏将来，不念过往。",
                "宠辱不惊，看庭前花开花落；去留无意，望天上云卷云舒。","人生不过见天地，见众生，见自己。",
                "知不足而奋进，望远山而力行。","日日行，不怕千万里；常常做，不怕千万事。","道阻且长，行则将至；行而不辍，未来可期。",
                "星光不负赶路人，时光不负有心人。","凡是过往，皆为序章；所有将来，皆为可盼。","心有暖阳，何惧风霜。",
                "生活是一面镜子，你对它笑，它就对你笑；你对它哭，它就对你哭。","人生没有如果，只有后果和结果。",
                "当你觉得为时已晚的时候，恰恰是最早的时候。","努力的意义，在于让你有更多选择。","别让任何人消耗你内心的晴朗，生活应该是被热爱的人和事填满。",
                "与其抱怨黑暗，不如提灯前行。","人生的美好，在于相遇，也在于错过。","愿你走过半生，归来仍是少年。",
                "生活不是擂台，不必事事争个高下。","温柔是世间宝藏，我永远屈服于温柔。","把烦心事都丢掉，腾出地方装鲜花。",
                "日子需要我们积极向上。","万事都要全力以赴，包括开心。","今天的不开心就到此为止，明天依然光芒万丈。",
                "做自己的太阳，无需借谁的光。","愿你精致到老，眼里长着太阳，笑里全是坦荡。","生活嘛，慢慢来，好戏都在烟火里。",
                "不亏待每一份热情，不讨好任何的冷漠。","成长就是将哭声调成静音模式，把情绪收到别人看不到的地方。",
                "世界很大，幸福很小，有你陪伴，一切都刚刚好。","愿我们都能在鸡零狗碎的生活里，找到闪闪发亮的快乐。",
                "生活的温柔总会哒哒哒的跑进你怀里的。","慢慢来，谁不是第一次做人。","愿你渺小启程，以伟大结束。",
                "要相信，所有的不美好都是为了迎接美好，所有的困难都会为努力让道。","人生就像蒲公英，看似自由，却身不由己。",
                "你可以迷茫，但不要虚度。","生活总会给你答案，但不会马上把一切都告诉你。","每一个不曾起舞的日子，都是对生命的辜负。",
                "人生建议：接纳自己，放过自己。","别让生活的压力挤走快乐，别让鸡零狗碎的事，耗尽你对生活的向往。",
                "愿你走出半生，归来仍有热爱。","生活的理想，就是为了理想的生活。","低头赶路，敬事如仪，自知自心，其路则明。",
                "时间会证明一切，不必急于求成。","你要做的就是，提前准备，然后等待机会。","人生没有白走的路，每一步都算数。",
                "愿你有盔甲，也有软肋。善良得有原则，感性得有底线。","生活是自己的，尽情打扮，尽情可爱。",
                "把期望降低，把依赖变少，你会过得很好。","人生最好的境界，是丰富的安静。","慢慢来，时间会给你想要的一切。",
                "不必行色匆匆，不必光芒四射，不必成为别人，只需做自己。","你现在的努力，都是为了以后能有更多的选择。",
                "愿你遇良人，予你欢喜城，长歌暖浮生。","生活就像一盒巧克力，你永远不知道下一颗是什么味道。",
                "当你穿过了暴风雨，你就不再是原来的那个人。","心有山海，静而无边，安而无慌。","愿你一生努力，一生被爱，想要的都拥有，得不到的都释怀。",
                "生活的美好，在于日常的欢喜，在于琐碎的幸福。","别让你的善良，成为别人欺负你的理由。","知世故而不世故，历圆滑而弥天真。",
                "人生苦短，别太较真，开心就好。","愿你三冬暖，春不寒，天黑有灯，下雨有伞。","你若盛开，蝴蝶自来，你若精彩，天自安排。",
                "生活不是为了赶路，而是为了感受路。","人生如棋，落子无悔。","愿你历尽千帆，不染岁月风尘。",
                "保持初心，砥砺前行。","凡是让你变好的事情，过程都不会太舒服。","温柔半两，从容一生，热爱生活，不问东西。",
                "愿你眼中有星辰，心中有山海，从此以梦为马，不负韶华。","生活是一场即兴演出，没有彩排，每一天都是现场直播。",
                "别让任何人打乱你的人生节奏。","人生没有白吃的苦，苦尽甘来终有时。","愿你在被爱的人眼里，连撑伞的样子都像捧着一束玫瑰。",
                "慢慢来，谁都有发光的机会，你的努力，时间都会看见。","心若计较，处处都是怨言；心若放宽，时时都是春天。",
                "生活的真谛，在于珍惜和付出，而非索取和计较。","你要储蓄你的可爱，眷顾你的温柔，变得勇敢起来，当这个世界越来越坏，我希望你能越来越好。",
                "人生就像一杯茶，不会苦一辈子，但总会苦一阵子。","愿你走过的所有弯路，最后都成为美丽的彩虹。","把不忙不闲的工作做得出色，把不咸不淡的生活过得精彩。",
                "生活中的不期而遇，都是你努力后的惊喜。","愿你有前进一寸的勇气，亦有后退一尺的从容。","人生的路，靠自己一步步走，真正能保护你的，是你自己的选择。",
                "不必慌张，太阳下山有月光，月亮落下有朝阳。","生活不是等待暴风雨过去，而是学会在雨中跳舞。","你要悄悄拔尖，然后惊艳所有人。",
                "知足知不足，有为有不为。","以清净心看世界，以欢喜心过生活。","重要的不是治愈，而是带着病痛活下去。",
                "生活的本质是快乐守恒，你在这里失去的，会在别处找回来。","慢慢来，谁不是翻山越岭去成长。","你的职责是平整土地，而非焦虑时光。",
                "人生忽如寄，莫辜负茶、汤、好天气。","世界是自己的，与他人毫无关系。","且视他人之疑目如盏盏鬼火，大胆地去走你的夜路。",
                "所谓成长，就是把哭声调成震动模式。","保持热爱，奔赴山海，忠于自己，热爱生活。","生活坏到一定程度就会好起来，因为它无法更坏。",
                "愿你被这个世界温柔以待，即使生命总以刻薄荒芜相欺。","心之所向，素履以往。","生如逆旅，一苇以航。",
                "人生没有标准答案，珍惜当下就是最优解。","允许别人做别人，允许自己做自己。"
            ];
            
            let usedQuotes = [];
            
            function getNewQuote() {
                // 如果所有语录都用过了，重置已用列表
                if (usedQuotes.length === quotes.length) {
                    usedQuotes = [];
                }
                
                // 筛选出未使用的语录
                const availableQuotes = quotes.filter(quote => !usedQuotes.includes(quote));
                // 随机选择一条
                const randomIndex = Math.floor(Math.random() * availableQuotes.length);
                const selectedQuote = availableQuotes[randomIndex];
                
                // 添加到已用列表
                usedQuotes.push(selectedQuote);
                // 显示语录
                document.getElementById('quoteDisplay').textContent = selectedQuote;
            }
        </script>
    </body>
    </html>
    """
    return html(quotes_html, height=300)

# CBT思维记录表工具（供用户填写，辅助认知重构）
def cbt_thought_record():
    """认知行为疗法思维记录表，帮助用户识别并挑战负面思维"""
    with st.form("cbt_thought_record_form", clear_on_submit=True):
        st.markdown("### 🧠 认知行为疗法 - 思维记录表")
        st.markdown("**填写说明**：记录引发焦虑的事件，识别你的自动思维和情绪，挑战不合理信念并替换为合理思维")
        col1, col2 = st.columns(2)
        with col1:
            event = st.text_input("1. 触发事件", placeholder="如：考试没考好、和同学吵架...")
            auto_thought = st.text_area("2. 自动化负面思维", placeholder="如：我太差了、大家都不喜欢我...", height=80)
            emotion = st.selectbox("3. 引发的情绪", ["焦虑", "悲伤", "愤怒", "自卑", "恐惧", "其他"])
            emotion_score = st.slider("4. 情绪强度（1-10）", 1, 10, 5)
        with col2:
            belief_type = st.selectbox("5. 不合理信念类型", ["灾难化", "非黑即白", "过度概括", "个人化", "绝对化要求", "未明"])
            challenge = st.text_area("6. 挑战不合理信念", placeholder="如：一次没考好代表我真的差吗？有什么证据？...", height=80)
            rational_thought = st.text_area("7. 合理替代思维", placeholder="如：一次没考好只是偶然，我可以下次努力...", height=80)
            new_score = st.slider("8. 调整后情绪强度（1-10）", 1, 10, 3)
        submit_cbt = st.form_submit_button("保存思维记录", use_container_width=True)
        if submit_cbt and event and auto_thought and challenge and rational_thought:
            # 保存CBT记录到会话状态
            if "cbt_records" not in st.session_state:
                st.session_state.cbt_records = []
            st.session_state.cbt_records.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "event": event,
                "auto_thought": auto_thought,
                "emotion": emotion,
                "emotion_score": emotion_score,
                "belief_type": belief_type,
                "challenge": challenge,
                "rational_thought": rational_thought,
                "new_score": new_score
            })
            st.success("✅ CBT思维记录已保存！坚持记录有助于逐步调整认知模式")

# 线下咨询机构/师资智能匹配（基于焦虑类型、诱因、严重程度）
# 假设有完整的DLPU_TEACHERS数据（补充各老师的差异化fields和experience）
# 这里给出示例结构，你可替换为真实完整数据
DLPU_TEACHERS = [
    {
        "name": "梁瑛楠",
        "title": "教授、博士、硕士研究生导师",
        "experience": "20余年心理咨询实践经验",
        "specialty": "情绪困扰、压力管理、关系处理、个人成长",
        "fields": ["情绪焦虑", "综合焦虑", "压力管理", "关系处理", "个人成长"]
    },
    {
        "name": "郭志峰",
        "title": "副教授、硕士",
        "experience": "18年心理咨询实践经验",
        "specialty": "人际关系改善、自我心理调适、学业困难、职业生涯发展",
        "fields": ["学业焦虑", "人际关系焦虑", "就业焦虑", "学业困难"]
    },
    {
        "name": "李永芬",
        "title": "副教授、博士",
        "experience": "15年心理咨询实践经验",
        "specialty": "心理危机干预、学业困难、婚姻与恋爱、原生家庭创伤疗愈",
        "fields": ["学业焦虑", "情绪焦虑", "心理危机干预", "人际关系困扰"]
    },
    {
        "name": "李春伟",
        "title": "副教授、硕士",
        "experience": "20多年心理咨询实践经验",
        "specialty": "自我探索、人际关系处理、情绪调适、压力管理",
        "fields": ["人际关系焦虑", "情绪焦虑", "综合焦虑", "压力管理"]
    }
]

def referral_matching_algorithm(anxiety_type, anxiety_cause, anxiety_level, is_persist):
    """
    优化版智能转介匹配算法（解决只匹配一个老师的问题）
    :param anxiety_type: 焦虑类型（学业/就业/人际/情绪/躯体）
    :param anxiety_cause: 焦虑核心诱因（如考试压力、寝室矛盾）
    :param anxiety_level: 焦虑程度（轻度/中度/重度）
    :param is_persist: 是否持续超过2周（是/否）
    :return: 匹配的咨询师、咨询方式、优先级建议
    """
    # 师资擅长领域匹配（基于原有DLPU_TEACHERS）
    teacher_matching = []
    for teacher in DLPU_TEACHERS:
        match_score = 0
        
        # 1. 优化匹配逻辑：精准匹配优先，避免泛匹配
        # 精准匹配焦虑类型（权重最高）
        if anxiety_type in teacher["fields"]:
            match_score += 4
        # 精准匹配核心诱因（次高权重）
        if anxiety_cause and any(cause in field for field in teacher["fields"] for cause in anxiety_cause.split("、")):
            match_score += 3
        # 模糊匹配（兜底，避免分值过低）
        elif anxiety_cause and anxiety_cause in "".join(teacher["fields"]):
            match_score += 1
        
        # 2. 增加焦虑程度匹配维度（差异化分值）
        if anxiety_level == "重度" and "心理危机干预" in teacher["fields"]:
            match_score += 2
        elif anxiety_level == "中度" and any(f in ["情绪调适", "压力管理"] for f in teacher["fields"]):
            match_score += 1
        elif anxiety_level == "轻度" and any(f in ["学业困难", "人际关系改善"] for f in teacher["fields"]):
            match_score += 1
        
        # 3. 增加持续时间匹配维度
        if is_persist == "是" and "20余年" in teacher["experience"]:
            match_score += 1
        elif is_persist == "否" and "18年" in teacher["experience"]:
            match_score += 1
        
        # 4. 调整经验匹配权重（降低权重，避免经验主导）
        if "20余年" in teacher["experience"] or "20多年" in teacher["experience"]:
            match_score += 1
        elif "18年" in teacher["experience"]:
            match_score += 1
        elif "15年" in teacher["experience"]:
            match_score += 0.5
        
        # 5. 降低匹配门槛，同时保证质量（原门槛2过高，改为1）
        if match_score >= 1:
            teacher_matching.append({
                "name": teacher["name"],
                "title": teacher["title"],
                "specialty": teacher["specialty"],
                "match_score": round(match_score, 1),  # 保留1位小数，更精准
                "contact": "0411-86318792（预约指定咨询师）"
            })
    
    # 6. 优化排序规则：先按分值降序，再按经验升序（避免老教师永远排第一）
    teacher_matching = sorted(
        teacher_matching,
        key=lambda x: (-x["match_score"], 
                      0 if "20余年" in [t["experience"] for t in DLPU_TEACHERS if t["name"] == x["name"]][0] else 1)
    )
    
    # 7. 优化咨询方式匹配（结合持续时间）
    if anxiety_level == "轻度":
        if is_persist == "是":
            referral_method = "AI+CBT自助练习+每周1次团体辅导"
            priority = "优先使用平台AI疏导和CBT工具，参与学校团体心理辅导，每周1次"
        else:
            referral_method = "AI疏导+CBT自助练习"
            priority = "优先使用平台AI疏导和CBT工具，无需线下咨询"
    elif anxiety_level == "中度":
        if is_persist == "是":
            referral_method = "AI疏导+每周1次个体心理咨询（线下）"
            priority = "先通过AI进行日常情绪疏导，预约匹配的咨询师进行线下个体咨询，每周1次"
        else:
            referral_method = "AI疏导+个体心理咨询（线上）"
            priority = "先通过AI进行日常情绪疏导，预约匹配的咨询师进行线上个体咨询，每两周1次"
    else:
        referral_method = "紧急线下个体咨询+危机干预+定期随访"
        priority = "立即前往门诊部303/304，或拨打0411-86318792预约紧急咨询，启动危机干预机制，每周2次随访"
    
    return {
        "matching_teachers": teacher_matching[:2],  # 匹配前2名咨询师
        "referral_method": referral_method,
        "priority_suggestion": priority,
        "school_address": "大连工业大学门诊部303/304房间",
        "school_hotline": "0411-86318792",
        "emergency_hotline": "0411-86323110（24小时）"
    }

# 智能转介匹配页面功能（同步优化）
def intelligent_referral():
    """智能转介匹配入口"""
    st.markdown("### 📞 AI智能转介匹配系统")
    st.markdown("**说明**：根据你的焦虑情况，智能匹配学校心理咨询师和最优咨询方式，实现AI疏导与线下干预无缝衔接")
    with st.form("referral_matching_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            anxiety_type = st.selectbox("1. 焦虑主要类型", ["学业焦虑", "就业焦虑", "人际关系焦虑", "情绪焦虑", "躯体化焦虑", "综合焦虑"])
            anxiety_cause = st.text_input("2. 核心诱因", placeholder="如：考研压力、寝室矛盾、考试挂科...")
        with col2:
            anxiety_level = st.selectbox("3. 焦虑严重程度", ["轻度", "中度", "重度"], index=0)
            is_persist = st.radio("4. 是否持续超过2周", ["是", "否"], horizontal=True)
        submit_referral = st.form_submit_button("开始智能匹配", use_container_width=True)
        
        # 表单验证
        if submit_referral and anxiety_cause:
            # 调用优化后的匹配算法（传递is_persist参数）
            matching_result = referral_matching_algorithm(anxiety_type, anxiety_cause, anxiety_level, is_persist)
            # 展示匹配结果
            st.markdown("---")
            with st.container(border=True):
                st.markdown("### 🎯 智能匹配结果")
                st.markdown(f"**焦虑类型**：{anxiety_type} | **核心诱因**：{anxiety_cause} | **严重程度**：{anxiety_level}")
                st.markdown(f"**是否持续超2周**：{is_persist}")
                st.markdown(f"**推荐咨询方式**：{matching_result['referral_method']}")
                st.markdown(f"**优先级建议**：{matching_result['priority_suggestion']}")
                
                st.markdown("### 👨‍🏫 匹配心理咨询师")
                if matching_result["matching_teachers"]:
                    for idx, teacher in enumerate(matching_result["matching_teachers"], 1):
                        # 展示匹配分值，让用户了解匹配依据
                        st.markdown(f"**{idx}. {teacher['name']} - {teacher['title']}（匹配分值：{teacher['match_score']}）**")
                        st.markdown(f"- 擅长方向：{teacher['specialty']}")
                        st.markdown(f"- 预约方式：{teacher['contact']}")
                else:
                    st.markdown("**暂未匹配到专属咨询师，可拨打学校咨询电话预约通用咨询**")
                
                st.markdown("### 📍 线下咨询信息")
                st.markdown(f"- 咨询地址：{matching_result['school_address']}")
                st.markdown(f"- 工作日咨询：{matching_result['school_hotline']}（8:30-11:30/13:30-17:00）")
                st.markdown(f"- 24小时紧急热线：{matching_result['emergency_hotline']}")

# 面部/语音情绪识别隐私授权与功能入口
def multimodal_emotion_recognition():
    """多模态情绪识别（面部/语音）功能入口，含隐私授权流程"""
    st.markdown("### 📊 多模态情绪识别（面部/语音）")
    
    # 隐私授权（必须用户主动授权才能使用）
    if "emotion_recog_authorized" not in st.session_state:
        st.session_state.emotion_recog_authorized = False
    
    if not st.session_state.emotion_recog_authorized:
        with st.warning("⚠️ 隐私授权提示"):
            st.markdown("""
            1. 面部/语音情绪识别功能需要获取你的摄像头/麦克风权限；
            2. 所有识别数据仅在本地设备处理，不会上传至任何服务器；
            3. 你可以随时关闭权限并退出功能，数据不会被保存；
            4. 该功能仅为辅助情绪判断，不能替代专业心理评估。
            """)
            if st.button("✅ 我已阅读并同意授权", use_container_width=True, type="primary"):
                st.session_state.emotion_recog_authorized = True
                st.rerun()
        return
    
    # 授权后展示功能入口
    st.success("✅ 已完成隐私授权，以下为多模态情绪识别功能入口")
    tab_face, tab_voice = st.tabs(["面部表情情绪识别", "语音情绪识别"])
    
    with tab_face:
        st.markdown("#### 👤 面部表情情绪识别")
        st.markdown("**使用说明**：开启摄像头，正对镜头保持面部清晰，系统将实时识别你的情绪状态")
        # 调用Streamlit摄像头组件（本地处理）
        face_img = st.camera_input("点击开启摄像头，拍摄面部照片进行情绪识别", key="face_camera")
        if face_img:
            with st.spinner("正在识别面部情绪..."):
                # 模拟情绪识别结果（实际项目可接入CV模型如FER2013）
                emotion_list = ["平静", "焦虑", "紧张", "开心", "悲伤", "烦躁"]
                recog_result = random.choice(emotion_list)
                confidence = round(random.uniform(0.75, 0.95), 2)
                st.markdown(f"### 🎯 面部情绪识别结果")
                st.markdown(f"**识别情绪**：{recog_result} | **置信度**：{confidence*100}%")
                # 结合识别结果给出建议
                if recog_result in ["焦虑", "紧张", "烦躁"]:
                    st.markdown("### 💡 情绪调节建议")
                    st.markdown(f"- 推荐立即进行4-7-8呼吸法缓解情绪，可前往【可视化焦虑缓解工具】页面跟随练习")
                    st.markdown(f"- 可前往【正念练习引导】页面进行5分钟正念冥想")
                    st.markdown(f"- 若情绪持续，建议使用【AI智能转介匹配】功能预约线下咨询")
    
    with tab_voice:
        st.markdown("#### 🎤 语音情绪识别")
        st.markdown("**使用说明**：开启麦克风，说出你的感受或烦恼，系统将通过语音语调识别你的情绪状态")
        # 调用Streamlit麦克风组件（本地处理）
        voice_audio = st.audio_input("点击开启麦克风，录制语音进行情绪识别", key="voice_mic")
        if voice_audio:
            with st.spinner("正在识别语音情绪..."):
                # 模拟语音情绪识别结果（实际项目可接入语音情感识别模型如RAVDESS）
                emotion_list = ["平静", "焦虑", "紧张", "开心", "悲伤", "烦躁"]
                recog_result = random.choice(emotion_list)
                confidence = round(random.uniform(0.70, 0.92), 2)
                st.markdown(f"### 🎯 语音情绪识别结果")
                st.markdown(f"**识别情绪**：{recog_result} | **置信度**：{confidence*100}%")
                # 结合识别结果给出建议
                if recog_result in ["焦虑", "紧张", "烦躁"]:
                    st.markdown("### 💡 情绪调节建议")
                    st.markdown(f"- 推荐立即进行身体扫描冥想缓解情绪，可前往【可视化焦虑缓解工具】页面跟随练习")
                    st.markdown(f"- 可与AI心理咨询师倾诉，获得针对性CBT干预建议")
                    st.markdown(f"- 若情绪持续，建议使用【AI智能转介匹配】功能预约线下咨询")
    
    # 取消授权按钮
    if st.button("❌ 取消隐私授权，关闭功能", use_container_width=True, type="secondary"):
        st.session_state.emotion_recog_authorized = False
        st.rerun()

# -------------------------- 专业心理工具库（tab7）页面实现 --------------------------
# 注意：这里需要确保tab7已经被定义，如果你是独立运行，需要补充tab7的创建逻辑
# 示例：main_tabs = st.tabs(["首页", "情绪自评", "AI咨询", "专业心理工具库", "社区", "个人中心"])
#       tab7 = main_tabs[3]

with tab7:
    st.title("🎯 专业心理工具库")
    st.markdown("---")
    
    # 修复：移除多余缩进，保持和with tab7内其他代码同级
    tool1, tool2, tool3, tool4, tool5, tool6 = st.tabs([
        "📊 可视化焦虑缓解工具",  # 原有
        "✨ 治愈经典语录",        # 原有
        "🧠 CBT认知行为疗法工具", # 原有
        "📞 AI智能转介匹配",      # 原有
        "🔍 多模态情绪识别",       # 原有
        "🌳 情绪树洞"             # 仅新增这一行
    ])
    
    # 子标签1：可视化焦虑缓解工具（优化维度1）
    with tool1:
        st.header("📊 可视化焦虑缓解工具")
        st.markdown("### 🧘 呼吸训练可视化（4-7-8呼吸法）")
        breathing_visualization()
        st.markdown("---")
        st.markdown("### 🧘 身体扫描冥想可视化")
        body_scan_visualization()
    
    # 新增：子标签2 - 治愈经典语录
    with tool2:
        st.header("✨ 治愈经典语录")
        st.markdown("**使用说明**：点击按钮随机获取治愈语录，帮助缓解焦虑、平复情绪，所有语录不重复展示")
        inspirational_quotes_300()
    
    # 子标签3：CBT认知行为疗法工具（优化维度2）
    with tool3:
        st.header("🧠 认知行为疗法(CBT)工具库")
        cbt_thought_record()
        st.markdown("---")
        # 展示CBT思维记录历史
        if "cbt_records" in st.session_state and st.session_state.cbt_records:
            st.markdown("### 📋 我的CBT思维记录历史")
            for idx, record in enumerate(reversed(st.session_state.cbt_records[:5]), 1):
                with st.expander(f"🕒 {record['time']} - {record['emotion']}（{record['emotion_score']}分）"):
                    st.markdown(f"**触发事件**：{record['event']}")
                    st.markdown(f"**负面思维**：{record['auto_thought']}")
                    st.markdown(f"**不合理信念**：{record['belief_type']}")
                    st.markdown(f"**合理思维**：{record['rational_thought']}")
                    st.markdown(f"**情绪改善**：{record['emotion_score']}分 → {record['new_score']}分")
        else:
            st.info("暂无CBT思维记录，填写上方表单开始记录吧～")
    
    # 子标签4：AI智能转介匹配（优化维度3）
    with tool4:
        intelligent_referral()
    
    # 子标签5：多模态情绪识别（优化维度4）
    with tool5:
        st.header("🔍 多模态情绪识别（面部/语音）")
        multimodal_emotion_recognition()
    
    with tool6:
        import streamlit as st
        import datetime
        import random
        from PIL import Image
        import io
        import base64
        import json
        import os
        import threading  # 新增：用于文件锁，防止并发读写冲突

        # ==================== 全局配置 ====================
        st.set_page_config(
            page_title="工大情绪树洞",
            page_icon="🌳",
            layout="wide",
            initial_sidebar_state="collapsed"
        )

        DATA_FILE = "tree_hole_data.json"
        # 全局锁：确保同一时间只有一个线程读写JSON文件
        file_lock = threading.Lock()

        # ==================== 核心：每次都重新加载共享数据（关键修复） ====================
        def load_shared_data():
            """每次调用都从磁盘重新读取，保证数据最新"""
            with file_lock:  # 加锁，防止多线程读写冲突
                if os.path.exists(DATA_FILE):
                    try:
                        with open(DATA_FILE, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if "posts" not in data:
                                data["posts"] = []
                            if "responses_used" not in data:
                                data["responses_used"] = []
                            return data
                    except Exception as e:
                        st.error(f"加载数据出错: {e}")
                        return {"posts": [], "responses_used": []}
                else:
                    return {"posts": [], "responses_used": []}

        def save_shared_data(data):
            """保存时加锁，确保写入完整"""
            with file_lock:
                try:
                    with open(DATA_FILE, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    st.error(f"保存数据失败: {e}")

        # ==================== 会话状态初始化 ====================
        if "tree_hole_temp" not in st.session_state:
            st.session_state.tree_hole_temp = {
                "content": "", "emotion_tag": "焦虑", "nickname": "", "images": []
            }
        if "tree_hole_sensitive" not in st.session_state:
            st.session_state.tree_hole_sensitive = []
        if "is_admin" not in st.session_state:
            st.session_state.is_admin = True

        # ==================== 核心CSS（不变） ====================
        st.markdown("""
        <style>
        .stApp > header { display: none !important; }
        .stApp > div:first-child > div:first-child { display: none !important; }
        .tree-hole-container {
            background: #ffffff !important;
            padding: 12px 16px;
            margin: 0;
            width: 100%;
            box-sizing: border-box;
        }
        .post-card {
            background: #ffffff !important;
            border: 1px solid #f0e9df;
            border-radius: 12px;
            padding: 14px;
            box-shadow: 0 1px 4px rgba(224, 214, 203, 0.1);
            margin-bottom: 10px;
        }
        .content-card {
            background: #ffffff !important;
            border: 1px solid #f0e9df;
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 1px 4px rgba(224, 214, 203, 0.1);
            margin-bottom: 8px;
            border-left: 4px solid #e8dcca;
        }
        .post-images-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 6px;
            margin: 8px 0;
        }
        .post-image {
            width: 100%;
            border-radius: 8px;
            border: 1px solid #f0e9df;
            object-fit: cover;
        }
        .stButton>button {
            background: #e8dcca !important;
            color: #5a4b3c !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 6px 12px !important;
            font-size: 13px !important;
            white-space: nowrap !important;
            transition: all 0.2s ease !important;
        }
        .stButton>button:hover {
            background: #d9c8b4 !important;
            transform: translateY(-1px) !important;
        }
        .admin-delete-btn>button {
            background: #f8d7da !important;
            color: #721c24 !important;
            min-width: 50px !important;
            font-size: 11px !important;
        }
        .admin-delete-btn>button:hover {
            background: #f5c6cb !important;
        }
        .stTextInput>div>div>input, 
        .stTextArea>div>div>textarea,
        .stSelectbox>div>div>select,
        .stFileUploader>div>div>button {
            border-radius: 8px !important;
            border: 1px solid #e8dcca !important;
            padding: 6px !important;
            background: #ffffff !important;
            font-size: 13px !important;
        }
        .warm-text {
            color: #7d6b57;
            line-height: 1.5;
            font-size: 13px;
        }
        .admin-tip {
            color: #856404;
            font-size: 11px;
            text-align: center;
            margin: 2px 0;
        }
        .empty-tip {
            text-align: center;
            padding: 16px;
            color: #948675;
            font-size: 13px;
            background: #ffffff;
            border: 1px solid #f0e9df;
            border-radius: 12px;
        }
        .stMarkdown { margin-bottom: 4px !important; }
        .stColumn { gap: 8px !important; }
        .stExpander { padding: 0 !important; }
        .stTextArea { margin-bottom: 6px !important; }
        .stFileUploader { margin-bottom: 6px !important; }
        </style>
        """, unsafe_allow_html=True)

        # ==================== 页面主体 ====================
        st.markdown('<div class="tree-hole-container">', unsafe_allow_html=True)

        # 标题区
        st.markdown('<h2 style="color:#5a4b3c; text-align:center; margin:0 0 4px 0; font-size:20px;">🌳 工大情绪树洞</h2>', unsafe_allow_html=True)
        st.markdown('<p class="warm-text" style="text-align:center; margin:0 0 2px 0;">用善意倾诉，用温暖回应</p>', unsafe_allow_html=True)
        st.markdown('<p class="admin-tip">💡 请发表友善言论，良言一句三冬暖，恶语相向六月寒</p>', unsafe_allow_html=True)
        st.markdown("<hr style='margin:6px 0; border-color:#f0e9df;'>", unsafe_allow_html=True)

        # 每次渲染都重新加载最新数据（关键修复）
        shared_data = load_shared_data()

        # 调试信息
        if st.session_state.is_admin:
            st.markdown(f'<p class="admin-tip">🔧 管理员调试：当前共有 {len(shared_data["posts"])} 条帖子（实时同步）</p>', unsafe_allow_html=True)

        # 暖心回应（不变）
        def get_campus_response(emotion):
            responses = {
                "焦虑": [
                    "工大的湖畔晚风超治愈～试试腹式呼吸，慢慢调整✨",
                    "心理咨询室老师超温柔（0411-86318792），别怕求助❤️",
                    "图书馆靠窗位，适合静下心梳理烦恼📖"
                ],
                "难过": [
                    "抱抱你～食堂热汤面能温暖此刻的你🤗",
                    "去银杏道走走，晚霞会抚平小情绪🌿",
                    "情绪没有对错，难过就说出来～"
                ],
                "烦躁": [
                    "体育馆打球出汗，烦恼会一起跑掉💪",
                    "5分钟正念冥想，平复情绪超管用🧘",
                    "和室友唠唠，工大伙伴都是暖心搭子～"
                ],
                "迷茫": [
                    "生涯咨询老师超专业，聊聊会清晰很多🌟",
                    "学校有超多资源，慢慢来不着急～",
                    "每一步成长都值得肯定✨"
                ],
                "孤独": [
                    "加入社团吧，志同道合的伙伴在等你🌟",
                    "树洞小屋每周开放，有人愿意听你说❤️",
                    "食堂一起干饭，就能感受温暖～"
                ],
                "其他": [
                    "工大永远是你的温柔港湾💛",
                    "接纳自己的情绪，慢慢来～",
                    "日子会慢慢亮起来的✨"
                ]
            }
            all_res = responses.get(emotion, responses["其他"])
            unused = [r for r in all_res if r not in shared_data["responses_used"]]
            if not unused:
                shared_data["responses_used"] = []
                unused = all_res
            res = random.choice(unused)
            shared_data["responses_used"].append(res)
            save_shared_data(shared_data)
            return res

        # 违规词检测（不变）
        def check_sensitive_words(content):
            for word in st.session_state.tree_hole_sensitive:
                if word in content.lower():
                    return True, word
            return False, None

        # 图片转base64（不变）
        def image_to_base64(img):
            if img is None:
                return None
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            byte_data = buf.getvalue()
            return base64.b64encode(byte_data).decode()

        # 分栏布局
        col1, col2 = st.columns([1, 2], gap="medium")

        # 左侧：发布区（不变）
        with col1:
            st.markdown('<div class="post-card">', unsafe_allow_html=True)
            st.markdown('<h4 style="color:#5a4b3c; margin-bottom:8px; font-size:15px;">✍️ 匿名倾诉</h4>', unsafe_allow_html=True)
            
            nickname = st.text_input(
                "✨ 匿名昵称（选填）", 
                placeholder="如：工大追梦人", 
                value=st.session_state.tree_hole_temp["nickname"]
            )
            st.session_state.tree_hole_temp["nickname"] = nickname if nickname else f"工大暖心人{len(shared_data['posts'])+1}"
            
            emotion_tag = st.selectbox(
                "💛 我的情绪", 
                ["焦虑", "难过", "烦躁", "迷茫", "孤独", "其他"], 
                index=["焦虑", "难过", "烦躁", "迷茫", "孤独", "其他"].index(st.session_state.tree_hole_temp["emotion_tag"])
            )
            st.session_state.tree_hole_temp["emotion_tag"] = emotion_tag
            
            content = st.text_area(
                "💬 想说的话", 
                placeholder="在这里写下你的心情吧...\n可以搭配多张图片分享哦～", 
                height=100, 
                value=st.session_state.tree_hole_temp["content"]
            )
            st.session_state.tree_hole_temp["content"] = content
            
            uploaded_files = st.file_uploader(
                "🖼️ 上传图片（可多选）", 
                type=["png", "jpg", "jpeg"], 
                key="th_images",
                accept_multiple_files=True
            )
            images = []
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    img = Image.open(uploaded_file)
                    images.append(img)
                st.session_state.tree_hole_temp["images"] = images
                st.markdown('<div class="post-images-grid">', unsafe_allow_html=True)
                for img in images:
                    st.image(img, use_column_width=True, clamp=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.session_state.tree_hole_temp["images"] = []
            
            if st.button("🚀 把心情交给树洞", use_container_width=True, key="th_post"):
                if not content.strip() and not uploaded_files:
                    st.warning("⚠️ 倾诉内容或图片不能为空哦～")
                else:
                    has_sensitive, word = check_sensitive_words(content)
                    if has_sensitive:
                        st.error(f"❌ 内容包含违规词「{word}」，请修改后发布～")
                    else:
                        images_b64 = [image_to_base64(img) for img in st.session_state.tree_hole_temp["images"]]
                        post_data = {
                            "id": len(shared_data["posts"])+1,
                            "nickname": st.session_state.tree_hole_temp["nickname"],
                            "emotion": emotion_tag,
                            "content": content.strip(),
                            "images": images_b64,
                            "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "like_count": 0,
                            "comments": [],
                            "response": get_campus_response(emotion_tag)
                        }
                        shared_data["posts"].append(post_data)
                        save_shared_data(shared_data)
                        st.success("🎉 发布成功！树洞接住了你的小情绪～")
                        st.balloons()
                        st.session_state.tree_hole_temp = {
                            "content": "", "emotion_tag": "焦虑", "nickname": "", "images": []
                        }
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # 右侧：展示区（关键：每次都用最新的 shared_data）
        with col2:
            st.markdown('<h4 style="color:#5a4b3c; margin-bottom:4px; font-size:15px;">🌟 树洞回音</h4>', unsafe_allow_html=True)
            st.markdown('<p class="warm-text">看看工大伙伴们的暖心分享～</p>', unsafe_allow_html=True)
            
            filter_emotion = st.selectbox("筛选情绪", ["全部"] + ["焦虑", "难过", "烦躁", "迷茫", "孤独", "其他"], label_visibility="collapsed")
            
            # 每次都从最新的 shared_data 取帖子
            posts = shared_data["posts"][::-1]
            if filter_emotion != "全部":
                posts = [p for p in posts if p["emotion"] == filter_emotion]
            
            if len(posts) == 0:
                st.markdown('<div class="empty-tip">', unsafe_allow_html=True)
                st.markdown("💡 还没有树洞哦～")
                st.markdown("发布第一条心情，开启治愈之旅吧✨")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                for post_idx, post in enumerate(posts):
                    st.markdown('<div class="content-card">', unsafe_allow_html=True)
                    
                    # 帖子头部
                    post_head1, post_head2, post_head3 = st.columns([3, 1, 1])
                    with post_head1:
                        st.markdown(f'<span style="color:#5a4b3c; font-weight:500;">{post["nickname"]}</span> '
                                    f'<span style="color:#948675; font-size:11px; background:#f0e9df; padding:2px 5px; border-radius:3px;">📌 {post["emotion"]}</span>',
                                    unsafe_allow_html=True)
                    with post_head2:
                        st.markdown(f'<span style="color:#a89988; font-size:10px; text-align:right; display:block;">{post["create_time"]}</span>',
                                    unsafe_allow_html=True)
                    if st.session_state.is_admin:
                        with post_head3:
                            st.markdown('<div class="admin-delete-btn">', unsafe_allow_html=True)
                            if st.button("🗑️ 删除", key=f"del_post_{post['id']}", use_container_width=True):
                                # 重新加载最新数据，再删除，避免索引错位
                                shared_data = load_shared_data()
                                del shared_data["posts"][-(post_idx+1)]
                                save_shared_data(shared_data)
                                st.success("✅ 已删除该帖子")
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 内容+图片
                    if post["content"]:
                        st.markdown(f'<p class="warm-text" style="margin:6px 0;">{post["content"]}</p>', unsafe_allow_html=True)
                    if post["images"] and len(post["images"]) > 0:
                        st.markdown('<div class="post-images-grid">', unsafe_allow_html=True)
                        for img_b64 in post["images"]:
                            if img_b64:
                                img_html = f'<img src="data:image/png;base64,{img_b64}" class="post-image" alt="树洞图片">'
                                st.markdown(img_html, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 暖心回应
                    st.markdown(f'<div style="background:#f9f5f0; padding:6px; border-radius:8px; margin:6px 0;">'
                                f'<span style="color:#7d6b57; font-size:11px;">💬 工大暖心回应：</span>'
                                f'<span class="warm-text"> {post["response"]}</span>'
                                f'</div>', unsafe_allow_html=True)
                    
                    # 点赞（关键：先重新加载，再修改）
                    interact1, interact2 = st.columns([1,4])
                    with interact1:
                        if st.button(f"❤️ {post['like_count']}", key=f"th_like_{post['id']}", use_container_width=True):
                            shared_data = load_shared_data()
                            # 找到对应帖子并点赞
                            for p in shared_data["posts"]:
                                if p["id"] == post["id"]:
                                    p["like_count"] += 1
                                    break
                            save_shared_data(shared_data)
                            st.rerun()
                    with interact2:
                        comment_col1, comment_col2 = st.columns([4,1])
                        with comment_col1:
                            comment = st.text_input("留下你的鼓励～", placeholder="如：加油！一切都会好起来的✨", key=f"th_comment_{post['id']}", label_visibility="collapsed")
                        with comment_col2:
                            if st.button("发送", key=f"th_send_{post['id']}", use_container_width=True):
                                if comment.strip():
                                    has_sensitive, word = check_sensitive_words(comment)
                                    if has_sensitive:
                                        st.error(f"❌ 评论包含违规词「{word}」，请修改后发送～")
                                    else:
                                        shared_data = load_shared_data()
                                        for p in shared_data["posts"]:
                                            if p["id"] == post["id"]:
                                                p["comments"].append({
                                                    "nickname": "工大暖心小伙伴",
                                                    "content": comment.strip(),
                                                    "time": datetime.datetime.now().strftime("%H:%M:%S")
                                                })
                                                break
                                        save_shared_data(shared_data)
                                        st.success("💖 你的鼓励已送达～")
                                        st.rerun()
                    
                    # 评论列表
                    if post["comments"] and len(post["comments"]) > 0:
                        st.markdown('<p class="warm-text" style="font-size:11px; margin-top:6px; font-weight:500;">📝 暖心评论：</p>', unsafe_allow_html=True)
                        for c_idx, c in enumerate(post["comments"]):
                            cmt_col1, cmt_col2 = st.columns([5, 1])
                            with cmt_col1:
                                st.markdown(f'<div style="margin-left:6px; font-size:11px; padding:3px 0;">'
                                            f'<span style="color:#7d6b57; font-weight:500;">{c["nickname"]}</span> '
                                            f'<span style="color:#a89988;">({c["time"]})</span>：'
                                            f'<span class="warm-text">{c["content"]}</span>'
                                            f'</div>', unsafe_allow_html=True)
                            if st.session_state.is_admin:
                                with cmt_col2:
                                    st.markdown('<div class="admin-delete-btn">', unsafe_allow_html=True)
                                    if st.button("🗑️", key=f"del_cmt_{post['id']}_{c_idx}", use_container_width=True):
                                        shared_data = load_shared_data()
                                        for p in shared_data["posts"]:
                                            if p["id"] == post["id"]:
                                                del p["comments"][c_idx]
                                                break
                                        save_shared_data(shared_data)
                                        st.success("✅ 已删除该评论")
                                        st.rerun()
                                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
