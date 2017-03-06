#!/usr/bin/env python3

import re
import csv

from natsort import natsorted

filename=r"score_dump.csv"

"""
{'Username': 'LittleBigDej', 'Level Category': '63corvi', 'Level Number': '1', 'Level Name': 'QT-1',
 'Cycle Count': '20', 'Reactor Count': '1', 'Symbol Count': '5', 'Upload Time': '2013-08-15 10:23:14.329898', 'Youtube Link': ''}
"""

RNet_names_after_28 = "Cyanamide|Acetic Acid|Combustion Engine|Smelting Iron|Neodymium Magnet|Carbide Swap|Fuel Production|Siliconheart Piece|Raygun Mechanism|Sulfuric Acid|Fuming Nitric Acid|Rocket Fuel|Hydroxides|Nobility|Sortite|Radiation Treatment|Boron Compounds|Photovoltaic Cells|Elementary|Mixed Acids|Squaric Acid|Misproportioned|Narkotikum|Vereinheitlichung|Haber-Bosch|Mustard Oil|Nano Electric Motor|Count|Sharing is Caring|Reassembly|Cyanogen|Chloromethylsilane|Glyceraldehyde|Ethandiamin|Radikal|Kreisalkanol|Inorganic Pigments|Miller-Urey|Getting Pumped|Lewisite|Novichok|Ribulose|Knockout Drops|Strong Acids|Vitamin B3|1,2,3-Triphenol|1,3-Dimetoxibencene|Think in Spirals|Yellowcake|Thiourea|Downgrade|Wood Alcohol|Allyl Alcohol|Propargyl Alcohol|Condensation|Silane|Phosphine|Nuclear Medicine|Oxygen Supply|Red Cross|Fluoromethanes|Exercise|Nanoboxes" \
                     .split('|')

def tiebreak(this_score, best_score, stat1, stat2, stat3, stat4):
    return this_score[stat1] < best_score[stat1] or \
           (this_score[stat1] == best_score[stat1] and \
            (this_score[stat2] < best_score[stat2] or \
             (this_score[stat2] == best_score[stat2] and \
              (this_score[stat3] < best_score[stat3] or \
               (this_score[stat3] == best_score[stat3] and \
                this_score[stat4] < best_score[stat4]
               )
              )
             )
            )
           )

def printscore_vis(scores, category):
    score = scores[category]
    print('  {:29} U:{:14}  C:{:5} R:{:1} S:{:3}  T:{:26}  {}'.
          format(category, score['Username'],
                 score['Cycle Count'], score['Reactor Count'], score['Symbol Count'],
                 score['Upload Time'], 'Y:'+score['Youtube Link'] if score['Youtube Link'] else '')
         )


fmt_scores_with_bold = ['({}/{}/{}) {}', '(**{}**/{}/{}) {}', '({}/**{}**/{}) {}', '({}/{}/**{}**) {}']

def printscore(score, bold=0):
    fmt_score = fmt_scores_with_bold[bold].format(score['Cycle Count'], score['Reactor Count'], score['Symbol Count'],
                                                  score['Username'])
    if score['Youtube Link']:
        fmt_score = '[{}]({})'.format(fmt_score, score['Youtube Link'])
    print('| {:20}'.format(fmt_score),end=' ')


level_order = {'main':0, 'tf2':1, '63corvi':2, 'researchnet':3}

def reorder_levels(val):
    return (level_order[val[0][0]], val[0][1])


if __name__ == '__main__':
    
    levels = dict()
    
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            level_name = (row['Level Category'], row['Level Number'], row['Level Name'])
            this_score = {'Username': row['Username'],
                          'Cycle Count': int(row['Cycle Count']),
                          'Reactor Count': int(row['Reactor Count']),
                          'Symbol Count': int(row['Symbol Count']),
                          'Upload Time': row['Upload Time'],
                          'Youtube Link': row['Youtube Link']}
            
            # In, Out, 2 arrows, Swap = 5
            # In, Swap, Out /2 = 1.5
            if this_score['Symbol Count'] < 5*this_score['Reactor Count'] or \
               this_score['Cycle Count'] < 1.5*this_score['Reactor Count']:
                   continue
            
            if level_name not in levels:
                levels[level_name] = {}
                levels[level_name]['Least Cycles'] = this_score
                levels[level_name]['Least Symbols'] = this_score
                levels[level_name]['Least Cycles - Min Reactors'] = this_score
                levels[level_name]['Least Symbols - Min Reactors'] = this_score
            else:
                if tiebreak(this_score, levels[level_name]['Least Cycles'], 'Cycle Count', 'Reactor Count', 'Symbol Count', 'Upload Time'):
                    levels[level_name]['Least Cycles'] = this_score
                    
                if tiebreak(this_score, levels[level_name]['Least Symbols'], 'Symbol Count', 'Reactor Count', 'Cycle Count', 'Upload Time'):
                    levels[level_name]['Least Symbols'] = this_score
                
                if tiebreak(this_score, levels[level_name]['Least Cycles - Min Reactors'], 'Reactor Count', 'Cycle Count', 'Symbol Count', 'Upload Time'):
                    levels[level_name]['Least Cycles - Min Reactors'] = this_score
                    
                if tiebreak(this_score, levels[level_name]['Least Symbols - Min Reactors'], 'Reactor Count', 'Symbol Count', 'Cycle Count', 'Upload Time'):
                    levels[level_name]['Least Symbols - Min Reactors'] = this_score
    
    for name, scores in natsorted(levels.items(), key=reorder_levels):
        print('|{} - {} | Min Cycles | Min Symbols'.format(name[0], name[1]))
        match = re.match(r'ResearchNet Published (\d\d)-([1-3])', name[2])
        if match:
            realname = RNet_names_after_28[3*(int(match.group(1))-28)+int(match.group(2))-1]
        else:
            realname = name[2]
        print('|{:13} '.format(realname), end='')
        printscore(scores['Least Cycles'], bold=1)
        printscore(scores['Least Symbols'], bold=3)
        print()
        if scores['Least Cycles - Min Reactors'] != scores['Least Cycles'] or \
           scores['Least Symbols - Min Reactors'] != scores['Least Symbols']:
            print('|{} - N reactors '.format(realname), end='')
            printscore(scores['Least Cycles - Min Reactors'], bold=1)
            printscore(scores['Least Symbols - Min Reactors'], bold=3)
            print()
        print()
