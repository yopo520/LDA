#coding: utf-8
import pandas as pd
import fool

#-------------------  第一步 读取数据  ------------------------
f = open('正面评论.csv',encoding='utf-8')
df = pd.read_csv(f)
print(df.shape)         #查看数据维度
print(df.head())        #查看前几行数据

#-------------------  第二步 中文分词  -----------------------
import jieba
import jieba.posseg as psg

#格式转换 否则会报错  'float' object has no attribute 'decode'
df = pd.DataFrame(df['comment'].astype(str))

def chinese_word_cut(mytext):
    seg_list = fool.cut(mytext)
    return ' '.join('%s' %i for i in seg_list)

#增加一列数据
df['content_cutted'] = df['comment'].apply(chinese_word_cut)
df.content_cutted.head()

#-------------------  第三步 计算TF-IDF值  --------------------- 
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

#设置特征数
n_features = 30

stopwords=[i.strip() for i in open("stopwords.txt",encoding="utf8")]

tf_vectorizer = TfidfVectorizer(strip_accents = 'unicode',
                                max_features=n_features,#最常见的30个词
                                stop_words=stopwords,
                                max_df = 0.99,
                                min_df = 0.002) #去除文档内出现几率过大或过小的词汇
tf = tf_vectorizer.fit_transform(df.content_cutted)

print(tf.shape)
print(tf)

#---------------------  第四步 LDA分析  ---------------------- 
from sklearn.decomposition import LatentDirichletAllocation

#设置主题数
n_topics = 3

lda = LatentDirichletAllocation(n_components=n_topics,
                                max_iter=100,
                                learning_method='online',
                                learning_offset=50,
                                random_state=0)
lda.fit(tf)

#显示主题数 model.topic_word_
print(lda.components_)
#几个主题就是几行 多少个关键词就是几列 
print(lda.components_.shape)                         

#计算困惑度
print(u'困惑度：')
lda.perplexity(tf,sub_sampling = False)

#主题-关键词分布
def print_top_words(model, tf_feature_names, n_top_words):
    for topic_idx,topic in enumerate(model.components_):    # lda.component相当于model.topic_word_
        print('Topic #%d:' % topic_idx)
        print(' '.join([tf_feature_names[i] for i in topic.argsort()[:-n_top_words-1:-1]]))
        print("")

#定义好函数之后 暂定每个主题输出前20个关键词
n_top_words = 20
tf_feature_names = tf_vectorizer.get_feature_names()
#调用函数
print_top_words(lda, tf_feature_names, n_top_words)


#-------------------  第五步 可视化分析  --------------------- 
import pyLDAvis
import pyLDAvis.sklearn

#pyLDAvis.enable_notebook()

data = pyLDAvis.sklearn.prepare(lda,tf,tf_vectorizer)
#print(data)
pyLDAvis.save_json(data,'正面主题.html')
#显示图形
pyLDAvis.show(data)

#pyLDAvis.save_json(data,'正面主题.pdf')
