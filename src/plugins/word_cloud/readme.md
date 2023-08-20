# 词云插件


```python
on_command("词云", aliases={"wordcloud"}, priority=20, block=False)
```

后面可以接: "本周" 代表获取这一周
接: "本月" 代表获取本月词云
接: "历史" 代表获取历史词云


## 安装依赖
```bash
pip install -r requirements.txt
spacy download en_core_web_sm
```