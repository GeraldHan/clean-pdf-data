import os
import json
import tqdm
import multiprocessing
import time
from re import sub, split
import re
from test import analyse_font
# process zhiwang_download 
# extract abstract of every pdf 
# Also, find some wrong pdf file
# fengly: 2022/4/28/ 15

def contains_chinese(input_str):
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    match = re.search(pattern, input_str)
    if match:
        return True
    else:
        return False

class Process:
    def __init__(self, pool_num=40):
        self.pool_num = pool_num

    @staticmethod
    def clean_sentence(sentence):
        "clean one line from pdf"
        import re
        sub = re.sub
        result = sub("\u3000*\n*","", sentence).replace("\x82","")
        return result

    def parse_pdf(self, file_name):
        "按照文字块 提取 sort=True 未生效 自行排版"
        import fitz
        try:
            doc = fitz.open(file_name)
        except:
            print("file: {} is not pdf".format(file_name))
            return {}
        content_location_bool = 0
        abstract = ""
        page_content = ""
        end_bool = 0
        font_list = []
        for idx, page in enumerate(doc):
            if end_bool==1:
                break 
            page1text = page.get_text("blocks", sort=True)
            page_text =[i[-3:] for i in page1text if i[-1]==0]
            page_text.sort(key=lambda x:x[1])
            page_text_clean =[self.clean_sentence(j[0]) for j in page_text]
            # print(page_text_clean)
            
            for idx,line in enumerate(page_text_clean):
                # if "摘要" in line or "提要" in line:
                if re.search(r"摘.*要", line) or re.search(r"提.*要", line):
                    content_location_bool=1
                ##########################
                # filter special line
                if "关键词" in line: # 舍掉关键词
                    # in case that "关键词" is not used in some passages
                        content_location_bool=2
                        continue
                if "文献标识码" in line or "中图分类号" in line:
                    continue
                if re.search(r"第.*期", line) or re.search(r"第.*卷", line):
                    continue
                if "doi" in line:
                    continue
                #############################################
                if ("参考资料" in line) or ("参考文献" in line) or ("References" in line):
                    end_bool=1
                    break
                if content_location_bool==1:
                    abstract+=line.strip()
                if content_location_bool==2:# skip english abstract
                    from langdetect import detect_langs
                    try: 
                        lang_list = [i.lang for i in detect_langs(line)]
                        if 'zh-cn' in lang_list:# english abstarct lost
                            content_location_bool=3
                    except: 
                        pass

                if "Keywords" in line or "Key words" in line: # 中文摘要　开始信息缺失
                    content_location_bool=2
                    page_content = "" 
                    # recollect the main content ---> 2 check first chinese line to start 
                    # clear page_content
                    continue
                if "收稿日期" in line:
                    page_content = "" 
                
                if content_location_bool==3:
                    page_content+=line.strip()
            
            font_list += analyse_font(page)

        if len(page_content.strip()) == 0:
           page_content = "".join(page_content)

        # regex drop the expression like [4,5] [23, 1-15] [2,3-6,9]
        result_str1 = sub("\[[0-9]*-*~*,*[0-9]*-*[0-9]*(,[0-9]*)*\]","",page_content)
        result_str2 = sub("［[0-9]*－*[0-9]*］","",result_str1)
        dic_result={}
        dic_result["abstract"] = abstract
        dic_result["pdf_name"] = file_name
        dic_result["whole_content"] = result_str2
        split_list = split("[；。]", result_str2)
        dic_result["content_split_list"] = [i for i in split_list if i!=""]
        dic_result["font_split_list"] = font_list
    
        return dic_result
    
    def clean_txt(self, file_name):
        content_location_bool = 0
        abstract = ""
        page_content = ""
        end_bool = 0
        with open(file_name, 'r', encoding='gbk') as file:
            for line in file:
                if re.search(r"摘.*要", line) or re.search(r"提.*要", line):
                    content_location_bool=1
                ##########################
                # filter special line
                if "关键词" in line: # 舍掉关键词
                    # in case that "关键词" is not used in some passages
                    if line.startswith('关键词'):
                        continue
                    else:
                        line_split = line.split('关键词')
                        abstract+=line_split[0].strip()
                        line = line_split[-1]
                        content_location_bool = 2
                        continue
                if "中图分类号" in line:
                    content_location_bool = 2
                    continue
                if line.startswith('·') or line.startswith('*') or line.startswith('图') or line.startswith('Fig') or line.startswith('收稿日期') or line.startswith('引用格式') or line.startswith('0'):
                    continue
                if 'doi' in line:
                    continue
                #############################################
                if ("参考资料" in line) or ("参考文献" in line) or ("References" in line):
                    end_bool=1
                    break
                    
                if content_location_bool==1:
                    abstract+=line.strip()
                
                if content_location_bool == 2: #跳过英文摘要
                    if contains_chinese(line):
                        content_location_bool = 3
                    else:
                        continue

                if content_location_bool==3 or content_location_bool==1:
                    if contains_chinese(line):#跳过英文图题
                        page_content+=line

        if len(page_content.strip()) == 0:
           page_content = "".join(page_content)

        # regex drop the expression like [4,5] [23, 1-15] [2,3-6,9]
        result_str1 = sub("\[[0-9]*-*~*,*[0-9]*-*[0-9]*(,[0-9]*)*\]","",page_content)
        result_str2 = sub("［[0-9]*－*[0-9]*］","",result_str1)
        result_str3 = sub("\n","",result_str2)
        
        output_name = './outputs/' + file_name.split('/')[-1]
        with open(output_name, 'w') as outputs:
            outputs.write(result_str2)
        outputs.close()  

        dic_result={}
        dic_result["abstract"] = abstract
        dic_result["pdf_name"] = file_name
        split_list = split("[。\n]", result_str3)
        dic_result["content_split_list"] = [i for i in split_list if i not in ["", " "]]
    
        return dic_result
                
                        
    def extract_abstract_from_pdf_en(self, file_name):
        "extract_english_content from pdf"
        "按照文字块 提取 sort=True 未生效 自行排版"
        import fitz
        try:
            doc = fitz.open(file_name)
        except:
            print("file: {} is not pdf".format(file_name))
            return {}
        content_location_bool = 0
        abstract = ""
        page_content = ""
        end_bool = 0
        for idx, page in enumerate(doc):
            if end_bool==1:
                break 
            page1text = page.get_text("blocks", sort=True)
            page_text =[i[-3:] for i in page1text if i[-1]==0]
            page_text.sort(key=lambda x:x[1])
            page_text_clean =[self.clean_sentence(j[0]) for j in page_text]
            
            for idx,line in enumerate(page_text_clean):
                
                if "Abstract" in line:
                    content_location_bool=1
                ##########################
                # filter special line
                if "Introduction" in line: # 舍掉关键词
                    # in case that "关键词" is not used in some passages
                        content_location_bool=2
                        continue
                if "Equal contribution" in line:
                    continue
                #############################################
                if "References" in line:
                    end_bool=1
                    break
                    
                if content_location_bool==1:
                    abstract+=line.strip()
                
                if content_location_bool==2:
                    page_content+=line.strip()
        
        if len(page_content.strip()) == 0:
           page_content = "".join(page_content)

        # regex drop the expression like [4,5] [23, 1-15] [2,3-6,9]
        result_str1 = sub("\[[0-9]*-*~*,*[0-9]*-*[0-9]*(,[0-9]*)*\]","",page_content)
        result_str2 = sub("［[0-9]*－*[0-9]*］","",result_str1)
        dic_result={}
        dic_result["abstract"] = abstract
        dic_result["pdf_name"] = file_name
        dic_result["whole_content"] = result_str2
        split_list = split("[;.]", result_str2)
        dic_result["content_split_list"] = [i for i in split_list if i!=""]
        return dic_result

    def all_filename_list(self, dir_path):
        "generate filename_list from dir_name"
        t1 = time.time()
        path_name_list = []
        for root,_,files in os.walk(dir_path):
            if len(files)!=0:
                for filename in files:
                    path_name = os.path.join(root,filename)
                    path_name_list.append(path_name)
        t2 = time.time()
        print("length: ",len(path_name_list))
        print("time consuming: ",(t2-t1))
        return path_name_list

    def parallel_excute(self, path_name_list, save_pth, process_func):
        "multiprocess the process_pdf "
        pool = multiprocessing.Pool(self.pool_num)
        result_list = list(tqdm.tqdm(pool.imap(process_func, path_name_list),total=len(path_name_list),desc="processing: "))
        pool.close()
        pool.join()
        # filter
        if save_pth.endswith("json"):
            print('start saving json file {}'.format(save_pth))
            print("all_num: ", len(result_list))
            result = [i for i in result_list if i!={}]
            print("right_num: ", len(result))
            with open(save_pth, "w") as f:
                json.dump(result,f,indent=2,ensure_ascii=False)
        else:
            print("all_num: ", len(result_list))
            result = [i for i in result_list if i!="" and i!=[]]
            print(result[0], result[1])
            print("right_num: ", len(result))
            with open(save_pth, "w") as f:
                for i in result:
                    try:
                        f.write(i.strip())
                        f.write("\n")
                    except:
                        print(i)
        print("save successful as ", save_pth)

    

if __name__ =="__main__":
    # 
    #dir_path = "/raid/yiptmp/zhiwang_download/药学/药理学/临床药理学/合理用药"
    dir_path = "/tmp/result/experiment"
    save_pth = "/tmp/result/all_content_en_test.json"
    p = Process()
    list_names = p.all_filename_list(dir_path)
    p.parallel_excute(list_names, save_pth, p.extract_abstract_from_pdf_en)