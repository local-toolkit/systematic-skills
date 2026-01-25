这是一个需要实际执行的任务，而不是解释、分析或教学。

请调用已存在的 skill：
路径：.agent/skills/yt-dlp-expert  
执行入口：yt-dlp-tool/agent_client.py  

任务目标：
下载以下 YouTube 视频：
https://www.youtube.com/watch?v=cj_66lINnSs

执行要求：
1. 使用 yt-dlp 下载完整视频与音频
2. 优先选择最高可用分辨率与音质
3. 输出格式为 mp4
4. 下载完成后，仅返回：
   - 执行是否成功
   - 生成的文件完整路径

约束条件：
- 不要解释 yt-dlp 的原理
- 不要给出手动操作步骤
- 不要生成示例代码
- 如果执行失败，只返回明确的失败原因
