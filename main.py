from hostel.hostel import Collect_data

with Collect_data() as bot:
    bot.land_first_page()
    bot.select_place_to_go('Cusco')
    bot.select_dates()
    bot.click_search()
    bot.set_filter('1')
    #bot.get_data()
    bot.navigate_through_pages()