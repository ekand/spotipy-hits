import os
import sys
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from pathlib import Path

import typing
from typing import List

import pandas as pd
import datetime

import time
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.common.keys import Keys

# get the project directory
current_file_path = Path(__file__)
project_dir = str(Path(__file__).resolve().parents[2])


def get_list_of_dates(start_date: str, end_date: str) -> List[str]:
    """
    takes dates as a string in format YYYY-mm-dd and
    returns a list of strings in the form YYYY-mm-dd
    note: date should be a thursday
    """
    format_ = '%Y-%m-%d'
    start_datetime = datetime.datetime.strptime(start_date, format_)
    end_datetime = datetime.datetime.strptime(end_date, format_)

    assert start_datetime.weekday() == 3, 'date should be a thursday (3)'
    week_delta = datetime.timedelta(7)
    curr_datetime = start_datetime

    dates = [datetime.datetime.strftime(curr_datetime, format_)]
    while curr_datetime < end_datetime:
        curr_datetime += week_delta
        dates.append(datetime.datetime.strftime(curr_datetime, format_))
    return dates


def generate_url(date: str) -> str:
    """
    generate a url for the download, given a date string in format YYYY-mm-dd"""
    base_url = 'https://www.rollingstone.com/charts/albums/'
    url = base_url + date + '/'
    return url


def save_canned_soup(soup, date: str = 'YYYY-mm-dd') -> None:  # soup is type bs4 soup
    """
    given a soup object and a date string, saves a text file of a string representation
    of the soup object.
    Filepath of the save will be project_dir/data/raw/canned_soup_of_rs_200_albums_YYYY_mm_dd.txt'
    """
    canned_soup = str(soup)

    base_file_path = project_dir + '/data/raw/'
    file_name = 'canned_soup_of_rs_200_albums_' + date + '.txt'
    file_path = base_file_path + file_name

    assert not os.path.exists(file_path), "file already exists, write operation canceled"
    with open(file_path, "w") as f:
        f.write(canned_soup)


def save_canned_soup_to_data_raw(soup, curr_date):
    """
    saves a soup object as a text file.
    directory: project_dir + '/data/raw/'
    file_name format: 'canned_soup_of_rs_200_albums_' + date_string + '.txt'
    """
    canned_soup = str(soup)
    format_='%Y-%m-%d'
    base_file_path = project_dir + '/data/raw/'
    date_string = datetime.datetime.strftime(curr_date, format_)
    file_name = 'canned_soup_of_rs_200_albums_' + date_string + '.txt'
    file_path = base_file_path + file_name
    assert not os.path.exists(file_path), "file already exists, write operation canceled"
    with open(file_path, "w") as f:
      f.write(canned_soup)


def get_multiple_rs_200_albums_pages(start_date: str, end_date: str) -> None:
    """
    downloads and saves multiple pages of the rolling stone top 200 albums list
    for every week within the dates specified.
    Note: start date must be a thursday
    saves files for each week in form: 'canned_soup_of_rs_200_albums_' + date_string + '.txt'
    saves files in location: project_dir + '/data/raw/'
    """
    dates = get_list_of_dates(start_date, end_date)
    for date in dates:
        url = generate_url(date)
        soup = get_rs_200_albums_interactive(url)
        save_canned_soup(soup, date)
    return


def get_rs_200_albums_interactive(url=None):
    """
    Given a url, returns a beautiful soup object of the website,
    as it is after dismissing a privacy notice and clicking
    load more until all two hundred albums are displayed.
    By default, loads the most current (if no url specified)
    """
    if not url:
        url = 'https://www.rollingstone.com/charts/albums/'

    chromedriver = "/Applications/chromedriver"  # path to the chromedriver executable
    os.environ["webdriver.chrome.driver"] = chromedriver

    driver = webdriver.Chrome(chromedriver)

    driver.get(url)
    time.sleep(2)

    close_privacy_notice_button = driver.find_element_by_id('pmc_toupp_notice_close_btn')
    time.sleep(1)

    close_privacy_notice_button.click()
    time.sleep(1)

    for _ in range(13):
        try:
            load_more_button = driver.find_element_by_xpath(
                '//a[contains(@class, "c-chart__table--load-more")]'
            )
            load_more_button.click()
            time.sleep(2.5)
        except NoSuchElementException:
            print('the load more button is no longer here')

    soup = BeautifulSoup(driver.page_source, 'lxml')
    return soup


def make_rs_200_df(soup):
    """ given a soup object of the rolling stone 200 albums website,
    returns a pandas DataFrame containing information from the 200 albums"""
    #  get soup of albums
    chart_contents_div = soup.find("div", {"class": "c-content--charts"})

    soup_of_first_album = soup.find("section", {"class": "c-chart__table--first"})
    soup_of_grid_of_albums = chart_contents_div.find('section', {'l-section__charts--grid'})

    list_of_soup_of_album = [soup_of_first_album]
    list_of_soup_of_album.extend(soup_of_grid_of_albums.find_all('section', {'class': 'c-chart__table--single'}))

    property_dicts = []
    for soup_of_album in list_of_soup_of_album:
        property_dicts.append(extract_album_info(soup_of_album))

    albums_df = pd.DataFrame(property_dicts)
    return albums_df


def get_rs_albums_page_response(date=""):
    """
    gets the response from the rolling stone top 200 albums page for
    the specified date string (YYYY-mm-dd)
    """
    url = 'https://www.rollingstone.com/charts/albums/' + date
    rs_albums_response = requests.get(url)
    try:
        assert rs_albums_response.status_code == 200
    except AssertionError:
        print('sub-optimal response_code', rs_albums_response.status_code)
    return rs_albums_response


def extract_album_info(soup_of_album):
    album_property_dict = dict()
    rank = soup_of_album.find('div', {'class': 'c-chart__table--rank'}).getText()
    album_property_dict['rank'] = int(rank)

    title = soup_of_album.find('div', {'class': 'c-chart__table--title'}).get_text()
    album_property_dict['title'] = title

    caption_artist = soup_of_album.find('div', {'class': 'c-chart__table--caption'}).getText()
    album_property_dict['caption_artist'] = caption_artist

    album_units = (soup_of_album.find('div', {'class': 'c-chart__table--album-units'})
                   .find('span').getText())
    album_property_dict['album_units'] = album_units

    record_label = (soup_of_album.find('div', {'class': 'c-chart__table--label'})
                    .find('span', {'class': "c-chart__table--label-text"}).get_text())
    album_property_dict['record_label'] = record_label

    return album_property_dict


def get_album_properties(album_section_soup, class_names):
    """Given a soup object album section and a list of class names, returns a dict
    of class name keys and 'getText()' strings"""
    property_dict = dict()
    for class_name in class_names:
        try:
            property_dict[class_name] = album_section_soup.find('div', {'class': class_name}).getText()
        except AttributeError:
            property_dict[class_name] = None
            print('warning: one thing failed')
    return property_dict


def get_album_section_soups(rs_albums_response):
    """
    Returns a list of beautiful soup objects, one for each album
    currently displayed on the page (at time of download)
    """
    rs_albums_page = rs_albums_response.text
    soup = BeautifulSoup(rs_albums_page, 'html.parser')
    chart_contents_div = soup.find("div", {"class": "c-content--charts"})
    all_album_sections = chart_contents_div.findAll("section", {"class": "c-chart__table--single"})
    property_dicts = []
    for album_section in all_album_sections:
        property_dicts.append(get_album_properties(album_section, class_names))


if __name__ == "__main__":
    print('running', current_file_path)
    print(project_dir)
