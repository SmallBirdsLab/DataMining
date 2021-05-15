'''初始化数据集，返回事务列表，每个事务包含若干项'''
def init_data_set():
    # data_set = [['l1', 'l2', 'l5'],
    #             ['l2', 'l4'], 
    #             ['l2', 'l3'],
    #             ['l1', 'l2', 'l4'], 
    #             ['l1', 'l3'], 
    #             ['l2', 'l3'],
    #             ['l1', 'l3'], 
    #             ['l1', 'l2', 'l3', 'l5'], 
    #             ['l1', 'l2', 'l3']]
    data_set = [['牛肉', '鸡肉', '牛奶'],
                ['牛肉', '奶酪'], 
                ['靴子', '奶酪'],
                ['牛肉', '鸡肉', '奶酪'], 
                ['牛肉', '鸡肉', '牛奶', '奶酪', '衣服'], 
                ['鸡肉', '牛奶', '衣服'],
                ['鸡肉', '衣服', '牛奶']]
    # data_set = [['苹果','香蕉','鸭梨'],
    #             ['橘子','葡萄','苹果','哈密瓜','火龙果'],
    #             ['香蕉','哈密瓜','火龙果','葡萄'],
    #             ['橘子','橡胶'],
    #             ['哈密瓜','鸭梨','葡萄']]
    return data_set

'''创建频繁候选1项集集合并返回'''
def create_C1(T):
    C1 = set()
    for t in T:                          # 遍历事务集T里的每一事务
        for item in t:                   # 遍历事务的项
            item_set = frozenset([item]) # 列表长度不可变才能放入集合
            C1.add(item_set)
    return C1

'''Fk-1作为种子集合产生Ck，满足Ck的任意(k-1)子集都在Fk-1中'''
def candidate_gen(Fksub1, k):
    Ck = set()
    len_Fksub1 = len(Fksub1)
    list_Fksub1 = list(Fksub1)                              # Fk-1转换为列表以便有序查找
    for i in range(len_Fksub1):
        for j in range(i, len_Fksub1):                      # 不重复地选出待合并的项集f1，f2
            f1 = list(list_Fksub1[i])
            f2 = list(list_Fksub1[j])
            f1.sort()
            f2.sort()                                       # 项集转换为列表后排序，以便比较是否只有最后一项不同
            if f1[0:k-2] == f2[0:k-2] and f1[-1] != f2[-1]: # 找出只有最后一项不同的频繁项目集f1、f2
                c = list_Fksub1[i] | list_Fksub1[j]         # 合并： f1、f2生成新项集c

                is_add = 1   
                for item in c:                              # 剪枝： 存在c的(k-1)子集不是频繁项集（不在Fk-1中），就不添加c
                    if((c - frozenset([item])) not in Fksub1):
                        is_add = 0
                        break
                if(is_add == 1):
                    Ck.add(c)
    return Ck

'''计算Ck在数据集T中支持度生成频繁k项集集合Fk，并存储Fk的支持度'''
def generate_Fk_by_Ck(T, Ck, min_support, support_data):
    c_count = {}                     # Ck里候选项集出现次数的计数器，字典结构，键：候选项c，值：出现次数
    for t in T:                      # 遍历所有事务
        for c in Ck:                 # 遍历Ck
            if c.issubset(t):        # c所有元素是否都在t中
                if c in c_count:     # 计数器对应加一
                    c_count[c] += 1
                else:
                    c_count[c] = 1
    
    t_num = len(T)
    Fk = set()
    for c in c_count:
        if(c_count[c] / t_num >= min_support):
            Fk.add(c)
            support_data[c] = c_count[c] / t_num
    return Fk

'''
参数： 数据集T，最小支持度min_support
返回：频繁项集集合列表F，所有频繁项集的支持度support_data
'''
def Apriori(T, min_support):
    F = []                                                   # 所有频繁项集集合，列表结构，存集合Fk
    support_data = {}                                        # 所有频繁项集的支持度，字典结构，键：频繁项集，值：支持度

    C1 = create_C1(T)                                        # 对事务集T进行第一轮搜索得到频繁候选1项集C1
    F1 = generate_Fk_by_Ck(T, C1, min_support, support_data) # C1满足最小支持度的项集组合得到F1并跟新support_dat
    
    k = 2                                                    
    Fksub1 = F1.copy()                                       
    F.append(Fksub1)                                             # 浅copy，第一层是创建新地址
    while(Fksub1):                                               # k初始为2，Fk-1为F1，直到Fk为空循环结束
        Ck = candidate_gen(Fksub1, k)                            # Fk-1合并剪枝得到候选Ck
        Fk = generate_Fk_by_Ck(T, Ck, min_support, support_data) # Ck支持度筛选得到Fk并跟新support_dat
        k += 1                                                   # 跟新k和Fk-1
        Fksub1 = Fk.copy()                                       
        F.append(Fksub1)
    return F, support_data

'''
频繁项集fk生成的关联规则中：
利用关联规则后件的向下封闭属性，后件有m项的后件集合Hm生成后件有m+1项的后件集合Hm+1
并判断是否满足fk的关联规则
如此递归
'''
def ap_genRules(fk, k, Hm, m, support_data, min_conf):
    if(k > m + 1 and Hm):             # 递归终止条件
        HmAdd1 = candidate_gen(Hm, m) # 满足Hm+1的任意m项子集都在Hm中
        for h in HmAdd1:
            if(support_data[fk] / support_data[fk - h] >= min_conf):
                print(list(fk - h), ' => ', list(h), '\tsupport: ', support_data[fk], '\tconf: ', support_data[fk] / support_data[fk - h])
            else:
                HmAdd1 -= h
        ap_genRules(fk, k, HmAdd1, m+1, support_data, min_conf)

'''生成关联规则'''
def genRules(F, support_data, min_conf):
    # print('F: ', F, ' len: ', len(F))
    # F是频繁项集集合的列表，最后必有一个空集合，所以频繁k项集k的取值是[1, len(F))
    for k in range(1, len(F)): # 频繁k项集集合：F[k-1] 例：{frozenset({'l5', 'l1', 'l2'}), frozenset({'l3', 'l1', 'l2'})}
        for fk in F[k-1]:      # 频繁k项集：    fk     例： frozenset({'l5', 'l1', 'l2'})
            # print('freq_set: ', freq_set, ' k: ', k)
            H1 = set()         # 存关联规则1-后件
            for item in fk:    # 每个频繁k项集中的一项，都可能是关联规则1-后件
                # 满足 fk.support / (fk - item).support >= min_conf 就输出后件1项的关联规则
                if(fk - frozenset([item]) and support_data[fk] / support_data[fk - frozenset([item])] >= min_conf):
                    print(list(fk - frozenset([item])), ' => ', list(frozenset([item])), '\tsupport: ', support_data[fk], '\tconf: ', support_data[fk] / support_data[fk - frozenset([item])])
                    H1.add(frozenset([item]))
            # print('H1: ', H1)
            ap_genRules(fk, k, H1, 1, support_data, min_conf) # 利用后件的向下封闭属性继续输出后件多项的关联规则

if __name__ == "__main__":
    min_support = 0.3
    min_conf = 0.8
    T = init_data_set() # 数据集以列表结构存储
    F, support_data = Apriori(T, min_support)
    for Fk in F:        # 频繁k项集集合Fk的列表
        if(Fk):
            print ("="*50)
            print ("frequent " + str(len(list(Fk)[0])) + "-itemsets")
            print ("="*50)
            for fk in Fk:
                print (list(fk), '\tsupport: ', support_data[fk])
    print('\nRules:')
    genRules(F, support_data, min_conf)
