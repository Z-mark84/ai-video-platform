"""M4 文案生成 - 核心服务

支持两种模式：
1. LLM模式：使用Ollama deepseek-r1:7b生成文案
2. Mock模式：内置模板文案，用于开发和演示
"""

from __future__ import annotations
import uuid
import json
import random
from datetime import datetime
from typing import Optional

from app.models.copywrite import (
    CopywriteProject, CopywriteSegment, CopywriteTemplate,
    EmotionCurve, GenerateRequest,
)
from app.services.copywrite.llm import llm_service

# 内置文案模板
_MOCK_COPYWRITES: dict[str, list[dict]] = {
    "认知类": [
        {
            "title": "为什么穷人越穷，富人越富？",
            "segments": [
                {"title": "开篇", "content": "你有没有想过这样一个问题：为什么有些人轻轻松松就能赚到百万，而另一些人拼尽全力却只能勉强糊口？这不是一个关于运气的问题，而是一个关于系统的问题。今天，我们就来揭开这个被称为「马太效应」的社会现象背后的底层逻辑。", "scene": "城市对比延时摄影", "emotion": "neutral"},
                {"title": "复利的力量", "content": "富人的第一个秘密武器叫做复利。爱因斯坦曾说过，复利是世界第八大奇迹。当你的本金足够大时，即使每年只有5%的回报率，30年后你会获得超过4倍的收益。但对于一个月光族来说，复利只是一个遥不可及的概念。因为他们连本金都没有。", "scene": "图表动画展示复利增长曲线", "emotion": "analytical"},
                {"title": "杠杆效应", "content": "富人的第二个武器是杠杆。他们用别人的钱赚钱，用别人的时间赚钱，用别人的智慧赚钱。而穷人只有一种杠杆——他们的体力和时间。问题是，一天只有24小时。一个人的体力是有上限的。这就决定了单纯出卖劳动力的收入天花板是极其有限的。", "scene": "杠杆示意动画", "emotion": "analytical"},
                {"title": "信息差", "content": "第三个关键因素：信息差。在信息时代，信息就是财富。富人花大量时间获取一手的、有价值的信息，他们知道哪里有红利，哪里有风口。而普通人获取的信息往往是二手的、滞后的、甚至是被人加工过的。当你听说某个行业赚钱的时候，往往已经是红海了。", "scene": "信息流层级示意", "emotion": "slightly_urgent"},
                {"title": "风险承受力", "content": "第四个维度：风险承受能力。富人有足够多的资本去试错，一次失败对他们来说只是交了一点学费。但对于倾其所有去创业的普通人来说，一次失败可能就是万劫不复。这不是能力的差距，而是安全垫的差距。这也就是为什么富者愈富、贫者愈贫。", "scene": "风险与收益对比图", "emotion": "contemplative"},
                {"title": "破局之道", "content": "但这并不意味着普通人的命运就注定了。当你理解了这些规则，你就有了打破它们的机会。第一，积累你的第一桶金——哪怕每个月只存500块。第二，学会利用杠杆——学习投资而不是消费。第三，降低消费欲望，提高投资意识。第四，持续学习，缩小信息差。", "scene": "上升箭头动画", "emotion": "inspiring"},
                {"title": "结语", "content": "记住，财富积累是一场马拉松，而不是百米冲刺。今天的每一个小决定，都在塑造五年后的你。如果你觉得这个视频对你有帮助，请点赞收藏，让更多人看到。我们下期见。", "scene": "主播面对镜头", "emotion": "warm"},
            ]
        },
    ],
    "叙事类": [
        {
            "title": "一个普通人的不普通一年",
            "segments": [
                {"title": "起点", "content": "2025年的第一天，李明的银行卡里只剩下了368块钱。他坐在出租屋的床边，看着窗外灰蒙蒙的天空，脑子里只有一个想法：不能再这样下去了。", "scene": "灰调清晨出租屋", "emotion": "melancholic"},
                {"title": "转折", "content": "几个月后，他做出了一个让所有人都觉得疯狂的决定。辞掉了稳定的工作，用借来的2万块钱开始做AI视频。没有人看好他，连他的父母都觉得他疯了。", "scene": "切换明亮色调", "emotion": "tense"},
                {"title": "挣扎", "content": "前三个月是最难的。没有收入，只有支出。他在B站上发了30多个视频，播放量加在一起不超过500。他开始怀疑自己是不是真的选错了路。", "scene": "夜晚电脑前独坐", "emotion": "depressed"},
                {"title": "曙光", "content": "第四个月，奇迹发生了。他精心制作的一期视频突然爆了，播放量在一夜之间突破了100万。私信、评论、合作邀约像雪片一样飞来。", "scene": "屏幕数据飙升动画", "emotion": "excited"},
                {"title": "逆袭", "content": "一年后，李明的月收入已经超过了他在之前公司年薪的好几倍。他说：'我不是天才，我只是在最绝望的时候，选择再坚持了五分钟。'", "scene": "明亮的工作室", "emotion": "inspiring"},
            ]
        },
    ],
}

# 系统提示词
_SYSTEM_PROMPTS = {
    "cognitive": "你是一个专业的认知科普类长视频文案写手。你的任务是根据用户提供的主题，生成一段结构化的长视频文案。"
                 "要求：1)开篇抓人 2)层层递进 3)结尾升华 4)每段配场景描述 5)语言口语化、有感染力",
    "story": "你是一个专业的叙事类视频文案写手。要求：1)有故事高潮 2)人物有弧光 3)情感共鸣 4)结尾有反转或升华",
    "lecture": "你是一个专业的知识分享类视频文案写手。要求：1)逻辑清晰 2)案例丰富 3)难懂概念通俗化 4)每段有记忆点",
    "marketing": "你是一个专业的营销类视频文案写手。要求：1)痛点切入 2)价值展示 3)信任建立 4)行动号召",
}

# 过渡时长映射
_SEGMENT_DURATIONS = {
    "short": (15, 30),
    "medium": (30, 60),
    "long": (45, 90),
}


class CopywriteService:
    """文案生成服务"""

    def __init__(self):
        self._projects: dict[str, CopywriteProject] = {}
        self._segments: dict[str, list[CopywriteSegment]] = {}
        self._templates: list[CopywriteTemplate] = self._init_templates()

    def _init_templates(self) -> list[CopywriteTemplate]:
        return [
            CopywriteTemplate(
                id="tpl-cognitive-01", name="认知科普·标准结构", genre="cognitive",
                structure=[
                    {"title": "开篇钩子", "description": "用问题或现象抓住观众注意力", "word_count": 150},
                    {"title": "核心概念1", "description": "第一个论点+案例", "word_count": 300},
                    {"title": "核心概念2", "description": "第二个论点+数据支撑", "word_count": 300},
                    {"title": "核心概念3", "description": "第三个论点+对比", "word_count": 300},
                    {"title": "破局方法", "description": "给出可行建议", "word_count": 250},
                    {"title": "结尾升华", "description": "金句总结+互动引导", "word_count": 100},
                ],
                style_guide="开篇用疑问句；每段设置小高潮；结尾用金句；语速中速偏快",
                is_system=True,
            ),
            CopywriteTemplate(
                id="tpl-story-01", name="叙事故事·五幕结构", genre="story",
                structure=[
                    {"title": "起始状态", "description": "主角的日常/困境", "word_count": 150},
                    {"title": "触发事件", "description": "打破平静的契机", "word_count": 200},
                    {"title": "挣扎过程", "description": "遇到的困难和挑战", "word_count": 300},
                    {"title": "高潮转折", "description": "关键转折点", "word_count": 200},
                    {"title": "结局启示", "description": "改变后的状态+感悟", "word_count": 150},
                ],
                style_guide="细节描写要生动；对话增加代入感；高潮部分节奏加快",
                is_system=True,
            ),
        ]

    def generate(self, req: GenerateRequest) -> tuple[CopywriteProject, list[CopywriteSegment]]:
        """生成文案（LLM优先，Mock回退）"""
        project_id = f"cw-{uuid.uuid4().hex[:12]}"

        # 尝试LLM生成
        content = self._try_llm_generate(req)

        if content:
            segments = self._parse_llm_output(content, project_id, req)
        else:
            segments = self._mock_generate(project_id, req)

        # 计算总字数
        total_words = sum(s.word_count for s in segments)

        project = CopywriteProject(
            id=project_id,
            title=segments[0].content[:30] + "..." if segments else req.topic,
            topic=req.topic,
            genre=req.genre,
            target_length=req.target_length,
            style=req.style,
            status="completed",
            total_segments=len(segments),
            created_at=datetime.now().isoformat(),
        )

        self._projects[project_id] = project
        self._segments[project_id] = segments

        return project, segments

    def _try_llm_generate(self, req: GenerateRequest) -> str | None:
        """尝试用LLM生成文案"""
        if not llm_service.available:
            return None

        system_prompt = _SYSTEM_PROMPTS.get(req.genre, _SYSTEM_PROMPTS["cognitive"])

        word_map = {"short": "500-800字", "medium": "1000-1500字", "long": "2000-3000字"}
        style_map = {"normal": "平实客观", "emotional": "情感充沛", "humorous": "幽默风趣", "academic": "学术严谨"}

        user_prompt = (
            f"请根据以下主题，生成一篇{word_map.get(req.target_length, '1000-1500字')}的{style_map.get(req.style, '平实客观')}风格文案。\n\n"
            f"主题：{req.topic}\n"
        )
        if req.reference:
            user_prompt += f"\n参考内容：{req.reference}\n"
        if req.preserve_literary:
            user_prompt += "\n保留文学性修辞，允许使用比喻、拟人等手法。\n"

        user_prompt += (
            "\n要求：\n"
            "1. 分为5-8个段落，每个段落配标题\n"
            "2. 每个段落格式：\n"
            "【段落标题】\n"
            "正文内容...\n"
            "场景：[对应画面场景描述]\n"
            "情绪：[neutral/positive/negative/inspiring]\n"
            "---\n"
            "3. 语言口语化，适合视频配音"
        )

        return llm_service.generate(user_prompt, system_prompt, max_tokens=4096)

    def _parse_llm_output(self, content: str, project_id: str, req: GenerateRequest) -> list[CopywriteSegment]:
        """解析LLM输出为结构化段落"""
        segments = []
        blocks = content.split("---")

        length_ranges = {"short": (50, 150), "medium": (100, 300), "long": (200, 500)}
        min_w, max_w = length_ranges.get(req.target_length, (100, 300))

        for i, block in enumerate(blocks):
            block = block.strip()
            if not block:
                continue

            lines = block.split("\n")
            title = lines[0].strip("【】\n ") if lines else f"段落{i+1}"
            body_lines = [l for l in lines[1:] if not l.startswith("场景：") and not l.startswith("情绪：")]
            content_text = "\n".join(body_lines).strip()

            scene = ""
            emotion = "neutral"
            for l in lines:
                if l.startswith("场景："):
                    scene = l.replace("场景：", "").strip()
                elif l.startswith("情绪："):
                    emotion = l.replace("情绪：", "").strip()

            word_count = len(content_text)
            duration_sec = word_count / 3.5  # 按语速3.5字/秒估算

            segments.append(CopywriteSegment(
                id=f"seg-{uuid.uuid4().hex[:8]}",
                project_id=project_id,
                segment_index=i,
                title=title,
                content=content_text,
                word_count=word_count,
                estimated_duration_sec=round(duration_sec, 1),
                scene_description=scene,
                emotion=emotion,
                transition_hint="fade",
            ))

        return segments if segments else self._mock_generate(project_id, req)

    def _mock_generate(self, project_id: str, req: GenerateRequest) -> list[CopywriteSegment]:
        """Mock生成（内置模板文案）"""
        writeups = _MOCK_COPYWRITES.get(
            "认知类" if req.genre == "cognitive" else "叙事类",
            _MOCK_COPYWRITES["认知类"],
        )
        template = random.choice(writeups)
        segments = []

        for i, seg_data in enumerate(template["segments"]):
            word_count = len(seg_data["content"])
            dur_range = _SEGMENT_DURATIONS.get(req.target_length, (30, 60))
            duration_sec = random.uniform(*dur_range)

            segments.append(CopywriteSegment(
                id=f"seg-{uuid.uuid4().hex[:8]}",
                project_id=project_id,
                segment_index=i,
                title=seg_data["title"],
                content=seg_data["content"],
                word_count=word_count,
                estimated_duration_sec=round(duration_sec, 1),
                scene_description=seg_data.get("scene", ""),
                emotion=seg_data.get("emotion", "neutral"),
                transition_hint="fade",
            ))

        # 修改标题适应主题
        if segments:
            segments[0].content = f"今天我们来聊一个很多人都思考过的问题：{req.topic}。" + segments[0].content[30:]

        return segments

    @property
    def has_llm(self) -> bool:
        return llm_service.available

    def get_project(self, project_id: str) -> Optional[CopywriteProject]:
        return self._projects.get(project_id)

    def get_segments(self, project_id: str) -> list[CopywriteSegment]:
        return self._segments.get(project_id, [])

    def update_segment(self, segment_id: str, content: str, scene: str = "", emotion: str = "neutral") -> bool:
        for seg_list in self._segments.values():
            for seg in seg_list:
                if seg.id == segment_id:
                    seg.content = content
                    seg.scene_description = scene
                    seg.emotion = emotion
                    seg.word_count = len(content)
                    seg.status = "revised"
                    return True
        return False

    def get_templates(self, genre: str | None = None) -> list[CopywriteTemplate]:
        if genre:
            return [t for t in self._templates if t.genre == genre]
        return self._templates


copywrite_service = CopywriteService()
