async def request_gen_simple():
    price_list = [
        ("redlightning OR survival gear OR chromatic OR clothing bless deed OR strongbox customization OR ankh token OR battle commendation OR an emote deed OR shadow aspect distillation OR mastercrafting diagram OR skill mastery orb OR plant chemicals OR arcane scroll OR treasure undeciphered OR research materials OR prevalia coins"),
        # ("redlightning OR survival gear OR chromatic OR clothing bless deed OR strongbox customization"),
        # ("ankh token OR battle commendation OR an emote deed OR shadow aspect distillation OR mastercrafting diagram OR skill mastery orb"),
        # ("plant chemicals OR arcane scroll OR treasure undeciphered OR research materials OR prevalia coins"),
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    cookies = RequestsCookieJar()
    cookies.set("app", "MTcxNzkxMTY0NXxyMy1fUlZXNkswcGRXZEhXNWpZOXdHY1FQMHhSQ1Z4VUp0MnFlNkQxdWlKMnExdUNyRDFtaFBBSmpJNGRZUXZjYkdndFhFNWRFaFZDQXJ0emg3VjJfTllSd2FmZWdXOW1kTEF4MHNsdHJEQUJHYlU9fGerm92O8uhh1zqXUJc5DO5U3HJ2gx6aQKYCEwXjuI9S")

    async with aiohttp.ClientSession() as session:
        aux_data = []
        tasks = []
        for searchString in price_list:
            page_url = "https://outlandmalls.com/?item=" + quote_plus(searchString) + "&search_category_id=0"
            tasks.append(fetch(session, page_url, headers, cookies))
        
        responses = await asyncio.gather(*tasks)

        return [(response, master_prices, page_url, 60, 1, .90) for response in responses]