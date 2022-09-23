#2022_08_31 baizhen
import xlwings as xw
from xpinyin import Pinyin
import difflib
p = Pinyin()
author_dict={}
author_list=[]
############################################################################################################
'''
        1.使用xlwings包从excal文档中提取作者信息
        2.使用列表{author_list}记录所有的作者（使用split将列表内的字符串分割成单独的作者）
        3.使用xpinyin将所有的作者姓名拼音化，全部统一成大写然后比较相似度，判断为同一为作者有多个名字时通
            过字符编码判断中文名的位置，优先使用中文名。整理完成后接下来的数据都会使用列表中的标准名
        4.通过字典记录作者与作者之间的关系 确认关系前先保证两人之前没有关系。
        5.通过列表索引字典，通过xlwings将所有的数据输出到excal表格，并进行保存
        
        备注：  1.算法落后，跑起来很慢
                2.数据抓取环节不能处理空数据，需要手动进入excal对数据进行排序以消除空数据的影响
                3.作者拆分的不全面，代码不能识别全部的作者姓名
                4.同名识别存在问题，不能识别出所有单人多名情况，对于双汉字名，拼音缩写名两种情况处理效果不好
                3.主体是面向过程变成，程序泛用性低下。
                4.数据抓取范围需要手动进入代码进行修改
                5.写程序之前没有规划，代码结构混乱，中途存在多次巨大方向性的错误。
'''
##################################将得到的作者信息同类合并并且存储##########################################
def str_process(data):#将表格中的作者信息拆分
    data_pro = data.split(',')#得到一个去掉分号的列表
    for i in range(len(data_pro)):
        data_part = data.split(';')
        #将单一作者加入字典，如果重名则不添加
        for i in range(len(data_part)):
            if data_part[i] not in author_list:
                author_list.append(data_part[i])#整理所有的作者信息 将重复的信息整理到一起
def str_change(a):
    return p.get_pinyin(a,'').replace(',','').replace(' ','').upper()

def author_list_process():
    #print("开始进行作者合并")
    i=0
    k=len(author_list) #k是list的长度
    while i<k:
        j=len(author_list)-1
        while j>i:
            res = True#判断有没有中文名称，有的话就以中文为zhu
            for w in author_list[j]:
                if not '\u4e00' <= w <= '\u9fff':
                    res = False
            if (string_similar(str_change(author_list[i]),str_change(author_list[j])))> 0.89:
                if res == True:
                    #print(f'{author_list[j]}删掉了{author_list[i]}')
                    del author_list[i]
                    j=len(author_list)-1
                else:
                    #print(f'{author_list[i]}删false掉了{author_list[j]}')
                    del author_list[j]
                    j-=1
            else:
                j-=1
        i+=1
###############################################################根据作者列表进行信息填充################################

def str_find(a):#查找作者在列表中的名称
    for i in range(len(author_list)):#k是作者在列表中的名字
        if(string_similar(str_change(a),str_change(author_list[i])) > 0.89):
            return author_list[i]
                           
            
    
def type_in_dict(data):
    for i in range(len(data)):
        data_part = data[i].split(';')
        for j in range(len(data_part)):#j是作者在源文件中的名字
            for k in range(len(author_list)):#k是作者在列表中的名字
                if(string_similar(str_change(data_part[j]),str_change(author_list[k])))> 0.89: #超找到之后使用k代替j
                    #print(f'zhu jue deng chang {author_list[k]}')
                    if author_list[k] not in author_dict:
                        author_dict[author_list[k]] = []#将所有作者信息录入完毕
                        l=len(data_part)-1
                        for p in range(len(data_part)):#k是键，l是值    
                            if (l>p and (str_find(data_part[l]) not in author_dict[author_list[k]])and(str_find(data_part[l]) != author_list[k])):
                                author_dict[author_list[k]].append(str_find(data_part[l]))
                                #print(f'把{data_part[l]}-->{str_find(data_part[l])} in {author_list[k]}') 
                        l-=1
                                   
################################检测人名相似度函数######################################################################
def string_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()

#############################################打印配对结果###############################################################
def copy():
    d=0 #down
    sht = wb.sheets["sheet2"]
    for i in range(len(author_list)):
        a=author_list[i]
        if len(author_dict[a]) >0:
            for x in range(len(author_dict[a])):
                sht[d,0].value = a
                sht[d,1].value = author_dict[a][x]
                d+=1
#将data.xlsx->sheet1->(b2:b9193)中的人物数据（排序后排除空项，b1,b8934)
#进行配对记录,将结果记录在data.xlsx->sheet2中            
        
app = xw.App(add_book=False,visible=True)#应用
wb = app.books.open("data.xlsx")#打开工作簿
sht = wb.sheets["sheet1"]#选择工作表
print("正在提取数据")
data = sht.range("b1:b1001").value#提取数据
for i in range(len(data)):#将工作部中的作者信息载入到list
    str_process(data[i])
print("正在整理数据")
author_list_process()#整理list中的数据
type_in_dict(data)
print("正在向excal写入数据")
copy()#向excal里写入数据
print("正在保存,数据将将保存到当前目录下的task_data.xlsx")
wb.save("task_data.xlsx")#保存工作簿
print("保存完毕")
app.quit()



