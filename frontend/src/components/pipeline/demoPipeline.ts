/**
 * Demo Pipeline — 浏览器内置模拟流水线
 *
 * 当后端 API 不可用时（如 GitHub Pages 纯静态托管），
 * 在浏览器中运行完整的模拟视频生成流程。
 */

import type { PipelineStageResult, PipelineGenerateResponse } from '../../api/pipeline'

interface DemoRequest {
  topic: string
  genre: string
  targetLength: string
  style: string
  voiceStyle: string
}

// 内置文案模板
const MOCK_CONTENTS: Record<string, { title: string; segments: { title: string; content: string; scene: string; emotion: string }[] }> = {
  cognitive: {
    title: '为什么穷人越穷，富人越富？',
    segments: [
      { title: '开篇', content: '你有没有想过：为什么有些人轻松赚百万，而另一些人拼尽全力只能勉强糊口？这不是运气问题，而是系统问题。今天揭开「马太效应」背后真相。', scene: '城市对比延时摄影', emotion: 'neutral' },
      { title: '复利的力量', content: '爱因斯坦说复利是世界第八大奇迹。本金足够大时，每年5%回报率，30年超4倍收益。但月光族连本金都没有，复利只是概念。', scene: '图表动画展示复利增长曲线', emotion: 'analytical' },
      { title: '杠杆效应', content: '富人的第二个武器是杠杆——用别人的钱赚钱，用别人的时间赚钱。穷人只有体力和时间，一天24小时是上限。', scene: '杠杆示意动画', emotion: 'analytical' },
      { title: '信息差', content: '信息就是财富。富人获取一手有价值信息，普通人获取的是二手滞后信息。听说某个行业赚钱时，往往已是红海。', scene: '信息流层级示意', emotion: 'slightly_urgent' },
      { title: '风险承受力', content: '富人有足够资本试错，一次失败只是学费。普通人倾其所有创业，一次失败可能是万劫不复。这是安全垫的差距。', scene: '风险与收益对比图', emotion: 'contemplative' },
      { title: '破局之道', content: '当你理解规则，就有了打破的机会。第一，积累第一桶金。第二，学会利用杠杆。第三，降低消费提高投资意识。第四，持续学习缩小信息差。', scene: '上升箭头动画', emotion: 'inspiring' },
      { title: '结语', content: '财富积累是马拉松不是百米冲刺。今天的每个小决定都在塑造五年后的你。点赞收藏，让更多人看到。', scene: '主播面对镜头', emotion: 'warm' },
    ]
  },
  story: {
    title: '一个普通人的不普通一年',
    segments: [
      { title: '起点', content: '2025年的第一天，李明银行卡只剩368块。坐在出租屋床边，看着窗外灰蒙蒙天空，脑子里只有一个想法：不能再这样下去了。', scene: '灰调清晨出租屋', emotion: 'melancholic' },
      { title: '转折', content: '几个月后他做出让所有人疯狂的决定——辞掉稳定工作，借2万块做AI视频。没人看好他，父母都觉得他疯了。', scene: '切换明亮色调', emotion: 'tense' },
      { title: '挣扎', content: '前三个月最难。没有收入只有支出。B站发30多个视频，播放量不到500。开始怀疑自己选错了路。', scene: '夜晚电脑前独坐', emotion: 'depressed' },
      { title: '曙光', content: '第四个月奇迹发生。精心制作的视频突然爆了，一夜突破100万播放。私信评论合作邀约雪片般飞来。', scene: '屏幕数据飙升动画', emotion: 'excited' },
      { title: '逆袭', content: '一年后李明月收入超过之前年薪好几倍。他说：我不是天才，我只是在最绝望时选择再坚持五分钟。', scene: '明亮工作室', emotion: 'inspiring' },
    ]
  },
}

const MOCK_IMAGES: Record<string, string> = {
  '城市对比延时摄影': 'https://placehold.co/1920x1080/1a1a2e/e94560?text=城市对比',
  '图表动画展示复利增长曲线': 'https://placehold.co/1920x1080/16213e/0f3460?text=复利增长曲线',
  '杠杆示意动画': 'https://placehold.co/1920x1080/533483/e94560?text=杠杆效应',
  '信息流层级示意': 'https://placehold.co/1920x1080/1a1a2e/00b4d8?text=信息差',
  '风险与收益对比图': 'https://placehold.co/1920x1080/0f3460/e94560?text=风险承受力',
  '上升箭头动画': 'https://placehold.co/1920x1080/16213e/2dc653?text=破局之道',
  '主播面对镜头': 'https://placehold.co/1920x1080/533483/f72585?text=结语',
  '灰调清晨出租屋': 'https://placehold.co/1920x1080/1a1a2e/6b7280?text=起点',
  '切换明亮色调': 'https://placehold.co/1920x1080/0f3460/f59e0b?text=转折',
  '夜晚电脑前独坐': 'https://placehold.co/1920x1080/16213e/4361ee?text=挣扎',
  '屏幕数据飙升动画': 'https://placehold.co/1920x1080/1a1a2e/2dc653?text=曙光',
  '明亮工作室': 'https://placehold.co/1920x1080/533483/f72585?text=逆袭',
}

function delay(ms: number): Promise<void> {
  return new Promise(r => setTimeout(r, ms))
}

export async function runDemoPipeline(req: DemoRequest): Promise<PipelineGenerateResponse> {
  const projectId = `demo-${Date.now().toString(36)}`
  const stages: PipelineStageResult[] = []

  // Stage 1: 提示词优化
  stages.push({ stage: 'prompt', status: 'pending', progress: 0, message: '', output: {} })
  await delay(300)
  stages[0] = {
    stage: 'prompt', status: 'completed', progress: 1.0,
    message: `提示词优化完成: ${req.genre === 'story' ? '叙事类' : '认知科普类'}`,
    output: { classification: req.genre === 'story' ? 'fusion' : 'scene', positive_prompt: `${req.topic}, cinematic, 8k`, negative_prompt: 'low quality, blurry' }
  }

  // Stage 2: 文案生成
  stages.push({ stage: 'copywrite', status: 'pending', progress: 0, message: '', output: {} })
  await delay(500)
  const template = MOCK_CONTENTS[req.genre === 'story' ? 'story' : 'cognitive'] || MOCK_CONTENTS.cognitive
  const segs = template.segments.map((s, i) => ({
    id: `seg-${i}`, title: s.title, content: s.content,
    word_count: s.content.length, estimated_duration_sec: s.content.length / 3.5,
    scene_description: s.scene, emotion: s.emotion,
  }))
  const totalDur = segs.reduce((sum, s) => sum + s.estimated_duration_sec, 0)
  stages[1] = {
    stage: 'copywrite', status: 'completed', progress: 1.0,
    message: `文案生成完成: ${template.title}，${segs.length}段，${totalDur.toFixed(0)}秒`,
    output: { project_id: `cw-${projectId}`, title: template.title, segments: segs, total_word_count: segs.reduce((s, seg) => s + seg.word_count, 0), total_duration_sec: +totalDur.toFixed(1), mode: 'demo' }
  }

  // Stage 3: AI绘图
  stages.push({ stage: 'draw', status: 'pending', progress: 0, message: '', output: {} })
  await delay(600)
  const images = segs.map((s, i) => ({
    segment_index: i, task_id: `draw-${i}`,
    image_url: MOCK_IMAGES[s.scene_description] || `https://placehold.co/1920x1080/1a1a2e/4361ee?text=${encodeURIComponent(s.scene_description || '场景')}`,
    scene: s.scene_description,
  }))
  stages[2] = {
    stage: 'draw', status: 'completed', progress: 1.0,
    message: `AI绘图完成: ${images.length}张配图`,
    output: { images, total_images: images.length, pipeline: 'demo' }
  }

  // Stage 4: TTS配音
  stages.push({ stage: 'tts', status: 'pending', progress: 0, message: '', output: {} })
  await delay(400)
  const audio = segs.map((s, i) => ({
    segment_index: i, audio_url: `/mock/tts/seg_${i}.wav`,
    duration_sec: s.estimated_duration_sec, word_count: s.word_count,
  }))
  const totalAudioDur = audio.reduce((sum, a) => sum + a.duration_sec, 0)
  stages[3] = {
    stage: 'tts', status: 'completed', progress: 1.0,
    message: `TTS配音完成: ${audio.length}段，${totalAudioDur.toFixed(0)}秒`,
    output: { job_id: `tts-${projectId}`, audio_segments: audio, total_duration_sec: +totalAudioDur.toFixed(1), mode: 'demo' }
  }

  // Stage 5: 智能剪辑
  stages.push({ stage: 'edit', status: 'pending', progress: 0, message: '', output: {} })
  await delay(500)
  stages[4] = {
    stage: 'edit', status: 'completed', progress: 1.0,
    message: `视频合成完成: ${segs.length}片段，1080p`,
    output: { project_id: `vid-${projectId}`, video_url: `/mock/video/output.mp4`, segments_count: segs.length, total_duration_sec: +totalDur.toFixed(1), resolution: '1920x1080' }
  }

  // Stage 6: 质量评估
  stages.push({ stage: 'quality', status: 'pending', progress: 0, message: '', output: {} })
  await delay(300)
  const overallScore = 78 + Math.floor(Math.random() * 16)
  stages[5] = {
    stage: 'quality', status: 'completed', progress: 1.0,
    message: `质量评估完成: 综合${overallScore}/100分`,
    output: { report_id: `q-${projectId}`, passed: overallScore >= 70, lpips_avg: 0.08, clip_score_avg: 0.82, suggestions: ['质量达标，可发布'], summary: `✅ Demo评估通过 (${overallScore}/100)` }
  }

  return {
    project_id: projectId,
    title: template.title,
    status: 'completed',
    stages,
    current_stage: 'quality',
    overall_progress: 1.0,
    estimated_duration_sec: totalDur,
    created_at: new Date().toISOString(),
  }
}
