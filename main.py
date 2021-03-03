# coding:utf-8
import json
import re
import time
import urllib.parse

import pandas as pd
import requests
import scipy.io
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
from stanfordcorenlp import StanfordCoreNLP
# nlp = StanfordCoreNLP(r'E:\stanford-corenlp-latest\stanford-corenlp-4.2.0')

# import wikipedia
#

class RDF:
    """
| name | attr_name | weight | trust |
| ---- | --------- | ------ | ----- |
| ABC  | old       | 1      | 1     |
| ABC  | male      | 1      | 0     |
| ABD  | old       | 1      | 1     |
    """

    def __init__(self, load=True, file="data.csv", columns=["name", "attr_name", "weight", "trust"]):
        self.columns = columns
        self.pop = pd.DataFrame(columns=self.columns)
        self.data = pd.DataFrame(columns=self.columns)
        if load:
            self.load(file)

    def add(self, insert_data):
        self.data = self.data.append(pd.DataFrame(insert_data, columns=self.columns))
        return self.data

    def distrust(self, name):
        if not isinstance(name, list):
            self.pop = self.data[(self.data["name"] == name) & (self.data["trust"] == 0)]
        else:
            for i in name:
                self.pop.append(self.data[(self.data["name"] == i) & (self.data["trust"] == 0)])
        return self.pop

    def exist(self, name, attr_name):
        name = self.data[(self.data["name"] == name) & (self.data["attr_name"] == attr_name)]
        if len(name) == 0:
            return False
        else:
            return True

    # def not_exist(self,names,attrs):
    #     not_exist = list()
    #     for i in names:
    #         for k in attrs:
    #             if not self.exist(i,k):
    #                 print("{}'s {} is not exist in data".format(i,k))
    #                 not_exist.append([i,k])
    #     print(not_exist)
    #     return not_exist
    # def change_value(self,data_change):
    #     self.data

    def save(self, file="data.csv", columns=["name", "attr_name", "weight"]):
        self.data.to_csv(file, index=False, header=False, columns=columns)

    def load(self, file="data.csv",):
        try:
            self.data = pd.read_csv(file,names=self.columns)
        except:
            pass


def search(name):
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"}

    req = requests.get('https://en.wanweibaike.com/wiki-'+name, headers=header)
    res = req.text
    print(res)
    # ny = wikipedia.page(name)
    # print(ny.content)


def find_answers(response):
    res_bs = BeautifulSoup(response, 'lxml')
    src = res_bs.select('html head script')[2].string
    jsvar, _, jsvalue = src.partition('=')
    jsvar, _, jsvalue = jsvalue.partition(';')
    value = json.loads(jsvar)
    return value['componentData']['searchProps']['searchResults']


def search_answers(question):
    url = "https://www.answers.com/search?q=" + question
    # if
    result = dict()
    response = requests.get(url=url)
    response_txt = response.text
    answers_list = find_answers(response_txt)
    # print(res_json)
    print(len(answers_list))
    for item in answers_list:
        question_item = item['title']
        answer_item = item['answer_preview']
        result.update({question_item: answer_item})
    return result


# cookies
# cookies = None

def get_entity_wiki_en(name, relations):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/83.0.4103.61 Safari/537.36"}
    # global cookies
    req = requests.get("https://en.wanweibaike.com/wiki-" + name, headers=header)
    res = req.text
    # print(req.cookies)
    # if cookies is None:
    #     cookies = req.cookies
    result = {name: dict()}
    '''
    ['age', 'education', 'alma mater', 'parents']
    '''
    res_bs = BeautifulSoup(res, 'lxml')
    if "操作成功" in res:
        # print(res)
        # herf = res_bs
        # print("you are too fast,sleep 2 s")
        time.sleep(2)
        req = requests.get("https://en.wanweibaike.com/wiki-" + name, headers=header, cookies=req.cookies)
        res = req.text
        res_bs = BeautifulSoup(res, 'lxml')
    if "操作失败" in res:
        # print("warning: {} page in wiki en is not exit".format(name))
        return result
    src = res_bs.select('tr')

    for i in src:
        tag = i.select('th')
        if tag == []: continue
        for tag_item in tag:
            # if "Born" in tag_item:
            #     try:
            #         entity = i.find('span', class_="bday").string
            #     except:
            #         print("dby type error ! source is \n{}\n".format(tag_item))
            #     year = entity.split('-')[0]
            #     age = 2020 - int(year)
            #     if age <= 35:
            #         result.update({"age": "yong"})
            #     elif age >= 65:
            #         result.update({"age": "old or die"})
            #     else:
            #         result.update({"age": "middle"})
            #     print("find {} Born is {}".format(name, entity))
            # middle necessary information
            if "Parents" in tag_item:
                # print("Find Parents!")
                result[name]["Parents"] = list()
                entity = i.select('td')
                for Parents_item in entity:
                    # print(Parents_item.text)
                    result[name]["Parents"].append(Parents_item.text)
            if "Occupation" in tag_item:
                # print("Find Occupation!")
                result[name]["Occupation"] = list()
                entity = i.select('td')
                for Occupation_item in entity:
                    # print(Occupation_item.text)
                    result[name]["Occupation"].append(Occupation_item.text)
            if "Education" in tag_item:
                # print("Find Education!")
                result[name]["Education"] = list()
                entity = i.select('td')
                for school_item in entity:
                    # print(school_item.text)
                    result[name]["Education"].append(school_item.text)
            if "Alma_mater" in tag_item:
                # print("Find Alma mater!")
                result[name]["Alma_mater"] = list()
                entity = i.select('td').text
                for school_item in entity:
                    # print(school_item)
                    result[name]["Alma_mater"].append(school_item.text)
    src = res_bs.select('#mw-content-text div p')
    inform_text = ""
    if len(src) < 2:
        # print(res_bs)
        # print("page error,{}".format("https://en.wanweibaike.com/wiki-" + name))
        return result
    for i in src[:2]:
        # print(i.text)
        inform_text = inform_text + i.text
    inform_text = inform_text.split('.')
    result[name]["text_wiki_en"] = inform_text
    return result


def get_entity_wiki_cn(name):
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/83.0.4103.61 Safari/537.36"}
    req = requests.get("https://www.wanweibaike.com/wiki-" + name, headers=header)
    res = req.text
    cn_name = ""
    result = dict()
    '''
     ['民族父系', '民族母系']
    '''
    res_bs = BeautifulSoup(res, 'lxml')
    if "操作失败" in res:
        # print("warning: {} page in wiki en is not exit".format(name))
        return False
    src = res_bs.select('tr')
    result = {name: dict()}
    for i in src:
        tag = i.select('th')
        if not tag: continue
        for tag_item in tag:
            # middle necessary information
            if "职业" in tag_item:
                print("Find 职业!")
                entity = i.select('td div')
                result[name]["职业"] = list()
                for school_item in entity:
                    print(school_item.text)
                    result[name]["职业"].append(school_item.text)
            if "民族" in tag_item:
                print("Find 民族!")
                entity = i.select('td a')
                result[name]["民族"] = list()
                for school_item in entity:
                    print(school_item.text)
                    result[name]["民族"].append(school_item.text)
    try:
        cn_name = res_bs.select('html body div div  div  div h1')[0].contents[0]
        print(cn_name)
        result[name]["cn_name"] = cn_name
    except:
        pass
    return result, cn_name


def get_entity_baidu_cn(name):
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"}
    req = requests.get("https://baike.baidu.com/search/word?word=" + urllib.parse.quote(name), headers=header,
                       allow_redirects=False)
    res = req.text
    print(req.headers['Location'])
    req_infor = requests.get("https:" + req.headers['Location'], headers=header)
    res_infor = req_infor.text
    re_resarch_zy = \
        """<dt class="basicInfo-item name">职&nbsp;&nbsp;&nbsp;&nbsp;业</dt>
<dd class="basicInfo-item value">
(.*?)
</dd>"""
    re_result = re.compile(re_resarch_zy)
    # print(re_result)
    re_result = re_result.findall(res_infor)
    if re_result:
        print(re_result)


def get_person_name(file='lfw_att_40.mat', load_txt=True):
    if not load_txt:
        names = set()
        if '.mat' in file:

            mat = scipy.io.loadmat(file)
            name_mat = mat['name'][0]
            # print(mat['name'])
            for item in name_mat:
                # print(i[0],type(i[0]))
                name_item = item[0].split("\\")[0]
                names.add(name_item)
                # print(i.dtype)
                # break
        # print(names)
        with open('person_name.txt', 'w') as f:
            f.write(str(names))
    else:
        with open('person_name.txt', 'r') as f:
            names = eval(f.read())
        # print(names, type(names))
    return names


def get_entity_lfw(RDF_lfw, name='Abdullah_Gul'):
    """
     get entity in LFWA+ dataset
    :param name: name of famous person name
    :return: attr of famous person name
    """
    zero_add = [[0], [9, 10, 11, 58], [17, 18]]
    add_attr = ["Female", "Other_Hair", "Calm"]
    file = "lfw_att_73_7.1.mat"
    data = scipy.io.loadmat(file)
    print(data.keys())
    attr = data['AttrName'][0]
    # print(attr)
    names = data['name'][0]
    label = data['label']
    data_df = pd.DataFrame(label)
    name_df = pd.DataFrame(names)
    name_df.columns = ['names']
    # data_df.insert(0,'names',names)
    name_df['names'] = name_df['names'].astype(str)
    name_df['names'] = name_df['names'].str.split("\\", expand=True)
    # data_df['names'] = data_df['names'].str.split("'")
    name_df = name_df['names'].str.split("'", expand=True)
    name_df.columns = ['1', 'names']
    data_df = pd.concat([name_df['names'], data_df], axis=1)
    # print(data_df)
    for item_name in tqdm(name):
        data_RDF = list()
        attr_df = data_df[data_df['names'] == item_name]
        # print(attr_df)
        attr_df = attr_df.mean()
        attrs_id = range(73)
        for id_attr in attrs_id:
            if attr_df[id_attr] >= 2 / 3:
                data_RDF.append([item_name, attr[id_attr][0], attr_df[id_attr], 1])
            elif attr_df[id_attr] >= 1 / 3:
                data_RDF.append([item_name, attr[id_attr][0], attr_df[id_attr], 0])
        index = 0
        for i in zero_add:
            if attr_df[i].sum() < 1 / 3:
                data_RDF.append([item_name, add_attr[index], 1 - attr_df[i].sum(), 1])
            index += 1
        RDF_lfw.add(data_RDF)
        # print(RDF_lfw.data)
        # check_item(attr_df)
        # break
        # print(data_RDF)
    return RDF_lfw


def check_item(attr_df):
    """
    0 male/female   0-1
    1-3 human color 0-1[]
    4-8 age 0-1[]
    9-11 58 hair color black/blond/brown/gray 0-1 or 0
    12 28-33 bald 秃forehead type    0-1
    13-15 eyewear no/eye/sun    0-1
    16 45-46 mustache/beard 0-1
    17-18 smiling/unhappy   0-1 or 0
    19 chubby weight big
    20-24 blurry/flash/outdoor...
    25-27 hair type 0-1
    34-35 Eyebrows 0-1
    36-37 eye type  0-1
    38-39 nose  0-1 or 0
    40 厚嘴唇
    41-44 mouth and teeth not visible 0-1
    47-48 下巴
    49 hat
    50-52 face type 0-1
    53-54 pic type
    55-56 beautiful
    57 indian
    59 眼袋
    60-61 64-67 Makeup化妆
    62-63 skin
    68 type face quangu
    69 eye color brown
    70-72 装饰 earrings/necktie/necklace
    :param attr_df:
    :return:
    """
    zero_add = [[0], [9, 10, 11, 58], [17, 18]]
    add_attr = ["female", "other_hair", "calm"]
    # ones_sum = [[1, 2, 3], [4, 5, 6, 7, 8], [9, 10, 11, 58], [12, 28, 29, 30, 31, 32, 33], [13, 14, 15], [16, 45, 46],
    #             [17, 18], [25, 26, 27], [34, 35], [41, 42, 43, 44], [50, 51, 52]]

    for i in zero_add:
        # print(attr_df[i])
        male = attr_df[i].sum()
        if male < 1 / 3:
            # add =
            print(attr_df[i])
        # if attr_df[i]

    return attr_df


def find_entity_text(nlp, sentence, name):
    output_res = nlp.annotate(sentence, properties={'annotators': 'kbp'})
    try:
        output = json.loads(output_res)
    except:
        print(output_res)
        return []
    relations = ['per:alternate_names', 'per:cause_of_death', 'per:charges', 'per:children', 'per:cities_of_residence',
                 'per:city_of_birth', 'per:city_of_death', 'per:countries_of_residence', 'per:country_of_birth',
                 'per:country_of_death', 'per:date_of_birth', 'per:date_of_death', 'per:employee_of', 'per:member_of',
                 'per:origin', 'per:other_family', 'per:parents', 'per:religion', 'per:schools_attended',
                 'per:siblings', 'per:spouse', 'per:stateorprovince_of_birth', 'per:stateorprovince_of_death',
                 'per:stateorprovinces_of_residence', 'per:title']
    result = []
    for i in output['sentences']:
        for k in i['kbp']:
            if k['relation'] in relations:
                # print(k["subject"], k["relation"], k["object"])
                if ((set(k["subject"].split(' ')) & set(name.split('_'))) or (
                        k["subject"] in ["She", "He", "she", "he"])):
                    result.append([name, k["relation"], k["object"]])

    return result


if __name__ == '__main__':
    # names = ['Barack_Obama']
    person_name = get_person_name('lfw_att_40_7.1.mat')

    # ! 'born',
    # relations_wiki_en = ['age', 'education', 'alma mater', 'parents', 'occupation']
    # relations_wiki_cn = ['民族父系', '民族母系']
    # relations_baidu_cn = ['职业']
    # relations_answers = ['weight', 'gender', 'ethnic group', 'syndrome', 'character', 'hair color', 'hair length',
    #                      'bald', 'beard', 'eyeglasses', 'impression']

    if os.path.exists("wiki_data.txt") and os.path.getsize("wiki_data.txt") > 0:
        with open(file="wiki_data.txt", mode="r", encoding='utf-8') as f:
            wiki_data = eval(f.read())
    else:
        wiki_data = dict()
    '''
    nlp StanfordCoreNLP
    '''
    # nlp = StanfordCoreNLP(r'E:\stanford-corenlp-latest\stanford-corenlp-4.2.0')
    # or
    # java -Xmx4g -cp "E:\stanford-corenlp-latest\stanford-corenlp-4.2.0\*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000
    nlp = StanfordCoreNLP("http://localhost", port=9000)
    nlp_data = RDF(load=True, file="nlp_data.csv", columns=["name", "relation", "object"])
    print(nlp_data.data.keys())
    # nlp_data.data["object"].replace({' ':'_',',':'_'},inplace=True,regex=True)
    # nlp_data.data["object"].replace({'_+':'_'},inplace=True,regex=True)
    # nlp_data.data["weight"] = 1.0
    # nlp_data.data.drop(labels=["relation"],axis=1,inplace=True)
    # print(nlp_data.data)
    # all_data = RDF(columns=["name", "object", "weight"])
    # print(all_data.data)
    # data = all_data.data.append(nlp_data.data)
    # print(data)
    # data.to_csv("all_data.csv", index=False, header=False)
    # print()
    # all_data.

    # print(nlp_data.data["object"])
    # data =
    index = 0
    for i in tqdm(person_name):
        if wiki_data.get(i, False):
            if not wiki_data[i].get("text_wiki_en",False):
                continue
            for k in wiki_data[i]["text_wiki_en"]:
                # text = "Obama was born in Honolulu, Hawaii."
                nlp_data_item = find_entity_text(nlp, k.replace('\n', ''), i)
                if nlp_data_item:
                    nlp_data.add(nlp_data_item)
                # print(i, nlp_data_item)
        if index % 1000:
            nlp_data.save(file="nlp_data.csv", columns=["name", "relation", "object"])
        index += 1
    '''
    find sentence in wiki english
    '''
    # index = 0
    # for i in tqdm(person_name):
    #     if not wiki_data.get(i, False):
    #         # print(i)
    #         wiki_data_item = get_entity_wiki_en(i, relations=[])
    #         # print(wiki_data_item)
    #         wiki_data.update(wiki_data_item)
    #     # print(wiki_data)
    #         # wiki_data_item,cn_name = get_entity_wiki_cn(person_name_item)
    #         # if cn_name != "":
    #         #     get_entity_baidu_cn(cn_name)
    #         # break
    #     if index % 100 == 0:
    #         with open(file="wiki_data.txt", mode='w',encoding='utf-8') as f:
    #             f.write(str(wiki_data).encode('utf-8',errors='ignore').decode('utf-8'))
    #     index += 1
    '''
    RDF  save lfwa+ dataset
    '''
    # RDF_data = RDF(load=False)
    # RDF_data = get_entity_lfw(RDF_data,person_name)
    # print(RDF_data.data)
    # RDF_data.save()

    # for person_name_item in person_name:
    #     print(person_name_item)
    #     get_entity_lfw(person_name_item)
    #     break
    # person_name_item = "Barack_Obama"
    # wiki_data_item,cn_name = get_entity_wiki_cn(person_name_item)
    # if cn_name != "":
    #     get_entity_baidu_cn(cn_name)
    # break

    # entity = list()
    # for i in relations:
    #     entity.append(get_entity(i))
    # print(entity)

    # search_answers('Barack_Obama')
    # for i in names:
    #     search(name = i)
