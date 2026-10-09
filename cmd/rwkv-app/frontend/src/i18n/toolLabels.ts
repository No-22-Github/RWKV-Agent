/*
 * 工具名的界面文案。目前界面只有中文，这里先按 zh / en 两份写好，
 * 以后做英文界面时把 locale 接到全局语言设置即可。
 */

export type Locale = 'zh' | 'en'

type ToolCopy = {
  /** 行内动词：「读取 README.md」/ "Read README.md" */
  verb: string
  /** 摘要里的宾语与量词：读取了 3 个文件 / Read 3 files */
  noun: string
  unit?: string
  /** 英文复数；缺省为 noun + s */
  plural?: string
  /** 英文进行时动词：Reading / Searching */
  ing?: string
  /** 行内标签，替代 verb：动词放在参数前读着别扭时用（「查询 合肥」→「天气 合肥」） */
  row?: string
}

type ToolEntry = { zh: ToolCopy; en: ToolCopy }

const TOOLS: Record<string, ToolEntry> = {
  read_file: { zh: { verb: '读取', noun: '文件', unit: '个' }, en: { verb: 'Read', ing: 'Reading', noun: 'file' } },
  read_lines: { zh: { verb: '读取', noun: '文件片段', unit: '段' }, en: { verb: 'Read', ing: 'Reading', noun: 'file excerpt' } },
  list_files: { zh: { verb: '列出', noun: '目录', unit: '个' }, en: { verb: 'Listed', ing: 'Listing', noun: 'directory', plural: 'directories' } },
  search_text: { zh: { verb: '搜索', noun: '代码', unit: '次' }, en: { verb: 'Searched', ing: 'Searching', noun: 'code', plural: 'code' } },
  write_file: { zh: { verb: '写入', noun: '文件', unit: '个' }, en: { verb: 'Wrote', ing: 'Writing', noun: 'file' } },
  append_file: { zh: { verb: '追加', noun: '文件内容', unit: '处' }, en: { verb: 'Appended to', ing: 'Appending to', noun: 'file' } },
  replace_lines: { zh: { verb: '编辑', noun: '文件', unit: '处' }, en: { verb: 'Edited', ing: 'Editing', noun: 'file' } },
  web_search: { zh: { verb: '搜索', noun: '网页', unit: '次' }, en: { verb: 'Searched', ing: 'Searching', noun: 'the web', plural: 'the web' } },
  web_fetch: { zh: { verb: '读取', noun: '网页', unit: '个' }, en: { verb: 'Fetched', ing: 'Fetching', noun: 'page' } },
  spawn_agents: { zh: { verb: '派出', noun: '子 Agent', unit: '批' }, en: { verb: 'Spawned', ing: 'Spawning', noun: 'subagent' } },
  calculator: { zh: { verb: '计算', noun: '算式', unit: '个' }, en: { verb: 'Calculated', ing: 'Calculating', noun: 'expression' } },
  get_weather: { zh: { verb: '查询', noun: '天气', unit: '次', row: '天气' }, en: { verb: 'Checked', ing: 'Checking', noun: 'the weather', plural: 'the weather', row: 'Weather' } },
  datetime: { zh: { verb: '查询', noun: '时间', unit: '次' }, en: { verb: 'Checked', ing: 'Checking', noun: 'the time', plural: 'the time' } },
  load_tools: { zh: { verb: '加载', noun: '工具', unit: '组' }, en: { verb: 'Loaded', ing: 'Loading', noun: 'tool set' } },
}

/** 未登记的工具：动词用通用的「调用」，宾语就是工具名本身。 */
function entry(tool: string): ToolEntry {
  return TOOLS[tool] || { zh: { verb: '调用', noun: tool, unit: '次' }, en: { verb: 'Used', noun: tool, plural: tool, ing: 'Using' } }
}

export function toolVerb(tool: string, locale: Locale = 'zh') {
  const copy = entry(tool)[locale]
  return copy.row || copy.verb
}

export function isKnownTool(tool: string) {
  return tool in TOOLS
}

/** 一个工具的完成态短语：读取了文件 / 读取了 3 个文件；Read a file / Read 3 files */
export function toolPhrase(tool: string, count: number, locale: Locale = 'zh') {
  const copy = entry(tool)[locale]
  if (locale === 'zh') return count > 1 ? `${copy.verb}了 ${count} ${copy.unit || '次'}${copy.noun}` : `${copy.verb}了${copy.noun}`
  const counted = copy.plural === copy.noun
  if (counted) return count > 1 ? `${copy.verb} ${copy.noun} ×${count}` : `${copy.verb} ${copy.noun}`
  const article = /^[aeiou]/i.test(copy.noun) ? 'an' : 'a'
  return count > 1 ? `${copy.verb} ${count} ${copy.plural || `${copy.noun}s`}` : `${copy.verb} ${article} ${copy.noun}`
}

/** 进行态：正在读取文件 / Reading file… 用于运行中的摘要行。 */
export function toolRunning(tool: string, locale: Locale = 'zh') {
  const copy = entry(tool)[locale]
  return locale === 'zh' ? `正在${copy.verb}${copy.noun}` : `${copy.ing || copy.verb} ${copy.noun}…`
}

/** 整张卡片的摘要：读取了 3 个文件、搜索了网页 / Read 3 files, searched the web */
export function toolSummary(counts: ReadonlyArray<readonly [string, number]>, locale: Locale = 'zh') {
  const shown = counts.slice(0, 3).map(([tool, count]) => toolPhrase(tool, count, locale))
  const rest = counts.length - shown.length
  if (locale === 'zh') return shown.join('、') + (rest > 0 ? ` 等 ${counts.length} 类操作` : '')
  const text = shown.map((phrase, index) => index === 0 ? phrase : phrase[0].toLowerCase() + phrase.slice(1)).join(', ')
  return text + (rest > 0 ? ` and ${rest} more` : '')
}
