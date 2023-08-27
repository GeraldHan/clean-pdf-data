# chinese_science_paper_to_text
读取多层级目录下的pdf文件，通常是爬虫爬下来的，将其中摘要和正文抽取出来。可以初步结构化pdf，快速抽取，并且简单清洗数据，得到想要的文本内容，得到（1）摘要（2）正文
使用了python 多进程加速程序，适用大规模pdf抽取。 

results文件中,是dict 的list.键值包括文件名，摘要，还有按`。`和`\n`断句的正文。

outputs文件夹中是清洗后按照段落的txt。

#### 每个dict:
 {"pdf_name":pdf全局path, "abstract": abstract, "content_split_list":断句结果}

## 用法

使用PyMuPDF包直接分析pdf（识别误差多），并且在pdf质量很差（影印）情况下文字提取很差。
```Python3
python main.py --lang chinese --pdf_dir_pth ./test_pdf --result_json_file ./reult.json --num 40
```
配合Acrobat的宏功能提取。
具体流程为

1. Acrobat的``动作向导``功能，添加去除水印，删除页眉页脚，另存为txt，即可批量处理整个文件夹中的pdf文件。
2. 如果质量很差，可以先将pdf批量转为word可以识别文字（大概用了OCR），然后从word转txt（Office的批量需要代码写宏，可以通过adobe将word批量转pdf再从转后的pdf进行步骤1）
3. 将txt文件另存为另一个文件夹进行初步清洗
清洗txt
```Python3、
python main.py --lang txt --pdf_dir_pth ./test_txt --result_json_file ./reult.json --num 40
```
4. 采用李广老师提供gpt工具可以对文字进一步改善


## 参数说明
1. --lang 选择pdf语言 有 chinese english txt 
2. --pdf_dir_pth  pdf所在目录,可任意深度,只要pdf/txt 在最深层
3. --result_json_file 结果
4. --num 并发进程数目
