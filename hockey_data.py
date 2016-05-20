import csv

def load_team_seasons(include_OT=False):
    with open("2016_regular_season.csv") as games:
        games_reader = csv.reader(games, delimiter=',')
        next(games_reader) # Eliminate row headings
        
        team_seasons = {}

        for game in games_reader:
            add_game(team_seasons, game, include_OT)

    return team_seasons

def add_game(team_seasons, game, include_OT):
    date, visitor, visitor_goals, home, home_goals, \
        OT_SO, attendance, game_length = game

    home_winner = home_goals > visitor_goals
    winner, loser = (home, visitor) if home_winner else (visitor, home)

    if include_OT:
        winner_result = "W" + OT_SO
        loser_result = "L" + OT_SO
    else:
        winner_result = "W"
        loser_result = "L"

    if winner not in team_seasons:
        team_seasons[winner] = []
    if loser not in team_seasons:
        team_seasons[loser] = []

    team_seasons[winner].append(winner_result)
    team_seasons[loser].append(loser_result)

def process_chains(team_seasons):
    team_chains = {}
    for team, games in team_seasons.items():
        outcomes = set(games)

        chains = {}
        for outcome1 in outcomes:
            for outcome2 in outcomes:
                chains[(outcome1, outcome2)] = 0

        for i in range(len(games)-1):
            prev_result = games[i]
            curr_result = games[i+1]
            chains[(prev_result, curr_result)] += 1

        team_chains[team] = chains

    return team_chains

def get_chain_probabilities(all_chains):
    team_probabilities = {}
    for team, chains in all_chains.items():
        outcomes = set([chain[0] for chain in chains])

        denominators = {outcome: 0 for outcome in outcomes}

        for chain, num_games in chains.items():
            prev_result = chain[0]
            denominators[prev_result] += num_games

        probabilities = {}
        for chain, num_games in chains.items():
            prev_result = chain[0]
            probabilities[chain] = num_games/denominators[prev_result]

        team_probabilities[team] = probabilities

    return team_probabilities

def process_probabilities(all_probabilities):
    num_teams = len(all_probabilities)

    win_differences = []
    total_win_differences = 0
    for team, probabilities in all_probabilities.items():
        WW_prob = probabilities[('W', 'W')]
        LW_prob = probabilities[('L', 'W')]

        win_differences.append((team, WW_prob - LW_prob))
        total_win_differences += WW_prob - LW_prob

    win_differences.sort(key=lambda x: x[1])

    print("Additional Win Percentage Gained by Win in Previous Game")
    print("NHL average:", total_win_differences/num_teams)
    for team, chance in win_differences:
        print(team, chance)



team_seasons = load_team_seasons()
all_chains = process_chains(team_seasons)
all_probabilities = get_chain_probabilities(all_chains)
process_probabilities(all_probabilities)

