from selenium import webdriver
import csv
from selenium.common.exceptions import NoSuchElementException, \
    ElementClickInterceptedException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def read_urls_file():
    with open('urls.txt', 'r') as urls_file:
        urls_list = urls_file.read().split('\n')
        return urls_list


def selenium_work(url):
    driver = webdriver.Firefox()
    try:
        driver.get(url)
        return driver
    except WebDriverException:
        driver.quit()
        return False


def get_pages(driver):
    paginator_pages = driver.find_element_by_class_name('searchResults-pagination').find_elements_by_class_name(
        'cx-enclosedBtn')
    pages_count = paginator_pages[-1].text
    return pages_count


def valid_url(driver):
    try:
        find_text = driver.find_element_by_class_name('searchResults-header'). \
            find_element_by_class_name('searchResults-count').text
        return True
    except (NoSuchElementException, WebDriverException):
        return False


def selenium_get_content(driver):

    agents_full_list = []


    find_text = driver.find_element_by_class_name('searchResults-header').\
        find_element_by_class_name('searchResults-count').text
    print(find_text)
    paginator_pages = driver.find_element_by_class_name('searchResults-pagination').\
        find_elements_by_class_name('cx-enclosedBtn')[-1].text
    print('Pages: ' + str(paginator_pages))

    delay = 3  # seconds
    for num_page in range(1, int(paginator_pages)+1):

        print(f'Page {num_page} is processing.')
        try:
            items_wait = WebDriverWait(driver, delay).\
                until(EC.presence_of_element_located((By.CLASS_NAME, 'agentCard')))
        except TimeoutException:
            print("Loading took too much time!")

        items = driver.find_elements_by_class_name('agentCard')

        for item in items:
            agent_name = (item.find_element_by_class_name('agentCard-imageWrapper').
                          find_element_by_class_name('textIntent-headline1').text.strip())
            contacts = item.find_element_by_class_name('agentCard-contact').find_elements_by_tag_name('a')
            try:
                agent_email = (contacts[0].text.strip())
            except (AttributeError, IndexError):
                agent_email = ''
            try:
                agent_phone = (contacts[1].text.strip().replace('\n', '').split(' ')[-1])
            except (AttributeError, IndexError):
                agent_phone = ''

            agents_full_list.append([agent_name, agent_email, agent_phone])

        print("Add {} agents. Summary: {} profiles.".format(len(items), len(agents_full_list)))

        try:
            button_next = driver.find_element_by_class_name('searchResults-pagination').\
                find_element_by_class_name('cx-react-pagination-next')
            driver.execute_script("arguments[0].scrollIntoView();", button_next)
            button_next.click()
        except ElementClickInterceptedException:
            break

    return agents_full_list


def save_to_scv(data, file):
    with open(file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(['agent_name', 'email', 'phone'])
        for row in data:
            writer.writerow([row[0], row[1], row[2]])


def main():
    urls = read_urls_file()
    print("Find {} urls".format(len(urls)))
    for index, url in enumerate(urls):
        print("URL {} is processing.".format(index + 1))
        driver = selenium_work(url)
        if driver and valid_url(driver):
            agents_full_list = selenium_get_content(driver)
            driver.quit()
            save_to_scv(agents_full_list, 'compass_url_{}.csv'.format(index + 1))
            print('Save all agents in compass_url_{}.csv'.format(index + 1))
        else:
            if driver:
                driver.quit()
                print("URL {} is not valid.".format(index + 1))
            else:
                print("URL {} is not valid.".format(index + 1))

if __name__ == '__main__':
    main()
