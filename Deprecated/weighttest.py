locations = [
('W Andaria Gate',		    {'Profit': 10000,	'CTP_Average': 0.6,	'Margin_Average': 0.8}),
('MyKruelz',		        {'Profit': 140000,	'CTP_Average': 0.7,	'Margin_Average': 0.6}),
('E Andaria Gate',		    {'Profit': 51000,	'CTP_Average': 0.7,	'Margin_Average': 0.4}),
('N Outpost Gate 2',		{'Profit': 31500,	'CTP_Average': 0.7,	'Margin_Average': 0.4}),
('AR3',		                {'Profit': 23000,	'CTP_Average': 0.7,	'Margin_Average': 0.4}),
("N of Anchor's Rest",		{'Profit': 4000,	'CTP_Average': 0.7,	'Margin_Average': 0.4}),
('NW Outpost Gate Far',		{'Profit': 3580,	'CTP_Average': 0.7,	'Margin_Average': 0.4}),
('SW Terran Clearing',		{'Profit': 9100,	'CTP_Average': 0.8,	'Margin_Average': 0.4}),
('E of GH',		            {'Profit': 440213,	'CTP_Average': 0.8,	'Margin_Average': 0.3}),
('SW Cambria Gate',		    {'Profit': 84000,	'CTP_Average': 0.8,	'Margin_Average': 0.3}),
('81a Xroad',		        {'Profit': 29500,	'CTP_Average': 0.8,	'Margin_Average': 0.3}),
('N Cambria Gate',		    {'Profit': 29112,	'CTP_Average': 0.8,	'Margin_Average': 0.3}),
('S Cambria Gate',		    {'Profit': 9000,	'CTP_Average': 0.8,	'Margin_Average': 0.3}),
('Cedar Island Center',		{'Profit': 3000,	'CTP_Average': 0.8,	'Margin_Average': 0.3}),
('N Prev Clearing E',		{'Profit': 3000,	'CTP_Average': 0.8,	'Margin_Average': 0.3}),
('Frozen Ruins SW',		    {'Profit': 3000,	'CTP_Average': 0.8,	'Margin_Average': 0.3}),
    ('TRT',		                {'Profit': 737500,	'CTP_Average': 0.8,	'Margin_Average': 0.2}),
    ('Mine',		            {'Profit': 677501,	'CTP_Average': 0.8,	'Margin_Average': 0.2}),
('N Andaria Gate',		    {'Profit': 169008,	'CTP_Average': 0.8,	'Margin_Average': 0.2}),
('AR5',		                {'Profit': 122500,	'CTP_Average': 0.8,	'Margin_Average': 0.2}),
('N Prev Clearing N',		{'Profit': 73001,	'CTP_Average': 0.8,	'Margin_Average': 0.2}),
('Frost Forest',		    {'Profit': 24000,	'CTP_Average': 0.8,	'Margin_Average': 0.2}),
('S Terran Clearing',		{'Profit': 16000,	'CTP_Average': 0.8,	'Margin_Average': 0.2}),
('AR1',		                {'Profit': 15000,	'CTP_Average': 0.8,	'Margin_Average': 0.2}),
('S Prev Xroad S',		    {'Profit': 15000,	'CTP_Average': 0.8,	'Margin_Average': 0.2}),
('S of Pulma',		        {'Profit': 12000,	'CTP_Average': 0.8,	'Margin_Average': 0.2}),
('AR2',		                {'Profit': 11001,	'CTP_Average': 0.8,	'Margin_Average': 0.2}),
('SE Cambria Gate',		    {'Profit': 8100,	'CTP_Average': 0.8,	'Margin_Average': 0.2}),
('N Prev Clearing S',		{'Profit': 475000,	'CTP_Average': 0.9,	'Margin_Average': 0.2}),
('AR0',		                {'Profit': 150000,	'CTP_Average': 0.9,	'Margin_Average': 0.2}),
('NE Outpost Close',		{'Profit': 70000,	'CTP_Average': 0.9,	'Margin_Average': 0.2}),
('SW Prev Clearing SW',		{'Profit': 20000,	'CTP_Average': 0.9,	'Margin_Average': 0.2}),
('Minotaur Island',		    {'Profit': 16407,	'CTP_Average': 0.9,	'Margin_Average': 0.2}),
('AR7',		                {'Profit': 12001,	'CTP_Average': 0.9,	'Margin_Average': 0.2}),
('S Prev Xroad N',		    {'Profit': 12000,	'CTP_Average': 0.9,	'Margin_Average': 0.2}),
('SW Prev Clearing SE',		{'Profit': 11251,	'CTP_Average': 0.9,	'Margin_Average': 0.2}),
('N Prev Clearing W',		{'Profit': 375000,	'CTP_Average': 0.9,	'Margin_Average': 0.1}),
('AR4',		                {'Profit': 20000,	'CTP_Average': 0.9,	'Margin_Average': 0.1}),
('Prev Gate',		        {'Profit': 20000,	'CTP_Average': 0.9,	'Margin_Average': 0.1}),
('NE Outpost Far',		    {'Profit': 13000,	'CTP_Average': 0.9,	'Margin_Average': 0.1}),
("S of Anchor's Rest",		{'Profit': 12000,	'CTP_Average': 0.9,	'Margin_Average': 0.1}),
('N Prevalia Sandbar',		{'Profit': 10000,	'CTP_Average': 0.9,	'Margin_Average': 0.1}),
('N Terran Clearing',		{'Profit': 8000,	'CTP_Average': 0.9,	'Margin_Average': 0.1}),
('Frozen Ruins SE',		    {'Profit': 3000,	'CTP_Average': 0.9,	'Margin_Average': 0.1})
]


# Define the max and min for each metric
max_profit = 737500
min_profit = 3000
max_ctp = 0.8
min_ctp = 0.6
max_margin = 0.8 
min_margin = 0.2

# Define the weights
w_profit = 0.65
w_ctp = 0.2
w_margin = 0.15

# Normalize the metrics and calculate the weighted score for each location
scores = []
for loc, metrics in locations:
    norm_profit = (metrics['Profit'] - min_profit) / (max_profit - min_profit)
    norm_ctp = 1 - (metrics['CTP_Average'] - min_ctp) / (max_ctp - min_ctp)
    norm_margin = (metrics['Margin_Average'] - min_margin) / (max_margin - min_margin)
    
    weighted_score = (norm_profit * w_profit) + (norm_ctp * w_ctp) + (norm_margin * w_margin)
    scores.append((loc, weighted_score, (norm_profit,norm_ctp,norm_margin)))

# Sort the locations by the weighted score in descending order
sorted_locations = sorted(scores, key=lambda x: x[1], reverse=True)

for loc, score, metrics in sorted_locations:
    print(f"{loc:25}score: {score:5.2f}{f'':5}n_p: {metrics[0]:5.2f}{f'':5}n_ctp: {metrics[1]:5.2f}{f'':5}n_m: {metrics[2]:5.2f}")