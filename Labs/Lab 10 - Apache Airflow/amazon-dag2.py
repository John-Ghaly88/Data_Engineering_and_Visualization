



import requests
from bs4 import BeautifulSoup
import sys
import os 

sys.path.insert(0,os.path.abspath(os.path.dirname(__file__)))

import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd 
import re 
import seaborn as sns 
import datetime
amazon_url = f'https://www.amazon.eg/s?k=iphone&ref=nb_sb_noss_2'
from airflow import DAG
from airflow.operators.python_operator import PythonOperator


default_args = {
    'owner': 'JOHN GHALY',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    # 'start_date':datetime(2020,12,25)
}

dag = DAG(
    dag_id='web_scraping_dag',
    default_args=default_args,
    description='A demo for airflow using bs4 lib',
    schedule_interval='@once',

)



	
def extract_data(**kwargs):
    response= requests.get(amazon_url)
    amazon_soup = BeautifulSoup(response.content,'lxml')
    print(amazon_soup.prettify()[:1000])
    items = amazon_soup.find_all('div',{'class':'a-section a-spacing-none'})
    prices = np.array([])
    titles = np.array([])

    for item in items: 
    
        price = item.find('span',{'class':'a-price-whole'})
        if price is None:
            continue
        price = int(re.sub('[,.]','',price.text).strip('\u200e'))
        title = item.find('span',{'class':'a-size-base-plus a-color-base a-text-normal'}).text
        print(title)
        print(price)
        prices=np.append(prices,price)
        titles=np.append(titles,title)
    df = pd.DataFrame({
        'Titles' :titles,
        'Prices':prices
    })
    return df; 


def visualize_date(**context):
    df = context['task_instance'].xcom_pull(task_ids='extract')
    plt.figure(fig_size=(10,10))
    sns.scatterplot(df.Prices)
    plt.savefig(f'visuals{datetime.datetime.now()}.png')
    plt.close()




t1=PythonOperator(
    task_id='extract',
    provide_context=True,
    python_callable=extract_data,
    dag=dag
)

t2=PythonOperator(
    task_id='visualize',
    provide_context=True,
    python_callable=visualize_date,
    dag=dag
)

t1>>t2