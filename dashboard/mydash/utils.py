# mydash/utils.py
def generate_query(keyword, website):
    """
    Create a Google search query for the Andishkadeh bot.
    
    Parameters:
        keyword (str): The keyword entered by the user.
        website (str): The URL of the research center.
        
    Returns:
        str: The formatted query string.
    """

    # Create the query string 
    query = f'allintext: "{keyword}" site:{website}'
    print('I generated the query mesle ye bacheye khoob.')
    
    return query
