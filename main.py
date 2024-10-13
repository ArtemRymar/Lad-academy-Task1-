import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def find_cities_id():
    areas_raw = requests.get("https://api.hh.ru/areas")

    if areas_raw.status_code == 200:
        areas = areas_raw.json()

        russia = next((country for country in areas if country['name'] == 'Россия'), None)

        if russia:
            cities_to_find = ['Нижний Новгород', 'Москва', 'Санкт-Петербург']
            ids_of_cities = {}


            for region in russia['areas']:
                if region['name'] in cities_to_find:
                    ids_of_cities[region['name']] = region['id']
                for city in region['areas']:
                    if (city['name'] in cities_to_find):
                        ids_of_cities[city['name']] = city['id']

            for city in cities_to_find:
                if city not in ids_of_cities:
                    print(f"Город {city} не найден.")
        else:
            print("Страна Россия не найдена.")
    else:
        print(f"Ошибка запроса: {areas_raw.status_code}")

    return(ids_of_cities)


def get_quant_of_vacancies(profession, experience_level, region):
    url = 'https://api.hh.ru/vacancies'
    params = {
        'text' : profession,
        'experience' : experience_level,
        'area' : region,
        'per_page' : 100
    }

    response = requests.get(url, params=params)
    data = response.json()
    return data['found']


if __name__ == '__main__':

    regions = find_cities_id()
    


    professions = ['Data Analyst', 'Data Scientist', 'Data Engineer']

    experience_levels = {
    'Junior': 'noExperience',
    'Middle': 'between1And3',
    'Senior': 'between3And6'
    }


    vacancies_data = []
    for profession in professions:
        for level, exp_code in experience_levels.items():
            for region_name, region_id in regions.items():
                count = get_quant_of_vacancies(profession, exp_code, region_id)
                vacancies_data.append([profession, level, region_name, count])

    df = pd.DataFrame(vacancies_data, columns=['Profession', 'Level', 'Region', 'Vacancies'])
    print(df)

    
    
    fig, axs = plt.subplots(3, 1, sharex=True, figsize=(8,8))
    gr = 0
    for region in df['Region'].unique():
        region_data = df[df['Region'] == region]
        x = np.arange(3)
        multiplier = 0
        width = 0.25
        for level in region_data['Level'].unique():
            level_data = region_data[region_data['Level'] == level]
            offset = width * multiplier
            rects = axs[gr].bar(x + offset, list(level_data['Vacancies']), width, label = level)
            axs[gr].bar_label(rects, padding=3)
            axs[gr].set_ylabel('Количество вакансий')
            axs[gr].set_title(region, fontsize=10)
            axs[gr].set_xticks(x + width, professions)
            axs[gr].spines['top'].set_visible(False)
            multiplier += 1
        
        gr += 1

    fig.legend(experience_levels.keys(), loc='upper right')
    fig.suptitle('Количество вакансий по профессиям и уровням')
    plt.show()



