# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 13:44:12 2017
@author: Paul Ogier
This script is adding a few complentary features on pandas
"""
import pandas as pd
import numpy as np
import sys
import stringcleaningtools as sct

# %%

nadict = sct.nadict


# %%
def map_values(myserie, mydict=None):
    '''
    Takes as input a panda Series and a dictionary
    Returns then a cleaned pandas.Series
    Simple implementation of pandas.Series.replace method
    :param myserie: pandas.Series to be cleaned
    :param mydict: pandas.Series used as dictionary
    :return: new pandas.Series with values replaced
    '''
    if mydict is None:
        print('Error: missing dict')
    myserie_cleaned = myserie.replace(nadict)
    myserie_cleaned = myserie_cleaned.replace(mydict)
    possiblevalues = mydict.unique()
    unknownvalues = [c for c in myserie_cleaned.unique() if not c in possiblevalues]
    if len(unknownvalues) > 0:
        print('Unknown values: ')
        print(unknownvalues)
    return myserie_cleaned


# %%
def checkcolumns(newcolumns, referencecolumns, coldict=None):
    '''
    Check the columns of a new dataframe against reference columns expected
    :param newcolumns: newcolumns as given by pandas.Dataframe.columns
    :param referencecolumns: referencecolumns (could be a list)
    :param coldict: optional, default None, dictionary to rename columns
    :return: new column names as pandas.Series
    '''
    newcolumns = pd.Series(newcolumns)
    referencecolumns = pd.Series(referencecolumns)
    if coldict is not None:
        newcolumns = newcolumns.replace(coldict)

    unknownvalues = [c for c in newcolumns if not c in referencecolumns]
    if len(unknownvalues) > 0:
        print('Unknown columns: ')
        print(unknownvalues, '\n')

    missingvalues = [c for c in referencecolumns if not c in newcolumns]
    if len(missingvalues) > 0:
        print('Missing columns: ')
        print(missingvalues, '\n')
    x = newcolumns.value_counts()
    x = x[x > 1]
    if x.shape[0] > 0:
        print('Duplicate Columns: ')
        print(x)
        print('\n')
    return newcolumns


# %%
def checkjointures(myserie, possiblevalues):
    '''
    Check the list of categories in a column against a provided standard list
    :param myserie: pandas.Series to be checked
    :param possiblevalues: list of standard values
    :return: None
    print:
    - if all values are matching, a simple message indicating evrything is correct
     - the percentage of rows and the percentage of unique values matching standard values
     - the number of rows and the number of unique values that are unknown in the standard values
     - example of non-matching values and the number of occurences
    '''
    matchingvalues = myserie[myserie.isin(possiblevalues)]
    unknownvalues = myserie[myserie.isin(possiblevalues) == False]
    if unknownvalues.shape[0] == 0:
        print('100% of values match')
    else:
        percentrowmatching = matchingvalues.shape[0] / myserie.shape[0]
        percentvaluematching = matchingvalues.unique().shape[0] / myserie.unique().shape[0]
        print('{:.0%}'.format(percentrowmatching), 'of rows matching for ', '{:.0%}'.format(percentvaluematching),
              'of values matching.')
        print(unknownvalues.shape[0], 'rows unknowns for ', unknownvalues.unique().shape[0], ' unknown unique values')
        print('Example unknowns:')
        print(unknownvalues.value_counts().iloc[:10])


# %%
def getunknownvalues(myserie, possiblevalues):
    '''
    return unique values from a pandas.Series that are unknown in a list of standard values
    :param myserie: pandas.Series to be checked
    :param possiblevalues: list of standard values
    :return: unknown values as a list
    '''
    myserie = pd.Series(myserie)
    unknownvalues = myserie[myserie.isin(possiblevalues) == False].unique().tolist()
    if len(unknownvalues) == 0:
        return None
    else:
        return unknownvalues


# %%
def getmatchingvalues(myserie, possiblevalues):
    '''
    return unique values from a pandas.Series that are matching a list of standard values
    :param myserie: pandas.Series to be checked
    :param possiblevalues: list of standard values
    :return: matching values as a list
    '''
    myserie = pd.Series(myserie)
    matchingvalues = myserie[myserie.isin(possiblevalues)].unique().tolist()
    if len(matchingvalues) == 0:
        return None
    else:
        return matchingvalues

# %%
def checkuniqueid(myserie):
    '''
    check if each value in a pandas.Series is unique
    :param myserie: pandas.Series to be checked
    :return: boolean
    '''
    if myserie.unique().shape[0] == myserie.shape[0]:
        return True
    else:
        print('{:.0%}'.format(myserie.unique().shape[0] / myserie.shape[0]), ' of values unique')
        return False


# %%
def checkna(myserie):
    '''
    counts the occurence of null values in a pandas.Series
    :param myserie: pandas.Series to be checked
    :return: dict, number and percentage of null values 
    '''
    mydict = {}
    mydict['nanValues'] = myserie.isnull().sum()
    mydict['percentNonNull'] = '{:.0%}'.format(1 - myserie.isnull().sum() / myserie.shape[0])
    return mydict


# %%
def summarize(X):
    '''
    
    :param X: DataFrame or Serie
    :return: print summarize on screen as a Dataframe
    '''
    if type(X) == pd.core.frame.DataFrame:
        return __summarize_df__(X)
    else:
        return __summarize_serie__(X)


# %%
def __summarize_df__(mydf):
    result = pd.DataFrame(
        index=['nanValues', 'percentNonNull', 'medianValue', 'minValue', 'maxValue', 'distinctValues', 'percentUnique',
               'exampleValues'],
        columns=mydf.columns)
    for c in mydf.columns:
        result[c] = __summarize_serie__(mydf[c])
    return result


# %%
def __summarize_serie__(myserie):
    '''
    Return a Serie with describing values (nan, unique,..)
    :param myserie: series
    :return: series
    '''
    #simple check to see if serie is a date
    if 'date' in myserie.name.lower():
        a = __describedate__(myserie)
        if a is not None:
            return a
    try:
        #then check to see if serie is a numeric serie
        myserie = myserie.astype(float)
        return __describenum__(myserie)
    except:
        #consider serie as a categorical
        return __describecat__(myserie)


# %%
def __describenum__(myserie):
    '''
    :param myserie: pandas.Series containing numerical values
    :return: number of nan values, minvalue, max value
    '''
    mydict = checkna(myserie)
    mydict['medianValue'] = myserie.dropna().median()
    mydict['minValue'] = myserie.dropna().min()
    mydict['maxValue'] = myserie.dropna().max()
    return pd.Series(mydict, name=myserie.name)


# %%
def __describecat__(myserie):
    '''
    
    :param myserie: pandas.Series containing numerical values
    :return: number of nan values, distinct values, percentage of unique values, examples
    '''
    mydict = checkna(myserie)
    mydict['distinctValues'] = myserie.unique().shape[0]
    mydict['percentUnique'] = '{:.0%}'.format(myserie.unique().shape[0] / myserie.shape[0])
    mydict['exampleValues'] = list(myserie.value_counts(dropna=False).index[:3])
    return pd.Series(mydict, name=myserie.name)


# %%
def __describedate__(myserie):
    '''
    
    :param myserie: pandas.Series containing dates values
    :return: number of nan values, minvalue, max value
    '''
    try:
        myserie = sct.convert_str_to_date(myserie)
    except:
        try:
            myserie = pd.to_datetime(myserie)
        except:
            return None
    mydict = checkna(myserie)
    mydict['maxValue'] = myserie.dropna().max()
    mydict['minValue'] = myserie.dropna().min()
    s = pd.to_timedelta(myserie.dropna() - myserie.dropna().min(), unit='ms').median()
    s = pd.to_datetime(myserie.dropna().min() + s)
    mydict['medianValue'] = s
    return pd.Series(mydict, name=myserie.name)


# %%
def generate_sample_dataframe(nrows=5):
    '''
    generate a sample dataframe
    :param nrows: number of rows of the dataframe
    :return: A pandas.DataFrame
    -float_col
    -float_withna_col
    -date_col
    -cat_col
    -parentcat_col
    -mixed_col
    
    '''
    import numpy as np
    df = pd.DataFrame(np.random.random((nrows, 1)))
    df.columns = ['float_col']
    df['float_col_hasna'] = np.random.choice([-1.0, 0.0, 0.7, 2.0, 3.0, np.nan], size=nrows)

    ##
    a = pd.datetime.today()
    d = []
    for c in range(nrows):
        delta = '{:.0f}'.format(np.random.uniform(-180, +180))
        b = b = a + pd.Timedelta(delta + ' days')
        d.append(b)
    df['date_col'] = d
    df['date_col'] = pd.to_datetime(df['date_col'].dt.date)
    if nrows > 2:
        df.loc[2, 'date_col'] = pd.to_datetime(np.nan)
    ###
    df['cat_col'] = np.random.choice(['foo', 'bar', 'baz', None], size=nrows)
    
    df['parentcat_col'] = df['cat_col'].replace({'foo': 'bing', 'bar': 'bing', 'baz': 'weez'})
    df['parentcat_col'] = df['parentcat_col'].fillna('weez')

    df['mixed_col'] = np.random.choice([1, 'foo', 2, 4.5, 'bar', pd.datetime.today(), None], size=nrows)

    return df


# %%
def aggregateby_category(s):
    '''
    This function should be applied on a grouped by data
    :param s: the groupbedby serie
    :return: the most common value (not na)
    example: gb['cat'].apply(lambda r:aggregateby_category(r))
    '''
    s = s.dropna()
    if len(s) == 0:
        return None
    else:
        return s.value_counts().index[0]


# %%
def aggregateby_value(s, aggfunc=None, isdate=False, dropna=True):
    '''
    This function should be applied on a grouped by data
    :param s: the groupedby serie
    :param aggfunc: aggregation function such as np.min
    :param isdate: if the serie is a date, default Faulse
    :param dropna: should we drop na values defautl True
    :return: the return of the aggfunc function
    '''
    if s.isnull().sum() > 0 and dropna == False:
        return None
    s = s.dropna()
    if len(s) == 0:
        return None
    if isdate:
        if aggfunc == np.min or aggfunc == np.max:
            return aggfunc(s)
        else:
            r = aggfunc(pd.to_timedelta(s - s.min(), unit='ms'))
            return pd.to_datetime(s.min() + r)
    else:
        return aggfunc(s)
        # %%
