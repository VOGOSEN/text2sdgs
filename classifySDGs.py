from matchNgrams import NgramMatcher
import numpy as np
import pandas as pd
import json

#loading ontology files
with open('sdg2conceptids.json', 'r') as file_:
    sdg2conceptids = [(sdg, set(concepts)) for sdg, concepts in json.load(file_).items()]

with open('id2concept.json', 'r') as file_:
    id2concept = json.load(file_)
    concept_names = np.array([name for idx,name in id2concept.items()])
    concept_ids = np.array([idx for idx,name in id2concept.items()])

#creating a NGram Matcher object
ngram_matcher = NgramMatcher(concept_names,
                             lowercase=True,
                             token_pattern=r'(?u)\b\w+\b',
                             ngram_size=(1, 4))

#function to extract concepts and frequencies from input text
def extract_concepts(text):
    idxs, frequencies = ngram_matcher.match([text])[0]
    ngrams = sorted(zip(concept_ids[idxs], concept_names[idxs], frequencies), key=lambda ng: len(ng[1]), reverse=True)
    final_list_of_ngrams = list()

    for idx, (ngram_id, ngram_name, frequency) in enumerate(ngrams):
        if frequency > 0:
            final_list_of_ngrams.append([ngram_id, ngram_name, frequency])

    return {concept_id: frequency for concept_id, _, frequency in final_list_of_ngrams}

#function to math sdgs and compute relevance based on extracted concepts and frequencies
def match_sdgs(conceptidswithfrequencies):
    n_min_relevant_concept = 1
    sdgs = []
    concept_ids = conceptidswithfrequencies.keys()

    for sdg, sdg_concept_ids in sdg2conceptids:
        relevant_concept_ids = sdg_concept_ids.intersection(concept_ids)

        if relevant_concept_ids and len(relevant_concept_ids) >= n_min_relevant_concept:
            relevance = 0
            #frequency is amplified by concept lenth (num of words)
            for concept_id in relevant_concept_ids:
                relevance += conceptidswithfrequencies.get(concept_id)* len(id2concept[concept_id].split())



            #"one word" concepts are excluded if they come alone, whatever their frequency
            if len(list(map(lambda concept_id: id2concept[concept_id], relevant_concept_ids))) <= 1 and len(id2concept[concept_id].split()) > 1 :
                sdgs.append({'sdg': sdg,
                            'relevance': float(relevance),
                            'concepts': list(map(lambda concept_id: id2concept[concept_id], relevant_concept_ids))})
            elif len(list(map(lambda concept_id: id2concept[concept_id], relevant_concept_ids))) > 1 :
                sdgs.append({'sdg': sdg,
                            'relevance': float(relevance),
                            'concepts': list(map(lambda concept_id: id2concept[concept_id], relevant_concept_ids))})

            
    return sorted(sdgs, key=lambda x: x['relevance'], reverse=True)


#table : fully written SDG goals (for display only)
sdgnumtogoal = ".\SDG_num2goal.csv"
SDGs2goal = pd.read_csv(sdgnumtogoal,sep=';', on_bad_lines='skip')

#input text
text = '''
Our plans go much further than just the turbines offshore. They see us investing in projects and in people — 
from EV charging to green hydrogen — aligned with Scotland’s energy transition plans.  
“This is good business — making disciplined investments and demonstrating what an integrated energy company can do; 
we can’t wait to get to work
'''

#processing

#extract conteps with frequencies and associate sdgs with relevance score     
conceptidswithfrequencies = extract_concepts(text)
sdgs = match_sdgs(conceptidswithfrequencies)
#init output tables
output = pd.DataFrame(columns=['sdg', 'goal', 'score'])
output_with_concepts = pd.DataFrame(columns=['sdg', 'concept'])
        
#populate output tables    
for sdg in sdgs:
    sdg_id = sdg['sdg']
    output = output.append({'sdg': sdg_id, 
                            'goal': SDGs2goal[SDGs2goal['SDG']==sdg_id]['Goals'].reset_index(drop=True)[0], 
                            'score': sdg['relevance']},
                            ignore_index=True)
    
    for concept_ in sdg['concepts']:
        output_with_concepts = output_with_concepts.append({'sdg': sdg['sdg'],
                                                            'concept': concept_},
                                                            ignore_index=True)

#display output tables
print(output)    
    
#save output to csv
output.to_csv('./output/'+"relatedsdgs"+'.csv', index=False, encoding='utf-8-sig')

print("Completed")