website_dict = {'careers.walmart': 'https://careers.walmart.com/', 'dmv.virginia.gov': 'https://www.dmv.virginia.gov/',
                'thumbtack': 'https://www.thumbtack.com/', 'redfin': 'https://www.redfin.com/',
                'weather': 'https://weather.com/', 'accuweather': 'https://www.accuweather.com/',
                'justice.gov': 'https://www.justice.gov/', 'babycenter': 'https://www.babycenter.com/',
                'gov.uk': 'https://www.gov.uk/', 'drugs': 'https://www.drugs.com/', 'webmd': 'https://www.webmd.com/',
                'stocktwits': 'https://stocktwits.com/', 'ohio.gov': 'https://ohio.gov/',
                'akc.org': 'https://www.akc.org/', 'healthgrades': 'https://www.healthgrades.com/',
                'mayoclinic.org': 'https://www.mayoclinic.org/', 'linkedin': 'https://www.linkedin.com/',
                'udemy': 'https://www.udemy.com/', 'finance.google': 'https://www.google.com/finance/',
                'ryanair': 'http://ryanair.com/', 'underarmour': 'https://www.underarmour.com/en-us/',
                'sports.yahoo': 'https://sports.yahoo.com/?guccounter=1', 'united': 'https://www.united.com/en/us',
                'uniqlo': 'https://www.uniqlo.com/us/en/', 'budget': 'https://www.budget.com/en/home',
                'target': 'https://www.target.com/', 'viator': 'https://www.viator.com/',
                'yellowpages': 'https://www.yellowpages.com/', 'eventbrite': 'https://www.eventbrite.com/',
                'spothero': 'https://spothero.com/', 'kayak': 'https://www.kayak.com/',
                'flightaware': 'https://www.flightaware.com/', 'cvs': 'https://www.cvs.com/',
                'carnival': 'https://www.carnival.com/', 'marriott': 'https://www.marriott.com',
                'nfl': 'https://www.nfl.com/', 'airbnb': 'https://www.airbnb.com/',
                'jetblue': 'https://www.jetblue.com/', 'cargurus': 'https://www.cargurus.com/',
                'kohls': 'https://www.kohls.com/', 'rei': 'https://www.rei.com/',
                'aa': 'https://www.aa.com/homePage.do',
                'qatarairways': 'https://www.qatarairways.com/en-us/homepage.html',
                'ultimate-guitar': 'https://www.ultimate-guitar.com/', 'trip': 'https://us.trip.com/?locale=en-us',
                'macys': 'https://www.macys.com/', 'bestbuy': 'https://www.bestbuy.com/',
                'cars': 'https://www.cars.com/', 'recreation.gov': 'https://www.recreation.gov/',
                'tiktok.music': 'https://music.tiktok.com/au/', 'tripadvisor': 'https://www.tripadvisor.com/',
                'shopping.google': 'https://shopping.google.com/', 'nba': 'https://www.nba.com/'}

tasks_from_website = [(
    'Book a cheapest bundle and save option for 2 adults from Ahmedabad to Dubai on November 18 with free cancellation options, hotel should be a 3 star near Burj Khalifa with guest rating above 4, one night',
    'https://us.trip.com/?locale=en-us'),
    ('Check the details of order 12345 with email 12345@gmail.com', 'https://www.macys.com/'),
    ('As a Verizon user, finance a new blue iPhone 13 with 256gb along with monthly apple care',
     'https://www.bestbuy.com/'),
    ('Compare the Acura CL 2003 with the ILX 2022.', 'https://www.cars.com/'), (
        'Find the cheapest 3-star hotel with a guest rating of 4 stars for booking two rooms in Pune, India, for 4 Adults and one 4 year child, near the airport with a check-in date of November 18 and checkout date of November 20.',
        'https://us.trip.com/?locale=en-us'),
    ('Find a highest rated dealer for Cadillac with rating above 4 star within 20 miles of zip 60606.',
     'https://www.cars.com/'), (
        'Discover the trade-in value of my intel 7th generation i3 windows 10, hp laptop in fair condition,  which has 8 GB memory and can be powered on, proceed for the in-store trade-in.',
        "https://www.bestbuy.com/"),
    ('Find me the cheapest Dodge Ram 1500 within 50 miles of 21122', "https://www.cars.com/"),
    ('Check permit availability for Bryce Canyon National Park.', "https://www.recreation.gov/"),
    ('Use a tense music from BCD Studio in tik tok video editor', "https://music.tiktok.com/au/"), (
        'Schedule a repair service for my gaming console closest to the zip code 10001 on December 11, anytime after 6 pm.',
        "https://www.bestbuy.com/"), ('Find recalls for the Alfa romeo 4C', "https://www.cars.com/"),
    ('Open list of creators with more than 10M followers.', "https://music.tiktok.com/au/"),
    ('Find cheapest flight from Toronto, Canada to New York City, USA for 1 adult.', "https://www.tripadvisor.com/"),
    ('Book a first class flight from Hong kong to Taipei leaving November 18 and returning November 19',
     "https://us.trip.com/?locale=en-us"), (
        'Compare prices and find cheapest total price for Granitestone Sandwich Maker from stores which offer free delivery',
        "https://shopping.google.com/"), (
        'Play a rock music from the artist zukisuzuki that can be used for tik tok series and usable  in helo, topbuzz.',
        "https://music.tiktok.com/au/"), ('Get keyword insights related to games.', "https://music.tiktok.com/au/"),
    ('Add the lowest in price Amusement park attraction in Seoul to my favorites', "https://us.trip.com/?locale=en-us"),
    ('Open the page to create a review for Hotel Xcaret Mexico.', "https://www.tripadvisor.com/"), (
        'View the speakers that are bluetooth and wireless and filter the results to only show models that are on sale and cost less than $50.',
        "https://www.bestbuy.com/"),
    ('Browse list of tiktok series songs longer than 60 seconds.', "https://music.tiktok.com/au/"), (
        'Check the speccification of the best selling HP FHD laptop with 12gb ram and core i7 running on windows 11',
        "https://www.bestbuy.com/"), ('Find the app for ios.', "https://www.recreation.gov/"),
    ('Find the next available dates for Alley Creek Camp.', "https://www.recreation.gov/"),
    ('Show me the statistics for assists per game.', "https://www.nba.com/"),
    ('Find the next available date for Albion Basin.', "https://www.recreation.gov/"),
    ('Show me the trending songs in canada for the last 30 days that are approved for business use',
     "https://music.tiktok.com/au/"),
    ('play the video where Larry Bird made his NBA debut vs the Houston Rockets.', "https://www.nba.com/"),
    ('Look for a White PlayStation 5 Console and save it', "https://shopping.google.com/")]

tasks_from_task = [
    ('Search for a one way flight from Dublin to Malta on November 18, 2023 for 2 adults.', "http://ryanair.com/"), (
        'Add a e-gift card to bag of $100 for recipient John and email address abc@test.com from buckeye.foobar@gmail.com with message gift card.',
        "https://www.underarmour.com/en-us/"),
    ('Find the last game of the season for the Toronto Raptors.', "https://sports.yahoo.com/?guccounter=1"),
    ('Find Hotel in Chicago with lowest price for 2 adults checking in on Apr 14 for 3 days.',
     "https://www.united.com/en/us"),
    ('Find the page with instructions on how to return orders online.', "https://www.uniqlo.com/us/en/"),
    ('Download the e-receipt with the last name Smith and confirmation number X123456989.',
     "https://www.budget.com/en/home"),
    ('Add a set of queen-sized bed sheets with at least a 4-star rating to the cart.', "https://www.target.com/"),
    ('Find a list of Tours that contain visits to the Louvre rated 5 stars', "https://www.viator.com/"),
    ('Look for hair salon coupons in San Diego.', "https://www.yellowpages.com/"),
    ('Search for a paid fishing class event on chicago', "https://www.eventbrite.com/"),
    ('Book the cheapest parking spot near Bradley Airport', "https://spothero.com/"), (
        'search the cheapest small car rental deals from Little Ferry, New Jersey, United States on 18th November to same location dropoff on December 4th 2pm.',
        "https://www.kayak.com/"), (
        'Find solutions for Airport and fill the contact form with message to "Send Brochure". Contact information John Smith. Email: abc@abc.com. Phone #: 88889999',
        "https://www.flightaware.com/"), ('Signup for virtual healthcare visit.', "https://www.cvs.com/"),
    ('Search for a 10 day cruise to Alaska from San Francisco in December 2023.', "https://www.carnival.com/"),
    ('Browse Marriott Bonvoy credit cards.', "https://www.marriott.com"),
    ('Show me the scores for the 2019 super bowl', "https://www.nfl.com/"), (
        'Find morning sports experiences in english for one adult and 2 children in portugal on December 2',
        "https://www.airbnb.com/"),
    ('Find flights going from Indira Gandhi to Los Cabos.', "https://www.flightaware.com/"),
    ('Book a room from Apr 30 to Jun 5 for two adults in Tallahassee.', "https://www.marriott.com"), (
        'Look for a business class flight to Paris from Salt Lake City on December 2, with a return on December 7, and checkout',
        "https://www.jetblue.com/"), (
        'Search for the lowest millage used Honda Crosstour 2012 to 2013 near 49102 less than $25000.',
        "https://www.cargurus.com/"),
    ('Browse spider-man toys for kids and sort by lowest price.', "https://www.kohls.com/"),
    ('Sign up for a REI Co-Op membership.', "https://www.rei.com/"),
    ('Browse medium cars for rent for a week in Las Vegas starting on Jun 5.', "https://www.kayak.com/"), (
        'Book the lowest-priced and quickest flight for 5 adults and 1 child on December 20 from Mumbai to any airport near Washington.',
        "https://www.aa.com/homePage.do"),
    ('Find a person by address Nice st - 1234, Good, FL.', "https://www.yellowpages.com/"),
    ('Check travel requirements for trips between Tokyo and Guangzhou.',
     "https://www.qatarairways.com/en-us/homepage.html"),
    ('upvote a comment on the most relevant kiss chords & tabs', "https://www.ultimate-guitar.com/"), (
        'Find the current NFL standings for the AFC East division and determine which team is in first place.',
        "https://www.nfl.com/")]

tasks_from_domain = [('Show me jobs for MBA & Graduate Internships.', "https://careers.walmart.com/"),
                     ('Find a driver training school in Dublin', "https://www.dmv.virginia.gov/"), (
                         'View the profile of a Wedding Photographer near 10203 for a 4 hour wedding on November 18',
                         "https://www.thumbtack.com/"), (
                         'Calculate what a 30 year fixed rate mortgage monthly payment would be for a $500k home purchase with $100k down in zip code 85747',
                         "https://www.redfin.com/"), (
                         'Find out if there are any current air quality alerts or warnings in effect for zip code 10019.',
                         "https://weather.com/"),
                     ('find the Monthly forecast for Manchester, GB for December', "https://www.accuweather.com/"),
                     ('Find latest publication of attorney general.', "https://www.justice.gov/"),
                     ('What are the similar names to the name carl', "https://www.babycenter.com/"), (
                         'Calculate Pregnancy Weight Gain for a 5 weeks pregnancy with a 169lb weight before pregnancy and a 175lb after pregnancy with a 5.6ft height.',
                         "https://www.babycenter.com/"), (
                         'Check if visa is required to work in UK for longer than 6 months in Healthcare as an American citizen.',
                         "https://www.gov.uk/"),
                     ('Find the Driver License Eligibility Requirements', "https://www.dmv.virginia.gov/"),
                     ('Show side effects of Tamiflu.', "https://www.drugs.com/"),
                     ('find electricians near 10203', "https://www.thumbtack.com/"),
                     ('Browse the natural products database.', "https://www.drugs.com/"),
                     ('View the wind flow map for Utah, the  United States without contours.',
                      "https://www.accuweather.com/"),
                     ('Find out how to transfer the title of vehicle when the owner is deceased.',
                      "https://www.dmv.virginia.gov/"),
                     ('Find symptoms of sleep apnea', "https://www.webmd.com/"),
                     (
                     'Create a room for AI stocks discussion, with the topic "Technology".', "https://stocktwits.com/"),
                     ('Find the latest COVID-19 Travel Advisory in Ohio', "https://ohio.gov/"),
                     ('Find the playful level of a corgi.', "https://www.akc.org/"),
                     ('Find the procedure to get the license for Athletic Trainer', "https://ohio.gov/"),
                     ('Browse list of Civil Division forms.', "https://www.justice.gov/"),
                     ('Check drug interaction for melatonin and Folate Forte.', "https://www.drugs.com/"), (
                         'Find a psychiatrist who offers virtual appointmentsthat has experience with treating neurodevelopment disorders and accepts new patients.',
                         "https://www.healthgrades.com/"),
                     ('Find the side effects of taking Montelukast', "https://www.drugs.com/"),
                     ('Find a doctor for back pain in Rochester', "https://www.mayoclinic.org/"),
                     ('Find Data Entry or similar jobs and save two of them.', "https://www.linkedin.com/"),
                     ('Find a AWS certification Software Development related to Amazon EC2.', "https://www.udemy.com/"),
                     ('Show me the monthly weather forecast for florida city', "https://www.accuweather.com/"),
                     ('Find the latest news about Netflix stock', "https://www.google.com/finance/")]

original_domain = [('Show me jobs for MBA & Graduate Internships.', 'careers.walmart'),
                   ('Find a driver training school in Dublin', 'dmv.virginia.gov'), (
                   'View the profile of a Wedding Photographer near 10203 for a 4 hour wedding on april 13',
                   'thumbtack'), (
                   'Calculate what a 30 year fixed rate mortgage monthly payment would be for a $500k home purchase with $100k down in zip code 85747',
                   'redfin'), (
                   'Find out if there are any current air quality alerts or warnings in effect for zip code 10019.',
                   'weather'), ('find the Monthly forecast for Manchester, GB for May', 'accuweather'),
                   ('Find latest publication of attorney general.', 'justice.gov'),
                   ('What are the similar names to the name carl', 'babycenter'), (
                   'Calculate Pregnancy Weight Gain for a 5 weeks pregnancy with a 169lb weight before pregnancy and a 175lb after pregnancy with a 5.6ft height.',
                   'babycenter'), (
                   'Check if visa is required to work in UK for longer than 6 months in Healthcare as an American citizen.',
                   'gov.uk'), ('Find the Driver License Eligibility Requirements', 'dmv.virginia.gov'),
                   ('Show side effects of Tamiflu.', 'drugs'), ('find electricians near 10203', 'thumbtack'),
                   ('Browse the natural products database.', 'drugs'),
                   ('View the wind flow map for Utah, the  United States without contours.', 'accuweather'),
                   ('Find out how to transfer the title of vehicle when the owner is deceased.', 'dmv.virginia.gov'),
                   ('Find symptoms of sleep apnea', 'webmd'),
                   ('Create a room for AI stocks discussion, with the topic "Technology".', 'stocktwits'),
                   ('Find the latest COVID-19 Travel Advisory in Ohio', 'ohio.gov'),
                   ('Find the playful level of a corgi.', 'akc.org'),
                   ('Find the procedure to get the license for Athletic Trainer', 'ohio.gov'),
                   ('Browse list of Civil Division forms.', 'justice.gov'),
                   ('Check drug interaction for melatonin and Folate Forte.', 'drugs'), (
                   'Find a psychiatrist who offers virtual appointmentsthat has experience with treating neurodevelopment disorders and accepts new patients.',
                   'healthgrades'), ('Find the side effects of taking Montelukast', 'drugs'),
                   ('Find a doctor for back pain in Rochester', 'mayoclinic.org'),
                   ('Find Data Entry or similar jobs and save two of them.', 'linkedin'),
                   ('Find a AWS certification Software Development related to Amazon EC2.', 'udemy'),
                   ('Show me the monthly weather forecast for florida city', 'accuweather'),
                   ('Find the latest news about Netflix stock', 'finance.google')]

original_task = [('Search for a one way flight from Dublin to Malta on April 22, 2023 for 2 adults.', 'ryanair'), (
'Add a e-gift card to bag of $100 for recipient John and email address abc@test.com from buckeye.foobar@gmail.com with message gift card.',
'underarmour'), ('Find the last game of the season for the Toronto Raptors.', 'sports.yahoo'),
                 ('Find Hotel in Chicago with lowest price for 2 adults checking in on Apr 14 for 3 days.', 'united'),
                 ('Find the page with instructions on how to return orders online.', 'uniqlo'),
                 ('Download the e-receipt with the last name Smith and confirmation number X123456989.', 'budget'),
                 ('Add a set of queen-sized bed sheets with at least a 4-star rating to the cart.', 'target'),
                 ('Find a list of Tours that contain visits to the Louvre rated 5 stars', 'viator'),
                 ('Look for hair salon coupons in San Diego.', 'yellowpages'),
                 ('Search for a paid fishing class event on chicago', 'eventbrite'),
                 ('Book the cheapest parking spot near Bradley Airport', 'spothero'), (
                 'search the cheapest small car rental deals from Little Ferry, New Jersey, United States on 23th March to same location dropoff on april 4th 2pm.',
                 'kayak'), (
                 'Find solutions for Airport and fill the contact form with message to "Send Brochure". Contact information John Smith. Email: abc@abc.com. Phone #: 88889999',
                 'flightaware'), ('Signup for virtual healthcare visit.', 'cvs'),
                 ('Search for a 10 day cruise to Alaska from San Francisco in June 2023.', 'carnival'),
                 ('Browse Marriott Bonvoy credit cards.', 'marriott'),
                 ('Show me the scores for the 2019 super bowl', 'nfl'), (
                 'Find morning sports experiences in english for one adult and 2 children in portugal on may 2',
                 'airbnb'), ('Find flights going from Indira Gandhi to Los Cabos.', 'flightaware'),
                 ('Book a room from Apr 30 to Jun 5 for two adults in Tallahassee.', 'marriott'), (
                 'Look for a business class flight to Paris from Salt Lake City on June 2, with a return on June 7, and checkout',
                 'jetblue'), (
                 'Search for the lowest millage used Honda Crosstour 2012 to 2013 near 49102 less than $25000.',
                 'cargurus'), ('Browse spider-man toys for kids and sort by lowest price.', 'kohls'),
                 ('Sign up for a REI Co-Op membership.', 'rei'),
                 ('Browse medium cars for rent for a week in Las Vegas starting on Jun 5.', 'kayak'), (
                 'Book the lowest-priced and quickest flight for 5 adults and 1 child on May 20 from Mumbai to any airport near Washington.',
                 'aa'), ('Find a person by address Nice st - 1234, Good, FL.', 'yellowpages'),
                 ('Check travel requirements for trips between Tokyo and Guangzhou.', 'qatarairways'),
                 ('upvote a comment on the most relevant kiss chords & tabs', 'ultimate-guitar'), (
                 'Find the current NFL standings for the AFC East division and determine which team is in first place.',
                 'nfl')]

original_website = [(
                    'Book a cheapest bundle and save option for 2 adults from Ahmedabad to Dubai on April 5 with free cancellation options, hotel should be a 3 star near Burj Khalifa with guest rating above 4, one night',
                    'trip'), ('Check the details of order 12345 with email 12345@gmail.com', 'macys'), (
                    'As a Verizon user, finance a new blue iPhone 13 with 256gb along with monthly apple care',
                    'bestbuy'), ('Compare the Acura CL 2003 with the ILX 2022.', 'cars'), (
                    'Find the cheapest 3-star hotel with a guest rating of 4 stars for booking two rooms in Pune, India, for 4 Adults and one 4 year child, near the airport with a check-in date of March 26 and checkout date of March 28.',
                    'trip'), (
                    'Find a highest rated dealer for Cadillac with rating above 4 star within 20 miles of zip 60606.',
                    'cars'), (
                    'Discover the trade-in value of my intel 7th generation i3 windows 10, hp laptop in fair condition,  which has 8 GB memory and can be powered on, proceed for the in-store trade-in.',
                    'bestbuy'), ('Find me the cheapest Dodge Ram 1500 within 50 miles of 21122', 'cars'),
                    ('Check permit availability for Bryce Canyon National Park.', 'recreation.gov'),
                    ('Use a tense music from BCD Studio in tik tok video editor', 'tiktok.music'), (
                    'Schedule a repair service for my gaming console closest to the zip code 10001 on March 24, anytime after 6 pm.',
                    'bestbuy'), ('Find recalls for the Alfa romeo 4C', 'cars'),
                    ('Open list of creators with more than 10M followers.', 'tiktok.music'),
                    ('Find cheapest flight from Toronto, Canada to New York City, USA for 1 adult.', 'tripadvisor'), (
                    'Book a first class flight from Hong kong to Taipei leaving April 13 and returning April 14',
                    'trip'), (
                    'Compare prices and find cheapest total price for Granitestone Sandwich Maker from stores which offer free delivery',
                    'shopping.google'), (
                    'Play a rock music from the artist zukisuzuki that can be used for tik tok series and usable  in helo, topbuzz.',
                    'tiktok.music'), ('Get keyword insights related to games.', 'tiktok.music'),
                    ('Add the lowest in price Amusement park attraction in Seoul to my favorites', 'trip'),
                    ('Open the page to create a review for Hotel Xcaret Mexico.', 'tripadvisor'), (
                    'View the speakers that are bluetooth and wireless and filter the results to only show models that are on sale and cost less than $50.',
                    'bestbuy'), ('Browse list of tiktok series songs longer than 60 seconds.', 'tiktok.music'), (
                    'Check the speccification of the best selling HP FHD laptop with 12gb ram and core i7 running on windows 11',
                    'bestbuy'), ('Find the app for ios.', 'recreation.gov'),
                    ('Find the next available dates for Alley Creek Camp.', 'recreation.gov'),
                    ('Show me the statistics for assists per game.', 'nba'),
                    ('Find the next available date for Albion Basin.', 'recreation.gov'), (
                    'Show me the trending songs in canada for the last 30 days that are approved for business use',
                    'tiktok.music'),
                    ('play the video where Larry Bird made his NBA debut vs the Houston Rockets.', 'nba'),
                    ('Look for a White PlayStation 5 Console and save it', 'shopping.google')]

if __name__ == "__main__":
    website_dict = {}
    for j, i in zip(original_domain, tasks_from_domain):
        website_dict[j[1]] = i[1]
    for j, i in zip(original_task, tasks_from_task):
        website_dict[j[1]] = i[1]
    for j, i in zip(original_website, tasks_from_website):
        website_dict[j[1]] = i[1]
    print(website_dict)
    print(len(website_dict))
