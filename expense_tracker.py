from robocorp.tasks import task
from robocorp import browser 
from RPA.HTTP import HTTP  
from RPA.FileSystem import FileSystem  
from RPA.PDF import PDF
from datetime import datetime

@task
def expense_tracker_bot():
    browser_instance = browser 
    browser_instance.configure(slowmo=200)
    open_expense_page(browser_instance)
    download_expense_file()
    expense_records = fill_form_with_data(browser_instance)
    capture_webpage_snapshot(browser_instance)
    generate_pdf_summary(expense_records)
#browsing the site
def open_expense_page(browser_instance):
    browser_instance.goto("https://fspacheco.github.io/rpa-challenge/expense-tracker.html")
def submit_expense_entry(browser_instance, expense):
    page = browser_instance.page()
    page.fill("#description", expense["Item"])
    page.fill("#amount", str(expense["Cost"])) 
    page.fill("#date", expense["TransactionDate"])  
    page.select_option("#category", expense["Category"])
    page.click("text= Add Expense")
def download_expense_file():
    http_client = HTTP()
    http_client.download(url="https://fspacheco.github.io/rpa-challenge/assets/list-expenses.txt", overwrite=True)
def fill_form_with_data(browser_instance):
    """Fetch the expense data from the text file and fill out the form"""
    file_system = FileSystem()
    file_content = file_system.read_file("list-expenses.txt")
    expense_data = []  
    for line in file_content.splitlines():
        columns = line.split()
        if len(columns) >= 4:  
            vendor_name = columns[1].strip() 
            amount = float(columns[2].strip().replace(",", ".")) 
            transaction_date = columns[0].strip()  
            category = columns[3].strip().lower()
            date_obj = datetime.strptime(transaction_date, "%d/%m")
            formatted_date = date_obj.strftime("2024-%m-%d")
            if "food" in category:
                category = "Food"
            elif "utilit" in category:
                category = "Utilities"
            elif "shop" in category or "shopping" in category or "shoping" in category:
                category = "Shopping"
            elif "entert" in category:
                category = "Entertainment"
            elif "oth" in category or "oter" in category:
                category = "Other"
            elif "transport" in category or "trasport" in category or "tranport" in category:
                category = "Transportation"
            expense_record = {
                "Item": vendor_name,
                "Cost": amount,
                "TransactionDate": formatted_date,
                "Category": category
            }
            expense_data.append(expense_record)  
            submit_expense_entry(browser_instance, expense_record) 
    return expense_data
#snapshot for expense summary
def capture_webpage_snapshot(browser_instance):
    """Take a screenshot of the current webpage"""
    page = browser_instance.page()
    page.screenshot(path="output/expense_summary.png")
'''pdf generation for including one line in the end with the category with higher expenses
and including another line in the end with the shop/company where the person spends more
'''
def generate_pdf_summary(expense_data):
    """Create a PDF report with expense details and summary using HTML to PDF conversion."""
    pdf = PDF()
    category_totals = {}
    vendor_totals = {}
    for expense in expense_data:
        category = expense["Category"]
        vendor = expense["Item"]
        cost = expense["Cost"]
        category_totals[category] = category_totals.get(category, 0) + cost
        vendor_totals[vendor] = vendor_totals.get(vendor, 0) + cost
    top_category = max(category_totals, key=category_totals.get)
    top_vendor = max(vendor_totals, key=vendor_totals.get)
    html_content = "<h1>Expense Report</h1>"
    html_content += "<table border='1'><tr><th>Date</th><th>Vendor</th><th>Category</th><th>Cost ($)</th></tr>"
    for expense in expense_data:
        html_content += f"<tr><td>{expense['TransactionDate']}</td><td>{expense['Item']}</td><td>{expense['Category']}</td><td>{expense['Cost']:.2f}</td></tr>"
        html_content += "</table>"
        html_content += f"<h2>Highest Spending Category: {top_category} (${category_totals[top_category]:.2f})</h2>"
        html_content += f"<h2>Highest Spending Vendor: {top_vendor} (${vendor_totals[top_vendor]:.2f})</h2>"
        pdf.html_to_pdf(html_content, "output/expense_summary_report.pdf")
