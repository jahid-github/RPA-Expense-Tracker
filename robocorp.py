from robocorp.tasks import task
from robocorp import browser
from datetime import datetime
from RPA.HTTP import HTTP

@task
def robot_spare_bin_python():
    """Insert the expense data and export it as a PDF"""
    browser.configure(
        slowmo=500,
     )
    open_the_intranet_website()
    download_text_file()
    expense=read_text_file()
    fill_data_from_text_file(expense)
    collect_results()

def open_the_intranet_website():
    """Navigates to the given URL"""
    browser.goto("https://fspacheco.github.io/rpa-challenge/expense-tracker.html")

def download_text_file():
    """Downloads file from the given URL"""
    http = HTTP()
    http.download(url="https://fspacheco.github.io/rpa-challenge/assets/list-expenses.txt" , overwrite=True)

def read_text_file():
    with open('list-expenses.txt', 'r') as file:
       content = file.read()
       modified_content = content.replace(',', '.')
       data = content.splitlines()
       return(data)
    


def fill_data_from_text_file(expense):
    page = browser.page()

    corrections ={
        "entert": "entertainment",
        "utilit": "utilities",
        "othr": "other",
        "shop": "shopping",
        "trasport": "transportation",
        "tranport": "transportation",
        "oter" : "other",
        "shoping":"shopping",
        "transport": "transportation",
         }

    print(type(expense))


    for item in expense:
        item = item.split()
        
        
        date = "date"
        date_str = item[0]
        date_obj = datetime.strptime(f"{date_str}/2024","%d/%m/%Y")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        print(formatted_date)


        page.fill("#description", item[1])
        page.fill("#amount",str(float(item[2].replace(',','.'))))
        page.fill("#date", formatted_date)

        categ=item[3]
        if item[3] in corrections:
            print(corrections[item[3]])
            categ=corrections[item[3]]

        page.select_option("#category", categ.capitalize())
        


        page.click("button:text('Add Expense')")
        


def collect_results():
    """Take a screenshot of the page"""
    page = browser.page()
    page.screenshot(path="output/expense.png")
