# program is make LFWA+ datasets and en.wanweibaike to knowledge graph 

## file list
- program
    - `main.py` main project function 
    - `nlp.py` just to test nlp api
- data
    - `lfw_att_40/73.mat` LFWA+ datasets file HDF type
    - `lfw_att_40/63_7.1.mat` LFWA+ datasets file V7.1 type and change space to _
    - `person_name.txt` person name in LFWA+ datasets
    - `data.csv` knowledge graph in LFWA+
    - `wiki_data.txt` text on https://en.wanweibaike.com
    - `nlp_data.csv` knowledge graph in wiki_data.txt
    - `all_data.csv` all knowledge graph
    
## quick start

- `class RDF`
  
  - `def __init__(self, load=True, file="data.csv", columns=["name", "attr_name", "weight", "trust"])`
    - `load`:load file in `file`
    - `file`:file path
    - `columns`:file columns
  - `def add(self, insert_data)`
    - `insert_data`:type is list
  - `def distrust(self, name)`
    - :no_entry_sign:not useful
  - `def exist(self, name, attr_name)`
    - :no_entry_sign:not useful
  - `def save(self, file="data.csv", columns=["name", "attr_name", "weight"])`
    - `file`:path to save
    - `columns`:colums to save
  - `def load(self, file="data.csv",)`
    - `file`:path to load
  
- `def search(name)`
  - search html of `name`
  - :no_entry_sign:not useful 
  
- `def find_answers(response)`
  - search answers in `www.answers.com`
  - :no_entry_sign:not useful

- `def get_entity_wiki_en(name, relations)`
  - `name`:name of search
  - `relations`is not useful
  - get basic infor and text from `https://en.wanweibaike.com`

- `def get_entity_baidu_cn(name)`

  - `name`:name of search
  - return infor from `https://baike.baidu.com`

- `def get_person_name(file='lfw_att_40.mat', load_txt=True)`

  - `file`:file name
  - `load_txt`:load from file
  - return `set`of person name

- `def get_entity_lfw(RDF_lfw, name='Abdullah_Gul')`

  - `RDF_lfw`:RDF type object
  - `name`:mast be list
  - return RDF type object

- `def check_item(attr_df)`

  - not useful

- `def find_entity_text(nlp, sentence, name)`

  - `nlp`:StanfordCoreNLP type
  - `sentence`:text from wiki
  - `name`:your wiki person name
  - `per:alternate_names` `per:cause_of_death` `per:charges` `per:children` `per:cities_of_residence` `per:city_of_birth` `per:city_of_death` `er:countries_of_residence` `per:country_of_birth` `per:country_of_death` `per:date_of_birth` `per:date_of_death` `per:employee_of` `per:member_of` `per:origin` `per:other_family` `per:parents` `per:religion` `per:schools_attended` `per:siblings` `per:spouse` `per:stateorprovince_of_birth` `per:stateorprovince_of_death` `per:stateorprovinces_of_residence` `per:title`

- RDF  save lfwa+ dataset

  ```python
  RDF_data = RDF(load=False)
  RDF_data = get_entity_lfw(RDF_data,person_name)
  print(RDF_data.data)
  RDF_data.save()
  ```

- find sentence in wiki english

  ```python
  index = 0
  for i in tqdm(person_name):
  	if not wiki_data.get(i, False):
  		wiki_data_item = get_entity_wiki_en(i, relations=[])
  		wiki_data.update(wiki_data_item)
      if index % 100 == 0:
          with open(file="wiki_data.txt", mode='w',encoding='utf-8') as f:
              f.write(str(wiki_data).encode('utf-8',errors='ignore').decode('utf-8'))
      index += 1
  ```

- sentence nlp

  - console run 

    ```bash
    java -Xmx4g -cp "E:\stanford-corenlp-latest\stanford-corenlp-4.2.0\*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000
    ```

  - code

    ```python
    nlp = StanfordCoreNLP("http://localhost", port=9000)
    nlp_data = RDF(load=True, file="nlp_data.csv", columns=["name", "relation", "object"])
    index = 0
    for i in tqdm(person_name):
        if wiki_data.get(i, False):
            if not wiki_data[i].get("text_wiki_en",False):
                continue
            for k in wiki_data[i]["text_wiki_en"]:
                nlp_data_item = find_entity_text(nlp, k.replace('\n', ''), i)
                if nlp_data_item:
                    nlp_data.add(nlp_data_item)
        if index % 1000:
            nlp_data.save(file="nlp_data.csv", columns=["name", "relation", "object"])
        index += 1
    ```
    
  
- merge all data

  ```python
  nlp_data.data["object"].replace({' ':'_',',':'_'},inplace=True,regex=True)
  nlp_data.data["object"].replace({'_+':'_'},inplace=True,regex=True)
  nlp_data.data["weight"] = 1.0
  nlp_data.data.drop(labels=["relation"],axis=1,inplace=True)
  all_data = RDF(columns=["name", "object", "weight"])
  data = all_data.data.append(nlp_data.data)
  data.to_csv("all_data.csv", index=False, header=False)
  ```

  

