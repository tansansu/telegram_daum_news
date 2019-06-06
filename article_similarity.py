"""
이전 기사들의 제목으로 유사도 계산(doc2vec)
"""

from konlpy.tag import Twitter; pos_tagger = Twitter()
import re
import os


# 단어 토크나이저 함수
def tokenizer(sentence):
    temp = ['/'.join(t) for t in pos_tagger.pos(sentence, norm=True, stem=True)]
    # only Verb, Noun, Adjective
    result = [x for x in temp \
    if re.match(r'([가-힣]+/Noun)|([가-힣]+/Verb)|([가-힣]+/Adjective)', x) != None]

    return(result)


# jaccard 유사도 계산 함수
def jaccard_similarity(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    #print(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return round(float(intersection / union), 4)


# 제목 풀에서의 유사도 계산 함수
def get_similarity(query, candid_list):
    result_sim = []
    for candid in candid_list:
        # 동일 문장 건너 뛰기
        if candid[0] == query:
            continue   
        similarity = jaccard_similarity(query, candid[0])
        result_sim.append([query, candid[1], candid[2], similarity])
    return sorted(result_sim, key=lambda x: x[3], reverse=True)


def judge(path: str, querys: list, threshold: float) -> list:
    # 데이터 로딩
    with open(os.path.join(path, 'article_dump.csv'), 'r') as f:
        tmp = f.readlines()
    dump = [x.replace('\n', '').split('^') for x in tmp]
    # 전처리
    dump_tokens = [(tokenizer(x[0]), x[0], x[2]) for x in dump]
    #print(dump_tokens)
    # 유사도가 높은 기사리스트만 추출
    result = []
    # 유사도 계산
    for i in range(len(querys)):
        sim_result = get_similarity(tokenizer(querys[i][0]), dump_tokens)
        if sim_result[0][3] > threshold:
            #print(querys[i], sim_result[0][3])
            result_tmp = querys[i].copy()
            result_tmp.extend([sim_result[0][1], sim_result[0][3]])
            result.append(result_tmp)
    
    return result
