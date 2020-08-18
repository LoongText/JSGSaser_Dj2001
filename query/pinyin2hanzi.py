from Pinyin2Hanzi import DefaultDagParams
from Pinyin2Hanzi import dag
from Pinyin2Hanzi import simplify_pinyin
from anjuke import pinyin


def pinyin2hanzi(pinyin_list):
    # pip install Pinyin2Hanzi
    dag_params = DefaultDagParams()
    result = dag(dag_params, pinyin_list, path_num=10, log=True)  # 10代表侯选值个数
    for item in result:
        score = item.score
        res = item.path  # 转化结果
        print(score, res)


def hanzi2pinyin():
    #  pip install pinyin4py
    """
    text：待转化的文本
    fmt：设定转换的方式的格式
        df - Default 全拼
        tm - Tone Marks 全拼带音调
        tn - Tone Numbers 全拼带数字形式的音调
        ic - Initial Consonant only 声母
        fl - First Letter 首字母
    sc：Split Character，是否以单个汉字为切割单位的拼音输出字为单位，其中True为单字拆分，False为不拆分。以输入的中文文本的分词为准。
    pp：Polyphone 是否输出无法判断的多音字(词)，其中False为不输出多音字，True为输出多音字
    fuzzy：Puzzy 拼音模糊化
        `0` - 不处理
        `1` - 模糊化 z-zh c-ch s-sh
        `2` - 模糊化 k-g f-h l-n l-r
        `4` - 模糊化 an-ang en-eng in-ing lan-lang uan-uang
    :return: 如果有多个格式选项，返回所有格式的结果。例如调用`convert('南京市 长江 大桥', fmt=[tm,tn,fl], sc=False)`
    """
    converter = pinyin.Converter()
    converter.load_word_file('words.txt')
    print(converter.convert('中华有为', fmt='fl', sc=False, pp=True, fuzzy=0))
    print(converter.convert('中华有为', fmt='df', sc=False, pp=True, fuzzy=0))


if __name__ == '__main__':
    test_list = ['zhong', 'xin']
    # 拼音转规范
    lst_simplified = []
    for item in test_list:
        lst_simplified.append(simplify_pinyin(item))
    print("修正后的拼音为：", lst_simplified)

    pinyin2hanzi(lst_simplified)
