# chinese_science_paper_to_text
读取多层级目录下的pdf文件，通常是爬虫爬下来的，将其中摘要和正文抽取出来。可以初步结构化pdf，快速抽取，并且简单清洗数据，得到想要的文本内容，得到（1）摘要（2）正文
使用了python 多进程加速程序，适用大规模pdf抽取。 

results文件中,是dict 的list.键值包括文件名，摘要，还有按。和换行断句的正文。

outputs文件夹中是清洗后按照段落的txt。

#### 每个dict:
 {"pdf_name":pdf全局path, "whole_content": 所有内容文本, "abstract":abstract, "content_split_list":断句结果}

## 用法

直接分析pdf（识别误差多）
```Python3
python main.py --lang chinese --pdf_dir_pth ./test_pdf --result_json_file ./reult.json --num 40
```
清洗txt
```Python3
python main.py --lang txt --pdf_dir_pth ./test_txt --result_json_file ./reult.json --num 40
```


## 参数说明
1. --lang 选择pdf语言 有 chinese english txt 
2. --pdf_dir_pth  pdf所在目录,可任意深度,只要pdf/txt 在最深层
3. --result_json_file 结果
4. --num 并发进程数目
