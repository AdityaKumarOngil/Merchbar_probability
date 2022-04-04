import warnings                                  # 'do not disturbe' mode
warnings.filterwarnings('ignore')

import pandas as pd
import os
# import numpy as np

# def get_attributes(df):
#     lst1 = []
#     for i in df.columns:
#         if df[i].dtype.name == 'int64' or df[i].dtype.name == 'float64' or df[i].dtype.name == 'category':
#             lst1.append(i)
#     return(lst1)

def crosstab_probability(df, attr_col_lst, attr_ind_lst):
    data = pd.crosstab(index=[df[x] for x in attr_ind_lst], columns=[df[y] for y in attr_col_lst], margins=True, normalize= 'index', dropna=True)
    return (data)

df1 = pd.read_excel('merchbar_artist_dashboard_31.03.22.xlsx')

#Enter column names that have catgorical values
# arr1 = ['brand', 'in_stock', 'genre', 'color', 'product_type', 'category', 'sub_category', 'price_tier.x', 'price_tier.y']

# for i in arr1:
#     df1[i] = pd.Categorical(df1[i])

# attr = get_attributes(df1)

def get_probability(df, brand, subcategory, min_revenue, max_revenue):
    lst_patch = df[(df['sub_category']==subcategory)]['brand'].unique()
    genre = df[df['brand']==brand]['genre'].unique()[0]
    if brand in lst_patch:
        df = df[df['genre']==genre] 
        df = df[(df['sub_category']==subcategory)]
        prob_count = 2
        cond_count = 1

        prob_lst = [None]*prob_count
        cond_lst = [None]*cond_count

        prob_lst[0] = ['sub_category']
        prob_lst[1] = ['Revenue', [min_revenue, max_revenue]]

        # cond_lst[0] = ['genre']
        cond_lst[0] = ['brand']

        prob_attr = []
        cond_attr = []

        str1 = ''
        prob1 = 1
        for i in range(0, prob_count):
            if i != prob_count-1:
                add_str = '&'
            else:
                add_str = ''
            if df[prob_lst[i][0]].dtype.name == 'int64' or df[prob_lst[i][0]].dtype.name == 'float64':
                # if len(prob_lst[i][1]) == 2:
                #     str1 = str1+str(prob_lst[i][0])+' >= '+str(prob_lst[i][1][0])+' & '+str(prob_lst[i][0])+' <= '+str(prob_lst[i][1][1])+' '+add_str+' '
                # else:
                #     str1 = str1+str(prob_lst[i][0])+' == '+str(prob_lst[i][1][0])+' '+add_str+' '
                small_df = df[df[prob_lst[i][0]] > prob_lst[i][1][0]].reset_index()
                small_df = small_df[small_df[prob_lst[i][0]] < prob_lst[i][1][1]].reset_index()
                prob1 = prob1 * (len(small_df)/len(df))
            else:
                if len(prob_lst[i]) == 2:
                    for j in range (len(prob_lst[i][1])):
                        str1 = str1+str(prob_lst[i][0])+' == '+str(prob_lst[i][1][j])+' '+add_str+' '
                else:
                    prob_attr.append(prob_lst[i][0])

        # if str1 != '':
        #     if str1[-2]=='&':
        #         try:
        #             str1 = str1[0 : -2 : ] + str1[-2 + 1 : :]
        #         except:
        #             pass

        str2 = ''
        for i in range(0, cond_count):
            if i != cond_count-1:
                add_str = '&'
            else:
                add_str = ''
            if df[cond_lst[i][0]].dtype.name == 'int64' or df[cond_lst[i][0]].dtype.name == 'float64':
                if len(cond_lst[i][1]) == 2:
                    str2 = str2+str(cond_lst[i][0])+' >= '+str(cond_lst[i][1][0])+' & '+str(cond_lst[i][0])+' <= '+str(cond_lst[i][1][1])+' '+add_str+' '
                else:
                    str2 = str2+str(cond_lst[i][0])+' == '+str(cond_lst[i][1][0])+' '+add_str+' '
            else:
                if len(cond_lst[i]) == 2:
                    for j in range (len(cond_lst[i][1])):
                        str2 = str2+str(cond_lst[i][0])+' == '+str(cond_lst[i][1][j])+' '+add_str+' '
                else:
                    cond_attr.append(cond_lst[i][0])

        if str2 != '':
            try: 
                if str2[-2]=='&':
                    try:
                        str2 = str2[0 : -2 : ] + str2[-2 + 1 : :]
                    except:
                        pass
            except:
                pass

        # str3 = str1+' & '+str2
        str3 = str2
        # if str3[-2]=='&':
        #     str3 = str3[0 : -2 : ] + str3[-2 + 1 : :]
        # if str3[1] == '&':
        #     str3 = str3[0 : 1 : ] + str3[1 + 1 : :]
        if str3 == '':
            x = crosstab_probability(df, prob_attr, cond_attr ).loc[brand][subcategory] * prob1
        else:
            x = crosstab_probability(df.query(str3), prob_attr, cond_attr ).loc[brand][subcategory] * prob1
        output = brand+' is already selling '+subcategory+' and the likelihood that they are generating a revenue between $'+str(min_revenue)+' and $'+str(max_revenue)+' is: '+str(round(x*100, 2))+'%'
    elif brand not in lst_patch:
        new_df = pd.DataFrame(columns = df.columns)
        for ii in lst_patch:
            new_temp = df[df['brand']==ii]
            new_df = pd.concat([new_df, new_temp])  #[(df['brand']== t for t in lst_patch) & (df['Revenue']>=min_revenue)]
        for cols in df.columns:
            new_df[cols] = new_df[cols].astype(df[cols].dtype.name)
        check_df = df[df['brand']==brand]
        new_df = new_df[new_df['genre']==genre]
        check_df = df[df['brand']==brand]
        sum1 = new_df['Revenue'].median()
        sum2 = check_df['Revenue'].sum()
        ratio = sum1/sum2
        if ratio > 1:
            min_revenue1 = min_revenue * new_df['Revenue'].median()
            max_revenue1 = max_revenue * new_df['Revenue'].median()
            prob_count = 2
            cond_count = 1
            
            prob_lst = [None]*prob_count
            cond_lst = [None]*cond_count

            prob_lst[0] = ['sub_category']
            prob_lst[1] = ['Revenue', [min_revenue1, max_revenue1]]            
        else:
            prob_count = 2
            cond_count = 1
            
            prob_lst = [None]*prob_count
            cond_lst = [None]*cond_count

            prob_lst[0] = ['sub_category']
            prob_lst[1] = ['Revenue', [min_revenue, max_revenue]]

        cond_lst[0] = ['genre']

        prob_attr = []
        cond_attr = []

        str1 = ''
        prob1 = 1
        for i in range(0, prob_count):
            if i != prob_count-1:
                add_str = '&'
            else:
                add_str = ''
            if new_df[prob_lst[i][0]].dtype.name == 'int64' or new_df[prob_lst[i][0]].dtype.name == 'float64':
                # if len(prob_lst[i][1]) == 2:
                #     str1 = str1+str(prob_lst[i][0])+' >= '+str(prob_lst[i][1][0])+' & '+str(prob_lst[i][0])+' <= '+str(prob_lst[i][1][1])+' '+add_str+' '
                # else:
                #     str1 = str1+str(prob_lst[i][0])+' == '+str(prob_lst[i][1][0])+' '+add_str+' '
                small_df = new_df[new_df[prob_lst[i][0]] > prob_lst[i][1][0]].reset_index()
                small_df = small_df[small_df[prob_lst[i][0]] < prob_lst[i][1][1]].reset_index()
                prob1 = prob1 * (len(small_df)/len(new_df))
            else:
                if len(prob_lst[i]) == 2:
                    for j in range (len(prob_lst[i][1])):
                        str1 = str1+str(prob_lst[i][0])+' == '+str(prob_lst[i][1][j])+' '+add_str+' '
                else:
                    prob_attr.append(prob_lst[i][0])

        # if str1 != '':
        #     if str1[-2]=='&':
        #         try:
        #             str1 = str1[0 : -2 : ] + str1[-2 + 1 : :]
        #         except:
        #             pass

        str2 = ''
        for i in range(0, cond_count):
            if i != cond_count-1:
                add_str = '&'
            else:
                add_str = ''
            if new_df[cond_lst[i][0]].dtype.name == 'int64' or new_df[cond_lst[i][0]].dtype.name == 'float64':
                if len(cond_lst[i][1]) == 2:
                    str2 = str2+str(cond_lst[i][0])+' >= '+str(cond_lst[i][1][0])+' & '+str(cond_lst[i][0])+' <= '+str(cond_lst[i][1][1])+' '+add_str+' '
                else:
                    str2 = str2+str(cond_lst[i][0])+' == '+str(cond_lst[i][1][0])+' '+add_str+' '
            else:
                if len(cond_lst[i]) == 2:
                    for j in range (len(cond_lst[i][1])):
                        str2 = str2+str(cond_lst[i][0])+' == '+str(cond_lst[i][1][j])+' '+add_str+' '
                else:
                    cond_attr.append(cond_lst[i][0])
        if str2 != '':
            try: 
                if str2[-2]=='&':
                    try:
                        str2 = str2[0 : -2 : ] + str2[-2 + 1 : :]
                    except:
                        pass
            except:
                pass
        str3 = str2

        # if str3[-2]=='&':
        #     str3 = str3[0 : -2 : ] + str3[-2 + 1 : :]
        # if str3[1] == '&':
        #     str3 = str3[0 : 1 : ] + str3[1 + 1 : :]

        if str3 == '':
            x = crosstab_probability(new_df, cond_attr, prob_attr).loc[subcategory][genre] * prob1
        else:
            x = crosstab_probability(new_df.query(str3), cond_attr, prob_attr).loc[subcategory][genre] *prob1
        output = 'The likelihood of '+brand+' selling '+subcategory+' for a revenue between $'+str(min_revenue)+' and $'+str(max_revenue)+' is: '+str(round(x*100, 2))+'%'
    return(output)

input1 = input('Enter the band of interest: ')
input2 = input('Enter the specific merchandise of interest: ')
input3 = float(input('Enter lower limit of revenue: '))
input4 = float(input('Enter upper limit of revenue: '))

print(get_probability(df1, input1, input2, input3, input4))
