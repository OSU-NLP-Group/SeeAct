
question_input = """"<<SYS>>
You are a helpful assistant that is great at website design, navigation, and executing tasks for the user.
<</SYS>>

'''
<html> <div> <div> <a tock home page /> <button id=0 book a reservation. toggle open> <span> Book a reservation </span> </button> <button book a reservation. toggle open> </button> </div> <div> <select id=1 type> <option reservations true> Dine in </option> <option pickup> Pickup </option> <option delivery> Delivery </option> <option events> Events </option> <option wineries> Wineries </option> <option all> Everything </option> </select> <div id=2> <p> Celebrating and supporting leading women shaking up the industry. </p> <span> Explore now </span> </div> </div> </div> </html>
'''

Based on the HTML webpage above, try to complete the following task:
Task: Check for pickup restaurant available in Boston, NY on March 18, 5pm with just one guest
Previous actions:
None
What should be the next action? Please select from the following choices (If the correct action is not in the page above, please select A. 'None of the above'):

A. None of the above
B. <button id=0 book a reservation. toggle open> <span> Book a
C. <select id=1 type> <option reservations true> Dine in </option> <option
D. <div id=2> <p> Celebrating and supporting leading women shaking up [/INST] Answer: C.
Action: SELECT
Value: Pickup <s> [INST] '''
<html> <div> <main main> <section tabpanel> <div> <ul tablist> <li tab heading level 3 search and> </li> <li id=0 tab heading level 3 search and> <span> Hotel </span> </li> <li tab heading level 3 search and> </li> <li tab heading level 3 search and> </li> </ul> <div tabpanel> <div id=1> <div> <span> Dates* </span> <button button clear dates /> </div> <div> <label> Travelers </label> <div> <p> 1 Adult </p> <button button> 1 Adult </button> <div dialog> <button button travel with a pet. this> <span> Travel with a pet </span> </button> <div> <button button clear all fields> Clear all </button> <button button> </button> </div> </div> </div> </div> </div> </div> </div> </section> </main> <footer contentinfo> <div> <h3> Stay Connected </h3> <ul id=2> <a mobile tools> </a> <a open united's tiktok feed in> </a> <a open united's facebook page in> </a> <a open united's twitter feed in> </a> <a open united's youtube page in> </a> <a open united's instagram feed in> </a> <a open united's linkedin profile in> </a> </ul> </div> </footer> </div> </html>
'''

Based on the HTML webpage above, try to complete the following task:
Task: Compare the fare types to book a 1-adult ticket from Springfiels, IL to Austin, TX for April 29th 2023
Previous actions:
[combobox]  Enter your departing city, airport name, or airpor... -> TYPE: SPRINGFIELD
[button]  Springfield, IL, US (SPI) -> CLICK
[combobox]  Enter your destination city, airport name, or airp... -> TYPE: AUSTIN
[button]  Austin, TX, US (AUS) -> CLICK
What should be the next action? Please select from the following choices (If the correct action is not in the page above, please select A. 'None of the above'):

A. None of the above
B. <li id=0 tab heading level 3 search and> <span> Hotel
C. <div id=1> <div> <span> Dates* </span> <button button clear dates
D. <ul id=2> <a mobile tools> </a> <a open united's tiktok [/INST] Answer: A. <s> [INST] '''
<html> <div> <nav main menu> <ul> <li> <div button> Car Sales </div> <div id=0> <div> <div> <div> Buy A Car </div> <div> Plan Your Purchase </div> </div> <div> <h4> Its Tax Refund Time. Treat Yourself to an Upgrade. </h4> <p> With a variety of options, invest your refund in what you really want - a quality, used vehicle from Enterprise. </p> <a> View Inventory </a> </div> </div> </div> </li> <div id=1> Enterprise Fleet Management </div> </ul> </nav> <div region> <button id=2 selected pick-up date 03/19/2023> <span> <span> 19 </span> <div> <span> Mar </span> <span> 2023 </span> </div> </span> </button> </div> </div> </html>
'''

Based on the HTML webpage above, try to complete the following task:
Task: Find a mini van at Brooklyn City from April 5th to April 8th for a 22 year old renter.
Previous actions:
[searchbox]  Pick-up & Return Location (ZIP, City or Airport) (... -> TYPE: Brooklyn
[option]  Brooklyn, NY, US Select -> CLICK
What should be the next action? Please select from the following choices (If the correct action is not in the page above, please select A. 'None of the above'):

A. None of the above
B. <div id=0> <div> <div> <div> Buy A Car </div> <div>
C. <div id=1> Enterprise Fleet Management </div>
D. <button id=2 selected pick-up date 03/19/2023> <span> <span> 19 </span> [/INST] Answer: D.
Action: CLICK <s> [INST] '''
<html> <div> <div> <fieldset> <label> Search by Keyword or Web ID </label> <input id=0 submit submit-search /> <input id=1 text search hi james, what are you /> </fieldset> <a id=2> <svg img /> <span> Shop by Category </span> </a> </div> <p> <span id=3> 10 </span> <svg img /> </p> <a id=4 3xl - selecting this item> <span> 3XL </span> <span> (4) </span> </a> </div> </html>
'''

Based on the HTML webpage above, try to complete the following task:
Task: Find the cheapest women's plus size brown color loungewear in 3xl size.
Previous actions:
[span]  Shop by Category -> CLICK
[link]  Women -> HOVER
[link]  Loungewear -> CLICK
[div]  Size -> CLICK
What should be the next action? Please select from the following choices (If the correct action is not in the page above, please select A. 'None of the above'):

A. None of the above
B. <input id=0 submit submit-search />
C. <input id=1 text search hi james, what are you />
D. <a id=2> <svg img /> <span> Shop by Category </span>
E. <span id=3> 10 </span>
F. <a id=4 3xl - selecting this item> <span> 3XL </span>"""

def get_question_input():
    return question_input
