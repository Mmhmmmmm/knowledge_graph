import json

from stanfordcorenlp import StanfordCoreNLP

# nlp = StanfordCoreNLP(r'E:\stanford-corenlp-latest\stanford-corenlp-4.2.0')
nlp = StanfordCoreNLP("http://localhost", port=9000)

sentence = 'Obama was born in Honolulu, Hawaii.'

output = nlp.annotate(sentence, properties={'annotators': 'kbp'})
output = json.loads(output)
# # print(output)
# # print(type(output))
relations = ['per:alternate_names','per:cause_of_death','per:charges','per:children','per:cities_of_residence','per:city_of_birth','per:city_of_death','per:countries_of_residence','per:country_of_birth','per:country_of_death','per:date_of_birth','per:date_of_death','per:employee_of','per:member_of','per:origin','per:other_family','per:parents','per:religion','per:schools_attended','per:siblings','per:spouse','per:stateorprovince_of_birth','per:stateorprovince_of_death','per:stateorprovinces_of_residence','per:title']

for i in output['sentences']:
    for k in i['kbp']:
        if k['relation'] in relations:
            print(k)
            print(k["subject"],k["relation"],k["object"])
nlp.close()  # Do not forget to close! The backend server will consume a lot memery
