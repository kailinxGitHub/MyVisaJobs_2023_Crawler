import re
import pandas as pd

def cleaning_green_card_applicant_profile(category):
    list_in_category = ['University Of Southern California(584)', ' Carnegie Mellon University(325)', ' Arizona State University(314)', ' Northeastern University(281)', ' New York University(247)', ' North Carolina State University(232)', ' The University Of Texas At Dallas(174)', ' State University Of New York At Buffalo(161)', ' University Of Florida(154)', ' San Jose State University(152)', ' University Of Texas At Dallas(151)', ' Georgia Institute Of Technology(149)']

    data = []
    # Mapping the items
    for item in list_in_category:
        letters_to_remove = "()"
        for letter in letters_to_remove:
            item = item.replace(letter, "")
        name_pattern = re.compile(r"[a-zA-Z\s]+")
        cat_items = name_pattern.search(item)
        if cat_items:
            cat_items_name = cat_items.group().strip()
            cat_items_name = re.sub(' +', ' ', cat_items_name)
        else:
            continue
        number_pattern = re.compile(r"\d+")
        number_match = number_pattern.search(item)
        if number_match:
            number = number_match.group()
        else:
            continue
        data.append(['Amazon,Com Services', cat_items_name, int(number)])

    # Create DataFrame
    df = pd.DataFrame(data, columns=['Company', 'University', 'Number'])
    print(df)

cleaning_green_card_applicant_profile(None)