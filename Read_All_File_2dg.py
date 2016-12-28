# -*- coding:utf-8 -*-  
import io 
import os
import sys
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030') #这一句是为了能在windows命令行下以UTF-8格式输出字符串
#reload(sys)
#sys.setdefaultencoding("utf-8")

Data_Dir = "Data_In"   #这个目录下面存了已经转成txt的对外投资信息
Data_Er = 'Data_Er'    #这个目录下面存了已经抽取出来的投资信息，以及证券简称和证券代码

Data_Er_Prefix = "Data_Er_"    # 投资信息文本文件名前缀 

# Unicode 格式转换  python2版本使用
def ChangeUnicode(Contents):

	if type(Contents) != unicode:
		Contents = unicode(Contents, "UTF-8")
		pass
	#Contents = re.sub("\s","",Contents)
	return Contents
	pass    

def Read_Single_File(f_name):
	StringAndIndex_List = []
	eachline_List = []
	# Load and read file.
	try:
		File = open(f_name, 'r') #这一步是先把硬盘上的文本文件映射成为一个文件流
		eachline_List = File.readlines()  #读取文件流及文本文件里面的内容
	except UnicodeError:
		print('*********************转码异常********************')
		print('转码异常的文件名:',f_name)
	 
	Preprocess_List = Preprocess(eachline_List) # 预处理 清除空格以及页脚信息
	ParagraphIndex_List = Paragraph(Preprocess_List) # 抽取段落标记信息
	
	StringAndIndex_List.append(Preprocess_List)
	StringAndIndex_List.append(ParagraphIndex_List)
	return StringAndIndex_List
	
def Preprocess(eachline_List):
	eachline_List2 = [] #去除了空格的List
	#eachline_List3 = [] #去除了页眉页脚的List
	
	for index,eachline in enumerate(eachline_List):
		if eachline.strip() != '' and eachline.strip() != ' ' :  #清除空格 生成eachline_List2
			eachline_List2.append(eachline)
	#FileString = ChangeUnicode(FileString)  #先将字符转换为统一码 #pythont2版本使用
	'''
	for index,eachline in enumerate(eachline_List2):    #清除页眉页脚信息
		if not ( re.search('公司 2015年半年度报告全文 ', eachline) ):   #这里去除页码还有点问题
			eachline_List3.append(eachline)
	'''
	return eachline_List2
	
	pass

def Paragraph(Preprocess_List):
	'''
		函数功能:为了提取段落标记
	'''
	ParagraphIndex_List = [] #只存储段落标记索引，判断每行里面是否有。 为准
	for index,eachline in enumerate(Preprocess_List):
		if re.match(r'。$', eachline):
			ParagraphIndex_List.append(index)
	return ParagraphIndex_List

def LineBreaks(Preprocess_List):
	'''
		函数功能：为了提取分行标记
	'''
	pass

def Information_extraction(File_Dict):

	'''
		函数:先把公司信息、盈利能力的表格信息和经营情况这三部分抽取出来
	'''
	for filename, StringAndIndex_List in File_Dict.items():
		try:
			print('**********************文件名**********************')
			print(filename)
			eachline_List = StringAndIndex_List[0]
			ParagraphIndex_List = StringAndIndex_List[1] 
			
			#规则定义
			
			#抽取标题信息
			Title_I = []
			#抽取公告日期
			AnnDate = []
			#公司信息
			infor_T = []

			#公司信息索引
			First_Index_T = 0
			Second_Index_T = 0
			
			#股票解除限售总体概括
			First_Index_gk = 0	#命名gk为概括
			Second_Index_gk = 0	#
			
			#股票解除限售的明细情况
			First_Index_gd = 0	#命名gd为股东
			Second_Index_gd = 0
			
			#证券简称和证券代码
			abbreviation = ' '
			code = ' '
			
			#检测所需信息的索引位置
			for index,eachline in enumerate(eachline_List):
				#print('#################Print每行读取的内容#################')
				#print(eachline) 
				'''
				#抽取标题模板 主要是抽取出减持股东的详情
				if re.search('的公告',eachline.strip()) or re.search('的提示性公告',eachline.strip()):
				'''	
				
				#抽取公司信息部分规则
				if re.search('证券代码',eachline.strip()) or re.search('证券简称',eachline.strip()):
					First_Index_T = index
				#股票解限的总体概述抽取
				m_start = re.search(r'一、', eachline.strip())
				m_end= re.search(r'二、', eachline.strip()) 
				if m_start:
					First_Index_gk = index
				if m_end:
					Second_Index_gk = index
				#简化版
				gd_start = re.search('二、', eachline.strip())
				gd_end= re.search(r'三、', eachline.strip())
				if gd_start:
					First_Index_gd = index
				if First_Index_gd > 0:
					if gd_end:
							Second_Index_gd = index

			#时间抽取
			time_m = re.compile(r'(.*?)(\d{2}月.*?\d{2}日)(.*?)')
			for eachline in eachline_List[-5:]:
				#print(eachline)
				if re.search(time_m, eachline):
					AnnDate = re.search(time_m, eachline).group(2)
			
			
			infor_T = eachline_List[First_Index_T]
			infor_gd = eachline_List[First_Index_gd + 1 : Second_Index_gd]
			infor_gk = eachline_List[First_Index_gk + 1 : Second_Index_gk]
			
			#抽取Title
			for line in infor_gk:
				Title_date_m = re.search(r'(.*?)(\d{2}月.*?\d{2}日)(.*?)', line.strip())
				Title_shares_m = re.search(r'(.*?)(\d+[,.\d]+股)(.*?)$', line.strip())
				if Title_date_m:
					Title_date = Title_date_m.group(2)
				if Title_shares_m:
					Title_shares = Title_shares_m.group(2)

			##股量转中文万单位
			Title_shares_chinese = float(re.sub(r',|股', '', Title_shares))
			if Title_shares_chinese > 10000:
				Title_shares_chinese = int(Title_shares_chinese / 10000)
				Title_shares_chinese = str(Title_shares_chinese) + '万'
			else:
				Title_shares_chinese = str(int(Title_shares_chinese))
			Title_I = str(Title_shares_chinese) + "限售股"+ Title_date + "可转让"

			#第二次抽取股东解限明细
			gd_reg = '^\d$'
			all_gd_list = []
			gd_index = 0
			gd_tag = 0
			temp_gd = []
			#获取单个股东信息，将信息保存到列表中
			#留着其他行的左边的空格，区别作用
			for line in infor_gd:
				line = line.rstrip().replace('\n', '')
				if re.match(r'('+gd_reg+')', line):
					gd_index += 1
					if gd_index != 1:
						gd_tag += 1
					if gd_tag:
						all_gd_list.append(temp_gd)
						temp_gd = []
				if gd_index:
					if line == '合计':
						break
					temp_gd.append(line)
					
			#还差最后一个
			all_gd_list.append(temp_gd)
			#从列表中获取股东具体信息
			#以及....只能添加一次，变量gd_add_tag来控制
			gd_add_tag = 1
			infor_gd_list = ['此次解禁的股东包括']
			for line in all_gd_list:
				for l in line[2:]:
					if re.match(r'^[^是否无合\d]', l.strip()):
						infor_gd_list.append(l)
				infor_gd_list.append(line[1])
				if line[2] == ' 是':
					infor_gd_list.append('(控股股东)')
					if gd_add_tag:
						infor_gd_list.append('，以及其余解禁股东')
						gd_add_tag = 0
			
			#print(infor_gd_list)
			#第二次抽取，将公司信息中的证券代码和证券简称抽取出来
			#print(''.join(infor_T))
			daima = '股份代码:|股份代码：|证券代码:|证券代码：'
			jiancheng = '股份简称:|股份简称：|证券简称:|证券简称：'
			#ListOfCompany = re.split(':|：', str(infor_T))
			m1 = re.search(r'^(' +daima+ ')(.*?)(' +jiancheng+ ')(.*?)主办券商', ''.join(eachline_List[0]).strip())

			#去除空格
			abbreviation = m1.group(4).strip()
			code = m1.group(2).strip()

			#list转为string连接
			Title_I = ''.join(Title_I)
			infor_gk = ''.join(infor_gk)
			infor_gd = ''.join(infor_gd_list)
			
			print('*****************数量转中文*****************')
			print(Title_shares_chinese)
			'''
			print('*****************标题*****************')
			
			print(Title_I)
			
			print('*****************股票解限情况概括*********************')
			print(infor_gk)

			print('*****************股东明细*********************')
			print(infor_gd_list)

			print('*****************公司信息:证券信息*********************')
			print(abbreviation)
			print(code)

			print('*****************公告日期*********************')
			print(AnnDate)
			'''
			#规则定义
			#拟添加抽取失败文件抛出文件名代码
			pass

		except IndexError:
			print('*********************出现异常********************')
			print('出现异常的文件名:',filename)
		
		#将抽取出来的信息写入文本文件
		Write_To_File(filename, abbreviation, code, Title_I, infor_gk, infor_gd, AnnDate.strip())
		
def Write_To_File(name, abbreviation, code, Title_I, infor_gk, infor_gd, AnnDate):
	'''
		函数功能：将抽取出来的信息写入文本文件
		参数说明：infor_J 涉及事后事项
				  infor_Y 权益变动情况
	'''
	#StrOfInfor_J = ('').join(infor_J)
	#StrOfInfor_Y = ('').join(infor_Y)
	
	#将信息写入文本文件
	Data_Er_file = open(os.path.join(Data_Er, Data_Er_Prefix + str(name)) , 'w')
		
	#将标题信息写入文本文件
	Data_Er_file.write(abbreviation+Title_I)
	
	#写入换成符，将两段内容分割开
	Data_Er_file.write('\n')
	Data_Er_file.write('\n')
	
	#将证券代码及证券简称写入文件开头
	abbr = abbreviation+'（'+code+'） '+AnnDate+'公告，'
	Data_Er_file.write(abbr)
	#print(abbreviation+'('+code+') '+AnnDate+'公告，')
	#将权益变动情况写入文本文件
	StrOfInfor_Y = infor_gk.strip()    #开头处添加两个空格
	StrOfInfor_Y = StrOfInfor_Y.replace('\n','')
	Data_Er_file.write(StrOfInfor_Y)
	
	#写入换成符，将两段内容分割开
	Data_Er_file.write('\n')
	Data_Er_file.write('\n')
	
	#将涉及事后事项写入文本文件
	StrOfInfor_J = infor_gd.strip()    #开头处添加两个空格
	Data_Er_file.write(StrOfInfor_J)
	
	Data_Er_file.close

def Read_All_File(Data_Dir):
	'''
		函数：读取Data_Dir目录下的所有文件，并返回File_Dict
		Input:
		Data_Dir 存放半年报的目录
		Output: 
		File_Dict 该字典key为文件名，value为文件包含的字符串信息
	'''
	File_Dict = {}
	File_Path_Prefix = os.path.join(os.getcwd(), Data_Dir) #os.getcwd() 获取当前工作目录
	for f_name in os.listdir(Data_Dir): #os.listdir获得指定目录中的内容
		if f_name.endswith(".txt"):  
			f_full_name = os.path.join(File_Path_Prefix, f_name)
			#print(f_full_name)
			File_Dict[f_name] = Read_Single_File(f_full_name)
	return File_Dict
	
def main():
	File_Dict = Read_All_File(Data_Dir)
	#print(Read_All_File(Data_Dir))
	Information_extraction(File_Dict)
	
	pass

if __name__ == '__main__':
	main()